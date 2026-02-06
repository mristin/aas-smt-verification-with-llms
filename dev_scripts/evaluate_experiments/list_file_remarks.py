"""
A script for manually comparing the remarks in the evaluation files side by side.
"""

from __future__ import annotations

import csv
import os
from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional, Set, Tuple, TypedDict


Key = Tuple[str, str]  # (Expectation, Case name)


class RowInfo(TypedDict):
    """
    Quick container for a remark and line that remark was found
    """

    remark: str
    line: int


def load_csv_index(path: str) -> tuple[Dict[Key, RowInfo], List[Key]]:
    """
    Returns:
      index: dict[(Expectation, Case name)] -> {"remark": str, "line": int}
      duplicates: list of keys that appeared more than once
    Line numbers are actual CSV line numbers including header line as line 1.
    """
    index: Dict[Key, RowInfo] = {}
    duplicates: List[Key] = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Header is line 1, first data row is line 2.
        line_no: int = 1
        for row in reader:
            line_no += 1
            exp: str = (row.get("Expectation") or "").strip()
            case: str = (row.get("Case name") or "").strip()
            key: Key = (exp, case)

            remark: str = (row.get("Remark") or "").strip()

            if key in index:
                duplicates.append(key)
                # Keep the first occurrence; you can change this if you prefer "last wins".
                continue

            index[key] = {"remark": remark, "line": line_no}

    return index, duplicates


def compare_csv_directory(directory_path: str) -> None:
    """
    Build an index for all CSV files in the given directory
    """
    csv_files: List[str] = sorted(
        f for f in os.listdir(directory_path) if f.lower().endswith(".csv")
    )

    if not csv_files:
        print("No CSV files found. Nature is healing.")
        return

    per_file: Dict[str, Dict[Key, RowInfo]] = {}
    all_keys: Set[Key] = set()
    any_duplicates: DefaultDict[Key, List[str]] = defaultdict(list)

    # Load and index each CSV by (Expectation, Case name)
    for filename in csv_files:
        path = os.path.join(directory_path, filename)
        idx, dups = load_csv_index(path)
        per_file[filename] = idx
        all_keys.update(idx.keys())
        for k in dups:
            any_duplicates[k].append(filename)

    # Warn about duplicates (they make comparisons ambiguous)
    if any_duplicates:
        print(
            "WARNING: Duplicate keys found (same Expectation + Case name) in these files:"
        )
        for (exp, case), files in any_duplicates.items():
            print(f"  ({exp!r}, {case!r}) -> {', '.join(files)}")
        print()

    # Sort keys for stable review order
    sorted_keys: List[Key] = sorted(all_keys, key=lambda k: (k[0], k[1]))

    for exp, case in sorted_keys:
        # Gather remarks for this key across files
        remarks: Dict[str, Optional[str]] = {}
        lines: Dict[str, Optional[int]] = {}

        for filename in csv_files:
            entry: Optional[RowInfo] = per_file[filename].get((exp, case))
            if entry is None:
                remarks[filename] = None  # missing test case in this file
                lines[filename] = None
            else:
                remarks[filename] = entry["remark"]
                lines[filename] = entry["line"]

        # Skip if ALL present remarks are empty AND no file is missing the key
        present_remarks: List[str] = [r for r in remarks.values() if r is not None]
        all_present_empty: bool = (
            all(r.strip() == "" for r in present_remarks) if present_remarks else True
        )
        any_missing: bool = any(r is None for r in remarks.values())

        if all_present_empty and not any_missing:
            continue

        print("\n" + "=" * 80)
        print(f"Expectation: {exp}")
        print(f"Case name : {case}")
        print("-" * 80)

        for filename in csv_files:
            r = remarks[filename]
            ln = lines[filename]
            if r is None:
                print(f"{filename} [MISSING]: (no such test case)")
            else:
                print(f"{filename} [line {ln}]:\t{r}")

        input("Press Enter to continue...")


if __name__ == "__main__":
    directory = "./gpt-5-2025-08-07/description_to_id_short/"
    compare_csv_directory(directory)
