"""Database model tests."""

from durable_monty.models import init_db, Execution, Call, to_json, from_json
from sqlalchemy.orm import Session


def test_database_models():
    """Test Execution and Call models with JSON helpers."""
    engine = init_db("sqlite:///:memory:")
    session = Session(engine)

    # Create execution
    exec = Execution(
        id="test-123",
        code="test",
        external_functions=to_json(["func1"]),
        status="scheduled",
        inputs=to_json({"x": 1}),
    )
    session.add(exec)
    session.commit()

    # Create call
    call = Call(
        execution_id="test-123",
        resume_group_id="group-1",
        call_id=0,
        function_name="func1",
        args=to_json([1, 2]),
        status="pending",
    )
    session.add(call)
    session.commit()

    # Query and verify
    exec_result = session.query(Execution).first()
    assert from_json(exec_result.inputs) == {"x": 1}

    call_result = session.query(Call).first()
    assert from_json(call_result.args) == [1, 2]
