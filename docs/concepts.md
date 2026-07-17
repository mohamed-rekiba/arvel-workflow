# Concepts & Best Practices

Durable execution has one core idea. Get it, and everything else follows.

## Workflow vs activity

| | **Workflow** | **Activity** |
|---|---|---|
| Role | orchestration — the steps and their order | one step that does I/O |
| Runs | inside a determinism sandbox | outside it, on the worker |
| May do I/O? | **no** (deterministic) | **yes** — network, DB, files, facades |
| Lives in | `app/workflows/` | `app/activities/` |
| Declared with | `@workflow` on a class | `@activity` on a function |

The workflow is a **recipe**; activities are the **steps that touch the world**. Temporal replays a
workflow's body to recover it after a crash, so the body must produce the same decisions every time
it runs — which is why it can't do I/O directly. Anything non-deterministic (an API call, the clock,
a random number, a DB read) goes in an activity.

### Why this is a good fit for arvel

The determinism rule sounds like a constraint, but it lands exactly where arvel wants a seam: **the
activity is where the container plugs in.** Activities are ordinary async functions, so they use
facades like any other code —

```python
@activity
async def charge(order_id: int) -> str:
    order = await Order.find(order_id)          # DB
    receipt = await Payments.charge(order)      # a service
    await Mail.to(order.email).send(Receipt(receipt))   # mail
    return receipt.id
```

— while the workflow that calls them stays a clean, readable sequence of steps. You don't wire
dependency injection for activities; they reach the same booted container your web process uses.

## Best practices

- **Put every side effect in an activity.** If a line talks to the network, the disk, the database,
  the clock, or randomness, it belongs in an activity — not the workflow body. This is the single
  rule that keeps workflows correct.
- **Keep workflow bodies about *control flow*.** Sequencing, branching, looping over results —
  yes. Doing the work — no.
- **Make activities idempotent where you can.** An activity can be retried (that's the point of
  durability), so "charge the card" should be safe to run twice, e.g. keyed on an idempotency token.
- **Return plain, serializable values** from activities and workflows (what JSON/msgspec can carry).
  They cross a process boundary.
- **One activity, one job.** Small activities are easier to retry, time out, and reason about than
  one big step.

## The sandbox, and why you don't see it

Temporal runs workflow code in a sandbox that re-imports the workflow module to enforce determinism.
In raw Temporal that forces you to wrap activity imports in a `with workflow.unsafe.imports_passed_through():`
block — boilerplate in every workflow file.

`arvel-workflow` deletes that. The worker is built with the framework and app modules already passed
through the sandbox, so your workflow's plain `from app.activities.greet import greet` works with no
ceremony. You write ordinary imports; the framework owns the sandbox configuration.

You should still **respect the determinism rule** — the sandbox is configured for ergonomics, not to
let you do I/O in a workflow body. Keep side effects in activities and you'll never see a sandbox
error.

## How it's wired (a quick tour)

- **Autoload** — every `*.py` in `app/workflows/` and `app/activities/` is imported when the worker
  starts, so `@workflow`/`@activity` decorators register their classes/functions. No manifest, no
  registry to maintain.
- **The worker** (`arvel workflow:work`) is one process; your web app is another. The web process
  never imports workflow modules, so it never pays for the engine.
- **The `Workflow` facade** is the client — it connects once (pooled) and offers `start`/`result`.
- **Health** — the worker registers as an arvel resource, so it shows in the startup log and on
  `/health`, and drains gracefully on shutdown.

## What's not here yet

This release is the durable-execution **core**. Deliberately not shipped (so the docs never promise
what the code can't do):

- signals, queries, and updates (sending events into a running workflow, reading its live state,
  human-in-the-loop approvals)
- child workflows and fan-out
- sagas / compensation, durable timers, scheduled workflows, per-activity retry & timeout sugar
- a time-skipping test harness

They're on the roadmap; today's surface is define → run → start → result.

## See also

- [Getting Started](getting-started.md) · [Configuration](configuration.md) · [Testing](testing.md)
