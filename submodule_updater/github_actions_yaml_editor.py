from submodule_updater.common_functions import *

import glob
import yaml


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


def revert_github_actions_yaml(repo_path, branch_name):
    """
    Revert all .yml files in .github/workflows/ to set push trigger branches back to ["develop"]
    if they were changed to ["develop", branch_name].
    """
    import os
    import glob
    import yaml
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
        on_section = get_on_section(data)
        if isinstance(on_section, dict):
            push_section = on_section.get("push")
            if isinstance(push_section, dict):
                branches = push_section.get("branches")
                if branches == ["develop", branch_name]:
                    push_section["branches"] = ["develop"]
                    with open(yml_file, "w", encoding="utf-8") as f:
                        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
                    changed_files.append(yml_file)
    if changed_files:
        brush_up_yaml_text(changed_files)

        cwd = os.path.abspath(repo_path)
        run_os_command("git add .github/workflows", cwd)
        run_os_command(
            f"git commit -m \"Revert GitHub Actions workflow branches to develop only\"", cwd)
        run_os_command(f"git push", cwd)
        print(f"Reverted workflow files: {changed_files}")
    else:
        print("No workflow files needed reverting.")
