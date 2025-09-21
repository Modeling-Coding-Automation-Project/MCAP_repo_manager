import os
import sys
sys.path.append(os.getcwd())

from datetime import datetime

from submodule_updater.common_functions import *
from submodule_updater.constants import *
from submodule_updater.github_actions_yaml_editor import *
from submodule_updater.github_actions_manager import add_actions_and_check_results

from parameter.MCAP_info import MCAP_info


def replace_github_to_local_path(url_path):
    local_path = url_path
    for github, local in GITHUB_TO_LOCAL_PATH:
        local_path = local_path.replace(
            github, local)
    return local_path


def update_submodules(repository_path):
    command = "python " + PULL_ALL_SUBMODULES_PATH + " " + repository_path
    run_os_command(command)


def create_working_branch(repo_path):
    today = datetime.now().strftime('%Y%m%d')
    branch_name = f"update-submodule-{today}"
    cwd = os.path.abspath(repo_path)

    run_os_command("git clean -fx -d", cwd)
    run_os_command("git fetch", cwd)
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


def squash_merge_and_push(repo_path, branch_name):
    """
    Squash merge branch_name into develop, push, then merge develop into main and push.
    The squash merge commit message is 'サブモジュール更新'.
    """
    cwd = os.path.abspath(repo_path)

    run_os_command("git checkout develop", cwd)
    run_os_command("git pull", cwd)

    run_os_command(f"git merge --squash {branch_name}", cwd)
    run_os_command("git commit -m \"サブモジュール更新\"", cwd)
    run_os_command("git push", cwd)

    run_os_command("git checkout main", cwd)
    run_os_command("git pull", cwd)

    run_os_command("git merge develop", cwd)
    run_os_command("git push", cwd)

    run_os_command(f"git branch -D {branch_name}", cwd)
    run_os_command(f"git push origin --delete {branch_name}", cwd)


if __name__ == "__main__":
    for repo_name, url_path in MCAP_info.repository_list.items():
        folder_path = replace_github_to_local_path(url_path)

        # update submodules
        update_submodules(folder_path)

        update_exists_flag, branch_name, head_sha = create_working_branch(
            folder_path)

        if update_exists_flag:
            # Update GitHub Actions workflow YAMLs to trigger on the new branch
            head_sha = update_github_actions_yaml(folder_path, branch_name)
            if not head_sha:
                print("There are no GitHub Actions workflow files.")

                squash_merge_and_push(folder_path, branch_name)
                print(f"Submodule update of {folder_path} completed.")
                continue

            # Trigger GitHub Actions
            success_flag = add_actions_and_check_results(
                branch_name, head_sha, folder_path)

            if not success_flag:
                sys.exit(1)

            revert_github_actions_yaml(folder_path, branch_name)

            squash_merge_and_push(folder_path, branch_name)
            print(f"Submodule update of {folder_path} completed.")
