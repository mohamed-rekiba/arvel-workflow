"""WorkflowServiceProvider — auto-registered via the ``arvel.providers`` entry point.

Binds the ``Workflow`` facade and contributes the ``workflow:work`` command; nothing here imports
``temporalio`` or touches I/O. The command is registered in ``register()`` (the synchronous phase
the console discovers commands from). Workflow/activity autoload runs **inside the worker command**,
not at boot — the web process must not import workflow modules (keeps ``temporalio`` off its path).
"""

from __future__ import annotations

from arvel.kernel import ServiceProvider

from .facade import Workflow


class WorkflowServiceProvider(ServiceProvider):
    def register(self) -> None:
        self.app.singleton("workflow", lambda c: Workflow(self.app))

        from .commands import WorkflowWorkCommand

        self.commands(WorkflowWorkCommand)

    def boot(self) -> None:
        from .resource import WorkflowWorkerResource

        self.app.resources.register(WorkflowWorkerResource(self.app))
