# MIST Configuration Guide

This document provides detailed instructions for configuring MIST (Model Intelligence System for Tasks) for various environments and integration scenarios.

## Environment Variables

MIST uses environment variables for configuration. These can be set in a `.env` file in the project root directory or in your system environment.

### Core Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MIST_NOTES_DIR` | Directory path where notes are stored | None | Yes |
| `MIST_NOTES_FORMAT` | Format for stored notes | `md` | No |

### Google API Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MIST_GOOGLE_CREDENTIALS_PATH` | Path to Google API credentials JSON file | `./credentials.json` | Yes for Google integration |
| `MIST_GOOGLE_TOKEN_PATH` | Path where OAuth token will be stored | `./token.json` | Yes for Google integration |
| `MIST_GOOGLE_SCOPES` | Comma-separated list of OAuth scopes | All required scopes | No |



## Example Configuration

Here's a sample `.env` file with all supported configuration options:

```env
# Notes storage configuration
MIST_NOTES_DIR=C:\\Users\\username\\Documents\\Notes
MIST_NOTES_FORMAT=md

# Google API configuration
MIST_GOOGLE_CREDENTIALS_PATH=./credentials.json
MIST_GOOGLE_TOKEN_PATH=./token.json
```

## AI Assistant Configuration

### Claude Desktop

To use MIST with Claude Desktop, add the following to your Claude Desktop configuration:

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
        "/path/to/mist",
        "mcp",
        "run",
        "/path/to/mist/server.py"
      ],
      "env": {
        "MIST_GOOGLE_CREDENTIALS_PATH": "/path/to/mist/credentials.json",
        "MIST_GOOGLE_TOKEN_PATH": "/path/to/mist/token.json",
        "MIST_NOTES_DIR": "/path/to/notes"
      }
    }
  }
}
```

### Zed Editor

To use MIST with Zed editor, add the following to your Zed settings:

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
        "/path/to/mist",
        "mcp",
        "run",
        "/path/to/mist/server.py"
      ],
      "env": {
        "MIST_GOOGLE_CREDENTIALS_PATH": "/path/to/mist/credentials.json",
        "MIST_GOOGLE_TOKEN_PATH": "/path/to/mist/token.json",
        "MIST_NOTES_DIR": "/path/to/notes"
      }
    },
    "settings": {
      "enable_server": true
    }
  }
}
```

## Path Configuration Guidelines

### Windows Paths

On Windows, use double backslashes or forward slashes in path strings:

```env
# Either of these formats works on Windows
MIST_NOTES_DIR=C:\\Users\\username\\Documents\\Notes
MIST_NOTES_DIR=C:/Users/username/Documents/Notes
```

### Linux/macOS Paths

On Linux and macOS, use standard path format:

```env
MIST_NOTES_DIR=/home/username/notes
```

## OAuth Scopes

MIST requests the following OAuth scopes by default:

| Service | Scopes |
|---------|--------|
| Gmail | `gmail.readonly`, `gmail.send`, `gmail.compose`, `gmail.labels` |
| Calendar | `calendar`, `calendar.events`, `calendar.readonly` |
| Tasks | `tasks`, `tasks.readonly` |

If you need to customize these scopes, you can set the `MIST_GOOGLE_SCOPES` environment variable with a comma-separated list of scopes.

## Security Considerations

1. **API Keys and Tokens**:
   - Keep your `.env` file secure and never commit it to version control
   - Consider using environment variables instead of the `.env` file in production

2. **OAuth Security**:
   - The `token.json` file contains sensitive OAuth credentials
   - Ensure it has appropriate file permissions (readable only by the user running MIST)
   - If your token may be compromised, revoke it in the Google Cloud Console and re-authenticate

## Advanced Configuration

### Running Behind a Proxy

If you need to run MIST behind a proxy, set the following environment variables:

```env
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
```

### Custom Note Templates

You can create custom note templates by modifying the note creation tool in the MIST codebase. Look for the `add_note` function in `tools/note_tools/tool.py`.

### Debugging

To enable debug logging, set:

```env
MIST_LOG_LEVEL=DEBUG
```

## Troubleshooting Configuration Issues

### Environment Variables Not Loading

- Verify your `.env` file is in the project root directory
- Ensure the file format is correct (no spaces around equal signs)
- Check file permissions

### Path Issues

- Verify all paths exist and are accessible
- Check for incorrect path separators
- Ensure paths are absolute or relative to the project root

### OAuth Configuration

- Verify your Google Cloud project has the correct APIs enabled
- Check that your OAuth consent screen is properly configured
- Ensure your credentials.json file is valid and contains the correct client ID and secret