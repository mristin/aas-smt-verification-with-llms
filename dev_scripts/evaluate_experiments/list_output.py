"""
Script to list the prompts and responses of one set of experiments
"""

import os

BASE_DIR = "../experiment_output/gpt-5-2025-08-07/concept_description_to_description/unexpected/"

for name in sorted(os.listdir(BASE_DIR)):
    subdir = os.path.join(BASE_DIR, name)
    if not os.path.isdir(subdir):
        continue

    prompt_path = os.path.join(subdir, "prompt.txt")
    response_path = os.path.join(subdir, "response.txt")

    if not (os.path.isfile(prompt_path) and os.path.isfile(response_path)):
        continue

    print("=" * 80)
    print(f"📁 {name}")
    print("-" * 80)

    print("PROMPT:")
    print("-" * 20)
    with open(prompt_path, "r", encoding="utf-8") as f:
        print(f.read())

    print("\nRESPONSE:")
    print("-" * 20)
    with open(response_path, "r", encoding="utf-8") as f:
        print(f.read())

    input("\nPress Enter to continue…")
