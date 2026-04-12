from langchain_core.messages import AIMessage
from langgraph.types import interrupt
from agent.state import AgentState
from langchain_core.messages import ToolMessage

WRITE_TOOLS = {"write_to_file"}


def tool_node(state: AgentState, tools_by_name: dict):
    last_message = state["messages"][-1]
    results = []
    trace = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name in WRITE_TOOLS:
            decision = interrupt({
                "tool": tool_name,
                "args": tool_args,
                "message": f"Agent wants to call '{tool_name}' with args {tool_args}. Approve or reject?"
            })
            if decision == "reject":
                results.append(ToolMessage(
                    content="User rejected this operation.",
                    tool_call_id=tool_call["id"]
                ))
                trace.append({"tool": tool_name, "args": tool_args, "status": "rejected"})
                continue

        tool = tools_by_name[tool_name]
        result = tool.invoke(tool_args)

        results.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        ))
        trace.append({"tool": tool_name, "args": tool_args, "result": str(result)})

    return {"messages": results, "trace": trace}