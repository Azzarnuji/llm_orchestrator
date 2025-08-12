from llm_orchestrator.core.agent.loader import AgentLoader
from llm_orchestrator.types.base_llm import LLMClientType
from llm_orchestrator.core.executor.executor import Executor
from llm_orchestrator.decorators.private import PrivateMethod

class LLMOrchestrator(AgentLoader, Executor):
    def __init__(self):
        """
        Initialize the LLMOrchestrator with a default LLM client of GEMINI.
        """
        super().__init__(
            llm_client = LLMClientType.GEMINI
        )
        
    async def warm_up(self):
        """
        Warm up the LLMOrchestrator by saving all the files and vectorizing them.
        
        This method is a coroutine.
        
        Raises:
            Exception: If there is an error while saving the files or vectorizing.
        """
        try:
            await self._save_files()
            await self._vectorize()
        except Exception as e:
            raise e