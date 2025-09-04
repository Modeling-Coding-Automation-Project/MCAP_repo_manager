import json
import subprocess
import time
from typing import Optional

from submodule_updater.constants import *


class GHError(Exception):
    pass


def gh_json(args: list[str], cwd=None) -> list[dict] | dict:
    """Execute the gh command with --json and return the JSON output"""
    cp = subprocess.run(
        ["gh"] + args,
        check=True,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    out = cp.stdout.strip()
    return json.loads(out) if out else {}


def find_run_id_for_sha(branch: str, head_sha: str, limit: int = 30, cwd=None) -> Optional[int]:
    """Look for recent runs on the target branch and return all that match the headSha as a list of databaseId."""
    data = gh_json([
        "run", "list",
        "--branch", branch,
        "--limit", str(limit),
        "--json", "databaseId,headSha,status,conclusion,displayTitle,createdAt",
    ], cwd=cwd)
    run_ids = [r.get("databaseId")
               for r in data if r.get("headSha") == head_sha]
    return run_ids if run_ids else None


def gh_wait_run(run_id: int, cwd=None) -> int:
    """Wait for the GitHub Actions run to complete and return the exit status."""
    cp = subprocess.run(
        ["gh", "run", "watch", str(run_id), "--exit-status"],
        text=True,
        cwd=cwd,
    )
    return cp.returncode


def add_actions_and_check_results(branch, head_sha, cwd=None):
    """
    Look for all run IDs for the given SHA/branch and
    wait for all workflow results. All must succeed.
    """
    run_ids = None
    time.sleep(CHECK_ACTIONS_INTERVAL_TIME)

    for i in range(CHECK_ACTIONS_MAX_TRY):
        run_ids = find_run_id_for_sha(branch, head_sha, cwd=cwd)
        if run_ids:
            break
        time.sleep(CHECK_ACTIONS_INTERVAL_TIME)

    if not run_ids:
        raise GHError("Could not find workflow run for the given SHA/branch")

    print(f"Found runs: {run_ids}. Waiting...")
    all_success = True
    for run_id in run_ids:
        code = gh_wait_run(run_id, cwd=cwd)
        if code == 0:
            print(f"Workflow {run_id} success")
        else:
            print(f"Workflow {run_id} failed")
            all_success = False
    if not all_success:
        raise SystemExit(1)
    print("All workflows succeeded")
    return True
