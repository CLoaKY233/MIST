# Contributing to MIST

Thank you for your interest in contributing to MIST! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Feature Requests](#feature-requests)
- [Bug Reports](#bug-reports)

## Code of Conduct

Please be respectful and considerate of others in all interactions. We aim to foster an inclusive and welcoming community.

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Development Setup

### Prerequisites

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Git

### Setting Up Your Development Environment

1. Fork the repository on GitHub

2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mist.git
   cd mist
   ```

3. Set up the upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/mist.git
   ```

4. Create a virtual environment and install dependencies:
   ```bash
   # Using UV (recommended)
   uv venv
   uv pip install -e .
   
   # Using standard venv
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -e .
   ```

5. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   # or
   pip install -e ".[dev]"
   ```

6. Configure your environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running the Development Server

```bash
uv run --with mcp[cli] --with-editable . mcp run mist/server.py
```

## Project Structure

```
mist/
├── server.py                  # Main MCP server entry point
├── tools/                     # Tool implementations
│   ├── note_tools/            # Note management
│   ├── gmail_tools/           # Gmail integration
│   ├── calendar_tools/        # Calendar integration
│   ├── tasks_tools/           # Tasks integration
│   └── google_api/            # Google API common utilities
├── config_docs/               # Configuration examples
├── tests/                     # Test suite
├── .env                       # Environment configuration
└── README.md                  # Project documentation
```

## Pull Request Process

1. **Create a branch**: Create a branch from `main` with a descriptive name:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**: Implement your feature or bug fix.

3. **Add and commit your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

4. **Run tests**: Ensure all tests pass:
   ```bash
   pytest
   ```

5. **Run linting**: Format your code and check for issues:
   ```bash
   ruff check .
   ruff format .
   ```

6. **Update documentation**: If necessary, update relevant documentation.

7. **Push your changes**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a pull request**: Go to GitHub and open a pull request against `main`.

9. **Review process**: Address any review comments and update your PR as needed.

## Coding Standards

We use [Ruff](https://github.com/astral-sh/ruff) for code formatting and linting.

Key guidelines:

- Use type hints for function parameters and return values
- Document functions, classes, and modules using Google-style docstrings
- Keep functions focused on a single responsibility
- Write clear, descriptive variable and function names
- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines

To format your code:

```bash
ruff format .
```

To run linting checks:

```bash
ruff check .
```

## Testing

We use [pytest](https://docs.pytest.org/) for testing. Tests are located in the `tests/` directory.

### Running Tests

Run all tests:

```bash
pytest
```

Run tests for a specific module:

```bash
pytest tests/test_note_tools.py
```

Run tests with coverage report:

```bash
pytest --cov=mist
```

### Writing Tests

- Each module should have corresponding tests
- Focus on unit tests for individual functions
- Mock external services (Google APIs) for testing
- Test both successful operations and error cases
- Use fixtures for common setup

Example test:

```python
def test_add_note(tmp_path, monkeypatch):
    # Setup
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    monkeypatch.setenv("MIST_NOTES_DIR", str(notes_dir))
    
    # Execute
    result = add_note("Test Note", "This is a test note", "Testing")
    
    # Verify
    assert "saved with ID" in result
    note_files = list(notes_dir.glob("*.md"))
    assert len(note_files) == 1
    assert note_files[0].read_text().startswith("# Test Note")
```

## Documentation

Good documentation is critical for the project. Please update documentation when making changes:

- Update function docstrings for any modified functions
- Update README.md if you've changed user-facing functionality
- Update or create documentation in `config_docs/` for new features
- Add examples for new functionality

We use Markdown for documentation.

## Feature Requests

We welcome feature requests! To propose a new feature:

1. Check existing issues to see if your feature has already been requested
2. Open a new issue with the label `enhancement`
3. Clearly describe the feature and its use cases
4. If possible, outline how it might be implemented

## Bug Reports

If you find a bug, please report it:

1. Check existing issues to see if the bug has already been reported
2. Open a new issue with the label `bug`
3. Include:
   - Description of the bug
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details (OS, Python version, MIST version)
   - Any relevant logs or error messages

## Advanced Development

### Adding New Tools

To add a new tool to MIST:

1. Create a new module in the appropriate directory under `tools/`
2. Define your tool functions
3. Create a `register_tools_xxx` function that registers the tools with MCP
4. Update `server.py` to call your registration function
5. Add tests for your new tool
6. Update documentation

Example tool function structure:

```python
def my_new_tool(param1: str, param2: int) -> str:
    """
    Description of what the tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
    # Implementation
    result = do_something(param1, param2)
    return result


def register_tools_mynewfeature(mcp):
    """Register all mynewfeature tools with the MCP server."""
    mcp.tool()(my_new_tool)
    # Register other tools...
```

### Working with Google APIs

When working with Google APIs:

1. Use the common authentication in `tools/google_api/`
2. Handle errors appropriately
3. Respect API rate limits
4. Document required OAuth scopes

### Local Development Tips

- Use the `--reload` flag to automatically reload the server when files change
- Create a test account for Google API development
- Use environment variables to switch between development and production configurations

Thank you for contributing to MIST!