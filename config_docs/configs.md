# MCP Configuration Templates

This document contains the configuration templates needed to connect the MIST (Model Intelligence System for Tasks) MCP server to different AI assistants and code editors.

## Environment Configuration

Before setting up your AI assistant connections, make sure you have created a `.env` file in the MIST root directory:

```env
# Notes storage configuration
MIST_NOTES_DIR=C:/Users/username/Documents/Notes

# Google API configuration
MIST_GOOGLE_CREDENTIALS_PATH=./credentials.json
MIST_GOOGLE_TOKEN_PATH=./token.json

# Optional debugging configuration
MIST_LOG_LEVEL=INFO
```

## 1. Claude Desktop Configuration

Add the following configuration to your Claude Desktop settings to connect to the MIST MCP server:

### Windows Example

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
        "C:/Users/username/projects/mist",
        "mcp",
        "run",
        "C:/Users/username/projects/mist/server.py"
      ],
      "env": {
        "MIST_GOOGLE_CREDENTIALS_PATH": "C:/Users/username/projects/mist/credentials.json",
        "MIST_GOOGLE_TOKEN_PATH": "C:/Users/username/projects/mist/token.json",
        "MIST_NOTES_DIR": "C:/Users/username/Documents/Notes"
      }
    }
  }
}
```

### macOS/Linux Example

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
        "/home/username/projects/mist",
        "mcp",
        "run",
        "/home/username/projects/mist/server.py"
      ],
      "env": {
        "MIST_GOOGLE_CREDENTIALS_PATH": "/home/username/projects/mist/credentials.json",
        "MIST_GOOGLE_TOKEN_PATH": "/home/username/projects/mist/token.json",
        "MIST_NOTES_DIR": "/home/username/Documents/Notes"
      }
    }
  }
}
```

## 2. Zed Editor Configuration

Add the following configuration to your Zed editor settings to connect to the MIST MCP server:

### Windows Example

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
        "C:/Users/username/projects/mist",
        "mcp",
        "run",
        "C:/Users/username/projects/mist/server.py"
      ],
      "env": {
        "MIST_GOOGLE_CREDENTIALS_PATH": "C:/Users/username/projects/mist/credentials.json",
        "MIST_GOOGLE_TOKEN_PATH": "C:/Users/username/projects/mist/token.json",
        "MIST_NOTES_DIR": "C:/Users/username/Documents/Notes"
      }
    },
    "settings": {
      "enable_server": true
    }
  }
}
```

### macOS/Linux Example

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
        "/home/username/projects/mist",
        "mcp",
        "run",
        "/home/username/projects/mist/server.py"
      ],
      "env": {
        "MIST_GOOGLE_CREDENTIALS_PATH": "/home/username/projects/mist/credentials.json",
        "MIST_GOOGLE_TOKEN_PATH": "/home/username/projects/mist/token.json", 
        "MIST_NOTES_DIR": "/home/username/Documents/Notes"
      }
    },
    "settings": {
      "enable_server": true
    }
  }
}
```

## 3. Running with Direct Command

You can also run MIST directly from the command line:

### Windows (Command Prompt)

```cmd
set MIST_NOTES_DIR=C:\Users\username\Documents\Notes
set MIST_GOOGLE_CREDENTIALS_PATH=C:\Users\username\projects\mist\credentials.json
set MIST_GOOGLE_TOKEN_PATH=C:\Users\username\projects\mist\token.json
cd C:\Users\username\projects\mist
uv run --with mcp[cli] --with-editable . mcp run mist/server.py
```

### Windows (PowerShell)

```powershell
$env:MIST_NOTES_DIR="C:\Users\username\Documents\Notes"
$env:MIST_GOOGLE_CREDENTIALS_PATH="C:\Users\username\projects\mist\credentials.json"
$env:MIST_GOOGLE_TOKEN_PATH="C:\Users\username\projects\mist\token.json"
cd C:\Users\username\projects\mist
uv run --with mcp[cli] --with-editable . mcp run mist/server.py
```

### macOS/Linux (Bash/Zsh)

```bash
export MIST_NOTES_DIR=/home/username/Documents/Notes
export MIST_GOOGLE_CREDENTIALS_PATH=/home/username/projects/mist/credentials.json
export MIST_GOOGLE_TOKEN_PATH=/home/username/projects/mist/token.json
cd /home/username/projects/mist
uv run --with mcp[cli] --with-editable . mcp run mist/server.py
```
