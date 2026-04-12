import os
from functools import partial
from dotenv import load_dotenv

from mem0 import MemoryClient
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from agent.state import AgentState
from agent.nodes.agent_node import agent_node
from agent.nodes.tool_node import tool_node
from agent.tools_registry import tools

load_dotenv()

def load_model():
    ollama_url = os.getenv("OLLAMA_BASE_URL")

    if ollama_url:
        from langchain_ollama import ChatOllama
        print("Using Ollama")
        model = ChatOllama(
            model=os.getenv("OLLAMA_MAIN_MODEL", "qwen3.5:4b"),
            base_url=ollama_url,
            temperature=0
        )
        return model.bind_tools(tools)

    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        from langchain_groq import ChatGroq
        print("Falling back to Groq")
        model = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0
        )
        return model.bind_tools(tools)

    raise RuntimeError(
        "No LLM configured. Set either OLLAMA_BASE_URL or GROQ_API_KEY in your .env file."
    )


def load_memory():
    if not os.getenv("MEM0_API_KEY"):
        raise RuntimeError(
            "No Memory API given, please provide the Mem0 API key by setting the `MEM0_API_KEY` environment variable."
        )

    return MemoryClient(
        org_id=os.getenv("MEM0_ORG_ID", ""),
        project_id=os.getenv("MEM0_PROJECT_ID", "")
    )

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


model = load_model()
tools_by_name = {tool.name: tool for tool in tools}
memory = load_memory()

_agent_node = partial(agent_node, model=model, memory_client=memory)
_tool_node = partial(tool_node, tools_by_name=tools_by_name)

graph = (
    StateGraph(AgentState)
    .add_node("agent", _agent_node)
    .add_node("tools", _tool_node)
    .add_edge(START, "agent")
    .add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    .add_edge("tools", "agent")
    .compile(checkpointer=MemorySaver())
)