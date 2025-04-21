# Make the note_tools directory a proper package
from .tool import register_tools

__all__ = ['register_tools']