import asyncio
import json
import httpx
from llm_orchestrator.core.llms.factory import LLMFactory
from llm_orchestrator.core.memory.factory import MemoryFactory
from llm_orchestrator.decorators.private import PrivateMethod
from llm_orchestrator.shared.helpers.qdrant_helper import QdrantHelper
from llm_orchestrator.types.base_llm import LLMClientType
from llm_orchestrator.types.memory import MemoryType
from llm_orchestrator.types.response_tool import ResponseTool

class Executor:
    def __init__(self):
        self.memory_manager = MemoryFactory.get(MemoryType.InMemory)
        self.llm_client = LLMFactory.get(LLMClientType.GEMINI)
        self.qdrant_helper = QdrantHelper()
        self.stream = False
        self.additional_prompt_to_ai = None
        
        
    async def invoke_query(self, query: str, top_k = 5, stream = False):
        self.stream = stream
        query_embedding = self.llm_client.embeddings([query])
        result = self.qdrant_helper.client.search(
            collection_name="llm_orchestrator",
            query_vector=query_embedding[0],
            limit=top_k
        )
        tools = [p.payload for p in result if p.score > 0.8]
        # for tool in tools:
        #     if tool["requiredAuth"] and tool["authType"] != "SSO":
        #         auth = self.auth_manager.get_auth(tool["agent_name"])
        #     else:
        #         auth = self.auth_manager.get_auth("SSO")
        #     print(auth)
        # if (tools is None or len(tools) == 0) and self.context.get("pending_request") == None:
        #     general_result = await self.llm_client.ask(query)
        #     return general_result.text
        
        # if self.context.get("pending_request"):
        #     pending = self.context["pending_request"]

        #     extracted_fields = await self.extract_missing_fields(pending, query)
        #     for k, v in extracted_fields.items():
        #         pending["payload"][k] = v

        #     if all(v is not None for v in pending["payload"].values()):
        #         self.context.pop("pending_request", None)
        #         self._save_pending_requests()
        #         return await self.perform_request(ResponseTool(**pending))
        #     else:
        #         self._save_pending_requests()
        #         missing = [k for k, v in pending["payload"].items() if v is None]
        #         explained_required_fields = await self.explain_required_fields(missing, query)
        #         return explained_required_fields.text
                
        tool_result = await self.get_tool(tools, query)
        # if isinstance(tool_result, dict) and tool_result.get("status") == "need_user_input":
        #     self.context["pending_request"] = tool_result["config"]
        #     self._save_pending_requests()
        #     explained_required_fields = await self.explain_required_fields(tool_result["missing_fields"], query)
        #     return explained_required_fields.text
        
        explained_answer = await self.explain_answer(tool_result, query)
        self.additional_prompt_to_ai = None
        if self.stream:
            return explained_answer
        return explained_answer.text
    
    @PrivateMethod
    async def explain_required_fields(self, fields: dict, user_query):
        prompt =f"""
        You're a explainer for required fields, act as you required the fields information
        
        Fields: {json.dumps(fields, indent=2)}
        
        explain the required fields
        User Language Prompt: {user_query}
        
        explain the answer based on user language
        """
        result = await self.llm_client.ask(prompt)
        return result
    
    @PrivateMethod
    async def extract_missing_fields(self, pending_config: dict, user_message: str) -> dict:
        missing_fields = [k for k, v in pending_config["payload"].items() if v is None]

        prompt = f"""
        Kamu adalah sistem yang membantu melengkapi payload API.
        Payload sekarang:
        {json.dumps(pending_config['payload'], indent=2)}
        
        Field yang masih kosong: {missing_fields}
        
        User memberikan jawaban: "{user_message}"
        
        Kembalikan JSON dengan hanya field yang berhasil diisi dari jawaban ini.
        Jika tidak ada yang cocok, kembalikan objek kosong {{}}.
        """

        result = await self.llm_client.ask(prompt, {
            "response_mime_type": "application/json"
        })

        try:
            extracted = json.loads(result.text)
            return extracted if isinstance(extracted, dict) else {}
        except:
            return {}

    @PrivateMethod
    async def get_tool(self, tools: list[dict], query: str)-> ResponseTool:
        prompt = f""" 
        The JSON Schema says:
            Schemas:
                {"\n".join([json.dumps(tool) for tool in tools])}
        Return Only 1 Schema based on user query:
        If user not provide the information fill it with None
        User Query: {query}
        """
        result = await self.llm_client.ask(prompt, {
            "response_mime_type": "application/json",
            "response_schema": ResponseTool,
        })
        if result.parsed.additional_prompt_to_ai:
            self.additional_prompt_to_ai = result.parsed.additional_prompt_to_ai
        return await self.perform_request(result.parsed)

    @PrivateMethod
    async def perform_request(self, config: ResponseTool, retries=3, backoff_factor=1.0):
        print(config.dict())
        if not hasattr(config.payload, "items"):
            return config.payload

        missing_fields = [k for k, v in config.payload.items() if v is None]

        if missing_fields:
            return {
                "status": "need_user_input",
                "missing_fields": missing_fields,
                "config": config.dict()
            }

        attempt = 0
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    kwargs = {}
                    if config.payload:
                        if config.method.upper() == "GET":
                            kwargs["params"] = config.payload
                        else:
                            kwargs["json"] = config.payload

                    response = await client.request(
                        method=config.method,
                        url=config.url,
                        **kwargs
                    )
                    response.raise_for_status()  # Raise jika status code 4xx/5xx
                    return response.text

            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                attempt += 1
                if attempt > retries:
                    raise  # Sudah melewati retry, lempar error
                delay = backoff_factor * (2 ** (attempt - 1))  # exponential backoff
                print(f"Request failed (attempt {attempt}), retrying after {delay:.1f}s...")
                await asyncio.sleep(delay)
        
    @PrivateMethod
    async def explain_answer(self, answer, previous_query):
        prompt = f""" 
        You're a explainer
        
        Previously user query: {previous_query}
        
        Answer: {answer}
        
        explain the answer basedon user language
        {self.additional_prompt_to_ai if self.additional_prompt_to_ai else ""}
        """
        result = await self.llm_client.ask(prompt, stream=self.stream)
        return result