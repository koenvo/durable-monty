"""Example showing the new worker-based flow."""

import logging
import time
from durable_monty import init_db, OrchestratorService, Worker, register_function

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# Register functions
@register_function("add")
def add(a, b):
    return a + b


@register_function("multiply")
def multiply(a, b):
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
    # Initialize
    engine = init_db("sqlite:///worker_example.db")
    service = OrchestratorService(engine)

    # 1. User: Schedule execution
    print("=== User: Scheduling execution ===")
    exec_id = service.start_execution(code, ["add", "multiply"])
    print(f"Scheduled execution: {exec_id}\n")

    # 2. Worker: Run in background (simulated with a few iterations)
    print("=== Worker: Processing ===")
    from durable_monty import LocalExecutor

    worker = Worker(service, LocalExecutor(), poll_interval=0.1)

    # Run worker for a few seconds
    import threading

    def run_worker():
        for _ in range(30):  # Run for 3 seconds
            if not worker.running:
                break
            worker._process_scheduled()
            worker._process_pending_calls()
            worker._process_submitted_jobs()
            worker._process_waiting()
            time.sleep(0.1)

    worker.running = True
    worker_thread = threading.Thread(target=run_worker)
    worker_thread.start()
    worker_thread.join()

    # 3. User: Check result
    print("\n=== User: Checking result ===")
    result = service.poll(exec_id)
    print(f"Status: {result['status']}")
    print(f"Output: {result['output']}")
