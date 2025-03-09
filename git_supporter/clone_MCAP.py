import os
import sys
sys.path.append(os.getcwd())

import tkinter as tk
from tkinter import filedialog

from parameter.MCAP_info import MCAP_info


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory()

    if folder_path == "":
        raise ValueError("Folder is not selected.")

    os.chdir(folder_path)

    for repo_path in MCAP_info.repository_list.values():
        os.system("git clone " + repo_path)
