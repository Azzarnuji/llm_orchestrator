from typing import Type, Union
from llm_orchestrator.types.base_llm import BaseLLM, LLMClientType
from llm_orchestrator.core.llms.llm_gemini import LLMGemini


LLM_CLIENT_MAP: dict[LLMClientType, Type[Union[LLMGemini]]] = {
    LLMClientType.GEMINI: LLMGemini,
}
class LLMFactory:
    _instances: dict[str, BaseLLM] = {}
    
    @classmethod
    def get(cls, client_type: LLMClientType) -> BaseLLM:
        """
        Get an instance of an LLM client given the client type.

        Args:
            client_type (LLMClientType): The type of LLM client to get.

        Returns:
            BaseLLM: An instance of the requested LLM client.
        """
        if client_type not in cls._instances:
            cls._instances[client_type] = LLM_CLIENT_MAP[client_type]()
        return cls._instances[client_type]