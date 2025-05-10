"""
Git MCP Server Implementation

This module provides a Model Context Protocol server for interacting with Git repositories.
It exposes Git commands as tools for AI assistants to use.
"""

from typing import List, Dict, Any, Optional, Tuple
import os
import re
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
    git_cherry_pick,
    git_stash_save,
    git_stash_apply,
    git_stash_pop,
    git_stash_drop,
    git_rebase,
    git_merge,
    git_tag_create,
    git_tag_list,
    git_tag_delete,
    git_amend_commit,
    git_blame,
    git_branch_delete,
    git_clean,
    git_config_get,
    git_config_set,
    git_reflog,
    git_submodule_add,
    git_submodule_update,
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

def reset_tool(repo_path: str, commit_ish: Optional[str] = None, mode: Optional[str] = None) -> str:
    """
    Reset the current HEAD to a specified state or unstage files.

    Args:
        repo_path: Path to the Git repository
        commit_ish: Optional. The commit to reset to (e.g., 'HEAD~1', commit hash).
                If None and mode is not 'hard'/'soft'/'mixed' for current branch, it unstages all changes from the index.
        mode: Optional. The reset mode. Can be 'soft', 'mixed', or 'hard'.
              Defaults to 'mixed' if commit_ish is provided but mode is not.
              If commit_ish is None and mode is None, it unstages all files (equivalent to `git reset`).
              - 'soft': Index and working directory are not altered. Changes are left as "Changes to be committed".
              - 'mixed': Index is reset to the specified commit. Changes in the working directory are preserved but unstaged.
              - 'hard': Index and working directory are reset to the specified commit. All changes to tracked files are discarded.

    Returns:
        Confirmation message
    """
    try:
        repo = get_repo(repo_path)
        result = git_reset(repo, commit_ish, mode)
        return result
    except Exception as e:
        return f"Error resetting repository: {str(e)}"

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

def push_tool(repo_path: str, remote: str = "origin", branch: Optional[str] = None, force: bool = False, tags: bool = False) -> str:
    """
    Push changes to a remote.

    Args:
        repo_path: Path to the Git repository
        remote: Name of the remote
        branch: Branch to push (optional)
        force: Force push even when it results in a non-fast-forward merge
        tags: Push all tags to the remote

    Returns:
        Push output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_push(repo, remote, branch, force, tags)
        push_target = f"{remote}/{branch}" if branch else remote
        force_info = " (forced)" if force else ""
        tags_info = " with tags" if tags else ""
        return f"Pushed to {push_target}{force_info}{tags_info}:\n\n{result}"
    except Exception as e:
        return f"Error pushing changes: {str(e)}"

def cherry_pick_tool(repo_path: str, commit_hash: str) -> str:
    """
    Apply the changes introduced by an existing commit.

    Args:
        repo_path: Path to the Git repository
        commit_hash: The commit hash to cherry-pick

    Returns:
        Cherry-pick output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_cherry_pick(repo, commit_hash)
        return f"Cherry-pick result for commit {commit_hash}:\n\n{result}"
    except Exception as e:
        return f"Error cherry-picking commit: {str(e)}"


def stash_save_tool(repo_path: str, message: Optional[str] = None, include_untracked: bool = False) -> str:
    """
    Stash changes in the working directory.

    Args:
        repo_path: Path to the Git repository
        message: Optional message for the stash
        include_untracked: Include untracked files in the stash

    Returns:
        Stash save output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_stash_save(repo, message, include_untracked)
        return f"Stash result:\n\n{result}"
    except Exception as e:
        return f"Error stashing changes: {str(e)}"


def stash_apply_tool(repo_path: str, stash_id: Optional[str] = None, index: bool = False) -> str:
    """
    Apply a stashed state.

    Args:
        repo_path: Path to the Git repository
        stash_id: Identifier of the stash to apply (e.g., 'stash@{0}')
        index: Whether to restore the index state as well

    Returns:
        Stash apply output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_stash_apply(repo, stash_id, index)
        stash_info = f" {stash_id}" if stash_id else ""
        index_info = " with index restoration" if index else ""
        return f"Applied stash{stash_info}{index_info}:\n\n{result}"
    except Exception as e:
        return f"Error applying stash: {str(e)}"


def stash_pop_tool(repo_path: str, stash_id: Optional[str] = None) -> str:
    """
    Apply and remove a stashed state.

    Args:
        repo_path: Path to the Git repository
        stash_id: Identifier of the stash to pop (e.g., 'stash@{0}')

    Returns:
        Stash pop output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_stash_pop(repo, stash_id)
        stash_info = f" {stash_id}" if stash_id else ""
        return f"Popped stash{stash_info}:\n\n{result}"
    except Exception as e:
        return f"Error popping stash: {str(e)}"


def stash_drop_tool(repo_path: str, stash_id: Optional[str] = None) -> str:
    """
    Remove a stashed state.

    Args:
        repo_path: Path to the Git repository
        stash_id: Identifier of the stash to drop (e.g., 'stash@{0}')

    Returns:
        Stash drop output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_stash_drop(repo, stash_id)
        stash_info = f" {stash_id}" if stash_id else ""
        return f"Dropped stash{stash_info}:\n\n{result}"
    except Exception as e:
        return f"Error dropping stash: {str(e)}"


def rebase_tool(repo_path: str, branch_or_commit: Optional[str] = None, interactive: bool = False, 
               abort: bool = False, continue_rebase: bool = False) -> str:
    """
    Rebase the current branch onto another branch or commit.

    Args:
        repo_path: Path to the Git repository
        branch_or_commit: Branch or commit to rebase onto
        interactive: Start an interactive rebase
        abort: Abort an in-progress rebase
        continue_rebase: Continue an in-progress rebase after resolving conflicts

    Returns:
        Rebase output as string
    """
    try:
        repo = get_repo(repo_path)
        
        if abort and continue_rebase:
            return "Error: Cannot specify both abort and continue"
        
        if (abort or continue_rebase) and branch_or_commit:
            return "Error: Cannot specify a branch/commit when aborting or continuing a rebase"
            
        if not (abort or continue_rebase) and not branch_or_commit:
            return "Error: Must specify a branch or commit to rebase onto"
            
        result = git_rebase(repo, branch_or_commit or "", interactive, abort, continue_rebase)
        
        if abort:
            return f"Rebase aborted:\n\n{result}"
        elif continue_rebase:
            return f"Rebase continued:\n\n{result}"
        else:
            int_info = " interactive" if interactive else ""
            return f"Rebased{int_info} onto {branch_or_commit}:\n\n{result}"
    except Exception as e:
        return f"Error during rebase: {str(e)}"


def merge_tool(repo_path: str, branch: Optional[str] = None, strategy: Optional[str] = None,
              commit_message: Optional[str] = None, no_ff: bool = False, abort: bool = False) -> str:
    """
    Merge a branch into the current branch.

    Args:
        repo_path: Path to the Git repository
        branch: Branch to merge
        strategy: Merge strategy (e.g., 'recursive', 'resolve', 'octopus', 'ours', 'subtree')
        commit_message: Custom commit message for the merge
        no_ff: Create a merge commit even if it's a fast-forward merge
        abort: Abort an in-progress merge

    Returns:
        Merge output as string
    """
    try:
        repo = get_repo(repo_path)
        
        if abort and branch:
            return "Error: Cannot specify a branch when aborting a merge"
            
        if not abort and not branch:
            return "Error: Must specify a branch to merge"
            
        result = git_merge(repo, branch or "", strategy, commit_message, no_ff, abort)
        
        if abort:
            return f"Merge aborted:\n\n{result}"
        else:
            strategy_info = f" using {strategy} strategy" if strategy else ""
            ff_info = " with no fast-forward" if no_ff else ""
            return f"Merged {branch}{strategy_info}{ff_info}:\n\n{result}"
    except Exception as e:
        return f"Error during merge: {str(e)}"


def tag_create_tool(repo_path: str, tag_name: str, message: Optional[str] = None, commit: Optional[str] = None) -> str:
    """
    Create a new tag.

    Args:
        repo_path: Path to the Git repository
        tag_name: Name of the tag
        message: Tag message (if not provided, creates a lightweight tag)
        commit: Commit to tag (if not provided, tags the current commit)

    Returns:
        Tag creation output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_tag_create(repo, tag_name, message, commit)
        tag_type = "annotated" if message else "lightweight"
        commit_info = f" at commit {commit}" if commit else " at current HEAD"
        return f"Created {tag_type} tag '{tag_name}'{commit_info}"
    except Exception as e:
        return f"Error creating tag: {str(e)}"


def tag_list_tool(repo_path: str) -> str:
    """
    List all tags.

    Args:
        repo_path: Path to the Git repository

    Returns:
        Formatted list of tags
    """
    try:
        repo = get_repo(repo_path)
        tags = git_tag_list(repo)
        
        if not tags:
            return "No tags found."
            
        result = f"Tags in {repo_path}:\n\n"
        
        for tag in tags:
            result += f"{tag['name']} - {tag['commit']}"
            if tag['message']:
                # Show first line of tag message if it exists
                message_first_line = tag['message'].split('\n')[0]
                result += f" - {message_first_line}"
            result += "\n"
            
        return result
    except Exception as e:
        return f"Error listing tags: {str(e)}"


def tag_delete_tool(repo_path: str, tag_name: str) -> str:
    """
    Delete a tag.

    Args:
        repo_path: Path to the Git repository
        tag_name: Name of the tag to delete

    Returns:
        Tag deletion output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_tag_delete(repo, tag_name)
        return f"Deleted tag '{tag_name}':\n\n{result}"
    except Exception as e:
        return f"Error deleting tag: {str(e)}"


def amend_commit_tool(repo_path: str, message: Optional[str] = None, no_edit: bool = False) -> str:
    """
    Amend the last commit.

    Args:
        repo_path: Path to the Git repository
        message: New commit message
        no_edit: Don't edit the commit message

    Returns:
        Amend commit output as string
    """
    try:
        repo = get_repo(repo_path)
        
        if message and no_edit:
            return "Error: Cannot specify both message and no_edit"
            
        result = git_amend_commit(repo, message, no_edit)
        
        msg_info = ""
        if no_edit:
            msg_info = " (message unchanged)"
        elif message:
            msg_info = f" with message: '{message}'"
            
        return f"Amended last commit{msg_info}:\n\n{result}"
    except Exception as e:
        return f"Error amending commit: {str(e)}"


def blame_tool(repo_path: str, file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Show who last modified each line of a file.

    Args:
        repo_path: Path to the Git repository
        file_path: Path to the file
        start_line: First line to show (1-based)
        end_line: Last line to show (1-based)

    Returns:
        Blame output as string
    """
    try:
        repo = get_repo(repo_path)
        
        # Convert absolute path to relative path within repo if needed
        repo_base = Path(repo_path)
        file_path_obj = Path(file_path)
        
        if file_path_obj.is_absolute():
            try:
                file_path = str(file_path_obj.relative_to(repo_base))
            except ValueError:
                return f"Error: File {file_path} is not within repository {repo_path}"
        
        result = git_blame(repo, file_path, start_line, end_line)
        
        line_info = ""
        if start_line and end_line:
            line_info = f" (lines {start_line}-{end_line})"
        elif start_line:
            line_info = f" (from line {start_line})"
            
        return f"Blame for {file_path}{line_info}:\n\n{result}"
    except Exception as e:
        return f"Error getting blame information: {str(e)}"


def branch_delete_tool(repo_path: str, branch_name: str, force: bool = False) -> str:
    """
    Delete a branch.

    Args:
        repo_path: Path to the Git repository
        branch_name: Name of the branch to delete
        force: Force deletion even if the branch contains unmerged changes

    Returns:
        Branch deletion output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_branch_delete(repo, branch_name, force)
        
        force_info = " forcefully" if force else ""
        return f"Deleted branch '{branch_name}'{force_info}:\n\n{result}"
    except Exception as e:
        return f"Error deleting branch: {str(e)}"


def clean_tool(repo_path: str, directories: bool = False, force: bool = False, dry_run: bool = True) -> str:
    """
    Remove untracked files from the working tree.

    Args:
        repo_path: Path to the Git repository
        directories: Also remove untracked directories
        force: Force removal (not asking for confirmation)
        dry_run: Just show what would be done

    Returns:
        Clean output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_clean(repo, directories, force, dry_run)
        
        dir_info = " and directories" if directories else ""
        mode_info = "Would remove" if dry_run else ("Removed" if force else "Removing")
        
        return f"{mode_info} untracked files{dir_info} in {repo_path}:\n\n{result}"
    except Exception as e:
        return f"Error cleaning repository: {str(e)}"


def config_get_tool(repo_path: str, key: str, global_config: bool = False) -> str:
    """
    Get a git configuration value.

    Args:
        repo_path: Path to the Git repository
        key: Configuration key (e.g., 'user.name')
        global_config: Get from global config instead of local repo config

    Returns:
        Configuration value as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_config_get(repo, key, global_config)
        
        config_type = "global" if global_config else "local"
        return f"{config_type} config {key} = {result}"
    except Exception as e:
        return f"Error getting configuration: {str(e)}"


def config_set_tool(repo_path: str, key: str, value: str, global_config: bool = False) -> str:
    """
    Set a git configuration value.

    Args:
        repo_path: Path to the Git repository
        key: Configuration key (e.g., 'user.name')
        value: Configuration value
        global_config: Set in global config instead of local repo config

    Returns:
        Confirmation message
    """
    try:
        repo = get_repo(repo_path)
        result = git_config_set(repo, key, value, global_config)
        
        config_type = "global" if global_config else "local"
        return f"Set {config_type} config {key} = {value}"
    except Exception as e:
        return f"Error setting configuration: {str(e)}"


def reflog_tool(repo_path: str, max_count: int = 10) -> str:
    """
    Show the reference logs.

    Args:
        repo_path: Path to the Git repository
        max_count: Maximum number of reflog entries to return

    Returns:
        Formatted reflog output
    """
    try:
        repo = get_repo(repo_path)
        entries = git_reflog(repo, max_count)
        
        if not entries:
            return "No reflog entries found."
            
        result = f"Reference log for {repo_path} (showing {len(entries)} entries):\n\n"
        
        for entry in entries:
            result += f"{entry['hash']} {entry['ref']}@{{{entry['index']}}}: {entry['action']}: {entry['message']}\n"
            
        return result
    except Exception as e:
        return f"Error getting reflog: {str(e)}"


def submodule_add_tool(repo_path: str, repository: str, path: str) -> str:
    """
    Add a new submodule.

    Args:
        repo_path: Path to the Git repository
        repository: URL of the submodule repository
        path: Path where to create the submodule

    Returns:
        Submodule add output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_submodule_add(repo, repository, path)
        return f"Added submodule {repository} at {path}:\n\n{result}"
    except Exception as e:
        return f"Error adding submodule: {str(e)}"


def submodule_update_tool(repo_path: str, init: bool = True, recursive: bool = True) -> str:
    """
    Update submodules.

    Args:
        repo_path: Path to the Git repository
        init: Initialize uninitialized submodules
        recursive: Update recursively

    Returns:
        Submodule update output as string
    """
    try:
        repo = get_repo(repo_path)
        result = git_submodule_update(repo, init, recursive)
        
        init_info = " and initialize" if init else ""
        recursive_info = " recursively" if recursive else ""
        
        return f"Updated{init_info} submodules{recursive_info}:\n\n{result}"
    except Exception as e:
        return f"Error updating submodules: {str(e)}"


# Register all tools with MCP
def register_tools_git(mcp):
    """Register all git tools with the MCP server."""
    # Register basic tools
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
    
    # Register advanced tools
    mcp.tool()(cherry_pick_tool)
    mcp.tool()(stash_save_tool)
    mcp.tool()(stash_apply_tool)
    mcp.tool()(stash_pop_tool)
    mcp.tool()(stash_drop_tool)
    mcp.tool()(rebase_tool)
    mcp.tool()(merge_tool)
    mcp.tool()(tag_create_tool)
    mcp.tool()(tag_list_tool)
    mcp.tool()(tag_delete_tool)
    mcp.tool()(amend_commit_tool)
    mcp.tool()(blame_tool)
    mcp.tool()(branch_delete_tool)
    mcp.tool()(clean_tool)
    mcp.tool()(config_get_tool)
    mcp.tool()(config_set_tool)
    mcp.tool()(reflog_tool)
    mcp.tool()(submodule_add_tool)
    mcp.tool()(submodule_update_tool)
