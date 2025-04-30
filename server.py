from mcp.server.fastmcp import FastMCP
from tools.note_tools import register_tools_note
from tools.gmail_tools import register_tools_mail
from tools.tasks_tools import register_tools_tasks
from tools.calendar_tools import register_tools_calendar
from tools.git_tools import register_tools_git


mcp = FastMCP(
    "M.I.S.T.",
    instructions="Save, Edit, Create, Delete Notes, Access and interact with Gmail, Calendar, Tasks, and Git repositories. You can get messages, search emails, send new messages, manage calendar events, organize tasks, and perform Git operations.",
)

register_tools_note(mcp)
register_tools_mail(mcp)
register_tools_tasks(mcp)
register_tools_calendar(mcp)
register_tools_git(mcp)
