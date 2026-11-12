"""Shared utilities: SWE-bench instance loading, repo access at a commit, gold-edit labels.

No model code here. Everything is deterministic and offline once the repos are cloned.
"""
from __future__ import annotations

import ast
import json
import subprocess
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from unidiff import PatchSet

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPOS = DATA / "repos"
import os as _os

# NULLEDIT_RESULTS lets the analysis read another arm's outputs (e.g. results_dgx/) without code changes
RESULTS = Path(_os.environ.get("NULLEDIT_RESULTS", ROOT / "results"))


def load_instances(path: Path | None = None) -> list[dict]:
    path = path or DATA / "swebench_verified.jsonl"
    return [json.loads(l) for l in open(path)]


def repo_dir(repo: str) -> Path:
    return REPOS / repo.replace("/", "_")


def git(repo: str, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo_dir(repo)), *args],
        capture_output=True,
        check=True,
    )
    return out.stdout.decode("utf-8", errors="replace")


@lru_cache(maxsize=4096)
def file_at(repo: str, commit: str, path: str) -> str:
    """File content at a commit: local clone if present, else raw.githubusercontent (disk-cached)."""
    if repo_dir(repo).exists():
        try:
            return git(repo, "show", f"{commit}:{path}")
        except Exception:
            pass  # clone missing/incomplete: fall back to the raw file
    cache = DATA / "filecache" / repo.replace("/", "_") / commit / path
    if cache.exists():
        return cache.read_text(encoding="utf-8", errors="replace")
    import urllib.request

    url = f"https://raw.githubusercontent.com/{repo}/{commit}/{path}"
    with urllib.request.urlopen(url, timeout=60) as r:
        txt = r.read().decode("utf-8", errors="replace")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(txt, encoding="utf-8")
    return txt


@lru_cache(maxsize=64)
def list_py_files(repo: str, commit: str) -> tuple[str, ...]:
    out = git(repo, "ls-tree", "-r", "--name-only", commit)
    return tuple(p for p in out.splitlines() if p.endswith(".py"))


def is_test_path(p: str) -> bool:
    parts = p.lower().split("/")
    name = parts[-1]
    return (
        any(x in ("tests", "test", "testing") for x in parts[:-1])
        or name.startswith("test_")
        or name.endswith("_test.py")
        or name == "conftest.py"
    )


@dataclass
class GoldFile:
    path: str
    # 1-based line numbers in the ORIGINAL (pre-fix) file that the gold patch touches.
    # Removed/modified lines are listed directly. A pure insertion is represented by
    # its two neighbouring original lines (the line before and the line after).
    lines: set[int] = field(default_factory=set)
    # subset of `lines` that were actually removed/modified (not insertion anchors)
    removed: set[int] = field(default_factory=set)
    n_added: int = 0
    n_removed: int = 0


def gold_edits(patch_text: str) -> dict[str, GoldFile]:
    """Parse a unified diff into per-file sets of touched original line numbers."""
    out: dict[str, GoldFile] = {}
    for pf in PatchSet(patch_text):
        if pf.is_added_file:
            continue
        g = GoldFile(path=pf.path)
        for hunk in pf:
            src_line = hunk.source_start
            prev_src = max(hunk.source_start - 1, 0)
            lines = list(hunk)
            i = 0
            while i < len(lines):
                ln = lines[i]
                if ln.is_context:
                    prev_src = ln.source_line_no
                    i += 1
                    continue
                # a change block: consecutive removed/added lines
                rem, add = [], 0
                while i < len(lines) and not lines[i].is_context:
                    if lines[i].is_removed:
                        rem.append(lines[i].source_line_no)
                    elif lines[i].is_added:
                        add += 1
                    i += 1
                g.n_added += add
                g.n_removed += len(rem)
                if rem:
                    g.lines.update(rem)
                    g.removed.update(rem)
                    prev_src = rem[-1]
                else:
                    # pure insertion between prev_src and prev_src + 1
                    if prev_src >= 1:
                        g.lines.add(prev_src)
                    g.lines.add(prev_src + 1)
        if g.lines:
            out[pf.path] = g
    return out


@dataclass
class Unit:
    """A function/method (or module-level remainder) of a source file."""

    name: str
    start: int  # 1-based inclusive
    end: int  # 1-based inclusive
    kind: str  # "function" | "class_header" | "module"


def function_units(source: str) -> list[Unit]:
    """Outermost function and method spans (nested defs belong to the enclosing function).

    Lines not covered by any def are grouped into residual "gap" units by units_with_module()."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return []
    units: list[Unit] = []

    def visit(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = min([child.lineno] + [d.lineno for d in child.decorator_list])
                units.append(Unit(prefix + child.name, start, child.end_lineno, "function"))
                # nested defs are part of the enclosing function unit
            elif isinstance(child, ast.ClassDef):
                visit(child, prefix + child.name + ".")
            else:
                visit(child, prefix)

    visit(tree)
    units.sort(key=lambda u: u.start)
    return units


def unit_of_line(units: list[Unit], line: int) -> int | None:
    for i, u in enumerate(units):
        if u.start <= line <= u.end:
            return i
    return None
