from langgraph.types import Command
from agent.graph import graph

config = {"configurable": {"thread_id": "test-session-1"}}


def stream_agent(input_text: str):
    print(f"\n>>> User: {input_text}\n")

    for chunk in graph.stream(
        {"messages": [{"role": "user", "content": input_text}]},
        config=config,
        stream_mode="updates"
    ):
        if "__interrupt__" in chunk:
            interrupt_data = chunk["__interrupt__"][0].value
            print(f"\n[HITL] Agent wants to: {interrupt_data['message']}")
            decision = input("Type 'approve' or 'reject': ").strip().lower()

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
    stream_agent("Write a short poem about the ocean to a file called ocean.txt")
    stream_agent("Summarize the file ocean.txt")
    
    
    print("\n\n#### TESTING MULTIPLE COMMANDS CHAINED TOGETHER ####\n\n")
    stream_agent("Write a short paragraph on AI Agents in a file called agents dot tee-ex-tee and then summarize the file ocean.txt")