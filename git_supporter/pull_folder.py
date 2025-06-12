"""
This module provides functionality to search for Git repositories within a specified root directory.
It defines a function to recursively traverse directories and identify those containing a '.git' folder,
indicating the presence of a Git repository.

Classes:
    None

Functions:
    find_git_directories(root_dir): Recursively searches for directories containing a '.git' folder
    within the given root directory and returns a list of their paths.
"""

import os
import subprocess
from find_git_repository import find_git_repository


def find_git_directories(root_dir):
    """
    Recursively searches for Git repositories within the specified root directory.

    Args:
        root_dir (str): The root directory to start searching from.

    Returns:
        list: A list of directory paths that contain a '.git' directory, indicating a Git repository.
    """
    git_dirs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '.git' in filenames:
            git_dirs.append(dirpath)
    return git_dirs


if __name__ == "__main__":

    git_directories = find_git_repository()

    original_directory = os.getcwd()

    for git_directory in git_directories:
        os.chdir(git_directory)
        subprocess.run("git checkout main", shell=True)
        subprocess.run("git pull", shell=True)
        subprocess.run("git checkout .", shell=True)
        os.chdir(original_directory)
