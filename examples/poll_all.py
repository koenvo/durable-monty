"""Example showing poll() with no arguments to check all executions."""

from durable_monty import init_db, OrchestratorService, register_function
from durable_monty.functions import execute_function


@register_function("add")
def add(a, b):
    return a + b


# Simple workflow
code = """
from asyncio import gather
results = await gather(add(1, 2), add(3, 4))
sum(results)
"""

if __name__ == "__main__":
    engine = init_db("sqlite:///poll_example.db")
    service = OrchestratorService(engine)

    # Start multiple executions
    print("Starting 3 executions...")
    exec_ids = [
        service.start_execution(code, ["add"]),
        service.start_execution(code, ["add"]),
        service.start_execution(code, ["add"]),
    ]
    print(f"Started: {exec_ids}\n")

    # Poll all - should show 3 pending
    print("Polling all executions...")
    results = service.poll()
    print(f"Found {len(results)} waiting executions")
    for r in results:
        print(f"  {r['execution_id'][:8]}... : {r['status']}, {len(r['pending_calls'])} pending calls")

    # Complete calls for first execution only
    print(f"\nCompleting calls for first execution...")
    pending = service.get_pending_calls(exec_ids[0])
    for call in pending:
        result = execute_function(call["function_name"], call["args"])
        service.complete_call(exec_ids[0], call["call_id"], result)

    # Poll all again
    print("\nPolling all executions...")
    results = service.poll()
    print(f"Found {len(results)} waiting executions")
    for r in results:
        short_id = r['execution_id'][:8]
        print(f"  {short_id}... : {r['status']}")
        if r["status"] == "completed":
            print(f"    Output: {r['output']}")

    # Complete remaining executions
    print("\nCompleting remaining executions...")
    for exec_id in exec_ids[1:]:
        pending = service.get_pending_calls(exec_id)
        for call in pending:
            result = execute_function(call["function_name"], call["args"])
            service.complete_call(exec_id, call["call_id"], result)

    # Final poll
    print("\nFinal poll...")
    results = service.poll()
    print(f"Found {len(results)} waiting executions")
    for r in results:
        short_id = r['execution_id'][:8]
        print(f"  {short_id}... : {r['status']}, output: {r['output']}")

    print("\nAll done!")
