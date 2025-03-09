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
