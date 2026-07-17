"""Minimal arvel app for the arvel-workflow example — worker only, no HTTP."""

from pathlib import Path
from arvel.kernel import Application

BASE_PATH = Path(__file__).resolve().parent.parent


def create_app() -> Application:
    return Application.configure(str(BASE_PATH)).with_config_dir(BASE_PATH / "config").create()
