"""
This module provides functionality to pull the latest changes from the 'main' branch and reset local changes
for all Git repositories and their submodules under a specified directory.

Functions:
    find_git_directories(root_dir): Recursively searches for all Git repository directories
      under the specified directory and returns them as a list.
    find_submodule_directories(repo_dir): Returns a list of submodule directories
    within the specified repository.
    pull_repo_and_submodules(repo_dir, original_directory): Executes 'git pull' and
    related commands for the specified repository and its submodules.

Classes:
    (No classes are defined in this module.)
"""

import os
import subprocess
from find_git_repository import find_git_repository


def find_git_directories(root_dir):
    """
    Recursively searches for all Git repository directories under the specified directory.

    root_dir (str): The directory to start searching from.

    list: A list of directories that contain a .git directory.
    """
    git_dirs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '.git' in dirnames:
            git_dirs.append(dirpath)
            # do not search deeper in this directory
            dirnames[:] = []
    return git_dirs


def find_submodule_directories(repo_dir):
    """
    Finds all submodule directories within a specified Git repository.

    repo_dir (str): The path to the Git repository.

    list: A list of submodule directory paths found in the repository.

    This function reads the `.gitmodules` file in the given repository directory,
    parses the paths of all submodules, and returns a list of their absolute paths
    if the directories exist.
    """
    submodules = []
    gitmodules_path = os.path.join(repo_dir, '.gitmodules')
    if not os.path.isfile(gitmodules_path):
        return submodules

    with open(gitmodules_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('path ='):
                sub_path = line.split('=', 1)[1].strip()
                submodule_dir = os.path.join(repo_dir, sub_path)
                if os.path.isdir(submodule_dir):
                    submodules.append(submodule_dir)
    return submodules


def pull_repo_and_submodules(repo_dir, original_directory):
    """
    Pulls the latest changes from the 'main' branch for the specified Git repository and all its submodules.

    This function changes the working directory to the target repository, checks out the 'main' branch,
    pulls the latest changes, and resets any local changes. It then iterates through all submodule directories,
    performing the same operations for each submodule. Finally, it restores the original working directory.

        repo_dir (str): The file system path to the main Git repository.
        original_directory (str): The original working directory to return to after operations are complete.

    Raises:
        FileNotFoundError: If the specified repository or submodule directories do not exist.
        subprocess.CalledProcessError: If any git command fails during execution.
    """
    os.chdir(repo_dir)
    # check if the main branch exists and pull changes
    result = subprocess.run("git branch --list main",
                            shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        subprocess.run("git checkout main", shell=True)
        subprocess.run("git pull", shell=True)
        subprocess.run("git checkout .", shell=True)

    submodules = find_submodule_directories(repo_dir)
    for submodule_dir in submodules:
        os.chdir(submodule_dir)
        result = subprocess.run("git branch --list main",
                                shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            subprocess.run("git checkout main", shell=True)
            subprocess.run("git pull", shell=True)
            subprocess.run("git checkout .", shell=True)
    os.chdir(original_directory)


if __name__ == "__main__":

    git_directories = find_git_repository()

    original_directory = os.getcwd()

    for repo_dir in git_directories:
        pull_repo_and_submodules(repo_dir, original_directory)
