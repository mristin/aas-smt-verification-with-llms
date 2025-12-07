#!/usr/bin/env python3
"""Inline response.txt contents into the manual evaluation CSV file."""

import argparse
import csv
import os
import pathlib
from typing import MutableMapping


def read_response_files(experiment_dir: pathlib.Path) -> MutableMapping[str, str]:
    """Read all response.txt files and key them by expectation and test case name."""
    responses = {}

    for expectation_dir in ["expected", "unexpected"]:
        exp_path = experiment_dir / expectation_dir
        if exp_path.exists():
            for test_case_dir in exp_path.iterdir():
                if test_case_dir.is_dir():
                    response_file = test_case_dir / "response.txt"
                    key = f"{expectation_dir}/{test_case_dir.name}"
                    if response_file.exists():
                        with open(response_file, "r", encoding="utf-8") as f:
                            content = f.read().strip()
                            responses[key] = content
                    else:
                        responses[key] = "FILE_NOT_FOUND"

    return responses


def main() -> None:
    """Execute the main routine."""
    parser = argparse.ArgumentParser(
        description="Inline response.txt contents into the manual evaluation CSV file."
    )
    parser.add_argument(
        "--edge",
        default="description_to_display_name",
        help="Edge type for the experiment",
    )
    parser.add_argument(
        "--username", default="mristin", help="Username for the evaluation file"
    )

    args = parser.parse_args()
    edge = args.edge
    username = args.username

    this_path = pathlib.Path(os.path.realpath(__file__))
    repo_root = this_path.parent.parent
    experiment_dir = repo_root / "experiment_output/gpt-5-2025-08-07" / edge
    csv_path = (
        repo_root
        / "experiment_evaluation/gpt-5-2025-08-07"
        / edge
        / f"manual-evaluation-{username}.csv"
    )

    responses = read_response_files(experiment_dir)

    print(f"Found {len(responses)} response files")

    # Read the CSV file and create updated content
    updated_lines = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        updated_lines.append(",".join(header))

        for row in reader:
            expectation, category, case_name, _, _ = row

            escaped_row = []
            for cell in row:
                if "," in cell or '"' in cell:
                    escaped_cell = cell.replace('"', '""')
                    escaped_row.append(f'"{escaped_cell}"')
                else:
                    escaped_row.append(cell)

            updated_lines.append(",".join(escaped_row))

            # Get the corresponding response using expectation and case name
            response_key = f"{expectation}/{case_name}"
            response = responses.get(response_key, "RESPONSE_NOT_FOUND")

            # Add response as second line (not as CSV, just raw content)
            updated_lines.append(response)

            print(f"Processed: {expectation} - {category} - {case_name}")

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        for line in updated_lines:
            f.write(line + "\n")

    print(f"Updated CSV file: {csv_path}")


if __name__ == "__main__":
    main()
