"""Typed view over the ``workflow`` config section — arvel's ``Settings`` pattern (msgspec),
same shape as ``AiSettings``. Field defaults ARE the package defaults; no ``temporalio`` here."""

from __future__ import annotations

from arvel.kernel.settings import Settings


class WorkflowSettings(Settings):
    __config_key__ = "workflow"

    target: str = "localhost:7233"  # Temporal server host:port
    namespace: str = "default"
    task_queue: str = "arvel"
