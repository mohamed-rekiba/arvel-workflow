"""``@workflow`` / ``@activity`` and the one Phase-0 workflow verb, ``run_activity``.

The engine (``temporalio``) is **lazy-imported** here, so ``import arvel_workflow`` for the
settings/facade surface never drags it in (dependency rule, DR-0050) — the import only fires
when an actual workflow/activity module loads (the worker process).

Phase 0 keeps the workflow body's activity call as a module-level helper (``run_activity``)
rather than an injected ``ctx.run`` — the ``ctx`` sugar and per-activity timeout/retry are
Phase-1 refinements. Either way, app code imports no ``temporalio``.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from .registry import ACTIVITIES, WORKFLOWS

_DEFAULT_ACTIVITY_TIMEOUT = timedelta(seconds=30)  # Phase 0: hardcoded (timeout sugar is Phase 1)


def workflow(cls: type) -> type:
    """Mark a class as a durable workflow. Applies Temporal's ``@workflow.defn`` to the class and
    ``@workflow.run`` to its ``run`` method, and records it so the worker autoloads it."""
    from temporalio import workflow as _twf

    run = getattr(cls, "run", None)
    if run is None:
        raise TypeError(f"@workflow {cls.__name__} needs an `async def run(self, ...)` method")
    cls.run = _twf.run(run)  # type: ignore[attr-defined]
    decorated = _twf.defn(cls)
    WORKFLOWS.append(decorated)
    return decorated


def activity(fn: Any) -> Any:
    """Mark a function as an activity — the I/O step, run outside the sandbox where arvel DI is
    available. Records it so the worker autoloads it."""
    from temporalio import activity as _tact

    decorated = _tact.defn(fn)
    ACTIVITIES.append(decorated)
    return decorated


async def run_activity(activity_fn: Any, *args: Any) -> Any:
    """Call an activity from a workflow body (the Phase-0 workflow's only side-effecting verb).
    Hides ``temporalio.workflow.execute_activity`` + the default timeout."""
    from temporalio import workflow as _twf

    return await _twf.execute_activity(
        activity_fn, *args, start_to_close_timeout=_DEFAULT_ACTIVITY_TIMEOUT
    )
