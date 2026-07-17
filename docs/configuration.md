# Configuration

All of it lives in one typed file. The field defaults **are** the package defaults, so the file is
optional for local dev — but writing it makes moving to production a config change, not a code change.

```python
# config/workflow.py
config = {
    "target": "localhost:7233",
    "namespace": "default",
    "task_queue": "arvel",
}
```

## Keys

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `target` | str | `"localhost:7233"` | The Temporal server's frontend address (`host:port`). The `Workflow` facade connects here, and `workflow:work` (without `--dev`) polls here. |
| `namespace` | str | `"default"` | The Temporal namespace to run in. |
| `task_queue` | str | `"arvel"` | The task queue the worker polls and the facade starts work on. The worker and the facade must agree — they both read this key, so they stay in sync. |

## Environment-driven config

Drive it from the environment like any arvel config, so the same code runs in every environment:

```python
# config/workflow.py
from arvel import env

config = {
    "target": env("TEMPORAL_TARGET", "localhost:7233"),
    "namespace": env("TEMPORAL_NAMESPACE", "default"),
    "task_queue": env("WORKFLOW_QUEUE", "arvel"),
}
```

## `--dev` and `target`

`arvel workflow:work --dev` starts an ephemeral local server bound to the host and port in `target`
(default `localhost:7233`). Because the facade also connects to `target`, a driver process (a route,
a script) reaches the dev server with no extra configuration — everything reads the one key. In
production you don't use `--dev`; you point `target` at your real Temporal server.

## Reading it yourself

You rarely need to — the worker and facade read it for you — but the typed view is there:

```python
from arvel_workflow.settings import WorkflowSettings

settings = WorkflowSettings.from_source(app.config("workflow"))
settings.task_queue        # "arvel"
```

## See also

- [Getting Started](getting-started.md) · [Concepts](concepts.md) · [Testing](testing.md)
