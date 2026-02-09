"""Test function registry."""

from durable_monty.functions import register_function, execute_function, FUNCTION_REGISTRY


def test_register_and_execute():
    """Test registering and executing a function."""

    @register_function("add")
    def add(a, b):
        return a + b

    @register_function("multiply")
    def multiply(a, b):
        return a * b

    assert "add" in FUNCTION_REGISTRY
    assert "multiply" in FUNCTION_REGISTRY

    assert execute_function("add", [2, 3]) == 5
    assert execute_function("multiply", [4, 5]) == 20
