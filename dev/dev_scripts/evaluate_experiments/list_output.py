# SPDX-FileCopyrightText: 2025 aas-smt-verification-with-llms AUTHORS
#
# SPDX-License-Identifier: MIT

"""
Script to list the prompts and responses of one set of experiments
"""

import os
import pathlib

BASE_DIR = (
    pathlib.Path(os.path.realpath(__file__)).parent.parent.parent.parent
    / "experiment_output"
    / "gpt-5-2025-08-07"
    / "concept_description_to_description"
    / "unexpected"
)

for subdir in sorted(BASE_DIR.iterdir()):
    if not subdir.is_dir():
        continue

    name = subdir.name
    prompt_path = subdir / "prompt.txt"
    response_path = subdir / "response.txt"

    if not (prompt_path.is_file() and response_path.is_file()):
        continue

    print("=" * 80)
    print(f"📁 {name}")
    print("-" * 80)

    print("PROMPT:")
    print("-" * 20)
    with prompt_path.open(encoding="utf-8") as f:
        print(f.read())

    print("\nRESPONSE:")
    print("-" * 20)
    with response_path.open(encoding="utf-8") as f:
        print(f.read())

    input("\nPress Enter to continue…")
