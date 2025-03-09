import os
import sys
sys.path.append(os.getcwd())

import subprocess
import tkinter as tk
from tkinter import filedialog

from parameter.MCAP_info import MCAP_info


if __name__ == "__main__":

    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory()

    if folder_path == "":
        raise ValueError("Folder is not selected.")

    repo_directories = list(MCAP_info.repository_list.keys())

    os.chdir(folder_path)
    original_directory = os.getcwd()

    for i, directory in enumerate(repo_directories):
        path = os.path.join(original_directory, directory)
        os.chdir(path)
        subprocess.run("git submodule update --progress --init", shell=True)
        os.chdir(original_directory)
