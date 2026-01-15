"""Generate the minimal test examples for concept description determining value type."""

import json
import os
import pathlib
import sys
from typing import Sequence
import dataclasses

from aas_core3 import (
    types as aas_types,
    verification as aas_verification,
    jsonization as aas_jsonization,
)

import dev_scripts.generate_minimal_examples.common


@dataclasses.dataclass
class Case:
    """Represents a test case for concept description to description experiment."""

    category: dev_scripts.generate_minimal_examples.common.Category
    concept_description: str
    description: str
    identifier: str


def _generate_environment(
    concept_description: str, description: str
) -> aas_types.Environment:
    concept_description_id = "urn:exampl.com:someConceptDescription"

    environment = aas_types.Environment(
        submodels=[
            aas_types.Submodel(
                id="https://example.org/some_submodel",
                submodel_elements=[
                    aas_types.Property(
                        id_short="some_id_short",
                        description=[
                            aas_types.LangStringTextType(
                                language="en", text=description
                            )
                        ],
                        value_type=aas_types.DataTypeDefXSD.DOUBLE,
                        semantic_id=aas_types.Reference(
                            type=aas_types.ReferenceTypes.EXTERNAL_REFERENCE,
                            keys=[
                                aas_types.Key(
                                    type=aas_types.KeyTypes.GLOBAL_REFERENCE,
                                    value=concept_description_id,
                                )
                            ],
                        ),
                    )
                ],
            )
        ],
        concept_descriptions=[
            aas_types.ConceptDescription(
                id=concept_description_id,
                description=[
                    aas_types.LangStringTextType(
                        language="en", text=concept_description
                    )
                ],
            )
        ],
    )

    errors = list(aas_verification.verify(environment))
    assert len(errors) == 0, f"Unexpected {errors=}"

    return environment


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
        # ---
        # Semantic inversion
        Case(
            category="expected",
            concept_description="Upper water pressure limit",
            description="Maximum water pressure limit",
            identifier="no_semantic_inversion",
        ),
        # Similar wording, same meaning: both refer to the highest allowed pressure
        Case(
            category="unexpected",
            concept_description="Upper water pressure limit",
            description="Lower water pressure limit",
            identifier="semantic_inversion",
        ),
        #  Similar wording, but Inverted meaning: upper vs lower
        # ---
        # Paraphrase / Synonymy
        Case(
            category="expected",
            concept_description="Product activation start time in seconds since 1970-01-01 UTC",
            description="Product activation beginning time in seconds since 1970-01-01 UTC",
            identifier="paraphrase_synonymy",
        ),
        # Different wording, same meaning (synonymous paraphrase)
        Case(
            category="unexpected",
            concept_description="Product activation start time in seconds since 1970-01-01 UTC",
            description="Product activation end time in seconds since 1970-01-01 UTC",
            identifier="no_paraphrase_synonymy",
        ),
        # Different wording, different meaning (not a valid paraphrase)
        # ---
        # Partial overlap
        Case(
            category="expected",
            concept_description="Steel grade European Norm (EN) number",
            description="Steel grade (martensitic) European Norm (EN) number",
            identifier="no_partial_overlap",
        ),
        # `description` is a more specific instance of the `concept description`
        # `concept description` is a generalization => acceptable
        Case(
            category="unexpected",
            concept_description="Steel grade European Norm (EN) number",
            description="Steel alloy epoxy coating grade European Norm (EN) number",
            identifier="partial_overlap",
        ),
        # `description` is a not just a specific instance (not fully overlapping) of
        # the `concept description`, Paint type and steel grade are different attributes
        # ---
        # Contradiction / factual inconsistency
        Case(
            category="expected",
            concept_description="Waterproof enclosure length",
            description="Water-resistant housing length",
            identifier="no_contradiction",
        ),
        # No contradiction, consistent meaning; `description` does not
        # contradict `concept_description`
        Case(
            category="unexpected",
            concept_description="Waterproof enclosure length",
            description="Non watertight casing length",
            identifier="contradiction",
        ),
        # `description` contradicts `concept_description`
        # ---
        # Ambiguity
        Case(
            category="expected",
            concept_description="Rated DC input voltage",
            description="Direct current rated voltage input",
            identifier="no_ambiguity",
        ),
        # Clear and unambiguous
        Case(
            category="unexpected",
            concept_description="Rated DC input voltage",
            description="Voltage",
            identifier="ambiguity",
        ),
        # `description` is ambiguous (AC? DC? input? output?)
        # ---
        # Omission / missing info
        Case(
            category="expected",
            concept_description="Maximum ambient relative humidity at 25°C",
            description="Max relative humidity (25°C) of the near environment",
            identifier="no_omission",
        ),
        # Semantically equivalent
        Case(
            category="unexpected",
            concept_description="Maximum ambient relative humidity at 25°C",
            description="Max humidity",
            identifier="omission",
        ),
        # `description` omits critical info (ambient? relative? absolute?)
        # ---
        # Context-dependent interpretation / word sense disambiguation (WSD)
        Case(
            category="expected",
            concept_description="Hydraulic flow rate",
            description="Flow rate of the hydraulic fluid",
            identifier="no_context_words_sense_disambiguation",
        ),
        # Clear context, same meaning
        Case(
            category="unexpected",
            concept_description="Hydraulic flow rate",
            description="Flow rate",
            identifier="context_words_sense_disambiguation",
        ),
        # Ambiguous: could be air flow, water flow, etc., can only be interpreted in context
        # ---
        # Syntax
        Case(
            category="expected",
            concept_description="Maximum torque output",
            description="Peak torque delivered",
            identifier="no_syntax_error",
        ),
        # Well-formed syntax
        Case(
            category="unexpected",
            concept_description="Maximum Torque Output",
            description="Peaktorquedelivered",
            identifier="syntax_error",
        ),
        # Syntax issue: No spaces in `description`
        # ---
        # Terminology mismatch
        Case(
            category="expected",
            concept_description=(
                "Battery electromotive force (EMF) at 100 percent "
                "state of charge (SOC) at 25°C"
            ),
            description="EMF of the battery at 100 percent SOC (25°C)",
            identifier="no_terminology_mismatch",
        ),
        # Consistent terminology
        Case(
            category="unexpected",
            concept_description=(
                "Battery electromotive force (EMF) at 100 percent "
                "state of charge (SOC) at 25°C"
            ),
            description=(
                "Measured voltage of the battery with the "
                "rated load at 100 percent SOC (25°C)"
            ),
            identifier="terminology_mismatch",
        ),
        # Mismatch: EMF vs Measured voltage (rated load voltage)
        # ---
        # Negation mismatch
        Case(
            category="expected",
            concept_description=(
                "Maximum allowable corrosion rate; corrosion rate "
                "should be ≤ 0.10 mm/year"
            ),
            description=(
                "Max Corrosion rate (rates less than or "
                "equal 0.10 mm/year are allowed)"
            ),
            identifier="no_negation_mismatch",
        ),
        # No negation mismatch
        Case(
            category="unexpected",
            concept_description=(
                "Maximum allowable corrosion rate; corrosion rate "
                "should be ≤ 0.10 mm/year"
            ),
            description="Max Corrosion rate (> 0.10 mm/year is also allowed)",
            identifier="negation_mismatch",
        ),
        # `description` negates `concept_description`
        # ---
        # Uncommon phrasing / language quality
        Case(
            category="expected",
            concept_description="Nominal electric current",
            description="Nominal value for the electric current",
            identifier="no_uncommon_phrasing",
        ),
        # Normal, clear phrasing
        Case(
            category="unexpected",
            concept_description="Nominal electric current",
            description="Current electric nominal amps",
            identifier="uncommon_phrasing",
        ),
        # Awkward word order in `description`
    ]

    print("Generating test data for 'concept description to description'")
    for case in case_specs:
        path = (
            experiment_data_dir
            / "concept_description_to_description"
            / case.category
            / case.identifier
            / "model.json"
        )

        environment = _generate_environment(
            concept_description=case.concept_description, description=case.description
        )

        jsonable = aas_jsonization.to_jsonable(environment)
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(json.dumps(jsonable, indent=2), encoding="utf-8")
        print(f"Saved to: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
