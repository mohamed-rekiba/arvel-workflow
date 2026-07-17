# arvel-workflow

**Durable execution for the [arvel](https://pypi.org/project/arvel/) framework** — backed by
[Temporal](https://temporal.io), with arvel's ergonomics instead of Temporal's setup tax.

Some work outlives a single request: an order that moves through authorize → fulfil → ship over
hours, a multi-step job that has to survive a restart halfway through. arvel's queue is
fire-and-forget; this is for work that must *remember where it got to*. You write plain workflows and
activities, run one command, and drive them through a facade — no Temporal boilerplate.

```bash
uv add 'arvel-workflow[temporal]'
```

Installing auto-registers the provider through arvel's entry-point mechanism — no wiring.

## The idea in one screen

An **activity** does the I/O (and can use any arvel facade); a **workflow** orchestrates activities
and stays pure. Both autoload from their folders.

```python
# app/activities/greet.py
from arvel_workflow import activity
from arvel import Cache

@activity
async def greet(name: str) -> str:
    count = await Cache.increment("greet:count")   # activities do I/O — arvel DI works here
    return f"hello {name} (#{count})"
```

```python
# app/workflows/greet.py
from arvel_workflow import workflow, run_activity
from app.activities.greet import greet          # a plain import — no ceremony

@workflow
class Greet:
    async def run(self, name: str) -> str:
        return await run_activity(greet, name)
```

Run the worker (`--dev` boots a throwaway local Temporal server — nothing to install first):

```bash
arvel workflow:work --dev
```

Start work and read the result from anywhere you have the app:

```python
handle = await app.make("workflow").start(Greet, "world")
print(await app.make("workflow").result(handle))   # hello world (#1)
```

No `with workflow.unsafe.imports_passed_through()` anywhere — the framework configures Temporal's
sandbox so plain imports work.

## Documentation

| Guide | What's in it |
|-------|--------------|
| [Getting Started](docs/getting-started.md) | install → define → run → drive → test, end to end |
| [Concepts & Best Practices](docs/concepts.md) | the workflow/activity split, the determinism rule, the sandbox, and the habits that keep you correct |
| [Configuration](docs/configuration.md) | every `config("workflow")` key and default |
| [Testing](docs/testing.md) | run the real engine, fake the world — the test pattern |

## Scope & roadmap

This release ships the durable-execution **core**: define workflows and activities, run a worker,
start work, and read its result. Documented capabilities are the ones that actually run today.

Coming next (not shipped yet — so the docs never promise what the code can't do):

- **signals / queries / updates** — send events into a running workflow, read its live state, drive
  human-in-the-loop approvals
- **child workflows & fan-out**, **sagas / compensation**, **durable timers**, **scheduled workflows**
- per-activity **retry & timeout** sugar and a **time-skipping test harness**

## Requirements

- Python **3.14+**
- **arvel** (installed with the package)
- The engine extra: `arvel-workflow[temporal]`. `--dev` downloads a local Temporal dev-server binary
  on first run.

## License

MIT — see [LICENSE](LICENSE).
