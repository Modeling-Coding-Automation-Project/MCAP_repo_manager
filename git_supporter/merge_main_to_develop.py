from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import tkinter as tk
from tkinter import filedialog

from submodule_updater.common_functions import run_os_command


def select_root_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="フォルダを選択してください")
    if not folder_path:
        print("フォルダが選択されませんでした。")
        return None
    return folder_path


def list_git_repositories(root_folder):
    git_repos = []
    for entry in Path(root_folder).iterdir():
        if entry.is_dir() and (entry / ".git").is_dir():
            git_repos.append(entry)
    return git_repos


def merge_main_to_develop(repo_path):
    cwd = os.path.abspath(repo_path)
    print(f"\n--- {cwd} ---")

    run_os_command("git fetch", cwd)
    run_os_command("git checkout main", cwd)
    run_os_command("git pull", cwd)

    main_sha = run_os_command("git rev-parse origin/main", cwd).stdout.strip()
    develop_sha = run_os_command(
        "git rev-parse origin/develop", cwd).stdout.strip()

    if main_sha == develop_sha:
        print("mainとdevelopは同じコミットを指しています。マージをスキップします。")
        return

    run_os_command("git checkout develop", cwd)
    run_os_command("git pull", cwd)
    run_os_command("git merge --ff main", cwd)
    run_os_command("git push", cwd)


if __name__ == "__main__":
    root_folder = select_root_folder()
    if root_folder is None:
        sys.exit(0)

    git_repos = list_git_repositories(root_folder)
    if not git_repos:
        print("Git管理されているフォルダが見つかりませんでした。")
        sys.exit(0)

    print(f"対象リポジトリ ({len(git_repos)}件):")
    for repo in git_repos:
        print(f"  {repo}")

    for repo in git_repos:
        merge_main_to_develop(repo)

    print("\n全リポジトリのマージが完了しました。")
