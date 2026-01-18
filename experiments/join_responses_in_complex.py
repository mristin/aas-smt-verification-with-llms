"""Join all responses from complex cases into one JSON object."""

import argparse
import collections
import json
import os
import pathlib
import sys
from typing import List


def main() -> int:
    """Execute the main routine."""
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.parse_args()

    repo_root = pathlib.Path(os.path.realpath(__file__)).parent.parent

    complex_output_dir = (
        repo_root / "experiment_output" / "gpt-5-2025-08-07" / "complex"
    )

    for done_path in sorted(complex_output_dir.glob("**/done")):
        case_dir = done_path.parent

        parts = ["["]  # type: List[str]

        object_count = 0

        for response_path in sorted(case_dir.glob("**/response_*.txt")):
            text = response_path.read_text(encoding="utf-8")

            try:
                # noinspection PyTypeChecker
                jsonable = json.loads(text, object_pairs_hook=collections.OrderedDict)
            except Exception as exception:
                parts.append(f"\n// Failed to parse {response_path.name}: {exception}")
                continue

            parts.append(f"\n// From: {response_path.name}")

            if isinstance(jsonable, list):
                if len(jsonable) == 0:
                    parts.append("\n// Empty list")
                else:
                    for item in jsonable:
                        if object_count > 0:
                            parts.append("\n,\n")
                        else:
                            parts.append("\n")

                        parts.append(json.dumps(item, indent=2))
                        object_count += 1
            else:
                if object_count > 0:
                    parts.append("\n,\n")
                else:
                    parts.append("\n")

                parts.append(json.dumps(jsonable, indent=2))
                object_count += 1

        parts.append("\n]")

        output = "".join(parts)

        output_path = case_dir / "all_responses_merged.json"
        output_path.write_text(output, encoding="utf-8")

        print(f"Written to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
