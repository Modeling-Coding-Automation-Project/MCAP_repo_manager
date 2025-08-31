"""
This module provides functionality to locate
 all Git repositories within a given root directory.
It recursively searches for directories containing a '.git' folder,
 which indicates the presence of a Git repository.

Functions:
    find_git_directories(root_dir): Recursively searches for and returns
      a list of directories under 'root_dir' that contain a '.git' folder,
        identifying them as Git repositories.

Classes:
    (No classes are defined in this module.)
"""

import os
import subprocess
from get_git_repository import get_git_repository


def find_git_directories(root_dir):
    """
    Recursively searches for Git repositories within the specified root directory.

    Args:
        root_dir (str): The path to the root directory to search for Git repositories.

    Returns:
        list: A list of directory paths that contain a '.git' directory,
          indicating a Git repository.
    """
    git_dirs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '.git' in filenames:
            git_dirs.append(dirpath)
    return git_dirs


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        original_directory = os.getcwd()
    else:
        folder_path, original_directory = get_git_repository()

    submodule_directories = find_git_directories(folder_path)
    for submodule_directory in submodule_directories:
        os.chdir(submodule_directory)
        subprocess.run("git checkout main", shell=True)
        subprocess.run("git pull", shell=True)
        subprocess.run("git checkout .", shell=True)
        os.chdir(original_directory)
