"""Generate the minimal test examples for concept description determining unit."""

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
    """Represents a test case for concept description to unit experiment."""

    category: dev_scripts.generate_minimal_examples.common.Category
    preferred_name: str
    concept_description: str
    unit: str
    identifier: str


def _generate_environment(
    preferred_name: str, concept_description: str, unit: str
) -> aas_types.Environment:
    concept_description_id = "urn:exampl.com:someConceptDescription"

    environment = aas_types.Environment(
        submodels=[
            aas_types.Submodel(
                id="https://example.org/some_submodel",
                submodel_elements=[
                    aas_types.Property(
                        id_short="some_id_short",
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
                embedded_data_specifications=[
                    aas_types.EmbeddedDataSpecification(
                        data_specification=aas_types.Reference(
                            type=aas_types.ReferenceTypes.EXTERNAL_REFERENCE,
                            keys=[
                                aas_types.Key(
                                    type=aas_types.KeyTypes.GLOBAL_REFERENCE,
                                    value="urn:example.com:someDataSpecification",
                                )
                            ],
                        ),
                        data_specification_content=aas_types.DataSpecificationIEC61360(
                            preferred_name=[
                                aas_types.LangStringPreferredNameTypeIEC61360(
                                    language="en", text=preferred_name
                                )
                            ],
                            definition=[
                                aas_types.LangStringDefinitionTypeIEC61360(
                                    language="en", text=concept_description
                                )
                            ],
                            unit=unit,
                        ),
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
        # Expected cases: semantic match without unit in description
        Case(
            category="expected",
            preferred_name="operatingTemperature",
            concept_description="Operating temperature of the motor",
            unit="°C",
            identifier="semantic_match_without_unit_in_description_temperature",
        ),
        Case(
            category="expected",
            preferred_name="appliedForce",
            concept_description="Applied force on the mechanical component",
            unit="N",
            identifier="semantic_match_without_unit_in_description_force",
        ),
        Case(
            category="expected",
            preferred_name="operatingPressure",
            concept_description="System operating pressure",
            unit="Pa",
            identifier="semantic_match_without_unit_in_description_pressure",
        ),
        Case(
            category="expected",
            preferred_name="energyConsumption",
            concept_description="Energy consumption during operation",
            unit="J",
            identifier="semantic_match_without_unit_in_description_energy",
        ),
        Case(
            category="expected",
            preferred_name="powerConsumption",
            concept_description="Electrical power consumption",
            unit="W",
            identifier="semantic_match_without_unit_in_description_power",
        ),
        # Expected cases: semantic match scale invariant -- kilo prefix
        Case(
            category="expected",
            preferred_name="appliedForce",
            concept_description="Applied force on the mechanical component",
            unit="kN",
            identifier="semantic_match_scale_invariant_force_kilo",
        ),
        Case(
            category="expected",
            preferred_name="operatingPressure",
            concept_description="System operating pressure",
            unit="kPa",
            identifier="semantic_match_scale_invariant_pressure_kilo",
        ),
        Case(
            category="expected",
            preferred_name="energyConsumption",
            concept_description="Energy consumption during operation",
            unit="kJ",
            identifier="semantic_match_scale_invariant_energy_kilo",
        ),
        Case(
            category="expected",
            preferred_name="powerConsumption",
            concept_description="Electrical power consumption",
            unit="kW",
            identifier="semantic_match_scale_invariant_power_kilo",
        ),
        # Expected cases: semantic match scale invariant - milli prefix
        Case(
            category="expected",
            preferred_name="appliedForce",
            concept_description="Applied force on the mechanical component",
            unit="mN",
            identifier="semantic_match_scale_invariant_force_milli",
        ),
        Case(
            category="expected",
            preferred_name="energyConsumption",
            concept_description="Energy consumption during operation",
            unit="mJ",
            identifier="semantic_match_scale_invariant_energy_milli",
        ),
        Case(
            category="expected",
            preferred_name="powerConsumption",
            concept_description="Electrical power consumption",
            unit="mW",
            identifier="semantic_match_scale_invariant_power_milli",
        ),
        # Expected cases: semantic match with alternative units
        Case(
            category="expected",
            preferred_name="operatingTemperature",
            concept_description="Operating temperature of the motor",
            unit="°F",  # Fahrenheit (alternative to Celsius)
            identifier="semantic_match_temperature_alternative",
        ),
        Case(
            category="expected",
            preferred_name="appliedForce",
            concept_description="Applied force on the mechanical component",
            unit="lbf",  # Pound-force (alternative to Newton)
            identifier="semantic_match_force_alternative",
        ),
        Case(
            category="expected",
            preferred_name="operatingPressure",
            concept_description="System operating pressure",
            unit="psi",  # Pounds per square inch (alternative to Pascal)
            identifier="semantic_match_pressure_alternative",
        ),
        Case(
            category="expected",
            preferred_name="energyConsumption",
            concept_description="Energy consumption during operation",
            # Watt-hour (alternative to Joule, commonly used for electrical energy)
            unit="Wh",
            identifier="semantic_match_energy_alternative",
        ),
        Case(
            category="expected",
            preferred_name="powerConsumption",
            concept_description="Electrical power consumption",
            # Horsepower (alternative to Watt, commonly used for mechanical power)
            unit="hp",
            identifier="semantic_match_power_alternative",
        ),
        # Unexpected cases: semantic mismatch - completely wrong units
        Case(
            category="unexpected",
            preferred_name="operatingTemperature",
            concept_description="Operating temperature of the motor",
            unit="kg",  # Mass unit for temperature - completely wrong
            identifier="semantic_mismatch_temperature",
        ),
        Case(
            category="unexpected",
            preferred_name="appliedForce",
            concept_description="Applied force on the mechanical component",
            unit="°C",
            identifier="semantic_mismatch_force",
        ),
        Case(
            category="unexpected",
            preferred_name="operatingPressure",
            concept_description="System operating pressure",
            unit="Hz",
            identifier="semantic_mismatch_pressure",
        ),
        Case(
            category="unexpected",
            preferred_name="energyConsumption",
            concept_description="Energy consumption during operation",
            unit="m",
            identifier="semantic_mismatch_energy",
        ),
        Case(
            category="unexpected",
            preferred_name="powerConsumption",
            concept_description="Electrical power consumption",
            unit="V",
            identifier="semantic_mismatch_power",
        ),
        # Unexpected cases: alternative unit instead of unit mentioned in description
        Case(
            category="unexpected",
            preferred_name="operatingTemperature",
            concept_description="Operating temperature of the motor in °C",
            unit="°F",
            identifier="alternative_instead_unit_in_description_temperature",
        ),
        Case(
            category="unexpected",
            preferred_name="appliedForce",
            concept_description="Applied force on the mechanical component in N",
            unit="lbf",
            identifier="alternative_instead_unit_in_description_force",
        ),
        Case(
            category="unexpected",
            preferred_name="operatingPressure",
            concept_description="System operating pressure in Pa",
            unit="psi",
            identifier="alternative_instead_unit_in_description_pressure",
        ),
        Case(
            category="unexpected",
            preferred_name="energyConsumption",
            concept_description="Energy consumption during operation in J",
            unit="Wh",
            identifier="alternative_instead_unit_in_description_energy",
        ),
        Case(
            category="unexpected",
            preferred_name="powerConsumption",
            concept_description="Electrical power consumption in W",
            unit="hp",
            identifier="alternative_instead_unit_in_description_power",
        ),
        # Unexpected cases: scale mismatch - easily confused scales
        Case(
            category="unexpected",
            preferred_name="appliedForce",
            concept_description=(
                "Applied force on the mechanical component in millinewtons"
            ),
            unit="MN",
            identifier="scale_mismatch_force",
        ),
        Case(
            category="unexpected",
            preferred_name="operatingPressure",
            concept_description="System operating pressure in kilopascals",
            unit="GPa",
            identifier="scale_mismatch_pressure",
        ),
        Case(
            category="unexpected",
            preferred_name="energyConsumption",
            concept_description="Energy consumption during operation in millijoules",
            unit="MJ",
            identifier="scale_mismatch_energy",
        ),
        Case(
            category="unexpected",
            preferred_name="powerConsumption",
            concept_description="Electrical power consumption in milliwatts",
            unit="MW",
            identifier="scale_mismatch_power",
        ),
    ]

    for case in case_specs:
        path = (
            experiment_data_dir
            / "concept_description_to_unit"
            / case.category
            / case.identifier
            / "model.json"
        )

        environment = _generate_environment(
            preferred_name=case.preferred_name,
            concept_description=case.concept_description,
            unit=case.unit,
        )

        jsonable = aas_jsonization.to_jsonable(environment)
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(json.dumps(jsonable, indent=2), encoding="utf-8")
        print(f"Saved to: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
