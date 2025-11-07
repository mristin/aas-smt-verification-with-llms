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
    """Represents a test case for concept description to value type experiment."""

    category: dev_scripts.generate_minimal_examples.common.Category
    concept_description: str
    value_type: aas_types.DataTypeDefXSD
    identifier: str


def _generate_environment(
    concept_description: str, value_type: aas_types.DataTypeDefXSD
) -> aas_types.Environment:
    concept_description_id = "urn:exampl.com:someConceptDescription"

    environment = aas_types.Environment(
        submodels=[
            aas_types.Submodel(
                id="https://example.org/some_submodel",
                submodel_elements=[
                    aas_types.Property(
                        id_short="some_id_short",
                        value_type=value_type,
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
        Case(
            category="expected",
            concept_description="Name of the product",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="string_match",
        ),
        Case(
            category="expected",
            concept_description="Machine is operational status indicator",
            value_type=aas_types.DataTypeDefXSD.BOOLEAN,
            identifier="boolean_match",
        ),
        Case(
            category="expected",
            concept_description="Temperature reading in degrees Celsius",
            value_type=aas_types.DataTypeDefXSD.INT,
            identifier="int_match",
        ),
        Case(
            category="expected",
            concept_description="Extremely large number of molecules in sample",
            value_type=aas_types.DataTypeDefXSD.INTEGER,
            identifier="integer_match",
        ),
        Case(
            category="expected",
            concept_description="Nanoseconds since epoch timestamp",
            value_type=aas_types.DataTypeDefXSD.LONG,
            identifier="long_match",
        ),
        Case(
            category="expected",
            concept_description="Component count in assembly",
            value_type=aas_types.DataTypeDefXSD.SHORT,
            identifier="short_match",
        ),
        Case(
            category="expected",
            concept_description="Error code value between 0 and 255",
            value_type=aas_types.DataTypeDefXSD.BYTE,
            identifier="byte_match",
        ),
        Case(
            category="expected",
            concept_description="Age of equipment in years, starting from one",
            value_type=aas_types.DataTypeDefXSD.POSITIVE_INTEGER,
            identifier="positive_integer_match",
        ),
        Case(
            category="expected",
            concept_description="Remaining service life in years",
            value_type=aas_types.DataTypeDefXSD.NON_NEGATIVE_INTEGER,
            identifier="non_negative_integer_match",
        ),
        Case(
            category="expected",
            concept_description="Count down in milliseconds, always negative",
            value_type=aas_types.DataTypeDefXSD.NEGATIVE_INTEGER,
            identifier="negative_integer_match",
        ),
        Case(
            category="expected",
            concept_description="Altitude below sea level",
            value_type=aas_types.DataTypeDefXSD.NON_POSITIVE_INTEGER,
            identifier="non_positive_integer_match",
        ),
        Case(
            category="expected",
            concept_description="Revision number of firmware",
            value_type=aas_types.DataTypeDefXSD.UNSIGNED_INT,
            identifier="unsigned_int_match",
        ),
        Case(
            category="expected",
            concept_description="Duration in milliseconds",
            value_type=aas_types.DataTypeDefXSD.UNSIGNED_LONG,
            identifier="unsigned_long_match",
        ),
        Case(
            category="expected",
            concept_description="Protocol version number",
            value_type=aas_types.DataTypeDefXSD.UNSIGNED_SHORT,
            identifier="unsigned_short_match",
        ),
        Case(
            category="expected",
            concept_description="Status register byte",
            value_type=aas_types.DataTypeDefXSD.UNSIGNED_BYTE,
            identifier="unsigned_byte_match",
        ),
        Case(
            category="expected",
            concept_description="Temperature measurement in degrees Celsius",
            value_type=aas_types.DataTypeDefXSD.FLOAT,
            identifier="float_match",
        ),
        Case(
            category="expected",
            concept_description="Precision measurement of pressure in Pascal",
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
            identifier="double_match",
        ),
        Case(
            category="expected",
            concept_description="High-precision financial value with arbitrary decimal places",
            value_type=aas_types.DataTypeDefXSD.DECIMAL,
            identifier="decimal_match",
        ),
        Case(
            category="expected",
            concept_description="Manufacturing date of the component",
            value_type=aas_types.DataTypeDefXSD.DATE,
            identifier="date_match",
        ),
        Case(
            category="expected",
            concept_description="Last maintenance timestamp",
            value_type=aas_types.DataTypeDefXSD.DATE_TIME,
            identifier="date_time_match",
        ),
        Case(
            category="expected",
            concept_description="Daily operation start time",
            value_type=aas_types.DataTypeDefXSD.TIME,
            identifier="time_match",
        ),
        Case(
            category="expected",
            concept_description="Service interval duration",
            value_type=aas_types.DataTypeDefXSD.DURATION,
            identifier="duration_match",
        ),
        Case(
            category="expected",
            concept_description="Day of month for scheduled maintenance",
            value_type=aas_types.DataTypeDefXSD.G_DAY,
            identifier="g_day_match",
        ),
        Case(
            category="expected",
            concept_description="Month of annual inspection",
            value_type=aas_types.DataTypeDefXSD.G_MONTH,
            identifier="g_month_match",
        ),
        Case(
            category="expected",
            concept_description="Monthly inspection day",
            value_type=aas_types.DataTypeDefXSD.G_MONTH_DAY,
            identifier="g_month_day_match",
        ),
        Case(
            category="expected",
            concept_description="Year of initial commissioning",
            value_type=aas_types.DataTypeDefXSD.G_YEAR,
            identifier="g_year_match",
        ),
        Case(
            category="expected",
            concept_description="Month and year of warranty expiration",
            value_type=aas_types.DataTypeDefXSD.G_YEAR_MONTH,
            identifier="g_year_month_match",
        ),
        Case(
            category="expected",
            concept_description="Reference URL to technical documentation",
            value_type=aas_types.DataTypeDefXSD.ANY_URI,
            identifier="any_uri_match",
        ),
        Case(
            category="expected",
            concept_description="Cryptographic certificate in base64 format",
            value_type=aas_types.DataTypeDefXSD.BASE_64_BINARY,
            identifier="base_64_binary_match",
        ),
        Case(
            category="expected",
            concept_description="Device fingerprint as hexadecimal data",
            value_type=aas_types.DataTypeDefXSD.HEX_BINARY,
            identifier="hex_binary_match",
        ),
        Case(
            category="unexpected",
            concept_description=(
                "High-precision financial transaction amount with "
                "arbitrary decimal places"
            ),
            value_type=aas_types.DataTypeDefXSD.DOUBLE,
            identifier="numeric_precision_mismatch_double_instead_of_decimal",
        ),
        Case(
            category="unexpected",
            concept_description=(
                "Precise monetary value for accounting "
                "with exact decimal representation"
            ),
            value_type=aas_types.DataTypeDefXSD.FLOAT,
            identifier="numeric_precision_mismatch_float_instead_of_decimal",
        ),
        Case(
            category="unexpected",
            concept_description="High-frequency temperature sensor measurement",
            value_type=aas_types.DataTypeDefXSD.DECIMAL,
            identifier="numeric_precision_mismatch_decimal_instead_of_double",
        ),
        Case(
            category="unexpected",
            concept_description="High-precision scientific measurement requiring double precision",
            value_type=aas_types.DataTypeDefXSD.FLOAT,
            identifier="numeric_precision_mismatch_float_instead_of_double",
        ),
        # Domain mismatch: numeric instead of non-numeric types
        Case(
            category="unexpected",
            concept_description="Product name",
            value_type=aas_types.DataTypeDefXSD.LONG,
            identifier="domain_mismatch_numeric_instead_of_string",
        ),
        Case(
            category="unexpected",
            concept_description="Manufacturing date of component",
            value_type=aas_types.DataTypeDefXSD.LONG,
            identifier="domain_mismatch_numeric_instead_of_date",
        ),
        Case(
            category="unexpected",
            concept_description="System operational status indicator",
            value_type=aas_types.DataTypeDefXSD.LONG,
            identifier="domain_mismatch_numeric_instead_of_boolean",
        ),
        Case(
            category="unexpected",
            concept_description="Maintenance start time of day",
            value_type=aas_types.DataTypeDefXSD.LONG,
            identifier="domain_mismatch_numeric_instead_of_time",
        ),
        Case(
            category="unexpected",
            concept_description="Last maintenance timestamp",
            value_type=aas_types.DataTypeDefXSD.LONG,
            identifier="domain_mismatch_numeric_instead_of_date_time",
        ),
        Case(
            category="unexpected",
            concept_description="Service interval duration",
            value_type=aas_types.DataTypeDefXSD.LONG,
            identifier="domain_mismatch_numeric_instead_of_duration",
        ),
        Case(
            category="unexpected",
            concept_description="Documentation reference URL",
            value_type=aas_types.DataTypeDefXSD.LONG,
            identifier="domain_mismatch_numeric_instead_of_any_uri",
        ),
        Case(
            category="unexpected",
            concept_description="Cryptographic certificate in base64 format",
            value_type=aas_types.DataTypeDefXSD.LONG,
            identifier="domain_mismatch_numeric_instead_of_base_64_binary",
        ),
        Case(
            category="unexpected",
            concept_description="Device fingerprint as hexadecimal data",
            value_type=aas_types.DataTypeDefXSD.LONG,
            identifier="domain_mismatch_numeric_instead_of_hex_binary",
        ),
        # Domain mismatch: string instead of numeric types
        Case(
            category="unexpected",
            concept_description="Temperature measurement in degrees Celcius",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_int",
        ),
        Case(
            category="unexpected",
            concept_description="Large molecular count value",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_integer",
        ),
        Case(
            category="unexpected",
            concept_description="Timestamp in nanoseconds",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_long",
        ),
        Case(
            category="unexpected",
            concept_description="Component count in batch",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_short",
        ),
        Case(
            category="unexpected",
            concept_description="Error code between 0 and 255",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_byte",
        ),
        Case(
            category="unexpected",
            concept_description="Equipment age in years from one",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_positive_integer",
        ),
        Case(
            category="unexpected",
            concept_description="Service life remaining in years",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_non_negative_integer",
        ),
        Case(
            category="unexpected",
            concept_description="Temperature drop below reference",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_negative_integer",
        ),
        Case(
            category="unexpected",
            concept_description="Depth below sea level measurement",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_non_positive_integer",
        ),
        Case(
            category="unexpected",
            concept_description="Firmware revision number",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_unsigned_int",
        ),
        Case(
            category="unexpected",
            concept_description="Duration measurement in milliseconds",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_unsigned_long",
        ),
        Case(
            category="unexpected",
            concept_description="Protocol version identifier",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_unsigned_short",
        ),
        Case(
            category="unexpected",
            concept_description="Status register byte value",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_unsigned_byte",
        ),
        Case(
            category="unexpected",
            concept_description="Temperature reading in Celsius",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_float",
        ),
        Case(
            category="unexpected",
            concept_description="Precision pressure measurement in Pascal",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_double",
        ),
        Case(
            category="unexpected",
            concept_description="Financial amount with decimal precision",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="domain_mismatch_string_instead_of_decimal",
        ),
        # Imprecise string instead of specific non-numeric types
        Case(
            category="unexpected",
            concept_description="Machine is operational status indicator",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_boolean",
        ),
        Case(
            category="unexpected",
            concept_description="Component manufacturing date",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_date",
        ),
        Case(
            category="unexpected",
            concept_description="Last maintenance timestamp",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_date_time",
        ),
        Case(
            category="unexpected",
            concept_description="Daily operation start time",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_time",
        ),
        Case(
            category="unexpected",
            concept_description="Service interval duration",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_duration",
        ),
        Case(
            category="unexpected",
            concept_description="Day of month for maintenance",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_g_day",
        ),
        Case(
            category="unexpected",
            concept_description="Month of annual inspection",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_g_month",
        ),
        Case(
            category="unexpected",
            concept_description="Monthly inspection day",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_g_month_day",
        ),
        Case(
            category="unexpected",
            concept_description="Year of commissioning",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_g_year",
        ),
        Case(
            category="unexpected",
            concept_description="Quarter and year of warranty expiration",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_g_year_month",
        ),
        Case(
            category="unexpected",
            concept_description="Technical documentation URL",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_any_uri",
        ),
        Case(
            category="unexpected",
            concept_description="Base64 encoded certificate",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_base_64_binary",
        ),
        Case(
            category="unexpected",
            concept_description="Hexadecimal device fingerprint",
            value_type=aas_types.DataTypeDefXSD.STRING,
            identifier="imprecise_string_instead_of_hex_binary",
        ),
    ]

    for case in case_specs:
        path = (
            experiment_data_dir
            / "concept_description_to_value_type"
            / case.category
            / case.identifier
            / "model.json"
        )

        environment = _generate_environment(
            concept_description=case.concept_description, value_type=case.value_type
        )

        jsonable = aas_jsonization.to_jsonable(environment)
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(json.dumps(jsonable, indent=2), encoding="utf-8")
        print(f"Saved to: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
