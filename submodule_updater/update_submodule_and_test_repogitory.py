import os
import sys
import subprocess
from datetime import datetime


def run_cmd(cmd, cwd=None, check=True):
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


def main(repo_path):
    today = datetime.now().strftime('%Y%m%d')
    branch_name = f"update-submodule-{today}"
    cwd = os.path.abspath(repo_path)

    # 1. checkout develop and pull
    run_cmd("git checkout develop", cwd)
    run_cmd("git pull", cwd)

    # 2. create new branch
    run_cmd(f"git checkout -b {branch_name}", cwd)

    # 3. update submodules
    run_cmd("git submodule update --remote", cwd)

    # 4. add submodule changes
    run_cmd("git add .", cwd)

    # 5. check if there is anything to commit
    result = run_cmd("git status --porcelain", cwd, check=False)
    if result.stdout.strip() == "":
        print("No changes to commit.")
        return

    # 6. commit
    run_cmd(f"git commit -m 'Update submodules {today}'", cwd)

    # 7. push
    run_cmd(f"git push -u origin {branch_name}", cwd)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_submodule_and_test_repogitory.py <repo_path>")
        sys.exit(1)
    main(sys.argv[1])
