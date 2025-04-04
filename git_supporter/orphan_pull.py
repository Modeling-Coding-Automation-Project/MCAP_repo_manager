#!/usr/bin/env python3

import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from get_git_repository import get_git_repository


def orphan_pull():
    # %% Init
    folder_path, original_directory = get_git_repository()
    os.chdir(folder_path)

    system_command = subprocess.run(
        "git branch", shell=True, capture_output=True, text=True)
    branch_list = system_command.stdout.split("\n")
    for i in range(len(branch_list)):
        if branch_list[i][:2] == "* ":
            branch_name = branch_list[i][2:]
            break

    branch_name_temp = branch_name + "_temp"

    # %% pull
    subprocess.run("git fetch", shell=True)

    subprocess.run("git checkout -b " + branch_name_temp, shell=True)
    subprocess.run("git branch -D " + branch_name, shell=True)

    subprocess.run("git checkout -b " + branch_name +
                   " origin/" + branch_name, shell=True)

    subprocess.run("git branch -D " + branch_name_temp, shell=True)


orphan_pull()
