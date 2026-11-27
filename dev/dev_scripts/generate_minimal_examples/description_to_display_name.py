# SPDX-FileCopyrightText: 2025 aas-smt-verification-with-llms AUTHORS
#
# SPDX-License-Identifier: MIT

"""
Generate ``experiment_data/description_to_display_name`` and
``experiment_data/description_to_id_short`` (statically).
"""

import dataclasses
import json
import os
import pathlib
import sys
from typing import Optional, Sequence

from aas_core3 import (
    jsonization as aas_jsonization,
    types as aas_types,
    verification as aas_verification,
)

import dev_scripts.generate_minimal_examples.common


@dataclasses.dataclass
class Case:
    """Represents a test example."""

    category: dev_scripts.generate_minimal_examples.common.Category
    description: str
    display_name: str
    identifier: str
    value_type: aas_types.DataTypeDefXSD


def _generate_environment(
    description: str,
    display_name: Optional[str],
    id_short: str,
    value_type: aas_types.DataTypeDefXSD,
) -> aas_types.Environment:
    """
    Generate a minimal environment with a submodel containing a single property.

    The property carries the given ``description`` and ``display_name`` in English.
    The ID of the submodel is fixed.
    """
    environment = aas_types.Environment(
        submodels=[
            aas_types.Submodel(
                id="https://example.org/some_submodel",
                submodel_elements=[
                    aas_types.Property(
                        id_short=id_short,
                        display_name=(
                            [
                                aas_types.LangStringNameType(
                                    language="en", text=display_name
                                )
                            ]
                            if display_name is not None
                            else None
                        ),
                        description=[
                            aas_types.LangStringTextType(
                                language="en", text=description
                            )
                        ],
                        value_type=value_type,
                    )
                ],
            )
        ]
    )

    errors = list(aas_verification.verify(environment))
    assert len(errors) == 0, f"Unexpected {errors=}"

    return environment


def _to_snake_case(s: str) -> str:
    return s.replace(" ", "_").lower()


def main() -> int:
    """Execute the main routine."""
    repo_root = pathlib.Path(os.path.realpath(__file__)).parent.parent.parent.parent
    experiment_data_dir = repo_root / "experiment_data"
    if not experiment_data_dir.exists():
        print(
            f"Experiment data directory does not exist: {experiment_data_dir}",
            file=sys.stderr,
        )
        return 1

    case_specs: Sequence[Case] = [
        # Semantic inversion
        Case(
            category="expected",
            description="Permitted voltage",
            display_name="Allowed voltage",
            identifier="semantic_inversion",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # Similar wording, same meaning
        Case(
            category="unexpected",
            description="Permitted voltage",
            display_name="Maximum voltage",
            identifier="semantic_inversion",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # Similar wording, but "permitted" = normal operating vs
        # "maximum" = absolute upper safety limit => not the same meaning.
        # Paraphrase / Synonymy
        Case(
            category="expected",
            description="Start time",
            display_name="Beginning time",
            identifier="no_paraphrase_synonymy",
            value_type=aas_types.DataTypeDefXSD.DATE_TIME,
        ),
        # Different wording, same meaning
        Case(
            category="unexpected",
            description="Start time",
            display_name="End time",
            identifier="paraphrase_synonymy",
            value_type=aas_types.DataTypeDefXSD.DATE_TIME,
        ),
        # Different wording, different meaning
        # Partial overlap
        Case(
            category="expected",
            description="Material (steel alloy)",
            display_name="Material",
            identifier="no_partial_overlap",
            value_type=aas_types.DataTypeDefXSD.STRING,
        ),
        # `description` is a more specific instance of the `display_name`
        # => Correct, but different level of detail
        Case(
            category="unexpected",
            description="Surface coating (steel alloy)",
            display_name="Material",
            identifier="partial_overlap",
            value_type=aas_types.DataTypeDefXSD.STRING,
        ),
        # `description` is not just a more detailed version of the `display_name`.
        # Contradiction / factual inconsistency
        Case(
            category="expected",
            description="Suitable for indoor use",
            display_name="For indoor environments",
            identifier="no_contradiction",
            value_type=aas_types.DataTypeDefXSD.BOOLEAN,
        ),
        # `description` does not contradict `display_name`
        Case(
            category="unexpected",
            description="Suitable for indoor use",
            display_name="For outdoor environments",
            identifier="contradiction",
            value_type=aas_types.DataTypeDefXSD.BOOLEAN,
        ),
        # `description` contradicts `display_name`
        # Ambiguity
        Case(
            category="expected",
            description="Electrical input power",
            display_name="Power consumption",
            identifier="no_ambiguity",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # No ambiguity
        Case(
            category="unexpected",
            description="Power",
            display_name="Rated power",
            identifier="ambiguity",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # Could be electrical? mechanical? thermal? -> not enough context to know
        # Omission / missing info
        Case(
            category="expected",
            description="Operating temperature range",
            display_name="Operating temperature",
            identifier="no_omission",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # Semantically still the same
        Case(
            category="unexpected",
            description="Operating temperature",
            display_name="Temperature",
            identifier="omission",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # `display_name` "Temperature" is too vague, could be anything
        # Context-dependent interpretation / words sense disambiguation (WSD)
        Case(
            category="expected",
            description="Mechanical output power",
            display_name="Mechanical power",
            identifier="context_words_sense_disambiguation",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # Semantically still the same
        Case(
            category="unexpected",
            description="Mechanical Power",
            display_name="Power",
            identifier="context_words_sense_disambiguation",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # `display_name` can only be interpreted in context (could be electrical,
        # thermal, hydraulic)
        # Syntax
        Case(
            category="expected",
            description="Nominal shaft speed",
            display_name="Nominal shaft speed",
            identifier="syntax",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # No syntax error
        Case(
            category="unexpected",
            description="Nominalshaftspeed",
            display_name="Nominal shaft speed",
            identifier="syntax",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # No spaces in `description`
        # Terminology mismatch
        Case(
            category="expected",
            description="Shaft diameter",
            display_name="Shaft diameter",
            identifier="no_terminology_mismatch",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # No mismatch
        Case(
            category="unexpected",
            description="Shaft diameter",
            display_name="Axle length",
            identifier="terminology_mismatch",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # Sounds related, but diameter != length
        # Negation mismatch
        Case(
            category="expected",
            description="Suitable for wet environments",
            display_name="Compatible with wet environments",
            identifier="no_negation_mismatch",
            value_type=aas_types.DataTypeDefXSD.BOOLEAN,
        ),
        # No mismatch
        Case(
            category="unexpected",
            description="Do not operate in wet conditions",
            display_name="Suitable for wet environments",
            identifier="negation_mismatch",
            value_type=aas_types.DataTypeDefXSD.BOOLEAN,
        ),
        # `display_name` is negation of `description`
        # Uncommon phrasing / language quality
        Case(
            category="expected",
            description="Weight",
            display_name="Weight",
            identifier="no_uncommon_phrasing",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # Normal terms used
        Case(
            category="unexpected",
            description="Weight heavy",
            display_name="Heaviness",
            identifier="uncommon_phrasing",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
        ),
        # Kind of intelligible by a human, but weird
    ]

    print("Generating test data for 'description to display name'")
    for case in case_specs:
        path = (
            experiment_data_dir
            / "description_to_display_name"
            / case.category
            / case.identifier
            / "model.json"
        )

        environment = _generate_environment(
            case.description, case.display_name, "some_id_short", case.value_type
        )

        jsonable = aas_jsonization.to_jsonable(environment)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(jsonable, indent=4), encoding="utf-8")
        print(f"Saved to: {path}")

    print("Generating test data for 'description to idShort'")
    for case in case_specs:
        path = (
            experiment_data_dir
            / "description_to_id_short"
            / case.category
            / case.identifier
            / "model.json"
        )

        environment = _generate_environment(
            case.description, None, _to_snake_case(case.display_name), case.value_type
        )

        jsonable = aas_jsonization.to_jsonable(environment)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(jsonable, indent=4), encoding="utf-8")
        print(f"Saved to: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
