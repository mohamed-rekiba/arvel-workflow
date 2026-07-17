# Testing

The rule for testing workflows: **run the real engine, fake the world.** Temporal ships a local
test server; use it. Mock the engine and you prove nothing — a mock can't reproduce the sandbox or
the replay that make a workflow durable, so a green mocked test says your workflow works when it may
not. Fake instead the things your *activities* reach (the network, a payment gateway, mail), the same
way you'd fake them anywhere else in arvel.

## The pattern

Boot your app, start Temporal's local server, run the worker in-process for the duration of the
test, and drive it through the facade:

```python
import pytest
from arvel_workflow.worker import build_worker
from temporalio.testing import WorkflowEnvironment


async def test_greet_completes(app):                     # `app` = your booted test app
    from app.workflows.greet import Greet

    async with await WorkflowEnvironment.start_local() as env:
        async with build_worker(env.client, "arvel"):     # worker runs for this block
            handle = await app.make("workflow").start(Greet, "world")
            result = await app.make("workflow").result(handle)

    assert result == "hello world (#1)"
```

`WorkflowEnvironment.start_local()` gives you a real (throwaway) Temporal server — the same engine as
production, just ephemeral. `build_worker(client, task_queue)` is the exact worker the
`workflow:work` command runs, so your test assembles the system the way production does.

## Faking activity dependencies

Your workflow body stays pure, so there's nothing to fake there. The I/O is in activities — fake it
with arvel's normal fakes and assert on the side effects:

```python
from arvel import Cache

async def test_greet_uses_cache(app):
    from app.workflows.greet import Greet

    async with await WorkflowEnvironment.start_local() as env:
        async with build_worker(env.client, "arvel"):
            handle = await app.make("workflow").start(Greet, "world")
            await app.make("workflow").result(handle)
            assert await Cache.get("greet:count") == 1     # the activity's side effect
```

Because the worker runs in-process with your test app, the activity resolves the *same* container —
so a `Mail.fake()`, a swapped repository, or an `AI.fake()` set up in your test is exactly what the
activity sees.

## Unit-testing the pieces

Not everything needs the engine. Pure logic — an activity's computation, a helper — is an ordinary
async function; call it directly:

```python
async def test_greet_activity_formats(app):
    from app.activities.greet import greet
    assert (await greet("sam")).startswith("hello sam")
```

Reserve the full engine test for the *orchestration* (does the workflow drive the activities to the
right result?); unit-test the *steps* directly.

## A note on speed

`start_local()` downloads the Temporal dev-server binary the first time (then caches it), so the
first run in a fresh environment is slower. Subsequent runs are fast. A time-skipping harness for
long-waiting workflows (so a multi-day timer runs in milliseconds) is on the roadmap.

## See also

- [Getting Started](getting-started.md) · [Concepts](concepts.md) · [Configuration](configuration.md)
