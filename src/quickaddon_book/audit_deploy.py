# audit_deploy.py
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Set

import os

try:
    import tomllib  # py3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore


class DeployTomlNotFoundError(FileNotFoundError):
    pass


class DeployTomlError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeployPolicy:
    """
    Policy is allow-list + blacklist.

    Allow checks (in order):
      - explicit allow_files (exact relative paths)
      - allow_dotfiles (basename match, e.g. ".nojekyll")
      - allow_exts (by suffix)
      - allow_globs (relative glob patterns, optional)

    Deny checks:
      - blacklist_basenames (basename match, e.g. ".DS_Store")
      - deny_globs (relative glob patterns, optional)

    Returned file list is sorted, POSIX paths relative to deploy_root.
    """
    allow_exts: Set[str]
    allow_dotfiles: Set[str]
    allow_files: Set[str]
    allow_globs: List[str]

    blacklist_basenames: Set[str]
    deny_globs: List[str]


DEFAULT_POLICY = DeployPolicy(
    allow_exts={
        ".html", ".htm",
        ".css",
        ".js", ".mjs",
        ".json",
        ".xml",
        ".txt",
        ".svg",
        ".png", ".jpg", ".jpeg", ".webp", ".gif",
        ".ico",
        ".woff", ".woff2", ".ttf", ".otf", ".eot",
        ".map",
        ".pdf",
    },
    allow_dotfiles={".nojekyll"},
    allow_files=set(),
    allow_globs=[],
    blacklist_basenames={".DS_Store", "Thumbs.db"},
    deny_globs=[],
)


def _load_toml(path: Path) -> dict:
    if tomllib is None:
        raise DeployTomlError("Python 3.11+ required (tomllib missing).")
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise DeployTomlError(f"Failed to parse {path}: {e}") from e


def load_policy(project_root: Path) -> DeployPolicy:
    """
    Reads project_root/deploy.toml

    Expected shape:

      [deploy.audit]
      allow_exts = [".html", ".css", ...]
      allow_dotfiles = [".nojekyll"]
      allow_files = ["searchindex.js", "robots.txt"]
      allow_globs = ["css/**", "fonts/**"]
      blacklist_basenames = [".DS_Store", "Thumbs.db"]
      deny_globs = ["**/.git/**"]

    Any missing fields fall back to defaults.
    """
    deploy_toml = project_root / "deploy.toml"
    if not deploy_toml.exists():
        raise DeployTomlNotFoundError(f"deploy.toml not found at: {deploy_toml}")

    data = _load_toml(deploy_toml)

    audit = (data.get("deploy", {}) or {}).get("audit", {}) or {}

    def _get_list(key: str) -> list[str]:
        v = audit.get(key, None)
        if v is None:
            return []
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            raise DeployTomlError(f"deploy.toml: [deploy.audit].{key} must be a list of strings")
        return v

    allow_exts = set(x.lower() for x in (_get_list("allow_exts") or list(DEFAULT_POLICY.allow_exts)))
    allow_dotfiles = set(_get_list("allow_dotfiles") or list(DEFAULT_POLICY.allow_dotfiles))
    allow_files = set(_normalize_rel(x) for x in _get_list("allow_files"))
    allow_globs = _get_list("allow_globs")

    blacklist_basenames = set(_get_list("blacklist_basenames") or list(DEFAULT_POLICY.blacklist_basenames))
    deny_globs = _get_list("deny_globs")

    return DeployPolicy(
        allow_exts=allow_exts,
        allow_dotfiles=allow_dotfiles,
        allow_files=allow_files,
        allow_globs=allow_globs,
        blacklist_basenames=blacklist_basenames,
        deny_globs=deny_globs,
    )


def _normalize_rel(p: str) -> str:
    # normalize to POSIX-style relative path without leading "./" or "/"
    p2 = p.replace("\\", "/").lstrip("/")
    if p2.startswith("./"):
        p2 = p2[2:]
    return p2


def _rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _match_any_glob(rel_posix: str, patterns: Iterable[str]) -> bool:
    # relative glob match against POSIX paths
    p = Path(rel_posix)
    for pat in patterns:
        pat_norm = _normalize_rel(pat)
        if p.match(pat_norm):
            return True
    return False


def audit(project_root: Path | str, deploy_root: Path | str) -> list[str]:
    """
    High-level contract:

      audit(project_root, deploy_root) -> list[str]

    - Recurses deploy_root
    - Applies filter rules from project_root/deploy.toml
    - Returns list of files relative to deploy_root (POSIX paths)
    - Raises DeployTomlNotFoundError if deploy.toml missing
    """
    project_root = Path(project_root).resolve()
    deploy_root = Path(deploy_root).resolve()

    policy = load_policy(project_root)

    if not deploy_root.exists():
        raise DeployTomlError(f"deploy_root does not exist: {deploy_root}")
    if not deploy_root.is_dir():
        raise DeployTomlError(f"deploy_root is not a directory: {deploy_root}")

    out: list[str] = []

    for p in deploy_root.rglob("*"):
        if not p.is_file():
            continue

        rel = _rel_posix(p, deploy_root)
        base = p.name

        # blacklist basenames always denied
        if base in policy.blacklist_basenames:
            continue

        # deny globs (relative to deploy_root)
        if policy.deny_globs and _match_any_glob(rel, policy.deny_globs):
            continue

        # explicit allow files
        if rel in policy.allow_files:
            out.append(rel)
            continue

        # allow dotfiles only if whitelisted
        if base.startswith("."):
            if base in policy.allow_dotfiles:
                out.append(rel)
            continue

        # allow globs (relative path patterns like "css/**")
        if policy.allow_globs and _match_any_glob(rel, policy.allow_globs):
            out.append(rel)
            continue

        # allow extensions
        if p.suffix.lower() in policy.allow_exts:
            out.append(rel)

    out.sort()
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".", help="Project root containing deploy.toml")
    ap.add_argument("--deploy-root", required=True, help="Folder to audit (e.g. gh-pages/docs)")
    ap.add_argument("--print", action="store_true", help="Print audited file list")
    args = ap.parse_args()

    try:
        files = audit(Path(args.project_root), Path(args.deploy_root))
    except DeployTomlNotFoundError as e:
        print(str(e))
        return 2

    if args.print:
        for f in files:
            print(f)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())