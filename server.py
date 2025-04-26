from mcp.server.fastmcp import FastMCP
from tools.note_tools import register_tools_note
from tools.gmail_tools import register_tools_mail
from tools.tasks_tools import register_tools_tasks
from tools.calendar_tools import register_tools_calendar


mcp = FastMCP(
    "M.I.S.T.",
    instructions="Save, Edit, Create, Delete Notes, Access and interact with Gmail, Calendar, and Tasks. You can get messages, search emails, send new messages, manage calendar events, and organize tasks.",
)

register_tools_note(mcp)
register_tools_mail(mcp)
register_tools_tasks(mcp)
register_tools_calendar(mcp)
