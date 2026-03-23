#!/usr/bin/env python
"""
Bulk IP load pipeline: run NSTLLoadInsCheck and NSTLLoadIPCheck on an Excel file,
and optionally run NSTLLoadIPRange on the generated "to load" file.

Usage (from project root):
  python scripts/bulk_ip_load_pipeline.py <path_to_excel> [--load] [--no-docker-filter]

  --load              After checks, run NSTLLoadIPRange on NSTL_all_ip_to_load.xlsx
  --no-docker-filter  If python3 is missing, skip the overlap filter (do not use Docker)

The overlap filter (filter_nstl_ip_check_error_overlap_only.py) is pure file I/O
(openpyxl only; no Django). If `python3` is not on PATH, the pipeline tries:
  docker run ... python:3.11-slim-bookworm  (override with NSTL_PY3_FILTER_IMAGE)

Override image: NSTL_PY3_FILTER_IMAGE=python:3.12-slim python scripts/bulk_ip_load_pipeline.py ...
"""
from __future__ import print_function

import argparse
import os
import shutil
import subprocess
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(SCRIPT_DIR))
TO_LOAD_FILE = "NSTL_all_ip_to_load.xlsx"
DEFAULT_PY3_FILTER_IMAGE = "python:3.11-slim-bookworm"

try:
    _which = shutil.which
except AttributeError:

    def _which(cmd):
        from distutils.spawn import find_executable

        return find_executable(cmd)


def _call(cmd, cwd=None):
    """Py2-compatible subprocess (no subprocess.run)."""
    return subprocess.call(cmd, cwd=cwd)


def _run_overlap_filter(use_docker):
    """
    Produce NSTL_all_ip_check_error_overlap_only.xlsx from NSTL_all_ip_check_error.xlsx.
    No Django — only openpyxl. Prefer local python3; else optional one-off Docker container.
    """
    filter_script = os.path.join(SCRIPT_DIR, "filter_nstl_ip_check_error_overlap_only.py")
    if not os.path.isfile(filter_script):
        print("Overlap filter script missing: {}".format(filter_script), file=sys.stderr)
        return False

    py3 = _which("python3")
    if py3:
        print("Running: filter_nstl_ip_check_error_overlap_only.py (local python3)")
        rc = _call([py3, filter_script], cwd=PROJECT_ROOT)
        if rc != 0:
            print(
                "Overlap-only filter failed (install: python3 -m pip install openpyxl). "
                "Review full NSTL_all_ip_check_error.xlsx.",
                file=sys.stderr,
            )
        return rc == 0

    if use_docker and _which("docker"):
        image = os.environ.get("NSTL_PY3_FILTER_IMAGE", DEFAULT_PY3_FILTER_IMAGE)
        print(
            "Running: filter_nstl_ip_check_error_overlap_only.py "
            "(one-off container {}; no app / Python 2 image required)".format(image)
        )
        inner = (
            "pip install --no-cache-dir -q openpyxl && "
            "python scripts/filter_nstl_ip_check_error_overlap_only.py"
        )
        cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            "{}:/work".format(PROJECT_ROOT),
            "-w",
            "/work",
            image,
            "bash",
            "-lc",
            inner,
        ]
        rc = _call(cmd, cwd=PROJECT_ROOT)
        if rc != 0:
            print(
                "Overlap-only filter via Docker failed (check docker network for pip, image pull). "
                "Review full NSTL_all_ip_check_error.xlsx.",
                file=sys.stderr,
            )
        return rc == 0

    print(
        "Skipping overlap-only filter: no python3 and no docker (or use --no-docker-filter). "
        "From project root on a machine with Docker:\n"
        "  docker run --rm -v \"$PWD:/work\" -w /work {img} bash -lc "
        "'pip install --no-cache-dir -q openpyxl && "
        "python scripts/filter_nstl_ip_check_error_overlap_only.py'".format(
            img=DEFAULT_PY3_FILTER_IMAGE
        ),
        file=sys.stderr,
    )
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Run NSTL ins check and IP check; optionally load IP ranges"
    )
    parser.add_argument("excel_path", help="Path to Excel file (serial id, cn name, en name, start ip, end ip)")
    parser.add_argument(
        "--load",
        action="store_true",
        help="Run NSTLLoadIPRange on " + TO_LOAD_FILE + " after checks",
    )
    parser.add_argument(
        "--no-docker-filter",
        action="store_true",
        help="If python3 is missing, do not run the overlap filter in a one-off Python 3 container",
    )
    args = parser.parse_args()

    excel_path = os.path.abspath(args.excel_path)
    if not os.path.isfile(excel_path):
        print("Error: file not found: {}".format(excel_path), file=sys.stderr)
        return 1

    def run_script(name, script_args):
        cmd = [sys.executable, os.path.join(SCRIPT_DIR, name)] + script_args
        print("Running: {} {}".format(name, " ".join(script_args)))
        rc = _call(cmd, cwd=PROJECT_ROOT)
        if rc != 0:
            print("{} exited with code {}".format(name, rc), file=sys.stderr)
            return False
        return True

    if not run_script("NSTLLoadInsCheck.py", [excel_path]):
        return 1
    if not run_script("NSTLLoadIPCheck.py", [excel_path]):
        return 1

    _run_overlap_filter(use_docker=not args.no_docker_filter)

    if args.load:
        to_load_path = os.path.join(PROJECT_ROOT, TO_LOAD_FILE)
        if not os.path.isfile(to_load_path):
            print("Error: {} not found (run without --load first and fix errors)".format(TO_LOAD_FILE), file=sys.stderr)
            return 1
        if not run_script("NSTLLoadIPRange.py", [to_load_path]):
            return 1
        print("Load complete.")
    else:
        print(
            "Checks done. Review NSTL_all_ip_to_load.xlsx and "
            "NSTL_all_ip_check_error_overlap_only.xlsx (overlap-only). "
            "Full errors: NSTL_all_ip_check_error.xlsx"
        )
        print("To load IPs, run: python scripts/bulk_ip_load_pipeline.py <excel> --load")
    return 0


if __name__ == "__main__":
    sys.exit(main())
