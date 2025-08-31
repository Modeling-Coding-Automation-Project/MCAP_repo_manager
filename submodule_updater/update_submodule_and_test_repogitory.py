import os
import sys
sys.path.append(os.getcwd())

import subprocess
import glob
import yaml
from datetime import datetime

from submodule_updater.parameter import *
from submodule_updater.manage_github_actions import add_actions_and_check_results


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


def get_on_section(data):
    on_section = data.get("on")

    if not on_section:
        on_section = data.get(True)

    return on_section


def brush_up_yaml_text(changed_files):
    for file_path in changed_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        text = text.replace("true:", "\non:")
        text = text.replace("jobs:", "\njobs:")
        text = text.replace("    strategy:", "\n    strategy:")
        text = text.replace("    steps:", "\n    steps:")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)


def update_github_actions_yaml(repo_path, branch_name):
    """
    Update all .yml files in .github/workflows/ to add the new branch to push trigger.
    """
    workflows_dir = os.path.join(repo_path, ".github", "workflows")
    if not os.path.isdir(workflows_dir):
        print(f"No workflows directory: {workflows_dir}")
        return
    yml_files = glob.glob(os.path.join(workflows_dir, "*.yml")) + \
        glob.glob(os.path.join(workflows_dir, "*.yaml"))
    changed_files = []
    for yml_file in yml_files:
        with open(yml_file, encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except Exception as e:
                print(f"Failed to parse {yml_file}: {e}")
                continue
        # Check for the pattern: on: push: branches: [ develop ]
        on_section = get_on_section(data)
        if isinstance(on_section, dict):
            push_section = on_section.get("push")
            if isinstance(push_section, dict):
                branches = push_section.get("branches")
                if branches == ["develop"]:
                    # Add the new branch
                    push_section["branches"] = ["develop", branch_name]
                    with open(yml_file, "w", encoding="utf-8") as f:
                        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
                    changed_files.append(yml_file)
    if changed_files:
        brush_up_yaml_text(changed_files)

        cwd = os.path.abspath(repo_path)
        run_os_command("git add .github/workflows", cwd)
        run_os_command(
            f"git commit -m \"Update GitHub Actions workflow branches for {branch_name}\"", cwd)
        run_os_command(f"git push", cwd)
        # Get the latest commit sha after push
        sha_result = run_os_command("git rev-parse HEAD", cwd)
        head_sha = sha_result.stdout.strip()
        print(f"Updated workflow files: {changed_files}")
    else:
        print("No workflow files needed updating.")
        head_sha = None

    return head_sha


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
