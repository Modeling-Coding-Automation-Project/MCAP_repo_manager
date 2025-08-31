import os
import sys
sys.path.append(os.getcwd())

import subprocess
from datetime import datetime

from submodule_updater.parameter import *


def run_os_command(cmd, cwd=None, check=True):
    print(f"[RUN] {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd,
                            capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")

    return result


def update_submodules(repository_path):
    command = PULL_ALL_SUBMODULES_PATH + " " + repository_path
    run_os_command(command)


def create_working_branch(repo_path):
    today = datetime.now().strftime('%Y%m%d')
    branch_name = f"update-submodule-{today}"
    cwd = os.path.abspath(repo_path)

    run_os_command("git checkout develop", cwd)
    run_os_command("git pull", cwd)

    run_os_command(f"git checkout -b {branch_name}", cwd)

    run_os_command("git add .", cwd)

    # check if there is anything to commit
    result = run_os_command("git status --porcelain", cwd, check=False)
    if result.stdout.strip() == "":
        print("No changes to commit.")

        run_os_command("git checkout -", cwd)
        run_os_command(f"git branch -D {branch_name}", cwd)
        return

    run_os_command(f"git commit -m 'Update submodules {today}'", cwd)

    run_os_command(f"git push -u origin {branch_name}", cwd)


if __name__ == "__main__":
    folder_path = REPOSITORY_TO_UPDATE_LIST[0]

    # update submodules
    update_submodules(folder_path)

    create_working_branch(folder_path)
