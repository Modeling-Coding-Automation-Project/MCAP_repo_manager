import os
import sys
sys.path.append(os.getcwd())

from datetime import datetime

from submodule_updater.common_functions import *
from submodule_updater.parameter import *
from submodule_updater.github_actions_yaml_editor import *
from submodule_updater.manage_github_actions import add_actions_and_check_results


def update_submodules(repository_path):
    command = "python " + PULL_ALL_SUBMODULES_PATH + " " + repository_path
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
        update_exists_flag = False
        head_sha = None
        branch_name = None
    else:
        run_os_command(f"git commit -m \"Update submodules {today}\"", cwd)
        run_os_command(f"git push -u origin {branch_name}", cwd)
        # get latest commit hash (head sha)
        sha_result = run_os_command("git rev-parse HEAD", cwd)
        head_sha = sha_result.stdout.strip()
        update_exists_flag = True

    return update_exists_flag, branch_name, head_sha


if __name__ == "__main__":
    folder_path = REPOSITORY_TO_UPDATE_LIST[0]

    # update submodules
    update_submodules(folder_path)

    update_exists_flag, branch_name, head_sha = create_working_branch(
        folder_path)

    if update_exists_flag:
        # Update GitHub Actions workflow YAMLs to trigger on the new branch
        head_sha = update_github_actions_yaml(folder_path, branch_name)
        # Trigger GitHub Actions
        success_flag = add_actions_and_check_results(
            branch_name, head_sha, folder_path)

        if not success_flag:
            sys.exit(1)
