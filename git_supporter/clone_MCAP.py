"""
This script provides a command-line utility to clone multiple Git repositories listed in the MCAP_info module.
It allows the user to specify a target folder via a command-line argument or a GUI folder selection dialog.
The script changes the working directory to the selected folder and clones each repository using the system's Git command.
"""

import os
import sys
sys.path.append(os.getcwd())

import argparse
import tkinter as tk
from tkinter import filedialog

from parameter.MCAP_info import MCAP_info


def main():
    parser = argparse.ArgumentParser(
        description="Clone repositories listed in MCAP_info.")
    parser.add_argument(
        "--folder",
        type=str,
        help="Path to the folder where repositories will be cloned.",
        required=False
    )
    args = parser.parse_args()

    folder_path = args.folder

    if not folder_path:
        root = tk.Tk()
        root.withdraw()

        folder_path = filedialog.askdirectory()

    if not folder_path:
        raise ValueError("Folder is not selected.")

    os.chdir(folder_path)

    for repo_path in MCAP_info.repository_list.values():
        os.system("git clone " + repo_path)


if __name__ == "__main__":
    main()
