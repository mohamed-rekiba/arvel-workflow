"""``build_worker`` — wraps ``temporalio``'s Worker with the passthrough sandbox runner.

The sandbox stays **on** (its runtime determinism checks still apply), but ``with_passthrough_modules``
passes the framework + app modules through, so a workflow file's plain ``from app.activities...
import ...`` needs no ``imports_passed_through()`` block. App authors write plain imports; the
sandbox wiring lives here.
"""

from __future__ import annotations

from typing import Any


def build_worker(client: Any, task_queue: str) -> Any:
    from temporalio.worker import Worker
    from temporalio.worker.workflow_sandbox import (
        SandboxedWorkflowRunner,
        SandboxRestrictions,
    )

    from .registry import ACTIVITIES, WORKFLOWS

    runner = SandboxedWorkflowRunner(
        restrictions=SandboxRestrictions.default.with_passthrough_modules(
            "arvel", "arvel_workflow", "app"
        )
    )
    return Worker(
        client,
        task_queue=task_queue,
        workflows=list(WORKFLOWS),
        activities=list(ACTIVITIES),
        workflow_runner=runner,
    )
