"""Module-level collectors. A workflow/activity module registers itself when it executes
(the ``@workflow``/``@activity`` decorators append here) — so autoload needs no reflection,
same contract as arvel's listener/MCP-tool autoload."""

from __future__ import annotations

from typing import Any

WORKFLOWS: list[Any] = []
ACTIVITIES: list[Any] = []
