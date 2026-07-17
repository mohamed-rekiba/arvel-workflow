"""Unit tests for the pure logic. The Temporal integration (sandbox, worker, real run-to-completion)
is exercised by the example (example/acceptance.py) against a live test server, not mocked here."""

from __future__ import annotations

import sys
from pathlib import Path

from arvel_workflow.facade import WorkflowHandle
from arvel_workflow.settings import WorkflowSettings


def test_settings_defaults() -> None:
    s = WorkflowSettings.from_source(None)
    assert (s.target, s.namespace, s.task_queue) == ("localhost:7233", "default", "arvel")


def test_settings_override() -> None:
    s = WorkflowSettings.from_source({"task_queue": "billing", "target": "temporal:7233"})
    assert s.task_queue == "billing" and s.target == "temporal:7233"


def test_workflow_handle_carries_id() -> None:
    assert WorkflowHandle("wf-1").id == "wf-1"


def test_autoload_is_dotted_and_skips_underscored(tmp_path: Path) -> None:
    # a temp app/activities package; the loader imports by DOTTED name
    (tmp_path / "app" / "activities").mkdir(parents=True)
    (tmp_path / "app" / "__init__.py").write_text("")
    (tmp_path / "app" / "activities" / "__init__.py").write_text("")
    (tmp_path / "app" / "activities" / "ping.py").write_text("LOADED = True\n")
    (tmp_path / "app" / "activities" / "_skip.py").write_text("raise RuntimeError('must not load')\n")
    sys.path.insert(0, str(tmp_path))
    try:
        from arvel_workflow.autoload import _discover_dir

        _discover_dir(str(tmp_path), "app/activities")  # must not raise (skips _skip.py)
        import app.activities.ping as ping  # dotted import worked → module is importable by name

        assert ping.LOADED is True
    finally:
        sys.path.remove(str(tmp_path))
        for m in [m for m in list(sys.modules) if m == "app" or m.startswith("app.")]:
            del sys.modules[m]


def test_autoload_missing_dir_is_noop() -> None:
    from arvel_workflow.autoload import discover

    discover("/nonexistent")  # must not raise
