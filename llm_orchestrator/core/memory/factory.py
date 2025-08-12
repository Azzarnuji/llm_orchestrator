from typing import Type, Union
from llm_orchestrator.types.memory import AbstractMemoryManager, MemoryType
from llm_orchestrator.core.memory.in_memory import InMemoryManager

MEMORY_MANAGER_MAP: dict[MemoryType, Type[Union[InMemoryManager]]] = {
    MemoryType.InMemory: InMemoryManager,
}
class MemoryFactory:
    _instances: dict[str, AbstractMemoryManager] = {}
    
    @classmethod
    def get(cls, memory_type: MemoryType):
        """
        Get an instance of a memory manager given the memory type.

        Args:
            memory_type (MemoryType): The type of memory manager to get.

        Returns:
            AbstractMemoryManager: An instance of the requested memory manager.
        """

        if memory_type not in cls._instances:
            cls._instances[memory_type] = MEMORY_MANAGER_MAP[memory_type]()
        return cls._instances[memory_type]