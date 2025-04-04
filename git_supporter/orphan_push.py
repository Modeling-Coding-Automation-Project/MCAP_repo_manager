#!/usr/bin/env python3

import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from get_git_repository import get_git_repository


def orphan_push():
    # %% Init

    folder_path, original_directory = get_git_repository()
    os.chdir(folder_path)

    now = datetime.now()
    DateString = now.strftime("%Y%m%d%H%M%S")

    subprocess.run(
        "git config --local core.pager \"LESSCHARSET=utf-8 less\"", shell=True)
    subprocess.run("git config --local core.quotepath \"false\"", shell=True)

    # %% Orphan
    system_command = subprocess.run(
        "git branch", shell=True, capture_output=True, text=True)
    branch_list = system_command.stdout.split("\n")
    for i in range(len(branch_list)):
        if branch_list[i][:2] == "* ":
            branch_name = branch_list[i][2:]
            break

    temp_branch_name = branch_name + DateString
    temp_branch_name = temp_branch_name.replace("\n", "")

    subprocess.run("git checkout --orphan " + temp_branch_name, shell=True)

    # %% Commit
    subprocess.run("git commit -m \"orphan push\"", shell=True)

    # %% Push
    subprocess.run("git push origin " + temp_branch_name, shell=True)

    # %% Delete Branch
    subprocess.run("git push --delete origin " + branch_name, shell=True)
    subprocess.run("git branch -D " + branch_name, shell=True)

    # %% Rename
    subprocess.run("git branch -m " + branch_name, shell=True)
    subprocess.run("git push origin " + branch_name, shell=True)

    subprocess.run("git push origin --delete " + temp_branch_name, shell=True)

    # %% end
    os.chdir(original_directory)


orphan_push()
