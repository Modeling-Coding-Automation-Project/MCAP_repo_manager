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
