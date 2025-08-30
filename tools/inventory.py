"""Inventory tool: build an AST-based import graph and report reachable modules.

Usage: python tools/inventory.py > tools/inventory_result.json

This tool does not execute project code; it statically parses .py files and follows imports.
It marks modules reachable from entrypoints: spypoint_api.__init__, spypoint_api.client, tests/, examples/.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT


def iter_py_files(root: Path):
    for p in root.rglob("*.py"):
        # skip virtualenv or hidden dirs
        if any(part.startswith(".") or part in ("venv", ".venv") for part in p.parts):
            continue
        yield p


def module_name_from_path(p: Path) -> str:
    try:
        rel = p.relative_to(ROOT)
    except Exception:
        rel = p
    return str(rel).replace("/", ".").rstrip(".py")


def parse_imports(path: Path) -> Set[str]:
    text = path.read_text(encoding="utf8")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    imports: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports


def build_graph() -> Tuple[Dict[str, Set[str]], Dict[str, Path]]:
    graph: Dict[str, Set[str]] = {}
    paths: Dict[str, Path] = {}
    for p in iter_py_files(SRC):
        mod = module_name_from_path(p)
        paths[mod] = p
        graph[mod] = parse_imports(p)
    return graph, paths


def reachable_from(entry: List[str], graph: Dict[str, Set[str]]) -> Set[str]:
    seen: Set[str] = set()
    stack = list(entry)
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for child in graph.get(cur, []):
            if child not in seen:
                stack.append(child)
    return seen


def find_entrypoints(paths: Dict[str, Path]) -> List[str]:
    entries = []
    # canonical entries
    for candidate in ("spypoint_api.__init__", "spypoint_api.client", "spypointapi.client", "spypointapi.__init__"):
        if candidate in paths:
            entries.append(candidate)
    # include tests and examples modules
    for mod, p in paths.items():
        if str(p).startswith(str(ROOT / "tests")) or str(p).startswith(str(ROOT / "test")) or str(p).startswith(str(ROOT / "examples")):
            entries.append(mod)
    return sorted(set(entries))


def main():
    graph, paths = build_graph()
    entries = find_entrypoints(paths)
    reachable = reachable_from(entries, graph)
    all_modules = set(paths.keys())
    candidates = sorted(list(all_modules - reachable))
    result = {
        "root": str(ROOT),
        "entries": entries,
        "reachable_count": len(reachable),
        "all_count": len(all_modules),
        "reachable": sorted(list(reachable)),
        "candidates": candidates,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
