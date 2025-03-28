#!/usr/bin/env python3

import os
import sys
sys.path.append(os.getcwd())

import argparse

from parameter.MCAP_info import MCAP_info


def main():
    parser = argparse.ArgumentParser(description="Clone repositories listed in MCAP_info.")
    parser.add_argument(
        "--folder",
        type=str,
        help="Path to the folder where repositories will be cloned.",
        required=False
    )
    args = parser.parse_args()

    folder_path = args.folder

    if not folder_path:
        raise ValueError("Folder is not selected.")

    os.chdir(folder_path)

    for repo_path in MCAP_info.repository_list.values():
        os.system("git clone " + repo_path)

if __name__ == "__main__":
    main()
