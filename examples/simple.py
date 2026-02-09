"""Simple example using OrchestratorService."""

from durable_monty import init_db, OrchestratorService, register_function
from durable_monty.functions import execute_function


# Register functions
@register_function("add")
def add(a, b):
    print(f"  Adding {a} + {b} = {a + b}")
    return a + b


@register_function("multiply")
def multiply(a, b):
    print(f"  Multiplying {a} * {b} = {a * b}")
    return a * b


# Workflow code
code = """
from asyncio import gather
results = await gather(
    add(1, 2),
    add(3, 4),
    multiply(5, 6)
)
sum(results)
"""

if __name__ == "__main__":
    # Initialize service
    engine = init_db("sqlite:///example_service.db")
    service = OrchestratorService(engine)

    # Start execution
    print("Starting execution...")
    exec_id = service.start_execution(code, ["add", "multiply"])
    print(f"Execution ID: {exec_id}\n")

    # Poll - should show pending calls
    result = service.poll(exec_id)
    print(f"Status: {result['status']}")
    print(f"Pending calls: {len(result['pending_calls'])}\n")

    # Get pending calls and execute them
    pending = service.get_pending_calls(exec_id)
    print("Executing calls:")
    for call in pending:
        result_value = execute_function(call["function_name"], call["args"])
        service.complete_call(exec_id, call["call_id"], result_value)

    # Poll again - should be completed now
    print("\nPolling for result...")
    result = service.poll(exec_id)
    print(f"Status: {result['status']}")
    print(f"Output: {result['output']}")
