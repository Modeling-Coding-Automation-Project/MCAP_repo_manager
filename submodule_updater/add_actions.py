import json
import subprocess
import time
from typing import Optional

from submodule_updater.parameter import *


class GHError(Exception):
    pass


def gh_json(args: list[str]) -> list[dict] | dict:
    """ghコマンドを --json 付きで実行してJSONを返す"""
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
    gh run list で対象ブランチの最近のRunを見て、headSha一致を拾う。
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
    gh run watch --exit-status で待機。成功=0, 失敗≠0
    """
    cp = subprocess.run(
        ["gh", "run", "watch", str(run_id), "--exit-status"],
        text=True,
    )
    return cp.returncode


if __name__ == "__main__":
    branch = "update-submodule-20250830-01"
    head_sha = "YOUR_PUSHED_COMMIT_SHA"

    # run-idを探す（push直後は数秒遅延することがある）
    run_id = None
    for i in range(30):  # 最大 ~5分探す例
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
    else:
        print("Workflow failed")
    raise SystemExit(code)
