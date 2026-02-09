"""Example using RQ executor for distributed execution.

To run this:
1. Start Redis: redis-server
2. Start RQ worker: rq worker durable-monty
3. Run this script: python examples/with_rq.py
"""

import logging
import time
from durable_monty import init_db, OrchestratorService, Worker, register_function
from durable_monty.executors.rq import RQExecutor

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
    # Initialize with RQ executor
    engine = init_db("sqlite:///rq_example.db")
    service = OrchestratorService(engine)

    try:
        executor = RQExecutor()
        print("✓ RQ executor initialized (Redis connected)")
    except Exception as e:
        print(f"✗ Failed to initialize RQ executor: {e}")
        print("  Make sure Redis is running: redis-server")
        exit(1)

    # 1. User: Schedule execution
    print("\n=== Scheduling execution ===")
    exec_id = service.start_execution(code, ["add", "multiply"])
    print(f"Scheduled: {exec_id[:8]}")

    # 2. Worker: Process with RQ executor
    print("\n=== Worker processing (using RQ) ===")
    worker = Worker(service, executor, poll_interval=0.5)

    # Run worker for a few seconds
    import threading
    def run_worker():
        for _ in range(20):  # Run for 10 seconds
            if not worker.running:
                break
            worker._process_scheduled()
            worker._process_pending_calls()
            worker._process_submitted_jobs()
            worker._process_waiting()
            time.sleep(0.5)

    worker.running = True
    worker_thread = threading.Thread(target=run_worker)
    worker_thread.start()
    worker_thread.join()

    # 3. Check result
    print("\n=== Result ===")
    result = service.poll(exec_id)
    print(f"Status: {result['status']}")
    if result["status"] == "completed":
        print(f"Output: {result['output']}")
    else:
        print("Note: RQ workers need to be running to execute tasks")
        print("Start with: rq worker durable-monty")
