#!/usr/bin/env python3
"""
deploy_ghpages.py

Cross-platform GitHub Pages deploy for mdBook projects.

Guards (seatbelts):
1) Must be run from the git repo root (cwd == git rev-parse --show-toplevel).
2) Must have book.toml in cwd.
3) Must have explicit [build].build-dir in book.toml.
4) build-dir must be either "gh-pages" or start with "gh-pages/".
5) Refuse if the pages repo dir (gh-pages) is tracked by the main repo.
6) Warn (but do not refuse) if the pages repo dir (gh-pages) is not ignored.

Deploy behavior:
- Runs `mdbook build`.
- Uses first component of build-dir as pages repo dir (gh-pages).
- Uses remainder as content subpath (e.g. docs).
- Ensures gh-pages/.git exists, origin matches main repo origin,
  ensures branch gh-pages exists (orphan init if needed),
  stages only the content subtree, commits if changed, pushes.

Requirements:
- git on PATH
- mdbook on PATH
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


BRANCH = "gh-pages"
BOOK_TOML = "book.toml"


class DeployError(RuntimeError):
    pass


def run(cmd: list[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    pretty = " ".join(shlex.quote(c) for c in cmd)
    try:
        cp = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return cp
    except subprocess.CalledProcessError as e:
        raise DeployError(
            f"Command failed: {pretty}\n"
            f"cwd: {cwd or Path.cwd()}\n"
            f"exit: {e.returncode}\n"
            f"stdout:\n{e.stdout}\n"
            f"stderr:\n{e.stderr}"
        ) from e


def which_or_die(exe: str) -> None:
    from shutil import which

    if which(exe) is None:
        raise DeployError(f"Missing required command on PATH: {exe}")


@dataclass(frozen=True)
class BuildPaths:
    build_dir_raw: str
    pages_repo_dir: Path
    content_subpath: Path


def git_output(args: list[str], cwd: Optional[Path] = None) -> str:
    cp = run(["git", *args], cwd=cwd)
    return cp.stdout.strip()


def git_try(args: list[str], cwd: Optional[Path] = None) -> bool:
    try:
        run(["git", *args], cwd=cwd, check=True)
        return True
    except DeployError:
        return False

def copy_main_gitignore(main_repo: Path, pages_repo: Path) -> None:
    src = main_repo / ".gitignore"
    dst = pages_repo / ".gitignore"

    if not src.exists():
        return  # nothing to copy

    # Always overwrite to keep them in sync
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

def enforce_repo_root(cwd: Path) -> None:
    top = git_output(["rev-parse", "--show-toplevel"], cwd=cwd)
    top_path = Path(top).resolve()
    cwd_path = cwd.resolve()
    if top_path != cwd_path:
        raise DeployError(
            "Refusing to run: not in git repo root.\n"
            f"Repo root: {top_path}\n"
            f"Current:   {cwd_path}\n"
            "cd to the repo root and run again."
        )


def parse_mdbook_build_dir(book_toml_path: Path) -> str:
    if not book_toml_path.is_file():
        raise DeployError("book.toml not found in current directory. Aborting.")

    in_build = False
    build_dir: Optional[str] = None

    section_re = re.compile(r"^\[(.+?)\]\s*$")
    key_re = re.compile(r'^\s*build-dir\s*=\s*"(.*)"\s*$')

    for raw in book_toml_path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue

        msec = section_re.match(line)
        if msec:
            in_build = (msec.group(1).strip() == "build")
            continue

        if in_build:
            mk = key_re.match(line)
            if mk:
                build_dir = mk.group(1).strip()
                break

    if not build_dir:
        raise DeployError(
            "No [build].build-dir found in book.toml.\n"
            "This deploy script requires an explicit build-dir under gh-pages/ (e.g. gh-pages/docs)."
        )

    return build_dir


def enforce_seatbelt(build_dir: str) -> None:
    norm = build_dir.replace("\\", "/").strip().strip("/")
    if norm == BRANCH or norm.startswith(f"{BRANCH}/"):
        return
    raise DeployError(
        f"Refusing to deploy: build-dir is '{build_dir}', which is not '{BRANCH}' or under '{BRANCH}/'.\n"
        f"Fix book.toml [build].build-dir to '{BRANCH}/docs' (recommended) or '{BRANCH}'."
    )


def compute_paths(build_dir: str) -> BuildPaths:
    norm = build_dir.replace("\\", "/").strip().strip("/")
    parts = [p for p in norm.split("/") if p]
    if not parts:
        raise DeployError(f"Unexpected build-dir value: {build_dir!r}")
    pages_repo = Path(parts[0])
    content = Path(".") if len(parts) == 1 else Path(*parts[1:])
    return BuildPaths(build_dir_raw=build_dir, pages_repo_dir=pages_repo, content_subpath=content)


def guard_pages_dir_not_tracked_and_warn_if_not_ignored(cwd: Path, pages_dir: Path) -> None:
    # Refuse if tracked
    tracked = git_output(["ls-files", "--", str(pages_dir)], cwd=cwd)
    if tracked.strip():
        sample = "\n".join(tracked.splitlines()[:10])
        raise DeployError(
            f"Refusing to deploy: '{pages_dir}' is tracked by the main repo.\n"
            "This will cause nested-repo headaches.\n"
            "Tracked examples:\n"
            f"{sample}\n"
            f"Fix:\n"
            f"  git rm -r --cached {pages_dir}\n"
            f"  echo {pages_dir}/ >> .gitignore\n"
            f"  git add .gitignore && git commit -m \"Ignore {pages_dir}/\"\n"
        )

    # Warn if not ignored (non-fatal)
    ignored = git_try(["check-ignore", "-q", str(pages_dir)], cwd=cwd)
    if not ignored:
        print(
            f"WARNING: '{pages_dir}' is not ignored by the main repo.\n"
            "It’s easy to accidentally stage generated site output on your main branch.\n"
            f"Recommended: add '{pages_dir}/' to .gitignore.\n",
            file=sys.stderr,
        )


def ensure_pages_repo(pages_repo: Path, origin_url: str) -> None:
    pages_repo.mkdir(parents=True, exist_ok=True)

    if not (pages_repo / ".git").exists():
        run(["git", "init"], cwd=pages_repo)

    copy_main_gitignore(Path.cwd(), pages_repo)
    run(["git", "add", ".gitignore"], cwd=pages_repo)

    existing_origin: Optional[str]
    try:
        existing_origin = git_output(["remote", "get-url", "origin"], cwd=pages_repo)
    except DeployError:
        existing_origin = None

    if not existing_origin:
        run(["git", "remote", "add", "origin", origin_url], cwd=pages_repo)
    elif existing_origin != origin_url:
        run(["git", "remote", "set-url", "origin", origin_url], cwd=pages_repo)

    try:
        run(["git", "fetch", "origin", "--prune"], cwd=pages_repo)
    except DeployError:
        pass


def ensure_branch_checked_out(pages_repo: Path) -> None:
    local_has = git_try(["show-ref", "--verify", "--quiet", f"refs/heads/{BRANCH}"], cwd=pages_repo)
    remote_has = git_try(["show-ref", "--verify", "--quiet", f"refs/remotes/origin/{BRANCH}"], cwd=pages_repo)

    if local_has:
        run(["git", "checkout", BRANCH], cwd=pages_repo)
    elif remote_has:
        run(["git", "checkout", "-b", BRANCH, "--track", f"origin/{BRANCH}"], cwd=pages_repo)
    else:
        run(["git", "checkout", "--orphan", BRANCH], cwd=pages_repo)

        for entry in pages_repo.iterdir():
            if entry.name == ".git":
                continue
            if entry.is_dir():
                for root, dirs, files in os.walk(entry, topdown=False):
                    for f in files:
                        Path(root, f).unlink(missing_ok=True)
                    for d in dirs:
                        Path(root, d).rmdir()
                entry.rmdir()
            else:
                entry.unlink(missing_ok=True)

        (pages_repo / "README.txt").write_text("GitHub Pages branch\n", encoding="utf-8")
        run(["git", "add", "-A"], cwd=pages_repo)
        run(["git", "commit", "-m", "Initialize gh-pages"], cwd=pages_repo)

    if remote_has:
        try:
            run(["git", "pull", "--rebase", "origin", BRANCH], cwd=pages_repo)
        except DeployError:
            pass


def stage_commit_push(pages_repo: Path, content_subpath: Path, build_dir_raw: str) -> None:
    content_abs = pages_repo if content_subpath == Path(".") else pages_repo / content_subpath
    if not content_abs.exists():
        raise DeployError(
            f"Expected content folder '{content_abs}' not found.\n"
            f"mdBook build-dir is '{build_dir_raw}'."
        )

    run(["git", "add", "-A", "--", str(content_subpath)], cwd=pages_repo)

    status = git_output(["status", "--porcelain"], cwd=pages_repo)
    if not status.strip():
        print(f"No changes to deploy (content: {build_dir_raw}).")
        return

    from datetime import datetime

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run(["git", "commit", "-m", f"deploy: {stamp}"], cwd=pages_repo)
    run(["git", "push", "origin", BRANCH], cwd=pages_repo)
    print(f"Deployed '{build_dir_raw}' on branch '{BRANCH}'.")


def main() -> int:
    try:
        which_or_die("git")
        which_or_die("mdbook")

        cwd = Path.cwd()
        enforce_repo_root(cwd)

        book_toml_path = cwd / BOOK_TOML
        if not book_toml_path.is_file():
            raise DeployError("book.toml not found in current directory. Aborting.")

        build_dir = parse_mdbook_build_dir(book_toml_path)
        enforce_seatbelt(build_dir)
        paths = compute_paths(build_dir)

        # Guard against nested-repo footguns
        guard_pages_dir_not_tracked_and_warn_if_not_ignored(cwd, paths.pages_repo_dir)

        origin_url = git_output(["remote", "get-url", "origin"], cwd=cwd)
        if not origin_url:
            raise DeployError("Could not determine 'origin' remote URL from the main repo.")

        # Build
        run(["mdbook", "build"], cwd=cwd)

        # Setup pages repo + branch
        ensure_pages_repo(paths.pages_repo_dir, origin_url)
        ensure_branch_checked_out(paths.pages_repo_dir)

        # Deploy only the content subtree (e.g. docs/)
        stage_commit_push(paths.pages_repo_dir, paths.content_subpath, paths.build_dir_raw)

        return 0

    except DeployError as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())