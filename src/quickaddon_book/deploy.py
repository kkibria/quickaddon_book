#!/usr/bin/env python3
"""
deploy_ghpages.py

Disposable GitHub Pages deploy for mdBook projects.

Philosophy:
- main branch is source of truth
- gh-pages is an artifact channel (no history needed)
- every deploy creates a fresh orphan commit and force-pushes it

Key behaviors:
- Must run from git repo root (cwd == git rev-parse --show-toplevel)
- Must have book.toml in cwd
- Reads [build].build-dir from book.toml
- Requires build-dir to be "gh-pages/docs" (or under "gh-pages/...", but we enforce docs by default)
- Runs `mdbook build`
- Audits deploy_root using project_root/deploy.toml via audit(project_root, deploy_root)
- Creates a temporary git worktree, wipes it, copies only audited files into `docs/`
- Commits and `git push -f origin gh-pages`

Dry run:
- `--dry-run` prints audited file list and exits (no git mutation)

Requires:
- git, mdbook on PATH
- audit_deploy.py (same folder or importable) providing:
    - audit(project_root, deploy_root) -> list[str] (paths relative to deploy_root)
    - DeployTomlNotFoundError
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .audit_deploy import audit, DeployTomlNotFoundError

BRANCH = "gh-pages"
BOOK_TOML = "book.toml"


class DeployError(RuntimeError):
    pass


def which_or_die(exe: str) -> None:
    if shutil.which(exe) is None:
        raise DeployError(f"Missing required command on PATH: {exe}")


def run(cmd: list[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        pretty = " ".join(cmd)
        raise DeployError(
            f"Command failed: {pretty}\n"
            f"cwd: {cwd or Path.cwd()}\n"
            f"exit: {e.returncode}\n"
            f"stdout:\n{e.stdout}\n"
            f"stderr:\n{e.stderr}"
        ) from e


def git_output(args: list[str], cwd: Optional[Path] = None) -> str:
    return run(["git", *args], cwd=cwd).stdout.strip()


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


@dataclass(frozen=True)
class BuildPaths:
    build_dir_raw: str
    deploy_root: Path  # absolute path to build output (e.g. <repo>/gh-pages/docs)


def compute_deploy_root(repo_root: Path, build_dir: str) -> BuildPaths:
    norm = build_dir.replace("\\", "/").strip().strip("/")
    # Enforce gh-pages/docs as safest contract (matches your GitHub Pages settings: branch gh-pages, folder /docs)
    if norm != "gh-pages/docs":
        raise DeployError(
            f"Refusing to deploy: build-dir is '{build_dir}', expected exactly 'gh-pages/docs'.\n"
            "Reason: simplest, safest publish contract (branch=gh-pages, folder=/docs)."
        )
    deploy_root = (repo_root / "gh-pages" / "docs").resolve()
    return BuildPaths(build_dir_raw=build_dir, deploy_root=deploy_root)


def purge_worktree_contents(worktree: Path) -> None:
    # Remove everything except .git
    for entry in worktree.iterdir():
        if entry.name == ".git":
            continue
        if entry.is_dir():
            shutil.rmtree(entry, ignore_errors=True)
        else:
            try:
                entry.unlink()
            except FileNotFoundError:
                pass


def copy_audited_files(
    deploy_root: Path,
    audited_relpaths: list[str],
    worktree: Path,
) -> None:
    """
    Copies files from deploy_root/<relpath> into worktree/docs/<relpath>
    """
    docs_root = worktree / "docs"
    docs_root.mkdir(parents=True, exist_ok=True)

    for rel in audited_relpaths:
        rel_norm = rel.replace("\\", "/").lstrip("/")
        src = deploy_root / rel_norm
        if not src.is_file():
            # If audit returned a non-existent file, that's a policy mismatch; fail fast.
            raise DeployError(f"Audit listed file that does not exist: {src}")
        dst = docs_root / rel_norm
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def make_worktree(repo_root: Path) -> Path:
    """
    Creates a temporary worktree for BRANCH.
    Returns the worktree path.
    """
    tmpdir = Path(tempfile.mkdtemp(prefix="ghpages_worktree_")).resolve()
    # Create/update local branch ref for worktree usage; doesn't matter what it points to (we will orphan reset).
    run(["git", "worktree", "add", "-B", BRANCH, str(tmpdir)], cwd=repo_root)
    return tmpdir


def remove_worktree(repo_root: Path, worktree: Path) -> None:
    try:
        run(["git", "worktree", "remove", "-f", str(worktree)], cwd=repo_root, check=False)
    finally:
        shutil.rmtree(worktree, ignore_errors=True)


def deploy_disposable(
    repo_root: Path,
    deploy_root: Path,
    audited_relpaths: list[str],
    dry_run: bool,
) -> None:
    if dry_run:
        print(f"DRY RUN: deploy_root={deploy_root}")
        print(f"DRY RUN: audited_files={len(audited_relpaths)}")
        for p in audited_relpaths:
            print(p)
        return

    origin_url = git_output(["remote", "get-url", "origin"], cwd=repo_root)
    if not origin_url:
        raise DeployError("Could not determine 'origin' remote URL from the main repo.")

    worktree = make_worktree(repo_root)
    try:
        # Ensure we are on the gh-pages branch
        run(["git", "checkout", BRANCH], cwd=worktree)

        # Remove everything from index and working tree except .git
        run(["git", "rm", "-rf", "."], cwd=worktree)
        purge_worktree_contents(worktree)

        # Copy only audited files into docs/
        copy_audited_files(deploy_root=deploy_root, audited_relpaths=audited_relpaths, worktree=worktree)

        # Ensure .nojekyll exists (even if policy forgot it)
        (worktree / "docs" / ".nojekyll").touch()

        # Stage and commit
        run(["git", "add", "-A"], cwd=worktree)
        status = git_output(["status", "--porcelain"], cwd=worktree)
        if not status.strip():
            print("No changes to deploy.")
            return

        run(["git", "commit", "-m", "deploy"], cwd=worktree)

        # Force push (artifact channel)
        run(["git", "push", "-f", "origin", BRANCH], cwd=worktree)
        print(f"Deployed '{deploy_root}' to branch '{BRANCH}' (single-commit artifact).")

    finally:
        remove_worktree(repo_root, worktree)


def main() -> int:
    try:
        which_or_die("git")
        which_or_die("mdbook")

        parser = argparse.ArgumentParser()
        parser.add_argument("--dry-run", action="store_true", help="Audit and print staged file list; do not push.")
        args = parser.parse_args()

        repo_root = Path.cwd()
        enforce_repo_root(repo_root)

        book_toml = repo_root / BOOK_TOML
        build_dir = parse_mdbook_build_dir(book_toml)
        paths = compute_deploy_root(repo_root, build_dir)

        # Build
        run(["mdbook", "build"], cwd=repo_root)

        if not paths.deploy_root.exists():
            raise DeployError(f"Build output not found: {paths.deploy_root}")

        # Audit
        try:
            audited = audit(project_root=repo_root, deploy_root=paths.deploy_root)
        except DeployTomlNotFoundError as e:
            raise DeployError(str(e)) from e

        # Deploy
        deploy_disposable(
            repo_root=repo_root,
            deploy_root=paths.deploy_root,
            audited_relpaths=audited,
            dry_run=args.dry_run,
        )

        return 0

    except DeployError as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())