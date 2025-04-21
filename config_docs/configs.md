# MCP Configuration Templates

This document contains the configuration templates needed to connect the MIST (Model Intelligence System for Tasks) MCP server to different AI assistants and code editors.

## 1. Claude Desktop Configuration

Add the following configuration to your Claude Desktop settings to connect to the MIST MCP server:

```json
{
  "mcpServers": {
    "M.I.S.T.": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with-editable",
        "B:\\Upcoming\\mist",
        "mcp",
        "run",
        "B:\\Upcoming\\mist\\server.py"
      ],
      "env": {
        "MCP_GMAIL_CREDENTIALS_PATH": "B:\\Upcoming\\mist\\credentials.json",
        "MCP_GMAIL_TOKEN_PATH": "B:\\Upcoming\\mist\\token.json"
      }
    }
  }
}
```

## 2. Zed Editor Configuration

Add the following configuration to your Zed editor settings to connect to the MIST MCP server:

```json
"context_servers": {
  "mist-server": {
    "command": {
      "path": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with-editable",
        "B:\\Upcoming\\mist",
        "mcp",
        "run",
        "B:\\Upcoming\\mist\\server.py"
      ],
      "env": {
        "MCP_GMAIL_CREDENTIALS_PATH": "B:\\Upcoming\\mist\\credentials.json",
        "MCP_GMAIL_TOKEN_PATH": "B:\\Upcoming\\mist\\token.json"
      }
    },
    "settings": {
      "enable_server": true
    }
  }
}
```

The document provides a simple structure with:

1. Brief introduction to the file
2. Claude Desktop configuration template
3. Zed Editor configuration template
