import os
import sys

from openai import max_retries
sys.path.append(os.getcwd())

import subprocess

from submodule_updater.constants import *


def run_os_command(cmd, cwd=None, check=True):
    print(f"[RUN] {cmd}")
    import time
    GIT_COMMAND_MAX_RETRIES = 5
    GIT_COMMAND_RETRY_INTERVAL = 2
    for attempt in range(1, GIT_COMMAND_MAX_RETRIES + 1):
        result = subprocess.run(cmd, shell=True, cwd=cwd,
                                capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if "index.lock" in (result.stderr or "") and "File exists" in (result.stderr or ""):
            if attempt < GIT_COMMAND_MAX_RETRIES:
                print(
                    f"index.lock detected. Waiting {GIT_COMMAND_RETRY_INTERVAL} seconds before retrying... (attempt {attempt}/{GIT_COMMAND_MAX_RETRIES})")
                time.sleep(GIT_COMMAND_RETRY_INTERVAL)
                continue
            else:
                print("index.lock error persists after retries.")
        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
        return result
    raise RuntimeError(
        f"Command failed after {GIT_COMMAND_MAX_RETRIES} retries due to index.lock: {cmd}\n{result.stderr}")
