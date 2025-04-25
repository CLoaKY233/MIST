---
name: Integration Issue
about: Report problems with integrating MIST with other tools or services
title: "[INTEGRATION] "
labels: integration
assignees: ''
---

## Integration Issue Description
A clear and concise description of the integration issue you're experiencing.

## Integration Details
- What are you trying to integrate MIST with? [e.g., Claude Desktop, Zed Editor, another AI assistant]
- Version of the other software/service: [e.g., Claude Desktop 1.0.5]

## Environment Information
- OS: [e.g., Windows 10, macOS 13.0, Ubuntu 22.04]
- Python Version: [e.g., 3.13.0]
- MIST Version: [e.g., 0.0.5]

## Configuration
Provide your integration configuration (redact any API keys or sensitive information):
```json
{
  "mcpServers": {
    "M.I.S.T.": {
      "command": "uv",
      "args": [
        "..."
      ],
      "env": {
        "MIST_GOOGLE_CREDENTIALS_PATH": "...",
        "MIST_NOTES_DIR": "..."
      }
    }
  }
}
```

## Error Messages
If applicable, include any error messages you're receiving:
```
Error message here
```

## Reproduction Steps
Steps to reproduce the integration issue:
1. Configure MIST with '...'
2. Set up integration with '...'
3. Try to '...'
4. Observe error '...'

## Expected Behavior
What did you expect to happen?

## Actual Behavior
What actually happened?

## Troubleshooting Steps Taken
What steps have you already taken to troubleshoot the issue?

## Additional Context
Add any other context, screenshots, or logs about the integration issue here.