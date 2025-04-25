# MIST Troubleshooting Guide

This guide provides solutions for common issues you may encounter when setting up or using MIST.

## Installation Issues

### Python Version Errors

**Issue**: Error about incompatible Python version.

**Solution**: 
- MIST requires Python 3.13 or newer
- Check your Python version with `python --version`
- Install the correct version of Python from [python.org](https://www.python.org/downloads/)

### Package Installation Failures

**Issue**: Dependencies fail to install with UV or pip.

**Solutions**:
1. Update your package manager:
   ```bash
   pip install --upgrade pip
   # or for UV
   pip install --upgrade uv
   ```

2. Check for system-level dependencies:
   - On Ubuntu/Debian: `sudo apt-get install build-essential python3-dev`
   - On Fedora/RHEL: `sudo dnf install gcc python3-devel`
   - On macOS: `xcode-select --install`

3. Try installing with verbose output to see specific errors:
   ```bash
   pip install -e . -v
   # or for UV
   uv install --verbose
   ```

## Configuration Issues

### Environment Variables Not Loading

**Issue**: MIST doesn't recognize environment variables set in `.env` file.

**Solutions**:
1. Verify your `.env` file is in the project root directory
2. Check file format - no spaces around equal signs:
   ```env
   # Correct
   MIST_NOTES_DIR=/path/to/notes
   
   # Incorrect (has spaces)
   MIST_NOTES_DIR = /path/to/notes
   ```
3. Set variables directly in your terminal to test:
   ```bash
   export MIST_NOTES_DIR=/path/to/notes
   ```

### Missing Configuration File

**Issue**: Error about missing configuration files like `credentials.json`.

**Solutions**:
1. Verify the file exists at the specified path
2. Check file permissions
3. For Google API credentials, ensure you've downloaded the JSON file from Google Cloud Console
4. Provide absolute paths instead of relative paths

## Authentication Issues

### Google OAuth Failures

**Issue**: Authentication fails with Google services.

**Solutions**:
1. Delete `token.json` (or the file specified in `MIST_GOOGLE_TOKEN_PATH`) and re-authenticate
2. Verify your credentials.json is valid and includes correct client ID and secret
3. Check that you've enabled the required APIs in Google Cloud Console:
   - Gmail API
   - Calendar API
   - Tasks API
4. Ensure your OAuth consent screen is properly configured with necessary scopes



## Server Connection Issues

### Server Fails to Start

**Issue**: MCP server doesn't start or crashes immediately.

**Solutions**:
1. Check for error messages in the terminal
2. Verify all required environment variables are set
3. Ensure no other process is using the same port
4. Check file permissions for directories and files accessed by MIST
5. Run with explicit debug output:
   ```bash
   MIST_LOG_LEVEL=DEBUG uv run --with mcp[cli] --with-editable . mcp run mist/server.py
   ```

### AI Assistant Cannot Connect to MIST

**Issue**: Claude Desktop or Zed can't connect to the MIST server.

**Solutions**:
1. Verify the server is running
2. Check paths in AI assistant configuration:
   - Paths should be absolute (e.g., `C:\path\to\mist` or `/path/to/mist`)
   - Verify all environment variables in the configuration
3. Look for firewall or antivirus blocking the connection
4. On Windows, run the terminal as administrator
5. Try restarting the AI assistant application

## Functionality Issues

### Notes Not Saving

**Issue**: Notes aren't being created or saved.

**Solutions**:
1. Check if the notes directory exists and is writable
   ```bash
   # Linux/macOS
   ls -la $MIST_NOTES_DIR
   touch $MIST_NOTES_DIR/test.txt
   
   # Windows
   dir %MIST_NOTES_DIR%
   echo test > %MIST_NOTES_DIR%\test.txt
   ```
2. Verify permissions on the notes directory
3. Check for disk space issues
4. Look for error messages in the terminal output

### Gmail API Errors

**Issue**: Email operations fail with API errors.

**Solutions**:
1. Check if you've granted the correct permissions:
   - `gmail.readonly` for reading emails
   - `gmail.send` for sending emails
   - `gmail.labels` for managing labels
2. Verify you haven't exceeded Google API quotas
3. Check if your token needs to be refreshed (delete token.json and re-authenticate)
4. For "Invalid Grant" errors, delete token.json and re-authenticate

### Calendar or Tasks API Issues

**Issue**: Calendar or Tasks operations fail.

**Solutions**:
1. Ensure the respective API is enabled in Google Cloud Console
2. Check if you have the correct permissions for the calendar/task list
3. Verify date formats are in RFC3339 format (e.g., `2023-06-03T10:00:00-07:00`)
4. For personal Google accounts, check if you've added yourself as a test user in OAuth consent screen

## Common Error Messages

### "No module named 'mcp'"

**Solution**: Install MCP with the CLI feature:
```bash
uv install --with mcp[cli]
```

### "Missing required option: credentials_path"

**Solution**: Set the MIST_GOOGLE_CREDENTIALS_PATH environment variable or provide it in the command.

### "Error: invalid_grant"

**Solution**: Your OAuth token is invalid or expired. Delete token.json and re-authenticate.

### "Error: insufficient_permission"

**Solution**: The Google account doesn't have permission for the requested operation, or you need to request additional OAuth scopes.

### "Error: daily limit exceeded"

**Solution**: You've hit Google API rate limits. Wait until the quota resets or request higher limits.

## Performance Issues

### Slow Response Times

**Issue**: MIST responds slowly to requests.

**Solutions**:
1. Reduce the scope of operations (request fewer emails, events, etc.)
2. Add more specific filters to search operations
3. Check system resources (CPU, memory)
4. Check your internet connection speed for operations involving Google APIs

### High Memory Usage

**Issue**: MIST uses excessive memory.

**Solutions**:
1. Process fewer items at once (use limits)
2. Implement more specific filters
3. Close and restart the server periodically
4. Check for memory leaks by monitoring usage patterns

## Log Collection

When reporting issues, include the following information:

1. MIST version
2. Python version
3. Operating system
4. Complete error message
5. Steps to reproduce the issue
6. Server logs (with sensitive information redacted)

To collect logs with increased verbosity:

```bash
MIST_LOG_LEVEL=DEBUG uv run --with mcp[cli] --with-editable . mcp run mist/server.py > mist_debug.log 2>&1
```

## Getting Help

If you continue to experience issues:

1. Check the GitHub repository for known issues
2. Search the discussions for similar problems
3. Create a new issue with detailed information about your problem
4. Include your system information and relevant logs

## Common Command Line Troubleshooting

### Check Environment Variables

```bash
# Linux/macOS
env | grep MIST

# Windows PowerShell
Get-ChildItem Env:*MIST*
```

### Test Directory Permissions

```bash
# Linux/macOS
touch $MIST_NOTES_DIR/test.txt && echo "Success" || echo "Failed"

# Windows
echo test > %MIST_NOTES_DIR%\test.txt && echo Success || echo Failed
```

### View OAuth Scopes

```bash
# Linux/macOS
cat token.json | grep scope

# Windows PowerShell
Get-Content token.json | Select-String scope
```

### Check Server Ports

```bash
# Linux/macOS
lsof -i :1334

# Windows
netstat -ano | findstr 1334
```