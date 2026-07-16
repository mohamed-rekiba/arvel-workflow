# arvel-workflow

Durable execution for [arvel](../arvel) — Temporal-native, with arvel's DX instead of Temporal's
setup tax. Define workflows in `app/workflows/` and activities in `app/activities/`, run
`arvel workflow:work --dev`, and drive them through the `Workflow` facade.

> **Phase 0 (vertical-slice spike).** This is the de-risking slice: one workflow + one activity +
> the `workflow:work --dev` worker + `Workflow.start/result`. The full authoring surface
> (signals/queries/updates/child-workflows/saga, timeout sugar, time-skip testing) is Phase 1.
> See `projects/arvel/product/prd-arvel-workflow.md` and DR-0048/0049/0050/0051.

```python
# app/activities/greet.py
from arvel_workflow import activity
from arvel import Cache

@activity
async def greet(name: str) -> str:
    count = await Cache.increment("greet:count")   # activities do I/O via arvel DI
    return f"hello {name} (#{count})"
```

```python
# app/workflows/greet.py
from arvel_workflow import workflow, run_activity
from app.activities.greet import greet          # plain import — no imports_passed_through

@workflow
class Greet:
    async def run(self, name: str) -> str:
        return await run_activity(greet, name)    # workflow body stays pure
```

```bash
arvel workflow:work --dev        # ephemeral Temporal dev server + worker, zero infra
```

```python
from arvel_workflow import Workflow
handle = await app.make("workflow").start(Greet, "world")
print(await app.make("workflow").result(handle))   # "hello world (#1)"
```

Requires the engine extra: `uv add 'arvel-workflow[temporal]'`.
