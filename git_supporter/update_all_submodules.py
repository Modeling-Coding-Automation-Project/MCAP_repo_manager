import os
import sys
sys.path.append(os.getcwd())

import argparse
import subprocess
import tkinter as tk
from tkinter import filedialog

from parameter.MCAP_info import MCAP_info


def main():
    """
    This script provides a command-line utility to update all git submodules for repositories listed in the MCAP_info configuration.
    It allows the user to specify a target folder via a command-line argument or a GUI folder selection dialog.
    For each repository directory specified in MCAP_info.repository_list, the script navigates to the directory and runs
    'git submodule update --progress --init' to initialize and update all submodules.
    """
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

    repo_directories = list(MCAP_info.repository_list.keys())

    os.chdir(folder_path)
    original_directory = os.getcwd()

    for i, directory in enumerate(repo_directories):
        path = os.path.join(original_directory, directory)
        os.chdir(path)
        subprocess.run("git submodule update --progress --init", shell=True)
        os.chdir(original_directory)


if __name__ == "__main__":
    main()
