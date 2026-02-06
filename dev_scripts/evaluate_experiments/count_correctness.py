"""
Script that does quantitative analysis on how many times the human experiment evaluations
agree with each other
"""

import os
import csv
from collections import defaultdict
from typing import DefaultDict, Dict, List, Set, Tuple, TypedDict


Key = Tuple[str, str]  # (Expectation, Case name)


class CountInfo(TypedDict):
    """
    Quick container for keeping track of various quantities
      - total cases
      - cases where all humans agree
      - cases where there is disagreement between human evaluators
    """

    total: int
    agreement: int
    disagreement: int


def load_csv_index_correct(path: str) -> tuple[Dict[Key, str], List[Key]]:
    """
    Create an index over all CSV files in the given directory
    """
    index: Dict[Key, str] = {}
    duplicates: List[Key] = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            exp: str = (row.get("Expectation") or "").strip()
            case: str = (row.get("Case name") or "").strip()
            key: Key = (exp, case)

            correct: str = (row.get("Correct") or "").strip().lower()

            if key in index:
                duplicates.append(key)
                continue

            index[key] = correct

    return index, duplicates


def count_correct_agreement(directory_path: str) -> None:
    """
    Counts various stats regarding the human evaluation and prints them out.
    """
    csv_files: List[str] = sorted(
        f for f in os.listdir(directory_path) if f.lower().endswith(".csv")
    )

    if not csv_files:
        print("No CSV files found. Consensus achieved through absence.")
        return

    per_file: Dict[str, Dict[Key, str]] = {}
    all_keys: Set[Key] = set()
    any_duplicates: DefaultDict[Key, List[str]] = defaultdict(list)

    for filename in csv_files:
        path = os.path.join(directory_path, filename)
        idx, dups = load_csv_index_correct(path)
        per_file[filename] = idx
        all_keys.update(idx.keys())
        for k in dups:
            any_duplicates[k].append(filename)

    if any_duplicates:
        print("WARNING: Duplicate keys found (same Expectation + Case name):")
        for (exp, case), files in any_duplicates.items():
            print(f"  ({exp!r}, {case!r}) -> {', '.join(files)}")
        print()

    counts: DefaultDict[str, CountInfo] = defaultdict(
        lambda: {"total": 0, "agreement": 0, "disagreement": 0}
    )

    overall_total: int = 0
    overall_agreement: int = 0

    for exp, case in all_keys:
        key: Key = (exp, case)
        counts[exp]["total"] += 1
        overall_total += 1

        values: List[str] = []
        missing: bool = False

        for filename in csv_files:
            if key not in per_file[filename]:
                missing = True
                break
            values.append(per_file[filename][key])

        if missing:
            counts[exp]["disagreement"] += 1
            continue

        if len(set(values)) == 1:
            counts[exp]["agreement"] += 1
            overall_agreement += 1
        else:
            counts[exp]["disagreement"] += 1

    print(f"\n\nExperiment: {directory_path}")
    for expectation in sorted(counts.keys()):
        total: int = counts[expectation]["total"]
        agreement: int = counts[expectation]["agreement"]

        ratio: float = round(agreement / total, 3) if total else 0.0

        print(f"Expectation: {expectation}")
        print(f"Total cases: {total}")
        print(f"Agreement: {agreement} cases")
        print(f"Disagreement: {counts[expectation]['disagreement']} cases")
        print(f"Agreement/total: {ratio}")
        print()

    overall_ratio: float = (
        round(overall_agreement / overall_total, 3) if overall_total else 0.0
    )

    print("Overall:")
    print(f"Total cases: {overall_total}")
    print(f"Total agreement: {overall_agreement}")
    print(f"Total agreement ratio: {overall_ratio}")
    print("-" * 80)


if __name__ == "__main__":
    directories: List[str] = [
        "../../experiment_evaluation/gpt-5-2025-08-07/concept_description_to_description/",
        "../../experiment_evaluation/gpt-5-2025-08-07/concept_description_to_unit/",
        "../../experiment_evaluation/gpt-5-2025-08-07/concept_description_to_value_type/",
        "../../experiment_evaluation/gpt-5-2025-08-07/description_to_display_name/",
        "../../experiment_evaluation/gpt-5-2025-08-07/description_to_id_short/",
    ]
    for directory in directories:
        count_correct_agreement(directory)
