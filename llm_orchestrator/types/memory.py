from abc import ABC, abstractmethod
from enum import Enum
from typing import Literal

from llm_orchestrator.exceptions.memory_manager_exception import MemoryManagerException


class MemoryType(Enum):
    InMemory = "InMemory"
    Redis = "Redis"
    Database = "Database"

class AbstractMemoryManager(ABC):
    
    @abstractmethod    
    async def get_memory(self, key: str):
        """
        Retrieves the value associated with the given key from memory.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            Any | None: The value associated with the given key if it exists, otherwise None.
        """
        raise MemoryManagerException("Method not implemented")

    @abstractmethod
    async def set_memory(self, key: str, value: str, append: bool = False):
        """
        Stores a value in memory with the given key.

        Args:
            key (str): The key to store the value with.
            value (str): The value to store.
            append (bool, optional): Whether to append the value to an existing list for the given key. Defaults to False.

        Returns:
            None
        """
        raise MemoryManagerException("Method not implemented")

    @abstractmethod
    async def clear_memory(self, key: str):
        """
        Clears the value associated with the given key from memory.

        Args:
            key (str): The key to clear the value for.

        Returns:
            None
        """

        raise MemoryManagerException("Method not implemented")
