# server.py
from mcp.server.fastmcp import FastMCP
from tools.note_tools import register_tools

# Create an MCP server
mcp = FastMCP("M.I.S.T.")

# Register note tools
register_tools(mcp)
