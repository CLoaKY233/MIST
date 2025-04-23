# Make the notion_tools directory a proper package
from .tool import register_tools_notion

__all__ = ["register_tools_notion"]