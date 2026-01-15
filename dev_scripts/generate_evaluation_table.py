"""Generate the evaluation table to make the manual inspection easy."""

import argparse
import os
import pathlib
import sys


def main() -> int:
    """Execute the main routine."""
    repo_root = pathlib.Path(os.path.realpath(__file__)).parent.parent

    base_experiment_output_dir = repo_root / "experiment_output/gpt-5-2025-08-07"

    test_case_names = [
        pth.name for pth in sorted(base_experiment_output_dir.iterdir()) if pth.is_dir()
    ]

    base_experiment_output_rel_dir = base_experiment_output_dir.relative_to(repo_root)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--test_name",
        help=f"Test case to be considered based on {base_experiment_output_rel_dir}",
        required=True,
        choices=test_case_names,
    )
    parser.add_argument(
        "--output",
        help="Path to the table; '-' for STDOUT",
        required=True,
    )
    args = parser.parse_args()

    test_case_dir = base_experiment_output_dir / args.test_name

    output_lines = ["Expectation,Category,Case name,Correct,Remark"]

    for expectation in ["expected", "unexpected"]:
        expectation_dir = test_case_dir / expectation
        if not expectation_dir.exists():
            continue

        test_cases = [
            case_dir.name
            for case_dir in sorted(expectation_dir.iterdir())
            if case_dir.is_dir()
        ]

        for case_name in test_cases:
            case_dir = expectation_dir / case_name
            response_file = case_dir / "response.txt"
            prompt_file = case_dir / "prompt.txt"

            response_content = ""
            if response_file.exists():
                try:
                    with open(response_file, "r", encoding="utf-8") as f:
                        response_content = f.read().strip()
                except Exception as e:
                    response_content = f"Error reading response.txt: {e}"
            else:
                response_content = "No response.txt found"

            # Read prompt data after "Here is the data to be analyzed:" if needed
            prompt_data = ""
            if prompt_file.exists():
                try:
                    with open(prompt_file, "r", encoding="utf-8") as f:
                        prompt_lines = f.readlines()

                    # Find the line with "Here is the data to be analyzed:"
                    data_start_idx = None
                    for i, line in enumerate(prompt_lines):
                        if line.strip() == "Here is the data to be analyzed:":
                            data_start_idx = i + 1
                            break

                    # Include everything after that line
                    if data_start_idx is not None and data_start_idx < len(
                        prompt_lines
                    ):
                        prompt_data = "".join(prompt_lines[data_start_idx:]).strip()
                        if prompt_data:
                            prompt_data = (
                                "PROMPT DATA:\n" + prompt_data + "\n\nRESPONSE:"
                            )
                except Exception as e:
                    prompt_data = f"Error reading prompt.txt: {e}"

            if expectation == "expected" and response_content == "[]":
                output_lines.append(f"{expectation},,{case_name},yes,")
            else:
                output_lines.append("---")
                output_lines.append(f"{expectation},,{case_name},yes,")

                if len(prompt_data) > 0:
                    output_lines.append(prompt_data)

                output_lines.append(response_content)
                output_lines.append("---")

    output_content = "\n".join(output_lines)

    if args.output == "-":
        print(output_content)
    else:
        output_path = pathlib.Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_content)
            f.write("\n")

        print(f"Table written to {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
