from arvel_workflow import activity
from arvel import Cache


@activity
async def greet(name: str) -> str:
    count = await Cache.increment("greet:count")  # real arvel DI, observable side effect
    return f"hello {name} (#{count})"
