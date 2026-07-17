"""arvel-workflow — durable execution for arvel (Temporal-native, framework-ergonomic).

Public surface (import-cheap — no ``temporalio`` until a workflow/activity module actually loads):
``workflow`` / ``activity`` decorators, ``run_activity`` (the Phase-0 workflow verb), and the
``Workflow`` client facade.
"""

from __future__ import annotations

from .decorators import activity, run_activity, workflow
from .facade import Workflow, WorkflowHandle

__version__ = "0.2.0"  # x-release-please-version

__all__ = ["__version__", "workflow", "activity", "run_activity", "Workflow", "WorkflowHandle"]
