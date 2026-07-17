# Getting Started

From nothing to a durable workflow running on your machine — install, define, run, drive, test —
in a few minutes, with no infrastructure to stand up first.

> **What "durable" buys you.** A workflow's progress is persisted by Temporal as it runs. If the
> worker restarts mid-flight, the workflow picks up where it left off instead of starting over or
> vanishing. That's the difference from a fire-and-forget [queue](https://pypi.org/project/arvel/)
> job — and the reason this is a separate package.

## 1. Install

```bash
uv add 'arvel-workflow[temporal]'
```

The `[temporal]` extra pulls the engine. Installing the package auto-registers its provider through
arvel's `arvel.providers` entry point — you don't edit `bootstrap/providers.py`.

## 2. Configure

```python
# config/workflow.py
config = {
    "target": "localhost:7233",   # your Temporal server (host:port)
    "namespace": "default",
    "task_queue": "arvel",
}
```

Every field has a sensible default (shown above), so this file is optional for local dev — but
create it now so production is a one-file change, not a code change.

## 3. Write an activity

An **activity** is a single step that does I/O. It runs outside Temporal's determinism sandbox, so
it's free to touch the network, the database, the filesystem — and, this being arvel, to use any
facade. Drop it in `app/activities/`; it's discovered automatically.

```python
# app/activities/greet.py
from arvel_workflow import activity
from arvel import Cache

@activity
async def greet(name: str) -> str:
    count = await Cache.increment("greet:count")   # real DI — the same Cache your app uses
    return f"hello {name} (#{count})"
```

## 4. Write a workflow

A **workflow** is the orchestration — the steps and their order. Its body is **deterministic**, so
it does no I/O itself; it calls activities for that. Drop it in `app/workflows/`.

```python
# app/workflows/greet.py
from arvel_workflow import workflow, run_activity
from app.activities.greet import greet          # a plain import — that's all

@workflow
class Greet:
    async def run(self, name: str) -> str:
        return await run_activity(greet, name)
```

Notice what's **not** there: no `with workflow.unsafe.imports_passed_through()` block around the
import. Raw Temporal makes you write that; `arvel-workflow` configures the sandbox for you so plain
imports just work. (See [Concepts](concepts.md#the-sandbox-and-why-you-dont-see-it).)

## 5. Run the worker

The worker is the process that actually executes your workflows and activities. One command
autoloads both folders and starts polling:

```bash
arvel workflow:work --dev
```

`--dev` boots a throwaway local Temporal server (it downloads the dev-server binary the first time,
then caches it) — so you get a running system with **nothing to install or configure**. You'll see:

```
[workflow:work] task_queue=arvel workflows=['Greet'] activities=['greet']
[workflow:work] dev server up at localhost:7233
[workflow:work] worker ready — Ctrl-C to drain
```

For a real deployment, drop `--dev` and point `config.target` at your Temporal server.

## 6. Start a workflow and read its result

The `Workflow` facade is the client side. From a route, a command, or a script (anywhere you have
the app), start work and await the outcome:

```python
handle = await app.make("workflow").start(Greet, "world")   # returns a durable handle
result = await app.make("workflow").result(handle)          # awaits completion
print(result)                                               # hello world (#1)
```

`start` hands back a handle immediately — the work runs on the worker, not in your request. `result`
awaits the final value. The `(#1)` is proof your activity ran and used the real `Cache`.

## 7. Test it

Don't mock the engine — a mock can't reproduce Temporal's sandbox, so it would prove nothing about
whether your workflow actually runs. Instead, run it against Temporal's local test server and fake
the *activity's* dependencies:

```python
import asyncio
from arvel_workflow.worker import build_worker
from temporalio.testing import WorkflowEnvironment

async def test_greet_runs(app):                       # `app` = your booted test app
    from app.workflows.greet import Greet
    async with await WorkflowEnvironment.start_local() as env:
        async with build_worker(env.client, "arvel"):
            handle = await app.make("workflow").start(Greet, "world")
            assert await app.make("workflow").result(handle) == "hello world (#1)"
```

See [Testing](testing.md) for faking activity dependencies (`Cache.fake()` etc.) and the full
pattern.

## Where next

- [Concepts](concepts.md) — the workflow/activity split, the determinism rule, and the best
  practices that keep you out of trouble.
- [Configuration](configuration.md) — every `config("workflow")` key.
- [Testing](testing.md) — the real-engine test pattern.
