import asyncio

from animepipeline.pool.task import AsyncTaskExecutor


def test_task_executor() -> None:
    # Example task function
    async def example_task(task_id: str, duration: int) -> None:
        print(f"Task {task_id} started, will take {duration} seconds.")
        await asyncio.sleep(duration)
        print(f"Task {task_id} completed.")

    async def _test() -> None:
        executor = AsyncTaskExecutor()

        for task_id in range(114):
            # Dynamically create a new task every few seconds
            await asyncio.create_task(executor.submit_task(f"task{task_id}", example_task, f"task{task_id}", 3))
            print(f"Task {task_id} has been submitted.")

        await executor.wait_all_tasks()

        assert len(executor.tasks) == 114
        for task_id in range(114):
            assert await executor.task_status(f"task{task_id}") == "Completed"

    asyncio.run(_test())
