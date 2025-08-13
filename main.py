from llm_orchestrator import LLMOrchestrator
from llm_orchestrator.types.agents import Agent
async def main():
    llm_orchestrator = LLMOrchestrator()
    
    await llm_orchestrator.register_agents(
        [
            Agent(
                name="AgentTest",
                # urlAgentFile="http://localhost:5173/test_agents/agent-test/agent.json"
                urlAgentFile="https://raw.githubusercontent.com/Azzarnuji/llm_orchestrator/refs/heads/main/test_agents/agent-test/agent.json"
            )
        ]
    )
    await llm_orchestrator.warm_up()
    
    while True:
        query = input("Enter your query: ")
        if query == "exit":
            break
        
        # STREAM EXAMPLE
        response = await llm_orchestrator.invoke_query(query, stream=True)
        for chunk in response:
            print(chunk.text, end="")
        print("\n")
        
        #NON STREAM EXAMPLE
        # response = await llm_orchestrator.invoke_query(query)
        # print(response.text)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())