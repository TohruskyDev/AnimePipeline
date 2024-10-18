import concurrent.futures
import threading
from typing import Any, Callable, Dict


class AsyncTaskExecutor:
    """
    A simple async task executor that can submit tasks and check their status.
    This class uses ThreadPoolExecutor to run tasks in parallel.
    """

    def __init__(self) -> None:
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.lock = threading.Lock()
        self.tasks: Dict[str, Any] = {}

    def submit_task(self, task_id: str, func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> None:
        """
        Submit a task to the executor.

        :param task_id: The task ID.
        :param func: The function to run.
        :param args: The arguments to pass to the function.
        :param kwargs: The keyword arguments to pass to the function.
        """

        with self.lock:
            if self.tasks.get(task_id) and not self.tasks[task_id].done():
                return

            self.tasks[task_id] = None

        future = self.executor.submit(func, *args, **kwargs)
        self.tasks[task_id] = future

    def task_status(self, task_id: str) -> str:
        """
        Check the status of a task.

        :param task_id: The task ID to check.
        """
        with self.lock:
            if self.tasks.get(task_id) and not self.tasks[task_id].done():
                return "Pending"
            elif self.tasks.get(task_id) and self.tasks[task_id].done():
                return "Completed"
            else:
                return "Unknown"

    def shutdown(self) -> None:
        """
        Shutdown the executor.
        """
        self.executor.shutdown(wait=True)
        print("All tasks have been shutdown.")
