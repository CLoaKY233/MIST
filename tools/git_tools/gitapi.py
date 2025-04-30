"""
Git functionality module for interacting with Git repositories.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import git
import os

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

def git_reset(repo: git.Repo) -> str:
    """
    Reset staged changes.

    Args:
        repo: git.Repo object

    Returns:
        Confirmation message
    """
    repo.index.reset()
    return "All staged changes reset"

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

def git_push(repo: git.Repo, remote: str = "origin", branch: Optional[str] = None) -> str:
    """
    Push changes to a remote.

    Args:
        repo: git.Repo object
        remote: Name of the remote
        branch: Branch to push (optional)

    Returns:
        Push output as string
    """
    if branch:
        return repo.git.push(remote, branch)
    else:
        return repo.git.push(remote)
