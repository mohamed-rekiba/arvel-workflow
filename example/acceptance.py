"""End-to-end example: boot the app, run the worker in-process, start a workflow through the
Workflow facade, and read back the side effect the activity left in the cache — the whole flow in
one script, run against a real local Temporal server."""

import asyncio
from bootstrap.app import create_app
from arvel.kernel.bootstrap import bootstrap_app
from arvel.kernel import set_application


async def main():
    app = create_app()
    bootstrap_app(app)  # sync: config load + provider register
    await app.boot()  # async: provider boot + resource startup
    set_application(app)  # facades (Cache, workflow) resolve against this app

    from arvel_workflow.autoload import discover
    from arvel_workflow.worker import build_worker
    from app.workflows.greet import Greet
    from arvel import Cache
    from temporalio.testing import WorkflowEnvironment

    discover(app.base_path)  # register Greet + greet
    async with await WorkflowEnvironment.start_local(ip="127.0.0.1", port=7233) as env:
        worker = build_worker(env.client, "arvel")
        async with worker:  # run worker in the background for the block
            wf = app.make("workflow")
            handle = await wf.start(Greet, "world")  # start through the facade
            result = await wf.result(handle)  # await the result
            count = await Cache.get("greet:count")  # the side effect the activity left
    print("RESULT:", result)
    print("Cache greet:count =", count)
    assert result == "hello world (#1)", result
    assert int(count) == 1, count
    print("OK: workflow completed via the facade; the activity used the real Cache")


asyncio.run(main())
