"""
This module provides a function to prompt the user to select a directory and verify if it is a valid Git repository.
It uses a graphical file dialog to select the folder, checks for the presence of a '.git' directory, and returns
the selected folder path along with the original working directory. If the selection is invalid or cancelled,
it prints an appropriate message and returns None.
"""

import os
import tkinter as tk
from tkinter import filedialog


def get_git_repository():

    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory()

    if folder_path == "":
        print("Folder is not selected.")
        return

    if not os.path.exists(folder_path + "/.git"):
        print(".git folder is not found.")
        return

    original_directory = os.getcwd()

    return folder_path, original_directory
