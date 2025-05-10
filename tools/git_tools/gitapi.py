"""
Git functionality module for interacting with Git repositories.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import git
import os
import re

from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

def get_repo(repo_path: str) -> git.Repo:
    """
    Get a git.Repo object for the given path.

    Args:
        repo_path: Path to the Git repository

    Returns:
        git.Repo object

    Raises:
        git.InvalidGitRepositoryError: If path is not a valid Git repository
        git.NoSuchPathError: If the repository path doesn't exist
    """
    try:
        return git.Repo(repo_path)
    except (InvalidGitRepositoryError, NoSuchPathError) as e:
        raise e

def git_status(repo: git.Repo) -> str:
    """
    Get the status of the Git repository.

    Args:
        repo: git.Repo object

    Returns:
        Status output as string

    Raises:
        GitCommandError: If git status command fails
    """
    try:
        return repo.git.status()
    except GitCommandError as e:
        return f"Error getting status: {str(e)}"

def git_diff_unstaged(repo: git.Repo) -> str:
    """
    Get the diff of unstaged changes.

    Args:
        repo: git.Repo object

    Returns:
        Diff output as string

    Raises:
        GitCommandError: If git diff command fails
    """
    try:
        return repo.git.diff()
    except GitCommandError as e:
        return f"Error getting unstaged diff: {str(e)}"

def git_diff_staged(repo: git.Repo) -> str:
    """
    Get the diff of staged changes.

    Args:
        repo: git.Repo object

    Returns:
        Diff output as string

    Raises:
        GitCommandError: If git diff command fails
    """
    try:
        return repo.git.diff("--cached")
    except GitCommandError as e:
        return f"Error getting staged diff: {str(e)}"

def git_diff(repo: git.Repo, target: str) -> str:
    """
    Get the diff between the current branch and a target.

    Args:
        repo: git.Repo object
        target: Target to compare (branch name, commit hash, etc.)

    Returns:
        Diff output as string

    Raises:
        GitCommandError: If git diff command fails
    """
    try:
        return repo.git.diff(target)
    except GitCommandError as e:
        return f"Error getting diff with {target}: {str(e)}"

def git_commit(repo: git.Repo, message: str) -> str:
    """
    Commit staged changes.

    Args:
        repo: git.Repo object
        message: Commit message

    Returns:
        Confirmation message with commit hash

    Raises:
        GitCommandError: If git commit command fails
    """
    try:
        commit = repo.index.commit(message)
        return f"Changes committed successfully with hash {commit.hexsha}"
    except GitCommandError as e:
        return f"Error committing changes: {str(e)}"

def git_add(repo: git.Repo, files: List[str]) -> str:
    """
    Add files to the staging area.

    Args:
        repo: git.Repo object
        files: List of file paths to add

    Returns:
        Confirmation message

    Raises:
        GitCommandError: If git add command fails
    """
    try:
        # Check if files exist before adding
        non_existent = [f for f in files if not os.path.exists(os.path.join(repo.working_dir, f))]
        if non_existent:
            return f"Error: The following files do not exist: {', '.join(non_existent)}"

        # Use Git's native add command which respects .gitignore and Git's internal rules
        result = repo.git.add(*files)
        return f"Files staged successfully: {', '.join(files)}"
    except GitCommandError as e:
        return f"Error staging files: {str(e)}"

def git_reset(repo: git.Repo, commit_ish: Optional[str] = None, mode: Optional[str] = None) -> str:
    """
    Reset the current HEAD to a specified state or unstage files.

    Args:
        repo: git.Repo object
        commit_ish: The commit to reset to (e.g., 'HEAD~1', commit hash).
                   If None and mode is not 'hard'/'soft'/'mixed' for current branch, it unstages all changes from the index.
        mode: The reset mode. Can be 'soft', 'mixed', or 'hard'.
              - 'soft': Index and working directory are not altered. Changes are left as "Changes to be committed".
              - 'mixed': Index is reset to the specified commit. Changes in working directory preserved but unstaged.
              - 'hard': Index and working directory are reset to the specified commit. All changes to tracked files are discarded.

    Returns:
        Confirmation message
    """
    if commit_ish is None and mode is None:
        # Just unstage all files (git reset)
        repo.index.reset()
        return "All staged changes reset"
    elif commit_ish is not None:
        # Reset to a specific commit with specified mode
        mode = mode or 'mixed'  # Default to mixed mode if not specified
        if mode not in ['soft', 'mixed', 'hard']:
            return f"Error: Invalid mode '{mode}'. Must be 'soft', 'mixed', or 'hard'."
        try:
            repo.git.reset(commit_ish, '--' + mode)
            return f"Repository reset to {commit_ish} using {mode} mode"
        except GitCommandError as e:
            return f"Error resetting to {commit_ish}: {str(e)}"
    else:
        # Only mode provided, but no commit - reset current HEAD with that mode
        if mode not in ['soft', 'mixed', 'hard']:
            return f"Error: Invalid mode '{mode}'. Must be 'soft', 'mixed', or 'hard'."
        try:
            repo.git.reset('HEAD', '--' + mode)
            return f"Repository reset to HEAD using {mode} mode"
        except GitCommandError as e:
            return f"Error resetting: {str(e)}"

def git_log(repo: git.Repo, max_count: int = 10) -> List[Dict[str, Any]]:
    """
    Get the commit log.

    Args:
        repo: git.Repo object
        max_count: Maximum number of commits to return

    Returns:
        List of commit details
    """
    commits = list(repo.iter_commits(max_count=max_count))
    log = []
    for commit in commits:
        log.append({
            "hash": commit.hexsha,
            "short_hash": commit.hexsha[:7],
            "author": f"{commit.author.name} <{commit.author.email}>",
            "date": commit.authored_datetime.isoformat(),
            "message": commit.message.strip(),
        })
    return log

def git_create_branch(repo: git.Repo, branch_name: str, base_branch: Optional[str] = None) -> str:
    """
    Create a new branch.

    Args:
        repo: git.Repo object
        branch_name: Name of the new branch
        base_branch: Base branch name (optional)

    Returns:
        Confirmation message
    """
    if base_branch:
        base = repo.refs[base_branch]
    else:
        base = repo.active_branch

    repo.create_head(branch_name, base)
    return f"Created branch '{branch_name}' from '{base.name}'"

def git_checkout(repo: git.Repo, branch_name: str) -> str:
    """
    Checkout a branch.

    Args:
        repo: git.Repo object
        branch_name: Name of the branch to checkout

    Returns:
        Confirmation message
    """
    repo.git.checkout(branch_name)
    return f"Switched to branch '{branch_name}'"

def git_show(repo: git.Repo, revision: str) -> str:
    """
    Show the contents of a commit.

    Args:
        repo: git.Repo object
        revision: Revision to show (commit hash, branch name, etc.)

    Returns:
        Commit details and diff as string
    """
    commit = repo.commit(revision)
    output = [
        f"Commit: {commit.hexsha}\n",
        f"Author: {commit.author.name} <{commit.author.email}>\n",
        f"Date: {commit.authored_datetime.isoformat()}\n",
        f"Message: {commit.message}\n\n",
    ]

    if commit.parents:
        parent = commit.parents[0]
        diff = parent.diff(commit, create_patch=True)
    else:
        diff = commit.diff(git.NULL_TREE, create_patch=True)

    for d in diff:
        output.append(f"\n--- {d.a_path}\n+++ {d.b_path}\n")
        # Handle different possible types of d.diff
        if d.diff is None:
            output.append("(No diff available)")
        elif isinstance(d.diff, bytes):
            output.append(d.diff.decode('utf-8'))
        else:
            # Already a string or another type that can be converted to string
            output.append(str(d.diff))

    return "".join(output)

def git_init(repo_path: str) -> str:
    """
    Initialize a new Git repository.

    Args:
        repo_path: Path where the repository should be initialized

    Returns:
        Confirmation message
    """
    try:
        repo = git.Repo.init(path=repo_path, mkdir=True)
        return f"Initialized empty Git repository in {repo.git_dir}"
    except Exception as e:
        return f"Error initializing repository: {str(e)}"

def git_branch_list(repo: git.Repo) -> List[Dict[str, Any]]:
    """
    List all branches.

    Args:
        repo: git.Repo object

    Returns:
        List of branch details
    """
    branches = []
    for branch in repo.branches:
        branches.append({
            "name": branch.name,
            "commit": branch.commit.hexsha[:7],
            "message": branch.commit.message.strip(),
            "is_active": branch.name == repo.active_branch.name
        })
    return branches

def git_remote_list(repo: git.Repo) -> List[Dict[str, str]]:
    """
    List all remotes.

    Args:
        repo: git.Repo object

    Returns:
        List of remote details
    """
    remotes = []
    for remote in repo.remotes:
        remotes.append({
            "name": remote.name,
            "url": next(remote.urls)
        })
    return remotes

def git_stash_list(repo: git.Repo) -> List[Dict[str, Any]]:
    """
    List all stashes.

    Args:
        repo: git.Repo object

    Returns:
        List of stash details
    """
    stashes = []
    for stash in repo.git.stash("list").splitlines():
        if stash:
            stashes.append({"description": stash})
    return stashes

def git_remote_add(repo: git.Repo, name: str, url: str) -> str:
    """
    Add a remote.

    Args:
        repo: git.Repo object
        name: Name of the remote
        url: URL of the remote

    Returns:
        Confirmation message
    """
    repo.create_remote(name, url)
    return f"Added remote '{name}' with URL '{url}'"

def git_pull(repo: git.Repo, remote: str = "origin", branch: Optional[str] = None) -> str:
    """
    Pull changes from a remote.

    Args:
        repo: git.Repo object
        remote: Name of the remote
        branch: Branch to pull (optional)

    Returns:
        Pull output as string
    """
    if branch:
        return repo.git.pull(remote, branch)
    else:
        return repo.git.pull(remote)

def git_push(repo: git.Repo, remote: str = "origin", branch: Optional[str] = None, force: bool = False, tags: bool = False) -> str:
    """
    Push changes to a remote.

    Args:
        repo: git.Repo object
        remote: Name of the remote
        branch: Branch to push (optional)
        force: Force push even when it results in a non-fast-forward merge
        tags: Push all tags to the remote

    Returns:
        Push output as string
    """
    args = []
    if force:
        args.append('--force')
    if tags:
        args.append('--tags')
    
    if branch:
        return repo.git.push(remote, branch, *args)
    else:
        return repo.git.push(remote, *args)

def git_cherry_pick(repo: git.Repo, commit_hash: str) -> str:
    """
    Apply the changes introduced by an existing commit.

    Args:
        repo: git.Repo object
        commit_hash: The commit hash to cherry-pick

    Returns:
        Cherry-pick output as string
    """
    try:
        return repo.git.cherry_pick(commit_hash)
    except GitCommandError as e:
        if "could not apply" in str(e) and "conflicts" in str(e):
            return f"Cherry-pick conflict: {str(e)}\nPlease resolve conflicts and complete the cherry-pick."
        return f"Error cherry-picking {commit_hash}: {str(e)}"

def git_stash_save(repo: git.Repo, message: Optional[str] = None, include_untracked: bool = False) -> str:
    """
    Stash changes in the working directory.

    Args:
        repo: git.Repo object
        message: Optional message for the stash
        include_untracked: Include untracked files in the stash

    Returns:
        Stash save output as string
    """
    args = []
    if message:
        args.extend(['save', message])
    if include_untracked:
        args.append('--include-untracked')
    
    return repo.git.stash(*args)

def git_stash_apply(repo: git.Repo, stash_id: Optional[str] = None, index: bool = False) -> str:
    """
    Apply a stashed state.

    Args:
        repo: git.Repo object
        stash_id: Identifier of the stash to apply (e.g., 'stash@{0}')
        index: Whether to restore the index state as well

    Returns:
        Stash apply output as string
    """
    args = ['apply']
    if index:
        args.append('--index')
    if stash_id:
        args.append(stash_id)
    
    try:
        return repo.git.stash(*args)
    except GitCommandError as e:
        if "conflicts" in str(e):
            return f"Stash apply conflict: {str(e)}\nPlease resolve conflicts manually."
        return f"Error applying stash: {str(e)}"

def git_stash_pop(repo: git.Repo, stash_id: Optional[str] = None) -> str:
    """
    Apply and remove a stashed state.

    Args:
        repo: git.Repo object
        stash_id: Identifier of the stash to pop (e.g., 'stash@{0}')

    Returns:
        Stash pop output as string
    """
    args = ['pop']
    if stash_id:
        args.append(stash_id)
    
    try:
        return repo.git.stash(*args)
    except GitCommandError as e:
        if "conflicts" in str(e):
            return f"Stash pop conflict: {str(e)}\nPlease resolve conflicts manually."
        return f"Error popping stash: {str(e)}"

def git_stash_drop(repo: git.Repo, stash_id: Optional[str] = None) -> str:
    """
    Remove a stashed state.

    Args:
        repo: git.Repo object
        stash_id: Identifier of the stash to drop (e.g., 'stash@{0}')

    Returns:
        Stash drop output as string
    """
    args = ['drop']
    if stash_id:
        args.append(stash_id)
    
    return repo.git.stash(*args)

def git_rebase(repo: git.Repo, branch_or_commit: str, interactive: bool = False, abort: bool = False, continue_rebase: bool = False) -> str:
    """
    Rebase the current branch onto another branch or commit.

    Args:
        repo: git.Repo object
        branch_or_commit: Branch or commit to rebase onto
        interactive: Start an interactive rebase
        abort: Abort an in-progress rebase
        continue_rebase: Continue an in-progress rebase after resolving conflicts

    Returns:
        Rebase output as string
    """
    if abort:
        try:
            return repo.git.rebase('--abort')
        except GitCommandError as e:
            return f"Error aborting rebase: {str(e)}"
    
    if continue_rebase:
        try:
            return repo.git.rebase('--continue')
        except GitCommandError as e:
            return f"Error continuing rebase: {str(e)}"
    
    args = []
    if interactive:
        args.append('-i')
    
    try:
        return repo.git.rebase(branch_or_commit, *args)
    except GitCommandError as e:
        if "conflicts" in str(e):
            return f"Rebase conflict: {str(e)}\nUse 'git rebase --continue' after resolving conflicts or 'git rebase --abort' to abort."
        return f"Error during rebase: {str(e)}"

def git_merge(repo: git.Repo, branch: str, strategy: Optional[str] = None, commit_message: Optional[str] = None, no_ff: bool = False, abort: bool = False) -> str:
    """
    Merge a branch into the current branch.

    Args:
        repo: git.Repo object
        branch: Branch to merge
        strategy: Merge strategy (e.g., 'recursive', 'resolve', 'octopus', 'ours', 'subtree')
        commit_message: Custom commit message for the merge
        no_ff: Create a merge commit even if it's a fast-forward merge
        abort: Abort an in-progress merge

    Returns:
        Merge output as string
    """
    if abort:
        try:
            return repo.git.merge('--abort')
        except GitCommandError as e:
            return f"Error aborting merge: {str(e)}"
    
    args = []
    if strategy:
        args.extend(['--strategy', strategy])
    if commit_message:
        args.extend(['-m', commit_message])
    if no_ff:
        args.append('--no-ff')
    
    try:
        return repo.git.merge(branch, *args)
    except GitCommandError as e:
        if "Automatic merge failed" in str(e) or "conflicts" in str(e).lower():
            return f"Merge conflict: {str(e)}\nResolve conflicts and commit, or use 'git merge --abort'."
        return f"Error merging {branch}: {str(e)}"

def git_tag_create(repo: git.Repo, tag_name: str, message: Optional[str] = None, commit: Optional[str] = None) -> str:
    """
    Create a new tag.

    Args:
        repo: git.Repo object
        tag_name: Name of the tag
        message: Tag message (if not provided, creates a lightweight tag)
        commit: Commit to tag (if not provided, tags the current commit)

    Returns:
        Tag creation output as string
    """
    args = []
    if message:
        args.extend(['-m', message])
    if commit:
        args.append(commit)
    
    return repo.git.tag(tag_name, *args)

def git_tag_list(repo: git.Repo) -> List[Dict[str, Any]]:
    """
    List all tags.

    Args:
        repo: git.Repo object

    Returns:
        List of tag details
    """
    tags = []
    for tag in repo.tags:
        tags.append({
            "name": tag.name,
            "commit": tag.commit.hexsha[:7],
            "message": tag.tag.message if hasattr(tag, 'tag') and tag.tag else "",
        })
    return tags

def git_tag_delete(repo: git.Repo, tag_name: str) -> str:
    """
    Delete a tag.

    Args:
        repo: git.Repo object
        tag_name: Name of the tag to delete

    Returns:
        Tag deletion output as string
    """
    return repo.git.tag('-d', tag_name)

def git_amend_commit(repo: git.Repo, message: Optional[str] = None, no_edit: bool = False) -> str:
    """
    Amend the last commit.

    Args:
        repo: git.Repo object
        message: New commit message
        no_edit: Don't edit the commit message

    Returns:
        Amend commit output as string
    """
    args = ['--amend']
    
    if no_edit:
        args.append('--no-edit')
    elif message:
        args.extend(['-m', message])
    
    try:
        return repo.git.commit(*args)
    except GitCommandError as e:
        return f"Error amending commit: {str(e)}"

def git_blame(repo: git.Repo, file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Show who last modified each line of a file.

    Args:
        repo: git.Repo object
        file_path: Path to the file
        start_line: First line to show (1-based)
        end_line: Last line to show (1-based)

    Returns:
        Blame output as string
    """
    args = [file_path]
    
    if start_line is not None and end_line is not None:
        args.append(f'-L {start_line},{end_line}')
    
    return repo.git.blame(*args)

def git_branch_delete(repo: git.Repo, branch_name: str, force: bool = False) -> str:
    """
    Delete a branch.

    Args:
        repo: git.Repo object
        branch_name: Name of the branch to delete
        force: Force deletion even if the branch contains unmerged changes

    Returns:
        Branch deletion output as string
    """
    arg = '-D' if force else '-d'
    try:
        return repo.git.branch(arg, branch_name)
    except GitCommandError as e:
        return f"Error deleting branch: {str(e)}"

def git_clean(repo: git.Repo, directories: bool = False, force: bool = False, dry_run: bool = True) -> str:
    """
    Remove untracked files from the working tree.

    Args:
        repo: git.Repo object
        directories: Also remove untracked directories
        force: Force removal (not asking for confirmation)
        dry_run: Just show what would be done

    Returns:
        Clean output as string
    """
    args = []
    if directories:
        args.append('-d')
    if force:
        args.append('-f')
    if dry_run:
        args.append('-n')
    
    return repo.git.clean(*args)

def git_config_get(repo: git.Repo, key: str, global_config: bool = False) -> str:
    """
    Get a git configuration value.

    Args:
        repo: git.Repo object
        key: Configuration key (e.g., 'user.name')
        global_config: Get from global config instead of local repo config

    Returns:
        Configuration value as string
    """
    args = []
    if global_config:
        args.append('--global')
    
    try:
        return repo.git.config(*args, key)
    except GitCommandError:
        return f"Config '{key}' not found"

def git_config_set(repo: git.Repo, key: str, value: str, global_config: bool = False) -> str:
    """
    Set a git configuration value.

    Args:
        repo: git.Repo object
        key: Configuration key (e.g., 'user.name')
        value: Configuration value
        global_config: Set in global config instead of local repo config

    Returns:
        Confirmation message
    """
    args = []
    if global_config:
        args.append('--global')
    
    repo.git.config(*args, key, value)
    return f"Config '{key}' set to '{value}'"

def git_reflog(repo: git.Repo, max_count: int = 10) -> List[Dict[str, Any]]:
    """
    Get the reference logs.

    Args:
        repo: git.Repo object
        max_count: Maximum number of reflog entries to return

    Returns:
        List of reflog entries
    """
    # Format: <short-hash> <ref>@{<index>}: <action>: <message>
    reflog_pattern = r"([0-9a-f]+) ([^@]+)@\{(\d+)\}: ([^:]+): (.+)"
    
    try:
        reflog_output = repo.git.reflog(f"-n {max_count}")
        entries = []
        
        for line in reflog_output.split('\n'):
            if not line:
                continue
            
            match = re.match(reflog_pattern, line)
            if match:
                entries.append({
                    "hash": match.group(1),
                    "ref": match.group(2),
                    "index": int(match.group(3)),
                    "action": match.group(4),
                    "message": match.group(5)
                })
        
        return entries
    except GitCommandError as e:
        return []

def git_submodule_add(repo: git.Repo, repository: str, path: str) -> str:
    """
    Add a new submodule.

    Args:
        repo: git.Repo object
        repository: URL of the submodule repository
        path: Path where to create the submodule

    Returns:
        Submodule add output as string
    """
    try:
        return repo.git.submodule('add', repository, path)
    except GitCommandError as e:
        return f"Error adding submodule: {str(e)}"

def git_submodule_update(repo: git.Repo, init: bool = True, recursive: bool = True) -> str:
    """
    Update submodules.

    Args:
        repo: git.Repo object
        init: Initialize uninitialized submodules
        recursive: Update recursively

    Returns:
        Submodule update output as string
    """
    args = ['update']
    if init:
        args.append('--init')
    if recursive:
        args.append('--recursive')
    
    try:
        return repo.git.submodule(*args)
    except GitCommandError as e:
        return f"Error updating submodules: {str(e)}"
