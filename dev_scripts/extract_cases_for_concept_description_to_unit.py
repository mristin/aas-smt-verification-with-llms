"""Extract concept descriptions with units from real IDTA submodel templates."""

import dataclasses
import json
import os.path
import pathlib
import random
import sys
from typing import List, Tuple, Dict

from aas_core3 import (
    types as aas_types,
    jsonization as aas_jsonization,
)
from aas_core3.types import EmbeddedDataSpecification

from aas_smt_verification_with_llms import aasing
from aas_smt_verification_with_llms.common import Filenameable


@dataclasses.dataclass(frozen=True)
class RelevantParts:
    """Capture the relevant part of a concept description related to the unit."""

    template_name: str
    preferred_name: str
    definition: str
    unit: str


@dataclasses.dataclass(frozen=True)
class Case:
    """Structure the test case file."""

    name: Filenameable
    environment: aas_types.Environment
    expected: bool


def _is_same_or_scaled_unit(that: str, other: str) -> bool:
    """
    Check whether ``that`` and ``other`` are the same or scaled units.

    That is, we check whether they represent the same unit or the same unit differing
    only by an SI magnitude prefix (*e.g.*, ``m`` for milli or ``k`` for kilo).

    >>> _is_same_or_scaled_unit('mm', 'mm')
    True

    It is case-insensitive:
    >>> _is_same_or_scaled_unit('mm', 'MM')
    True

    Meter and milimeter differ only in scale:
    >>> _is_same_or_scaled_unit('mm', 'm')
    True

    Meter and centimeter differ only in scale:
    >>> _is_same_or_scaled_unit('mm', 'cm')
    True

    >>> _is_same_or_scaled_unit('mm', 'Pa')
    False
    """
    that = that.lower()
    other = other.lower()
    if that == other:
        return True

    for prefix in ("m", "c", "k"):
        if f"{prefix}{that}" == other or that == f"{prefix}{other}":
            return True

    return False


def _unit_definition_to_environment(
    unit: str, definition: str
) -> aas_types.Environment:
    return aas_types.Environment(
        concept_descriptions=[
            aas_types.ConceptDescription(
                id="urn:someConceptDescription",
                description=[
                    aas_types.LangStringTextType(language="en", text=definition)
                ],
                embedded_data_specifications=[
                    EmbeddedDataSpecification(
                        data_specification=aas_types.Reference(
                            type=aas_types.ReferenceTypes.EXTERNAL_REFERENCE,
                            keys=[
                                aas_types.Key(
                                    type=aas_types.KeyTypes.GLOBAL_REFERENCE,
                                    value="urn:someDataSpecification",
                                )
                            ],
                        ),
                        data_specification_content=aas_types.DataSpecificationIEC61360(
                            preferred_name=[
                                aas_types.LangStringPreferredNameTypeIEC61360(
                                    language="en", text="something"
                                )
                            ],
                            unit=unit,
                            definition=[
                                aas_types.LangStringDefinitionTypeIEC61360(
                                    language="en", text=definition
                                )
                            ],
                        ),
                    )
                ],
            )
        ]
    )


def main() -> int:
    """Execute the main routine."""
    repo_root = pathlib.Path(os.path.realpath(__file__)).parent.parent

    submodel_templates_dir = repo_root / "idta_submodel_templates" / "templates"

    cases = []  # type: List[Case]

    for template_path in sorted(submodel_templates_dir.glob("*.json")):
        jsonable = json.loads(template_path.read_text(encoding="utf-8"))
        try:
            environment = aas_jsonization.environment_from_jsonable(jsonable)
        except aas_jsonization.DeserializationException as exception:
            print(f"Failed to de-serialize {template_path}: {exception}, skipping")
            continue

        relevant_parts_by_definition_unit = (
            dict()
        )  # type: Dict[Tuple[str, str], RelevantParts]

        for cd in environment.over_concept_descriptions_or_empty():
            description_in_en = aasing.text_in_english(cd.description)

            for eds in cd.over_embedded_data_specifications_or_empty():
                content = eds.data_specification_content
                if isinstance(content, aas_types.DataSpecificationIEC61360):
                    preferred_name = aasing.text_in_english(content.preferred_name)
                    definition_in_en = aasing.text_in_english(content.definition)
                    unit = content.unit

                    if (
                        preferred_name is not None
                        and definition_in_en is not None
                        and unit is not None
                        and len(unit) > 0
                    ):
                        if (
                            description_in_en is not None
                            and description_in_en != definition_in_en
                        ):
                            raise AssertionError(
                                f"Unexpected differing Concept Description and "
                                f"Embedded Data Specification definition: "
                                f"{description_in_en} and {definition_in_en}"
                            )

                        unit = unit.strip()
                        definition_in_en = definition_in_en.strip()

                        definition_unit = (definition_in_en, unit)

                        if definition_unit not in relevant_parts_by_definition_unit:
                            relevant_parts_by_definition_unit[definition_unit] = (
                                RelevantParts(
                                    template_name=template_path.stem,
                                    preferred_name=preferred_name,
                                    definition=definition_in_en,
                                    unit=unit,
                                )
                            )

        if len(relevant_parts_by_definition_unit) == 0:
            print(f"No units found in: {template_path}, skipping.")
            continue

        list_of_units = sorted(
            set(unit for definition, unit in relevant_parts_by_definition_unit).union(
                [
                    "m",
                    "kg",
                    "s",
                    "A",
                    "K",
                    "mol",
                    "cd",
                    "Hz",
                    "N",
                    "Pa",
                    "J",
                    "W",
                    "C",
                    "V",
                    "F",
                    "S",
                    "Wb",
                    "T",
                    "H",
                    "lm",
                    "lx",
                    "Bq",
                    "Gy",
                    "Sv",
                    "kat",
                ]
            )
        )

        for definition_unit in sorted(relevant_parts_by_definition_unit.keys()):
            rp = relevant_parts_by_definition_unit[definition_unit]

            cases.append(
                Case(
                    name=Filenameable(
                        (
                            f"{rp.template_name}"
                            f"_{rp.preferred_name}"
                            f"_{rp.unit}_real"
                        ).replace("/", "_per_")
                    ),
                    environment=_unit_definition_to_environment(
                        unit=rp.unit, definition=rp.definition
                    ),
                    expected=True,
                )
            )

            confusing_units = [
                unit
                for unit in list_of_units
                if not _is_same_or_scaled_unit(rp.unit, unit)
            ]

            if len(confusing_units) == 0:
                raise AssertionError(f"No confusing units found for: {rp}")

            confusing_unit = random.choice(confusing_units)

            cases.append(
                Case(
                    name=Filenameable(
                        (
                            f"{rp.template_name}"
                            f"_{rp.preferred_name}"
                            f"_{confusing_unit}_synthetic"
                        ).replace("/", "_per_")
                    ),
                    environment=_unit_definition_to_environment(
                        unit=confusing_unit, definition=rp.definition
                    ),
                    expected=False,
                )
            )

    concept_description_to_unit_dir = (
        repo_root / "experiment_data" / "concept_description_to_unit"
    )

    for case in cases:
        jsonable = aas_jsonization.to_jsonable(case.environment)

        expected_or_unexpected = "expected" if case.expected else "unexpected"

        case_path = (
            concept_description_to_unit_dir
            / expected_or_unexpected
            / case.name
            / "model.json"
        )
        case_path.parent.mkdir(exist_ok=True, parents=True)

        case_path.write_text(json.dumps(jsonable, indent=2), encoding="utf-8")
        print(f"Written to: {case_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
