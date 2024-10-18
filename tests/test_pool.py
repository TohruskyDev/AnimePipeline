import time

from animepipeline.pool.task import AsyncTaskExecutor


def test_task_executor() -> None:
    executor = AsyncTaskExecutor()

    def my_task(name: str, sb: int = 1) -> None:
        print(sb)
        print(f"Task {name} is starting.")
        time.sleep(1)
        print(f"Task {name} is completed.")

    executor.submit_task("1", my_task, "Task1", 114514)

    assert executor.task_status("1") == "Pending"

    executor.shutdown()

    assert len(executor.tasks) == 1
    assert executor.task_status("1") == "Completed"
