"""The workflow engine as a health-checkable arvel resource — like ``AiResource``. It puts the
configured Temporal target in the startup log + on ``/health``. Non-critical: a Temporal outage
doesn't stop the web process from serving (the worker process is where workflows actually run)."""

from __future__ import annotations

from typing import Any

from arvel.contracts import HealthResult, HealthStatus


class WorkflowWorkerResource:
    name = "workflow"

    def __init__(self, app: Any, *, critical: bool = False) -> None:
        self.app = app
        self.critical = critical

    async def check(self) -> HealthResult:
        from .settings import WorkflowSettings

        try:
            s = WorkflowSettings.from_source(self.app.config("workflow"))
        except Exception as exc:  # bad/missing config surfaces here, not on first use
            return HealthResult(HealthStatus.FAILED, detail=str(exc))
        return HealthResult(
            HealthStatus.OK, detail=f"temporal {s.target} · queue={s.task_queue}"
        )
