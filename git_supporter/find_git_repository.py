"""
This module provides a function to search for Git repositories within a user-selected directory.
It utilizes a graphical file dialog to prompt the user to select a folder, then scans the immediate
subdirectories for the presence of a '.git' directory, indicating a Git repository.

Functions:
    find_git_repository(): Prompts the user to select a directory and returns a list of subdirectories
    that are Git repositories (i.e., contain a '.git' folder).
"""

import os
import tkinter as tk
from tkinter import filedialog


def find_git_repository():

    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory()

    if folder_path == "":
        print("Folder is not selected.")
        return

    git_dirs = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            if '.git' in os.listdir(item_path):
                git_dirs.append(item_path)

    return git_dirs
