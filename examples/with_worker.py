"""Worker-based execution.

Run: uv run python examples/with_worker.py
"""

import time
import threading
from durable_monty import init_db, OrchestratorService, Worker, register_function, LocalExecutor


@register_function("add")
def add(a, b):
    return a + b


@register_function("multiply")
def multiply(a, b):
    return a * b


code = """
from asyncio import gather
results = await gather(add(1, 2), add(3, 4), multiply(5, 6))
sum(results)
"""

if __name__ == "__main__":
    service = OrchestratorService(init_db("sqlite:///worker.db"))

    # Schedule execution
    exec_id = service.start_execution(code, ["add", "multiply"])
    print(f"Scheduled: {exec_id[:8]}...")

    # Run worker
    executor = LocalExecutor()
    worker = Worker(service, executor, poll_interval=0.1)

    def run_worker():
        for _ in range(30):
            worker._process_scheduled()
            worker._process_pending_calls()
            worker._process_submitted_jobs()
            worker._process_waiting()
            time.sleep(0.1)

    worker.running = True
    thread = threading.Thread(target=run_worker)
    thread.start()
    thread.join()

    # Check result
    result = service.poll(exec_id)
    print(f"Status: {result['status']}, Output: {result['output']}")
