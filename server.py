# server.py
from mcp.server.fastmcp import FastMCP
from tools.note_tools import register_tools_note
from tools.gmail_tools import register_tools_mail
from tools.tasks_tools import register_tools_tasks

# Create an MCP server
mcp = FastMCP(
    "M.I.S.T.",
    instructions="Save, Edit, Create, Delete Notes, Access and interact with Gmail. You can get messages, threads, search emails, and send or compose new messages.",
)

register_tools_note(mcp)
register_tools_mail(mcp)
register_tools_tasks(mcp)
