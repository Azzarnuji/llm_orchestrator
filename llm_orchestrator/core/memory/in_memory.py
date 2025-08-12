from typing import Any
from llm_orchestrator.types.memory import AbstractMemoryManager
import asyncio

class InMemoryManager(AbstractMemoryManager):
    def __init__(self):
        """
        Initialize an instance of InMemoryManager.

        The memory dictionary is used to store values with a given key.
        The _lock is a Lock object to ensure thread safety when accessing the memory.
        """
        self.memory: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def get_memory(self, key: str) -> Any | None:
        """
        Retrieves the value associated with the given key from memory.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            Any | None: The value associated with the given key if it exists, otherwise None.
        """
        async with self._lock:
            return self.memory.get(key)

    async def set_memory(self, key: str, value: Any, append: bool = False) -> None:
        """
        Stores a value in memory with the given key.

        Args:
            key (str): The key to store the value with.
            value (Any): The value to store.
            append (bool, optional): Whether to append the value to an existing list for the given key. Defaults to False.

        Returns:
            None
        """
        async with self._lock:
            if append:
                if key not in self.memory or not isinstance(self.memory[key], list):
                    self.memory[key] = []
                self.memory[key].append(value)
            else:
                self.memory[key] = value

    async def clear_memory(self, key: str) -> bool:
        """
        Clears the value associated with the given key from memory.

        Args:
            key (str): The key to clear the value for.

        Returns:
            bool: Whether the key was successfully cleared.
        """
        async with self._lock:
            self.memory.pop(key, None)
        return True
