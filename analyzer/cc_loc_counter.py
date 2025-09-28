"""
File: cc_loc_counter.py

C/C++ source tree line counter with include resolution.

- Starts from a specified C/C++ file.
- Searches ONLY within the starting file's directory and its subdirectories.
  (Never searches parent directories.)
- Recursively resolves #include "..." and #include <...> to files that exist
  within this root. System headers are ignored unless they are found under root.
- Treats files with the same filename (basename) as identical: the first path
  discovered for a given basename is used, and duplicates are ignored.
- Counts "non-comment" lines for all discovered files, where "comment lines"
  are defined as:
    * The line where a block comment '/*' begins THROUGH the line where '*/'
      ends (inclusive), regardless of position in the line.
    * Lines whose first non-blank characters are '//'.
  (Optionally, blank-only lines may be excluded from the count via a flag.)

Usage:
        python cc_loc_counter.py [start.cpp] [--root /path/to/root]
                                                         [--include-blanks] [--csv out.csv]
                                                         [--list-only]

Notes:
- If the starting file argument is omitted, a native file selection dialog
    (e.g., Windows Explorer) will appear to let you choose a C/C++ file.
"""
from __future__ import annotations
import argparse
import os
import re
import sys
from collections import deque
from typing import Dict, Set, List, Tuple, Optional

# Recognized source/header extensions
DEFAULT_EXTS = [
    ".c", ".cc", ".cxx", ".cpp", ".c++",
    ".h", ".hh", ".hpp", ".hxx", ".inl", ".ipp"
]

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')


def is_code_like(path: str, exts: List[str]) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in exts


def build_index(root: str, exts: List[str]) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """
    Walk root and build:
      - name_to_path: map of basename -> first path found (preferred path)
      - name_to_all_paths: map of basename -> all matching paths (for diagnostics)
    """
    name_to_path: Dict[str, str] = {}
    name_to_all_paths: Dict[str, List[str]] = {}
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if is_code_like(fn, exts):
                p = os.path.join(dirpath, fn)
                bn = os.path.basename(fn)
                if bn not in name_to_path:
                    name_to_path[bn] = p
                name_to_all_paths.setdefault(bn, []).append(p)
    return name_to_path, name_to_all_paths


def parse_includes(file_path: str) -> List[str]:
    """Return list of include targets (raw tokens, e.g., 'foo.h' or 'sub/dir/foo.hpp')."""
    includes: List[str] = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = INCLUDE_RE.match(line)
                if m:
                    includes.append(m.group(1).strip())
    except Exception as e:
        print(f"[WARN] Failed to read {file_path}: {e}", file=sys.stderr)
    return includes


def resolve_include(root: str,
                    including_file: str,
                    target: str,
                    name_to_path: Dict[str, str]) -> Optional[str]:
    """
    Resolve include target to a path within root.
    Resolution strategy (within the root only):
      1) If the target contains path separators, try relative to including_file's dir.
      2) Fallback: by basename using name_to_path (first discovered path).
    Returns None if not found within root.
    """
    # If include looks like "sub/dir/foo.h": try relative to including file dir
    if os.sep in target or "/" in target:
        # Normalize both styles of separators
        target_norm = target.replace("\\", "/")
        # Try from including file's directory downward
        base_dir = os.path.dirname(including_file)
        candidate = os.path.normpath(os.path.join(base_dir, target_norm))
        # Ensure candidate is under root
        try:
            cand_real = os.path.realpath(candidate)
            root_real = os.path.realpath(root)
            if cand_real.startswith(root_real + os.sep) or cand_real == root_real:
                if os.path.exists(cand_real):
                    return cand_real
        except Exception:
            pass

        # If not found relative, fallback to basename lookup below

    bn = os.path.basename(target)
    # Only allow mapped names that live under root
    path = name_to_path.get(bn)
    if path:
        try:
            path_real = os.path.realpath(path)
            root_real = os.path.realpath(root)
            if path_real.startswith(root_real + os.sep) or path_real == root_real:
                return path
        except Exception:
            return None
    return None


def discover_closure(
        start_path: str, root: str, exts: List[str]
) -> Tuple[List[str], Dict[str, str], Dict[str, List[str]]]:
    """
    From start_path, recursively discover all included files (within root) while
    deduping by basename. Returns the ordered list of unique file paths (start first),
    along with name_to_path and name_to_all_paths for diagnostics.
    """
    name_to_path, name_to_all_paths = build_index(root, exts)

    start_bn = os.path.basename(start_path)
    if start_bn not in name_to_path:
        # Ensure start is included in the index if it wasn't by extension filtering
        if is_code_like(start_path, exts):
            name_to_path[start_bn] = start_path
            name_to_all_paths.setdefault(start_bn, []).append(start_path)
        else:
            print(
                f"[ERROR] Start file {start_path} does not look like a C/C++ source/header with known extensions.",
                file=sys.stderr)
            sys.exit(2)

    # BFS/DFS over includes while deduping by basename
    ordered_paths: List[str] = []
    seen_names: Set[str] = set()
    q: deque[Tuple[str, str]] = deque()  # (path, basename)

    # Seed
    first_path = name_to_path[start_bn] if start_bn in name_to_path else start_path
    q.append((first_path, start_bn))

    while q:
        path, bn = q.popleft()
        if bn in seen_names:
            continue
        seen_names.add(bn)
        ordered_paths.append(path)

        # Parse includes and resolve
        for inc in parse_includes(path):
            resolved = resolve_include(root, path, inc, name_to_path)
            if not resolved:
                # Not found locally under root -> ignore (likely system header)
                continue
            inc_bn = os.path.basename(resolved)
            if inc_bn not in seen_names:
                q.append((resolved, inc_bn))

    return ordered_paths, name_to_path, name_to_all_paths


def count_non_comment_lines(path: str, exclude_blank: bool = True) -> int:
    """
    Count lines that are NOT comment lines, where "comment lines" are:
      - From the line where '/*' appears to the line where '*/' appears (inclusive).
        (Even if '/*' occurs mid-line, the whole line is treated as a comment line.)
      - Lines whose first non-blank characters are '//'.
    If exclude_blank is True, lines that are blank (after stripping whitespace)
    are not counted either.
    NOTE: This is a simplified lexer and does not handle string literals that
    contain comment-like tokens.
    """
    loc = 0
    in_block = False

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                line = raw.rstrip("\n")
                stripped = line.lstrip()

                if in_block:
                    # Entire line is a comment line until we see */
                    end_idx = stripped.find("*/")
                    if end_idx != -1:
                        in_block = False
                    # Comment line -> skip counting
                    continue

                # Line starting with //
                if stripped.startswith("//"):
                    continue

                # Detect /* ... */
                start_idx = stripped.find("/*")
                if start_idx != -1:
                    # Begin block comment on this line; treat this entire line as comment
                    end_idx = stripped.find("*/", start_idx + 2)
                    if end_idx == -1:
                        in_block = True
                    # Either way, skip counting this line
                    continue

                # Non-comment line
                if exclude_blank and stripped == "":
                    continue
                loc += 1
    except Exception as e:
        print(f"[WARN] Failed to read {path}: {e}", file=sys.stderr)

    return loc


def ensure_within_root(path: str, root: str) -> None:
    pr = os.path.realpath(path)
    rr = os.path.realpath(root)
    if not (pr.startswith(rr + os.sep) or pr == rr):
        print(
            f"[ERROR] Start file must lie within root.\n  start={pr}\n  root ={rr}", file=sys.stderr)
        sys.exit(2)


def _select_file_via_gui(exts: List[str]) -> Optional[str]:
    """Open a native file selection dialog and return the chosen path or None if canceled.
    The filter will include common C/C++ extensions from `exts`.
    """
    # Import locally to avoid importing tkinter in non-GUI contexts
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as e:
        print(f"[ERROR] GUI file dialog is unavailable: {e}", file=sys.stderr)
        return None

    # Build file type filters
    patterns = " ".join(f"*{ext}" for ext in exts)
    filetypes = [
        ("C/C++ Files", patterns),
        ("All Files", "*.*"),
    ]

    root = tk.Tk()
    root.withdraw()  # Hide the empty root window
    root.update()
    try:
        filename = filedialog.askopenfilename(
            title="Select C/C++ start file",
            initialdir=os.getcwd(),
            filetypes=filetypes,
        )
    finally:
        try:
            root.destroy()
        except Exception:
            pass

    if not filename:
        return None
    return filename


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Count non-comment LOC for a C/C++ source file and its local #includes "
            "(within the same directory tree). If no start file is provided, a "
            "file selection dialog will open."
        ))
    ap.add_argument("start", nargs="?", default=None,
                    help="Path to the starting C/C++ file. If omitted, a GUI file chooser opens.")
    ap.add_argument(
        "--root", help="Restrict search to this root (default: directory of start file).", default=None)
    ap.add_argument("--exts", nargs="*", default=DEFAULT_EXTS,
                    help=f"File extensions considered as code (default: {DEFAULT_EXTS})")
    ap.add_argument("--include-blanks", action="store_true",
                    help="Count blank-only lines as code (default: exclude blanks).")
    ap.add_argument(
        "--csv", help="Optional path to write a CSV report (file,loc).")
    ap.add_argument("--list-only", action="store_true",
                    help="Only list discovered files (no counting).")
    args = ap.parse_args()

    # Resolve start file: from CLI or via GUI file chooser
    start_arg = args.start
    if not start_arg:
        selected = _select_file_via_gui(args.exts)
        if not selected:
            print("[ERROR] No file selected.", file=sys.stderr)
            sys.exit(1)
        start_arg = selected

    start_path = os.path.abspath(start_arg)
    if not os.path.exists(start_path):
        print(f"[ERROR] Start file not found: {start_path}", file=sys.stderr)
        sys.exit(1)

    if args.root:
        root = os.path.abspath(args.root)
    else:
        # Default to the parent of the start file's directory (one level up)
        start_dir = os.path.dirname(start_path)
        parent_dir = os.path.abspath(os.path.join(start_dir, os.pardir))
        # If the parent directory is the same as start_dir (e.g., start_dir is a drive root),
        # fall back to using start_dir as the root.
        if os.path.realpath(parent_dir) == os.path.realpath(start_dir):
            root = start_dir
        else:
            root = parent_dir
    ensure_within_root(start_path, root)

    files, name_to_path, name_to_all_paths = discover_closure(
        start_path, root, args.exts)

    print("# Discovered files (deduped by basename, search confined to root):")
    for p in files:
        print(p)

    if args.list_only:
        return

    print("\n# LOC per file (non-comment lines{}):".format(
        "" if args.include_blanks else ", blanks excluded"))
    total = 0
    per_file: List[Tuple[str, int]] = []
    for p in files:
        loc = count_non_comment_lines(
            p, exclude_blank=(not args.include_blanks))
        per_file.append((p, loc))
        total += loc
        print(f"{loc:8d}  {p}")

    print("\n# TOTAL LOC:", total)

    if args.csv:
        try:
            import csv
            with open(args.csv, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["file", "loc"])
                w.writerows(per_file)
                w.writerow(["TOTAL", total])
            print(f"\nCSV written to: {os.path.abspath(args.csv)}")
        except Exception as e:
            print(f"[WARN] Failed to write CSV: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
