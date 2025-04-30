"""
Git MCP Server Implementation

This module provides a Model Context Protocol server for interacting with Git repositories.
It exposes Git commands as tools for AI assistants to use.
"""

from typing import List, Dict, Any, Optional
import os
from pathlib import Path

from tools.git_tools.gitapi import (
    get_repo,
    git_status,
    git_diff_unstaged,
    git_diff_staged,
    git_diff,
    git_commit,
    git_add,
    git_reset,
    git_log,
    git_create_branch,
    git_checkout,
    git_show,
    git_init,
    git_branch_list,
    git_remote_list,
    git_stash_list,
    git_remote_add,
    git_pull,
    git_push,
)

def status_tool(repo_path: str) -> str:
    """
    Show the working tree status.

    Args:
        repo_path: Path to the Git repository

    Returns:
        Status output as string
    """
    try:
        repo = get_repo(repo_path)
        status = git_status(repo)
        return f"Repository status for {repo_path}:\n\n{status}"
    except Exception as e:
        return f"Error getting repository status: {str(e)}"

def diff_unstaged_tool(repo_path: str) -> str:
    """
    Show unstaged changes in the working directory.

    Args:
        repo_path: Path to the Git repository

    Returns:
        Diff output as string
    """
    try:
        repo = get_repo(repo_path)
        diff = git_diff_unstaged(repo)
        if not diff:
            return "No unstaged changes."
        return f"Unstaged changes in {repo_path}:\n\n{diff}"
    except Exception as e:
        return f"Error getting unstaged changes: {str(e)}"

def diff_staged_tool(repo_path: str) -> str:
    """
    Show changes staged for commit.

    Args:
        repo_path: Path to the Git repository

    Returns:
        Diff output as string
    """
    try:
        repo = get_repo(repo_path)
        diff = git_diff_staged(repo)
        if not diff:
            return "No staged changes."
        return f"Staged changes in {repo_path}:\n\n{diff}"
    except Exception as e:
        return f"Error getting staged changes: {str(e)}"

def diff_tool(repo_path: str, target: str) -> str:
    """
    Show differences between branches or commits.

    Args:
        repo_path: Path to the Git repository
        target: Target to compare (branch name, commit hash, etc.)

    Returns:
        Diff output as string
    """
    try:
        repo = get_repo(repo_path)
        diff = git_diff(repo, target)
        if not diff:
            return f"No differences between current HEAD and {target}."
        return f"Diff with {target} in {repo_path}:\n\n{diff}"
    except Exception as e:
        return f"Error getting diff: {str(e)}"

def commit_tool(repo_path: str, message: str) -> str:
    """
    Record changes to the repository.

    Args:
        repo_path: Path to the Git repository
        message: Commit message

    Returns:
        Confirmation message with commit hash
    """
    try:
        repo = get_repo(repo_path)
        result = git_commit(repo, message)
        return result
    except Exception as e:
        return f"Error committing changes: {str(e)}"

def add_tool(repo_path: str, files: List[str]) -> str:
    """
    Add file contents to the staging area.

    Args:
        repo_path: Path to the Git repository
        files: List of file paths to add

    Returns:
        Confirmation message
    """
    try:
        repo = get_repo(repo_path)

        # Convert relative paths to absolute paths within the repo
        repo_base = Path(repo_path)
        absolute_files = []

        for file in files:
            file_path = Path(file)
            # If it's already absolute, use it as is
            if file_path.is_absolute():
                absolute_files.append(str(file_path))
            else:
                # Otherwise, make it relative to the repo
                absolute_files.append(str(repo_base / file_path))

        result = git_add(repo, absolute_files)
        return result
    except Exception as e:
        return f"Error adding files: {str(e)}"

def reset_tool(repo_path: str) -> str:
    """
    Unstage all staged changes.

    Args:
        repo_path: Path to the Git repository

    Returns:
        Confirmation message
    """
    try:
        repo = get_repo(repo_path)
        result = git_reset(repo)
        return result
    except Exception as e:
        return f"Error resetting staged changes: {str(e)}"

def log_tool(repo_path: str, max_count: int = 10) -> str:
    """
    Show commit logs.

    Args:
        repo_path: Path to the Git repository
        max_count: Maximum number of commits to show

    Returns:
        Formatted log output as string
    """
    try:
        repo = get_repo(repo_path)
        commits = git_log(repo, max_count)

        if not commits:
            return "No commits found."

        result = f"Commit history for {repo_path} (showing {len(commits)} commits):\n\n"

        for commit in commits:
            result += (
                f"Commit: {commit['short_hash']} ({commit['hash']})\n"
                f"Author: {commit['author']}\n"
                f"Date: {commit['date']}\n"
                f"Message: {commit['message']}\n\n"
            )

        return result
    except Exception as e:
        return f"Error getting commit logs: {str(e)}"

def create_branch_tool(repo_path: str, branch_name: str, base_branch: Optional[str] = None) -> str:
    """
    Create a new branch.

    Args:
        repo_path: Path to the Git repository
        branch_name: Name of the new branch
        base_branch: Base branch name (optional)

    Returns:
        Confirmation message
    """
    try:
        repo = get_repo(repo_path)
        result = git_create_branch(repo, branch_name, base_branch)
        return result
    except Exception as e:
        return f"Error creating branch: {str(e)}"

def checkout_tool(repo_path: str, branch_name: str) -> str:
    """
    Switch branches.

    Args:
        repo_path: Path to the Git repository
        branch_name: Name of the branch to checkout

    Returns:
        Confirmation message
    """
    try:
        repo = get_repo(repo_path)
        result = git_checkout(repo, branch_name)
        return result
    except Exception as e:
        return f"Error checking out branch: {str(e)}"

def show_tool(repo_path: str, revision: str) -> str:
    """
    Show the contents of a commit.

    Args:
        repo_path: Path to the Git repository
        revision: Revision to show (commit hash, branch name, etc.)

    Returns:
        Commit details and diff as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_show(repo, revision)
        return f"Details for revision {revision} in {repo_path}:\n\n{result}"
    except Exception as e:
        return f"Error showing revision: {str(e)}"

def init_tool(repo_path: str) -> str:
    """
    Initialize a new Git repository.

    Args:
        repo_path: Path where the repository should be initialized

    Returns:
        Confirmation message
    """
    try:
        result = git_init(repo_path)
        return result
    except Exception as e:
        return f"Error initializing repository: {str(e)}"

def branch_list_tool(repo_path: str) -> str:
    """
    List all branches.

    Args:
        repo_path: Path to the Git repository

    Returns:
        Formatted list of branches
    """
    try:
        repo = get_repo(repo_path)
        branches = git_branch_list(repo)

        if not branches:
            return "No branches found."

        result = f"Branches in {repo_path}:\n\n"

        for branch in branches:
            active_marker = "* " if branch['is_active'] else "  "
            result += (
                f"{active_marker}{branch['name']} - {branch['commit']} - {branch['message']}\n"
            )

        return result
    except Exception as e:
        return f"Error listing branches: {str(e)}"

def remote_list_tool(repo_path: str) -> str:
    """
    List all remotes.

    Args:
        repo_path: Path to the Git repository

    Returns:
        Formatted list of remotes
    """
    try:
        repo = get_repo(repo_path)
        remotes = git_remote_list(repo)

        if not remotes:
            return "No remotes found."

        result = f"Remotes in {repo_path}:\n\n"

        for remote in remotes:
            result += f"{remote['name']} - {remote['url']}\n"

        return result
    except Exception as e:
        return f"Error listing remotes: {str(e)}"

def stash_list_tool(repo_path: str) -> str:
    """
    List all stashes.

    Args:
        repo_path: Path to the Git repository

    Returns:
        Formatted list of stashes
    """
    try:
        repo = get_repo(repo_path)
        stashes = git_stash_list(repo)

        if not stashes:
            return "No stashes found."

        result = f"Stashes in {repo_path}:\n\n"

        for stash in stashes:
            result += f"{stash['description']}\n"

        return result
    except Exception as e:
        return f"Error listing stashes: {str(e)}"

def remote_add_tool(repo_path: str, name: str, url: str) -> str:
    """
    Add a remote.

    Args:
        repo_path: Path to the Git repository
        name: Name of the remote
        url: URL of the remote

    Returns:
        Confirmation message
    """
    try:
        repo = get_repo(repo_path)
        result = git_remote_add(repo, name, url)
        return result
    except Exception as e:
        return f"Error adding remote: {str(e)}"

def pull_tool(repo_path: str, remote: str = "origin", branch: Optional[str] = None) -> str:
    """
    Pull changes from a remote.

    Args:
        repo_path: Path to the Git repository
        remote: Name of the remote
        branch: Branch to pull (optional)

    Returns:
        Pull output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_pull(repo, remote, branch)
        pull_target = f"{remote}/{branch}" if branch else remote
        return f"Pulled from {pull_target}:\n\n{result}"
    except Exception as e:
        return f"Error pulling changes: {str(e)}"

def push_tool(repo_path: str, remote: str = "origin", branch: Optional[str] = None) -> str:
    """
    Push changes to a remote.

    Args:
        repo_path: Path to the Git repository
        remote: Name of the remote
        branch: Branch to push (optional)

    Returns:
        Push output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_push(repo, remote, branch)
        push_target = f"{remote}/{branch}" if branch else remote
        return f"Pushed to {push_target}:\n\n{result}"
    except Exception as e:
        return f"Error pushing changes: {str(e)}"

def register_tools_git(mcp):
    """Register all git tools with the MCP server."""
    # Register tools
    mcp.tool()(status_tool)
    mcp.tool()(diff_unstaged_tool)
    mcp.tool()(diff_staged_tool)
    mcp.tool()(diff_tool)
    mcp.tool()(commit_tool)
    mcp.tool()(add_tool)
    mcp.tool()(reset_tool)
    mcp.tool()(log_tool)
    mcp.tool()(create_branch_tool)
    mcp.tool()(checkout_tool)
    mcp.tool()(show_tool)
    mcp.tool()(init_tool)
    mcp.tool()(branch_list_tool)
    mcp.tool()(remote_list_tool)
    mcp.tool()(stash_list_tool)
    mcp.tool()(remote_add_tool)
    mcp.tool()(pull_tool)
    mcp.tool()(push_tool)
