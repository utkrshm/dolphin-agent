from langchain_core.messages import SystemMessage, HumanMessage
from agent.state import AgentState
from langchain.chat_models import BaseChatModel
from mem0 import MemoryClient
from mem0.exceptions import MemoryError

SYSTEM_PROMPT = """
You are a helpful local voice assistant. The user's input has been transcribed from audio, so it may be informal or imprecise — interpret it charitably.

You have access to the following tools:
- read_file: Read the contents of a file from the output directory
- write_to_file: Write or append content to a file in the output directory
- summarize_file: Summarize the contents of a file

Rules you must follow:
- Always restrict file operations to the output directory
- Execute compound commands fully — if the user asks for multiple things, do all of them
- If a request is ambiguous, ask for clarification before executing
- Never guess file paths — only use filenames the user explicitly provides
"""


def agent_node(state: AgentState, model: BaseChatModel, memory_client: MemoryClient):
    user_id = state["mem0_user_id"]
    messages = state["messages"]

    # Retrieve relevant memory
    system_prompt = SYSTEM_PROMPT 
    
    try:
        memories = memory_client.search(messages[-1].content, filters={"user_id": user_id})
        memory_list = memories['results']

        context = "\nRelevant information from previous conversations:\n"
        for memory in memory_list:
            context += f"- {memory['memory']}\n"
        system_prompt = SYSTEM_PROMPT + context
        
        print(context)
    
    except MemoryError as e:
        print("[MEM0] Memory calling failed, reverting to memoryless state")
        print(f"Message: {e.message}\nSuggestion: {e.suggestion}")
        pass

    # Run the agent
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = model.invoke(messages)
    
    # Store the interaction in Memory layer
    try:
        user_message = next(m for m in state["messages"] if isinstance(m, HumanMessage))
        interaction = [
            {"role": "user", "content": user_message.content},
            {"role": "assistant", "content": response.content}
        ]
        result = memory_client.add(interaction, user_id=user_id)
        print(f"Memory saved: {len(result.get('results', []))} memories added")
    except Exception as e:
        print(f"Error saving memory: {e}")

    return {"messages": [response]}