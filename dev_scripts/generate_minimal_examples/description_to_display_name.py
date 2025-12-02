"""
This module generates the `experiment_data/description_to_display_name` (statically).

To run, you need the Eclipse BaSyx-Python SDK (`pip3 install basyx-python-sdk`)
"""

import os
import pathlib
import sys
from typing import Sequence, Optional
import dataclasses

from basyx.aas import model
from basyx.aas.adapter.json import json_serialization

import dev_scripts.generate_minimal_examples.common


@dataclasses.dataclass
class Case:
    """Represents a test example."""

    category: dev_scripts.generate_minimal_examples.common.Category
    description: str
    display_name: str
    identifier: str


def _generate_submodel(
    description: str, display_name: Optional[str], id_short: str
) -> model.Submodel:
    """
    Generate a minimal `Submodel` containing a `Property` with the given `description` and
    `display_name` inside its respective `MultiLanguage` objects.

    Note, that `Identifier` of the `Submodel` and `id_short` of the `Property` are fixed.
    """
    if display_name is None:
        display_name_mlp = None
    else:
        display_name_mlp = model.MultiLanguageNameType({"en": display_name})
    return model.Submodel(
        id_="https://example.org/some_submodel",
        submodel_element=[
            model.Property(
                id_short=id_short,
                value_type=model.datatypes.String,
                value="someString",
                display_name=display_name_mlp,
                description=model.MultiLanguageTextType({"en": description}),
            )
        ],
    )


def _to_snake_case(s: str) -> str:
    return s.replace(" ", "_").lower()


def main() -> int:
    """Execute the main routine."""
    repo_root = pathlib.Path(os.path.realpath(__file__)).parent.parent.parent
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
        ),
        # Similar wording, same meaning
        Case(
            category="unexpected",
            description="Permitted voltage",
            display_name="Maximum voltage",
            identifier="semantic_inversion",
        ),
        # Similar wording, but "permitted" = normal operating vs
        # "maximum" = absolute upper safety limit => not the same meaning.
        # Paraphrase / Synonymy
        Case(
            category="expected",
            description="Start time",
            display_name="Beginning time",
            identifier="no_paraphrase_synonymy",
        ),
        # Different wording, same meaning
        Case(
            category="unexpected",
            description="Start time",
            display_name="End time",
            identifier="paraphrase_synonymy",
        ),
        # Different wording, different meaning
        # Partial overlap
        Case(
            category="expected",
            description="Material (steel alloy)",
            display_name="Material",
            identifier="no_partial_overlap",
        ),
        # `description` is a more specific instance of the `display_name`
        # => Correct, but different level of detail
        Case(
            category="unexpected",
            description="Surface coating (steel alloy)",
            display_name="Material",
            identifier="partial_overlap",
        ),
        # `description` is not just a more detailed version of the `display_name`.
        # Contradiction / factual inconsistency
        Case(
            category="expected",
            description="Suitable for indoor use",
            display_name="For indoor environments",
            identifier="no_contradiction",
        ),
        # `description` does not contradict `display_name`
        Case(
            category="unexpected",
            description="Suitable for indoor use",
            display_name="For outdoor environments",
            identifier="contradiction",
        ),
        # `description` contradicts `display_name`
        # Ambiguity
        Case(
            category="expected",
            description="Electrical input power",
            display_name="Power consumption",
            identifier="no_ambiguity",
        ),
        # No ambiguity
        Case(
            category="unexpected",
            description="Power",
            display_name="Rated power",
            identifier="ambiguity",
        ),
        # Could be electrical? mechanical? thermal? -> not enough context to know
        # Omission / missing info
        Case(
            category="expected",
            description="Operating temperature range",
            display_name="Operating temperature",
            identifier="no_omission",
        ),
        # Semantically still the same
        Case(
            category="unexpected",
            description="Operating temperature",
            display_name="Temperature",
            identifier="omission",
        ),
        # `display_name` "Temperature" is too vague, could be anything
        # Context-dependent interpretation / words sense disambiguation (WSD)
        Case(
            category="expected",
            description="Mechanical output power",
            display_name="Mechanical power",
            identifier="context_words_sense_disambiguation",
        ),
        # Semantically still the same
        Case(
            category="unexpected",
            description="Mechanical Power",
            display_name="Power",
            identifier="context_words_sense_disambiguation",
        ),
        # `display_name` can only be interpreted in context (could be electrical,
        # thermal, hydraulic)
        # Syntax
        Case(
            category="expected",
            description="Nominal shaft speed",
            display_name="Nominal shaft speed",
            identifier="syntax",
        ),
        # No syntax error
        Case(
            category="unexpected",
            description="Nominalshaftspeed",
            display_name="Nominal shaft speed",
            identifier="syntax",
        ),
        # No spaces in `description`
        # Terminology mismatch
        Case(
            category="expected",
            description="Shaft diameter",
            display_name="Shaft diameter",
            identifier="no_terminology_mismatch",
        ),
        # No mismatch
        Case(
            category="unexpected",
            description="Shaft diameter",
            display_name="Axle length",
            identifier="terminology_mismatch",
        ),
        # Sounds related, but diameter != length
        # Negation mismatch
        Case(
            category="expected",
            description="Suitable for wet environments",
            display_name="Compatible with wet environments",
            identifier="no_negation_mismatch",
        ),
        # No mismatch
        Case(
            category="unexpected",
            description="Do not operate in wet conditions",
            display_name="Suitable for wet environments",
            identifier="negation_mismatch",
        ),
        # `display_name` is negation of `description`
        # Uncommon phrasing / language quality
        Case(
            category="expected",
            description="Weight",
            display_name="Weight",
            identifier="no_uncommon_phrasing",
        ),
        # Normal terms used
        Case(
            category="unexpected",
            description="Weight heavy",
            display_name="Heaviness",
            identifier="uncommon_phrasing",
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

        # Create the experiment data
        submodel = _generate_submodel(
            case.description, case.display_name, "some_id_short"
        )

        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write the AAS JSON file
        with open(path, "w", encoding="utf-8") as file:
            json_serialization.write_aas_json_file(
                file, model.DictObjectStore([submodel]), indent=4
            )
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

        # Create the experiment data
        submodel = _generate_submodel(
            case.description, None, _to_snake_case(case.display_name)
        )

        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write the AAS JSON file
        with open(path, "w", encoding="utf-8") as file:
            json_serialization.write_aas_json_file(
                file, model.DictObjectStore([submodel]), indent=4
            )
        print(f"Saved to: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
