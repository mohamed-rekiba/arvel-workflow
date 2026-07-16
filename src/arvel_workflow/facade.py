"""The ``Workflow`` facade — the client side. Phase 0 surface: ``start`` + ``result``.

Holds a lazily-connected, pooled ``temporalio`` client (connect-once, not per-call — one of
DR-0050's boilerplate deletions vs the course's connect-per-request). No ``temporalio`` type
crosses out: ``start`` returns an arvel-owned ``WorkflowHandle``.
"""

from __future__ import annotations

from typing import Any


class WorkflowHandle:
    """The durable id you pass to ``result``. arvel-owned — no engine type leaks out."""

    def __init__(self, id: str) -> None:
        self.id = id


class Workflow:
    def __init__(self, app: Any) -> None:
        self.app = app
        self._client: Any = None

    def _settings(self) -> Any:
        from .settings import WorkflowSettings

        return WorkflowSettings.from_source(self.app.config("workflow"))

    async def _connect(self) -> Any:
        if self._client is None:
            from temporalio.client import Client

            s = self._settings()
            self._client = await Client.connect(s.target, namespace=s.namespace)
        return self._client

    async def start(self, workflow: Any, *args: Any, id: str | None = None) -> WorkflowHandle:
        from arvel.support import Str

        client = await self._connect()
        settings = self._settings()
        workflow_id = id or f"wf-{Str.uuid()}"
        await client.start_workflow(
            workflow.run, *args, id=workflow_id, task_queue=settings.task_queue
        )
        return WorkflowHandle(workflow_id)

    async def result(self, handle: WorkflowHandle | str) -> Any:
        client = await self._connect()
        workflow_id = handle.id if isinstance(handle, WorkflowHandle) else handle
        return await client.get_workflow_handle(workflow_id).result()
