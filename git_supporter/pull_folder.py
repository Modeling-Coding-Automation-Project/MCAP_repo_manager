import os
import subprocess
from find_git_repository import find_git_repository


def find_git_directories(root_dir):
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
