import os
import subprocess
from get_git_repository import get_git_repository


def find_git_directories(root_dir):
    git_dirs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '.git' in filenames:
            git_dirs.append(dirpath)
    return git_dirs


if __name__ == "__main__":
    folder_path, original_directory = get_git_repository()

    submodule_directories = find_git_directories(folder_path)
    for submodule_directory in submodule_directories:
        os.chdir(submodule_directory)
        subprocess.run("git checkout main", shell=True)
        subprocess.run("git pull", shell=True)
        subprocess.run("git checkout .", shell=True)
        os.chdir(original_directory)
