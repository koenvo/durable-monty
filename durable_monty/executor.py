"""Execution engine abstraction for running external function calls."""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any

from durable_monty.functions import execute_function

logger = logging.getLogger(__name__)


class Executor(ABC):
    """Abstract base class for execution engines."""

    @abstractmethod
    def submit_call(self, function_name: str, args: list) -> str:
        """
        Submit a call for execution.

        Returns:
            job_id that can be used to check status later
        """
        pass

    @abstractmethod
    def check_job(self, job_id: str) -> dict[str, Any]:
        """
        Check job status.

        Returns:
            {"status": "finished|failed|queued|started", "result": ..., "error": ...}
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """Get executor statistics."""
        pass


class LocalExecutor(Executor):
    """Executes functions locally in the same process."""

    def __init__(self):
        self.results = {}  # job_id -> result
        self.stats = {"executed": 0, "failed": 0}

    def submit_call(self, function_name: str, args: list) -> str:
        """Execute function immediately and store result."""
        job_id = str(uuid.uuid4())

        try:
            logger.info(f"Executing {function_name}{tuple(args)}")
            result = execute_function(function_name, args)

            self.results[job_id] = {"status": "finished", "result": result}
            logger.info(f"Completed {function_name}{tuple(args)} = {result}")
            self.stats["executed"] += 1

        except Exception as e:
            logger.error(f"Failed {function_name}: {e}")
            self.results[job_id] = {"status": "failed", "error": str(e)}
            self.stats["failed"] += 1

        return job_id

    def check_job(self, job_id: str) -> dict[str, Any]:
        """Get result for a job."""
        return self.results.get(job_id, {"status": "error", "error": "Job not found"})

    def get_stats(self) -> dict[str, Any]:
        return self.stats.copy()


