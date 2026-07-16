"""The workflow worker command — ``arvel workflow:work [--dev]``.

An arvel ``Command`` subclass (not a typer group): the console discovers commands from the
registry populated during the *synchronous* bootstrap, so this is registered in the provider's
``register()``. ``temporalio`` is imported lazily inside ``handle`` — the command class itself is
engine-free.
"""

from __future__ import annotations

import asyncio
from typing import Any

from arvel.console import Command


class WorkflowWorkCommand(Command):
    signature = "workflow:work {--dev}"
    description = "Autoload app/workflows + app/activities and run the Temporal worker."

    async def handle(self, *_deps: Any) -> None:
        from arvel.kernel.globals import app as _app

        from .autoload import discover
        from .registry import ACTIVITIES, WORKFLOWS
        from .settings import WorkflowSettings

        application = _app()
        settings = WorkflowSettings.from_source(application.config("workflow"))
        discover(application.base_path)
        self.info(
            f"[workflow:work] task_queue={settings.task_queue} "
            f"workflows={[w.__name__ for w in WORKFLOWS]} "
            f"activities={[a.__name__ for a in ACTIVITIES]}"
        )
        await self._run(settings, bool(self.option("dev")))

    async def _run(self, settings: Any, dev: bool) -> None:
        if dev:
            from temporalio.testing import WorkflowEnvironment

            host, _, port = settings.target.partition(":")
            async with await WorkflowEnvironment.start_local(
                ip=host or "127.0.0.1", port=int(port or 7233)
            ) as env:
                self.info(f"[workflow:work] dev server up at {settings.target}")
                await self._serve(env.client, settings)
        else:
            from temporalio.client import Client

            client = await Client.connect(settings.target, namespace=settings.namespace)
            await self._serve(client, settings)

    async def _serve(self, client: Any, settings: Any) -> None:
        from .worker import build_worker

        worker = build_worker(client, settings.task_queue)
        self.info("[workflow:work] worker ready — Ctrl-C to drain")
        try:
            await worker.run()
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        self.info("[workflow:work] drained.")
