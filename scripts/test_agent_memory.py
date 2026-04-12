from langgraph.types import Command
from agent.graph import graph

config = {"configurable": {"thread_id": "test-session-1"}}


def stream_agent(input_text: str, mem0_user_id: str):
    print(f"\n>>> User: {input_text}\n")

    initial_state = {
        "messages": [{"role": "user", "content": input_text}], 
        "mem0_user_id": mem0_user_id
    }

    for chunk in graph.stream(
        initial_state,
        config=config,
        stream_mode="updates",
    ):
        if "__interrupt__" in chunk:
            interrupt_data = chunk["__interrupt__"][0].value
            print(f"\n[HITL] Agent wants to: {interrupt_data['message']}")
            decision = "approve"

            for chunk in graph.stream(
                Command(resume=decision),
                config=config,
                stream_mode="updates"
            ):
                if "agent" in chunk:
                    messages = chunk["agent"].get("messages", [])
                    for msg in messages:
                        if hasattr(msg, "content") and msg.content:
                            print(f"\n<<< Agent: {msg.content}")

        elif "agent" in chunk:
            messages = chunk["agent"].get("messages", [])
            for msg in messages:
                if hasattr(msg, "content") and msg.content:
                    print(f"\n<<< Agent: {msg.content}")

        elif "tools" in chunk:
            trace = chunk["tools"].get("trace", [])
            for entry in trace:
                print(f"[TRACE] Tool: {entry['tool']} | Args: {entry['args']} | Status: {entry.get('status', 'executed')}")


if __name__ == "__main__":
    mem0_user_id = "test-user"

    # stream_agent("Write a short poem about the ocean to a file called ocean.txt", mem0_user_id=mem0_user_id)
    stream_agent("Summarize the file ocean.txt", mem0_user_id=mem0_user_id)
    
    stream_agent("On which file did we just work?", mem0_user_id=mem0_user_id)
    