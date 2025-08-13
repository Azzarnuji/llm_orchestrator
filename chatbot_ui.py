import streamlit as st
import asyncio
from llm_orchestrator import LLMOrchestrator
from llm_orchestrator.types.agents import Agent

@st.cache_resource
def init_orchestrator():
    llm_orchestrator = LLMOrchestrator()

    async def setup():
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

    asyncio.run(setup())
    return llm_orchestrator


def get_available_tools(llm_orchestrator):
    """Ambil daftar tools dari semua agent, support instance atau dict."""
    tools_list = []

    agents_obj = llm_orchestrator.agents

    # Kalau dict of object → loop .values()
    if isinstance(agents_obj, dict):
        for agent in agents_obj.values():
            # agent bisa object atau dict
            if hasattr(agent, "tools"):  # Agent instance
                for tool in agent.tools:
                    tools_list.append(f"**{tool.name}** — {tool.description}")
            elif isinstance(agent, dict):  # dict biasa
                for tool in agent.get("tools", []):
                    tools_list.append(f"**{tool['name']}** — {tool['description']}")

    # Kalau list
    elif isinstance(agents_obj, list):
        for agent in agents_obj:
            if hasattr(agent, "tools"):
                for tool in agent.tools:
                    tools_list.append(f"**{tool.name}** — {tool.description}")
            elif isinstance(agent, dict):
                for tool in agent.get("tools", []):
                    tools_list.append(f"**{tool['name']}** — {tool['description']}")

    return tools_list


def main():
    st.title("💬 Chatbot")
    st.caption("🚀 A streamlit chatbot powered by LLM Orchestrator")

    llm_orchestrator = init_orchestrator()

    # 🔹 Ambil info tools yang tersedia
    available_tools = get_available_tools(llm_orchestrator)
    if available_tools:
        st.info("🛠 **Available Tools:**\n\n" + "\n\n".join(available_tools))
    else:
        st.warning("Tidak ada tools yang terdaftar.")

    # Session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):

                async def stream_response():
                    response = await llm_orchestrator.invoke_query(prompt, stream=True)
                    for chunk in response:
                        yield chunk.text

                response = st.write_stream(stream_response)

        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
