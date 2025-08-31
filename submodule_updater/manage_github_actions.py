import json
import subprocess
import time
from typing import Optional

from submodule_updater.parameter import *


class GHError(Exception):
    pass


def gh_json(args: list[str]) -> list[dict] | dict:
    """Execute the gh command with --json and return the JSON output"""
    cp = subprocess.run(
        ["gh"] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    out = cp.stdout.strip()
    return json.loads(out) if out else {}


def find_run_id_for_sha(branch: str, head_sha: str, limit: int = 30) -> Optional[int]:
    """
    Look for recent runs on the target branch and find one that matches the headSha.
    """
    data = gh_json([
        "run", "list",
        "--branch", branch,
        "--limit", str(limit),
        "--json", "databaseId,headSha,status,conclusion,displayTitle,createdAt",
    ])
    for r in data:
        if r.get("headSha") == head_sha:
            return r.get("databaseId")
    return None


def gh_wait_run(run_id: int) -> int:
    """
    Wait for the GitHub Actions run to complete and return the exit status.
    """
    cp = subprocess.run(
        ["gh", "run", "watch", str(run_id), "--exit-status"],
        text=True,
    )
    return cp.returncode


def add_actions_and_check_results(branch, head_sha):
    # Look for the run ID (there may be a delay of a few seconds immediately after push)
    run_id = None
    for i in range(CHECK_ACTIONS_MAX_TRY):
        run_id = find_run_id_for_sha(branch, head_sha)
        if run_id:
            break
        time.sleep(CHECK_ACTIONS_INTERVAL_TIME)

    if not run_id:
        raise GHError("Could not find workflow run for the given SHA/branch")

    print(f"Found run: {run_id}. Waiting...")
    code = gh_wait_run(run_id)
    if code == 0:
        print("Workflow success")
        success_flag = True
    else:
        print("Workflow failed")
        success_flag = False
    raise SystemExit(code)

    return success_flag
