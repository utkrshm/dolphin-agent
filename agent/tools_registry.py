from agent.tools.file_ops import read_file, write_to_file
from agent.tools.summarizer import summarize_file

from langchain.tools import tool

read_file_tool = tool(read_file)
write_file_tool = tool(write_to_file)
summarize_file_tool = tool(summarize_file)

tools = [
    read_file_tool,
    write_file_tool,
    summarize_file_tool
]