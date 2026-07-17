from arvel_workflow import workflow, run_activity
from app.activities.greet import (
    greet,
)  # plain import — the framework passthrough sandbox handles it


@workflow
class Greet:
    async def run(self, name: str) -> str:
        return await run_activity(greet, name)
