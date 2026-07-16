"""Discover ``app/workflows/`` + ``app/activities/`` by **dotted import** (DR-0051).

Unlike arvel's listener/MCP-tool autoload (which loads by path via ``spec_from_file_location``),
workflow modules must be loaded under their **real dotted name** — Temporal's sandbox re-imports
the workflow module *by name* each run to enforce determinism, and a synthetic
``_arvel_..._<stem>`` name is not re-importable. The app base is already on ``sys.path`` in a booted
arvel app (the console kernel adds cwd), so ``importlib.import_module('app.workflows.<stem>')``
resolves. Modules self-register via ``@workflow``/``@activity`` when they execute.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def _discover_dir(base_path: str, rel: str) -> None:
    directory = Path(base_path) / rel
    if not directory.is_dir():
        return
    module_prefix = rel.replace("/", ".").replace("\\", ".")
    for file in sorted(directory.glob("*.py")):
        if file.stem.startswith("_"):
            continue
        importlib.import_module(f"{module_prefix}.{file.stem}")


def discover(
    base_path: str,
    workflows_dir: str = "app/workflows",
    activities_dir: str = "app/activities",
) -> None:
    """Load activity modules first (so a workflow's ``from app.activities... import`` is already
    cached), then workflow modules. Both fill the registry as a side effect of importing."""
    _discover_dir(base_path, activities_dir)
    _discover_dir(base_path, workflows_dir)
