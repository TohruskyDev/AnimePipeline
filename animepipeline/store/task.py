import asyncio
import json
from copy import deepcopy
from pathlib import Path
from typing import Dict

from pydantic import BaseModel


class TaskStatus(BaseModel):
    status: str
    details: str = ""


class AsyncJsonStore:
    def __init__(self, file_path: str = "task.json") -> None:
        self.file_path = Path(file_path)
        self.lock = asyncio.Lock()  # 使用 asyncio.Lock 确保线程安全
        self.data: Dict[str, TaskStatus] = self.load_data()

    def load_data(self) -> Dict[str, TaskStatus]:
        """Load data from the JSON file."""
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as file:
                try:
                    j = json.load(file)
                except json.JSONDecodeError:
                    return {}

                return {task_id: TaskStatus(**task) for task_id, task in j.items()}
        return {}

    async def save_data(self) -> None:
        """Save data to the JSON file."""
        with open(self.file_path, "w", encoding="utf-8") as file:
            # convert TaskStatus objects to dictionaries
            data = {task_id: task.dict() for task_id, task in self.data.items()}
            json.dump(data, file, ensure_ascii=False, indent=4)

    async def add_task(self, task_id: str, status: TaskStatus) -> None:
        """Add a task or update if it already exists."""
        async with self.lock:
            self.data[task_id] = status
            await self.save_data()

    async def get_task(self, task_id: str) -> TaskStatus:
        """Get a task by its ID."""
        async with self.lock:
            if task_id in self.data:
                task = deepcopy(self.data.get(task_id))
                if task is None:
                    raise ValueError("Task value is None!")
                return task
            else:
                raise KeyError(f"Task with ID '{task_id}' not found.")

    async def update_task(self, task_id: str, status: TaskStatus) -> None:
        """Update a task's status and details."""
        async with self.lock:
            if task_id in self.data:
                self.data[task_id] = status
                await self.save_data()
            else:
                raise KeyError(f"Task with ID '{task_id}' not found.")

    async def delete_task(self, task_id: str) -> None:
        """Delete a task by its ID."""
        async with self.lock:
            if task_id in self.data:
                del self.data[task_id]
                await self.save_data()
            else:
                raise KeyError(f"Task with ID '{task_id}' not found.")
