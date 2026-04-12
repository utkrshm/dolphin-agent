import operator
from typing import List, Dict

from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    mem0_user_id: str
    messages: Annotated[list[BaseMessage], add_messages]
    trace: Annotated[list, operator.add]
