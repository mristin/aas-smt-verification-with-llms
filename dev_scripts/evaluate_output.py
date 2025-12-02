"""
This evaluates the output of our experiments.
"""

import pathlib
import sys
import os
import argparse
import json
from dataclasses import dataclass
from typing import List, Any


@dataclass
class Stats:
    """
    A class collecting stats for reporting.
    """

    expected_accepted: int = 0  # This is good :)
    expected_rejected: int = 0
    unexpected_accepted: int = 0
    unexpected_rejected: int = 0  # This is good :)
    invalid_json: int = 0

    def dump(self) -> None:
        """
        Dump the Stats to a file for persistence
        """

        def percent(v: float) -> str:
            """
            Translate a float between 0 and 1 to a string percentage
            """
            return f"{v*100:.0f}%"

        total = (
            self.expected_accepted
            + self.expected_rejected
            + self.unexpected_accepted
            + self.unexpected_rejected
            + self.invalid_json
        )
        if total == 0:
            print("No stats available")
            return

        print(f"Invalid json:            {self.invalid_json} of {total} files")
        print(
            f"Expected and accepted:   "
            f"{percent(self.expected_accepted / (self.expected_accepted + self.expected_rejected))}"
        )
        ratio = self.unexpected_rejected / (
            self.unexpected_accepted + self.unexpected_rejected
        )
        print(f"Unexpected and rejected: {percent(ratio)}")


def _load(response_file: pathlib.Path) -> List[Any]:
    with open(response_file, "rb") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(str(e)) from e
    if not isinstance(data, list):
        raise ValueError("does not contain a list")
    return data


def _evaluate(experiment_dir: pathlib.Path, stats: Stats) -> None:
    print(f"Evaluating {experiment_dir.name}")

    expected_dir = experiment_dir / "expected"
    assert expected_dir.exists() and expected_dir.is_dir()
    for i in expected_dir.iterdir():
        response_file = i / "response.txt"
        try:
            data = _load(response_file)
        except ValueError as e:
            print(f'Cannot de-serialize "{response_file}": {e}')
            stats.invalid_json += 1
            continue

        if len(data) == 0:
            stats.expected_accepted += 1
        else:
            stats.expected_rejected += 1

    unexpected_dir = experiment_dir / "unexpected"
    assert unexpected_dir.exists() and unexpected_dir.is_dir()
    for i in expected_dir.iterdir():
        response_file = i / "response.txt"
        try:
            data = _load(response_file)
        except ValueError as e:
            print(f'Cannot de-serialize "{response_file}": {e}')
            stats.invalid_json += 1
            continue

        if len(data) == 0:
            stats.unexpected_accepted += 1
        else:
            stats.unexpected_rejected += 1


def main() -> int:
    """
    Main method
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="gpt-5-2025-08-07")
    args = parser.parse_args()
    model: str = args.model

    repo_root = pathlib.Path(os.path.realpath(__file__)).parent.parent
    experiment_output_dir = repo_root / "experiment_output" / model
    stats = Stats()
    for i in experiment_output_dir.iterdir():
        _evaluate(i, stats)
    stats.dump()
    return 0


if __name__ == "__main__":
    sys.exit(main())
