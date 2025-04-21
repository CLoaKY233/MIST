# MIST - Model Intelligence System for Tasks

MIST is a comprehensive MCP (Model Context Protocol) server that provides intelligent assistant capabilities for both note-taking and Gmail integration. It allows AI assistants to save, edit, create, and delete notes, as well as access and interact with Gmail, including reading messages, searching emails, and sending or composing new messages.

## Features

### Note Management
- Create, read, edit, and delete notes
- Search notes by content or tags
- Generate summaries of notes
- Organize notes by subject

### Gmail Integration
- Query and search emails with advanced filtering
- Read email content
- Compose and send emails
- Manage email labels
- Mark messages as read

## Installation

### Prerequisites
- Python 3.13 or newer
- UV package manager (recommended)

### Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd mist
   ```

2. Install dependencies using UV:
   ```
   uv install
   ```
   
   Or with pip:
   ```
   pip install -e .
   ```

## Gmail API Configuration

There are several steps required to use the Gmail API:

### Google Cloud Setup

1. **Create a Google Cloud Project**
    - Go to [Google Cloud Console](https://console.cloud.google.com/)
    - Click on the project dropdown at the top of the page
    - Click "New Project"
    - Enter a project name (e.g., "MCP Gmail Integration")
    - Click "Create"
    - Wait for the project to be created and select it from the dropdown

2. **Enable the Gmail API**
    - In your Google Cloud project, go to the navigation menu (≡)
    - Select "APIs & Services" > "Library"
    - Search for "Gmail API"
    - Click on the Gmail API card
    - Click "Enable"

3. **Configure OAuth Consent Screen**
    - Go to "APIs & Services" > "OAuth consent screen"
    - Select "External" user type (unless you have a Google Workspace organization)
    - Fill in the required application information:
        - App name: "MCP Gmail Integration"
        - User support email: Your email address
        - Developer contact information: Your email address
    - Click "Save and Continue"
    - Add scopes: Add the necessary Gmail scopes (gmail.readonly, gmail.send, gmail.compose, gmail.labels)
    - Click "Save and Continue"
    - Add test users: Add your Google email address
    - Click "Save and Continue"

4. **Create OAuth Credentials**
    - Go to "APIs & Services" > "Credentials"
    - Click "Create Credentials" > "OAuth client ID"
    - Choose "Desktop app" as the application type
    - Enter a name (e.g., "MCP Gmail Desktop Client")
    - Click "Create"
    - Download the JSON file and save it as `credentials.json` in your project root directory

## Usage

### Running the MCP Server

Start the MCP server:

```
uv run --with mcp[cli] --with-editable . mcp run mist/server.py
```

### Connecting to AI Assistants

#### Claude Desktop

Add the following configuration to your Claude Desktop settings:

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
        "<path-to-mist-directory>",
        "mcp",
        "run",
        "<path-to-mist-directory>/server.py"
      ],
      "env": {
        "MCP_GMAIL_CREDENTIALS_PATH": "<path-to-mist-directory>/credentials.json",
        "MCP_GMAIL_TOKEN_PATH": "<path-to-mist-directory>/token.json"
      }
    }
  }
}
```

#### Zed Editor

Add the following configuration to your Zed editor settings:

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
        "<path-to-mist-directory>",
        "mcp",
        "run",
        "<path-to-mist-directory>/server.py"
      ],
      "env": {
        "MCP_GMAIL_CREDENTIALS_PATH": "<path-to-mist-directory>/credentials.json",
        "MCP_GMAIL_TOKEN_PATH": "<path-to-mist-directory>/token.json"
      }
    },
    "settings": {
      "enable_server": true
    }
  }
}
```

## First Run

When you first run the server, it will prompt you to authenticate with Gmail. Follow the instructions in the terminal to complete the authentication process.

## Project Structure

- `server.py` - Main MCP server entry point
- `tools/` - Contains implementations of all MIST tools
  - `note_tools/` - Note-taking functionality
  - `gmail_tools/` - Gmail interaction functionality
- `config_docs/` - Example configuration files

## License

This project is licensed under the MIT License - see the LICENSE file for details.
