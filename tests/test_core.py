"""Core workflow tests."""

from durable_monty import init_db, OrchestratorService, register_function
from durable_monty.functions import execute_function


@register_function("add")
def add(a, b):
    return a + b


def test_full_workflow():
    """Test complete workflow: schedule → start → execute → resume → complete."""
    code = """
from asyncio import gather
results = await gather(add(1, 2), add(3, 4))
sum(results)
"""
    service = OrchestratorService(init_db("sqlite:///:memory:"))

    # Schedule and start
    exec_id = service.start_execution(code, ["add"])
    service._process_execution(exec_id)

    # Check pending calls created
    result = service.poll(exec_id)
    assert result["status"] == "pending"
    assert len(result["pending_calls"]) == 2

    # Execute calls
    for call in service.get_pending_calls(exec_id):
        value = execute_function(call["function_name"], call["args"])
        service.complete_call(exec_id, call["call_id"], value)

    # Verify completed
    result = service.poll(exec_id)
    assert result["status"] == "completed"
    assert result["output"] == 10
