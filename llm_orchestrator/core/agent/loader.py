import hashlib
import json
import os
import traceback
from typing import List
import uuid

import aiofiles
import httpx

from llm_orchestrator.exceptions.agent_loader_exception import AgentLoaderException
from llm_orchestrator.schemas.agent import AgentSchema
from llm_orchestrator.types.agents import Agent
from llm_orchestrator.core.agent.validator import AgentValidator
from llm_orchestrator.decorators.private import PrivateMethod
from llm_orchestrator.core.memory.factory import MemoryFactory
from llm_orchestrator.types.base_llm import LLMClientType
from llm_orchestrator.types.memory import MemoryType
from llm_orchestrator.core.llms.factory import LLMFactory
from llm_orchestrator.shared.helpers.qdrant_helper import QdrantHelper
class AgentLoader:
    def __init__(self, llm_client: LLMClientType = LLMClientType.GEMINI):
        """
        Initialize AgentLoader with a default LLM client of GEMINI, unless otherwise specified.

        Args:
            llm_client (LLMClientType): The type of LLM client to use. Defaults to LLMClientType.GEMINI.
        """
        self.in_memory_manager = MemoryFactory.get(MemoryType.InMemory)
        self.llm_client = LLMFactory.get(llm_client)
        self.qdrant_helper = QdrantHelper()
    
    async def register_agents(self, agents: List[Agent]):
        """
        Registers a list of agents in memory.

        Args:
            agents (List[Agent]): A list of agents to register.
        """
        for agent in agents:
            await self.in_memory_manager.set_memory("REGISTERED_AGENTS", agent, append=True)
        
    async def get_agents(self)->List[Agent]:
        """
        Retrieves the list of registered agents from memory.

        Returns:
            List[Agent] or None: A list of registered agents if any are present,
            otherwise None.
        """

        return await self.in_memory_manager.get_memory("REGISTERED_AGENTS")
    
    @PrivateMethod
    async def _save_files(self):
        """
        Private method to save all agents in memory to storage/agents folder.

        This method downloads the agent file from the provided URL and saves it to
        storage/agents folder. It also saves a checksum of the file to
        storage/agents folder to check if the file has changed in the future.

        If the file has not changed (i.e. the checksum is the same), the method will
        skip the agent and not download it again.

        If the agent is not a valid schema, it will raise an AgentLoaderException.

        After saving all agents, this method clears the in-memory list of agents.

        Raises:
            AgentLoaderException: If any error occurs while fetching the agent.
        """
        agents = await self.get_agents()
        async with httpx.AsyncClient() as client:
            for agent in agents:
                try:
                    file_path = f'storage/agents/{agent.name}.json'
                    checksum_path = f'storage/agents/{agent.name}.checksum'

                    agent_file_resp = await client.get(agent.urlAgentFile)
                    agent_file_resp.raise_for_status()
                    agent_json = agent_file_resp.text

                    new_checksum = hashlib.md5(agent_json.encode()).hexdigest()

                    if os.path.exists(checksum_path):
                        async with aiofiles.open(checksum_path, 'r') as f:
                            old_checksum = (await f.read()).strip()
                        if old_checksum == new_checksum:
                            continue

                    os.makedirs('storage/agents', exist_ok=True)
                    is_agent_valid = AgentValidator.run(json.loads(agent_json))
                    if not is_agent_valid:
                        raise AgentLoaderException(f"Agent {agent.name} is not valid schema, please check it out.")

                    async with aiofiles.open(file_path, 'w') as f:
                        await f.write(agent_json)

                    async with aiofiles.open(checksum_path, 'w') as f:
                        await f.write(new_checksum)

                except Exception as e:
                    traceback.print_exc()
                    AgentLoaderException(
                        f"Error when fetching {agent.name}: {str(e)}"
                    )
                    continue
        await self.in_memory_manager.clear_memory("REGISTERED_AGENTS")
        
    @PrivateMethod
    async def _vectorize(self):
        """
        Private method to vectorize all agents in storage/agents folder.

        This method reads all agent files in storage/agents folder and vectorizes
        each tool in the agent using the LLMClient. The vectorized data is then
        stored in the Qdrant database.

        Raises:
            AgentLoaderException: If any error occurs while vectorizing the agents.
        """
        try:
            directory = 'storage/agents/'
            files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.json')]
            for file in files:
                async with aiofiles.open(f'storage/agents/{file}', 'r') as f:
                    agent_json = await f.read()
                    agent_data: AgentSchema = AgentValidator.run(json.loads(agent_json)).model_dump()
                    for tool in agent_data['tools']:
                        concated_text = (
                            f"Agent Name: {agent_data['agent_name']}, "
                            f"Tool Name: {tool['name']}, "
                            f"Tool Description: {tool['description']}, "
                            f"Tool Intents: {', '.join(tool['intent_examples'])}"
                        )

                        embedding = self.llm_client.embeddings([concated_text])[0]

                        self.qdrant_helper.upsert_with_filter(
                            collection_name="llm_orchestrator",
                            payload_filter={
                                "agent_name": agent_data["agent_name"],
                                "name": tool["name"]
                            },
                            vector=embedding,
                            payload={
                                **tool,
                                "agent_name": agent_data["agent_name"],
                                "requiredAuth": agent_data.get("requiredAuth", False),
                                "authType": agent_data.get("authType", "Individual")
                            }
                        )
        except Exception as e:
            traceback.print_exc()
            raise AgentLoaderException(f"Error when vectorizing: {str(e)}")