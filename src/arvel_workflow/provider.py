"""WorkflowServiceProvider — auto-registered via the ``arvel.providers`` entry point.

Binds the ``Workflow`` facade and contributes the ``workflow:work`` command; nothing here imports
``temporalio`` or touches I/O. The command is registered in ``register()`` (the synchronous phase
the console discovers commands from). Workflow/activity autoload runs **inside the worker command**,
not at boot — the web process must not import workflow modules (keeps ``temporalio`` off its path).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from arvel.kernel import ServiceProvider

from .facade import Workflow

if TYPE_CHECKING:
    from arvel.contracts import Container


class WorkflowServiceProvider(ServiceProvider):
    def register(self) -> None:
        def make_workflow(container: Container) -> Workflow:
            return Workflow(self.app)

        self.app.singleton("workflow", make_workflow)

        from .commands import WorkflowWorkCommand

        self.commands(WorkflowWorkCommand)

    def boot(self) -> None:
        from .resource import WorkflowWorkerResource

        self.app.resources.register(WorkflowWorkerResource(self.app))
