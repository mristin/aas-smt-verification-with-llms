"""Generate the minimal test examples for concept description determining value type."""

import json
import os
import pathlib
import sys
from typing import Sequence, Tuple, Literal, Union

from aas_core3 import (
    types as aas_types,
    verification as aas_verification,
    jsonization as aas_jsonization,
)


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


Category = Union[Literal["expected"] | Literal["unexpected"]]


def main() -> int:
    """Execute the main routine."""
    repo_root = pathlib.Path(os.path.realpath(__file__)).parent.parent
    experiment_data_dir = repo_root / "experiment_data"
    if not experiment_data_dir.exists():
        print(
            f"Experiment data directory does not exist: {experiment_data_dir}",
            file=sys.stderr,
        )
        return 1

    case_specs: Sequence[Tuple[Category, str, aas_types.DataTypeDefXSD, str]] = [
        (
            "expected",
            "Name of the product",
            aas_types.DataTypeDefXSD.STRING,
            "string_match",
        ),
        (
            "expected",
            "Machine is operational status indicator",
            aas_types.DataTypeDefXSD.BOOLEAN,
            "boolean_match",
        ),
        (
            "expected",
            "Temperature reading in degrees Celsius",
            aas_types.DataTypeDefXSD.INT,
            "int_match",
        ),
        (
            "expected",
            "Extremely large number of molecules in sample",
            aas_types.DataTypeDefXSD.INTEGER,
            "integer_match",
        ),
        (
            "expected",
            "Nanoseconds since epoch timestamp",
            aas_types.DataTypeDefXSD.LONG,
            "long_match",
        ),
        (
            "expected",
            "Component count in assembly",
            aas_types.DataTypeDefXSD.SHORT,
            "short_match",
        ),
        (
            "expected",
            "Error code value between 0 and 255",
            aas_types.DataTypeDefXSD.BYTE,
            "byte_match",
        ),
        (
            "expected",
            "Age of equipment in years, starting from one",
            aas_types.DataTypeDefXSD.POSITIVE_INTEGER,
            "positive_integer_match",
        ),
        (
            "expected",
            "Remaining service life in years",
            aas_types.DataTypeDefXSD.NON_NEGATIVE_INTEGER,
            "non_negative_integer_match",
        ),
        (
            "expected",
            "Count down in milliseconds, always negative",
            aas_types.DataTypeDefXSD.NEGATIVE_INTEGER,
            "negative_integer_match",
        ),
        (
            "expected",
            "Altitude below sea level",
            aas_types.DataTypeDefXSD.NON_POSITIVE_INTEGER,
            "non_positive_integer_match",
        ),
        (
            "expected",
            "Revision number of firmware",
            aas_types.DataTypeDefXSD.UNSIGNED_INT,
            "unsigned_int_match",
        ),
        (
            "expected",
            "Duration in milliseconds",
            aas_types.DataTypeDefXSD.UNSIGNED_LONG,
            "unsigned_long_match",
        ),
        (
            "expected",
            "Protocol version number",
            aas_types.DataTypeDefXSD.UNSIGNED_SHORT,
            "unsigned_short_match",
        ),
        (
            "expected",
            "Status register byte",
            aas_types.DataTypeDefXSD.UNSIGNED_BYTE,
            "unsigned_byte_match",
        ),
        (
            "expected",
            "Temperature measurement in degrees Celsius",
            aas_types.DataTypeDefXSD.FLOAT,
            "float_match",
        ),
        (
            "expected",
            "Precision measurement of pressure in Pascal",
            aas_types.DataTypeDefXSD.DOUBLE,
            "double_match",
        ),
        (
            "expected",
            "High-precision financial value with arbitrary decimal places",
            aas_types.DataTypeDefXSD.DECIMAL,
            "decimal_match",
        ),
        (
            "expected",
            "Manufacturing date of the component",
            aas_types.DataTypeDefXSD.DATE,
            "date_match",
        ),
        (
            "expected",
            "Last maintenance timestamp",
            aas_types.DataTypeDefXSD.DATE_TIME,
            "date_time_match",
        ),
        (
            "expected",
            "Daily operation start time",
            aas_types.DataTypeDefXSD.TIME,
            "time_match",
        ),
        (
            "expected",
            "Service interval duration",
            aas_types.DataTypeDefXSD.DURATION,
            "duration_match",
        ),
        (
            "expected",
            "Day of month for scheduled maintenance",
            aas_types.DataTypeDefXSD.G_DAY,
            "g_day_match",
        ),
        (
            "expected",
            "Month of annual inspection",
            aas_types.DataTypeDefXSD.G_MONTH,
            "g_month_match",
        ),
        (
            "expected",
            "Monthly inspection day",
            aas_types.DataTypeDefXSD.G_MONTH_DAY,
            "g_month_day_match",
        ),
        (
            "expected",
            "Year of initial commissioning",
            aas_types.DataTypeDefXSD.G_YEAR,
            "g_year_match",
        ),
        (
            "expected",
            "Month and year of warranty expiration",
            aas_types.DataTypeDefXSD.G_YEAR_MONTH,
            "g_year_month_match",
        ),
        (
            "expected",
            "Reference URL to technical documentation",
            aas_types.DataTypeDefXSD.ANY_URI,
            "any_uri_match",
        ),
        (
            "expected",
            "Cryptographic certificate in base64 format",
            aas_types.DataTypeDefXSD.BASE_64_BINARY,
            "base_64_binary_match",
        ),
        (
            "expected",
            "Device fingerprint as hexadecimal data",
            aas_types.DataTypeDefXSD.HEX_BINARY,
            "hex_binary_match",
        ),
        (
            "unexpected",
            "High-precision financial transaction amount with arbitrary decimal places",
            aas_types.DataTypeDefXSD.DOUBLE,
            "numeric_precision_mismatch_double_instead_of_decimal",
        ),
        (
            "unexpected",
            "Precise monetary value for accounting with exact decimal representation",
            aas_types.DataTypeDefXSD.FLOAT,
            "numeric_precision_mismatch_float_instead_of_decimal",
        ),
        (
            "unexpected",
            "High-frequency temperature sensor measurement",
            aas_types.DataTypeDefXSD.DECIMAL,
            "numeric_precision_mismatch_decimal_instead_of_double",
        ),
        (
            "unexpected",
            "High-precision scientific measurement requiring double precision",
            aas_types.DataTypeDefXSD.FLOAT,
            "numeric_precision_mismatch_float_instead_of_double",
        ),
        # Domain mismatch: numeric instead of non-numeric types
        (
            "unexpected",
            "Product name",
            aas_types.DataTypeDefXSD.LONG,
            "domain_mismatch_numeric_instead_of_string",
        ),
        (
            "unexpected",
            "Manufacturing date of component",
            aas_types.DataTypeDefXSD.LONG,
            "domain_mismatch_numeric_instead_of_date",
        ),
        (
            "unexpected",
            "System operational status indicator",
            aas_types.DataTypeDefXSD.LONG,
            "domain_mismatch_numeric_instead_of_boolean",
        ),
        (
            "unexpected",
            "Maintenance start time of day",
            aas_types.DataTypeDefXSD.LONG,
            "domain_mismatch_numeric_instead_of_time",
        ),
        (
            "unexpected",
            "Last maintenance timestamp",
            aas_types.DataTypeDefXSD.LONG,
            "domain_mismatch_numeric_instead_of_date_time",
        ),
        (
            "unexpected",
            "Service interval duration",
            aas_types.DataTypeDefXSD.LONG,
            "domain_mismatch_numeric_instead_of_duration",
        ),
        (
            "unexpected",
            "Documentation reference URL",
            aas_types.DataTypeDefXSD.LONG,
            "domain_mismatch_numeric_instead_of_any_uri",
        ),
        (
            "unexpected",
            "Cryptographic certificate in base64 format",
            aas_types.DataTypeDefXSD.LONG,
            "domain_mismatch_numeric_instead_of_base_64_binary",
        ),
        (
            "unexpected",
            "Device fingerprint as hexadecimal data",
            aas_types.DataTypeDefXSD.LONG,
            "domain_mismatch_numeric_instead_of_hex_binary",
        ),
        # Domain mismatch: string instead of numeric types
        (
            "unexpected",
            "Temperature measurement in degrees Celcius",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_int",
        ),
        (
            "unexpected",
            "Large molecular count value",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_integer",
        ),
        (
            "unexpected",
            "Timestamp in nanoseconds",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_long",
        ),
        (
            "unexpected",
            "Component count in batch",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_short",
        ),
        (
            "unexpected",
            "Error code between 0 and 255",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_byte",
        ),
        (
            "unexpected",
            "Equipment age in years from one",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_positive_integer",
        ),
        (
            "unexpected",
            "Service life remaining in years",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_non_negative_integer",
        ),
        (
            "unexpected",
            "Temperature drop below reference",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_negative_integer",
        ),
        (
            "unexpected",
            "Depth below sea level measurement",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_non_positive_integer",
        ),
        (
            "unexpected",
            "Firmware revision number",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_unsigned_int",
        ),
        (
            "unexpected",
            "Duration measurement in milliseconds",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_unsigned_long",
        ),
        (
            "unexpected",
            "Protocol version identifier",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_unsigned_short",
        ),
        (
            "unexpected",
            "Status register byte value",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_unsigned_byte",
        ),
        (
            "unexpected",
            "Temperature reading in Celsius",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_float",
        ),
        (
            "unexpected",
            "Precision pressure measurement in Pascal",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_double",
        ),
        (
            "unexpected",
            "Financial amount with decimal precision",
            aas_types.DataTypeDefXSD.STRING,
            "domain_mismatch_string_instead_of_decimal",
        ),
        # Imprecise string instead of specific non-numeric types
        (
            "unexpected",
            "Machine is operational status indicator",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_boolean",
        ),
        (
            "unexpected",
            "Component manufacturing date",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_date",
        ),
        (
            "unexpected",
            "Last maintenance timestamp",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_date_time",
        ),
        (
            "unexpected",
            "Daily operation start time",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_time",
        ),
        (
            "unexpected",
            "Service interval duration",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_duration",
        ),
        (
            "unexpected",
            "Day of month for maintenance",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_g_day",
        ),
        (
            "unexpected",
            "Month of annual inspection",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_g_month",
        ),
        (
            "unexpected",
            "Monthly inspection day",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_g_month_day",
        ),
        (
            "unexpected",
            "Year of commissioning",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_g_year",
        ),
        (
            "unexpected",
            "Quarter and year of warranty expiration",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_g_year_month",
        ),
        (
            "unexpected",
            "Technical documentation URL",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_any_uri",
        ),
        (
            "unexpected",
            "Base64 encoded certificate",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_base_64_binary",
        ),
        (
            "unexpected",
            "Hexadecimal device fingerprint",
            aas_types.DataTypeDefXSD.STRING,
            "imprecise_string_instead_of_hex_binary",
        ),
    ]

    for category, concept_description, value_type, identifier in case_specs:
        path = (
            experiment_data_dir
            / "concept_description_to_value_type"
            / category
            / identifier
            / "model.json"
        )

        environment = _generate_environment(
            concept_description=concept_description, value_type=value_type
        )

        jsonable = aas_jsonization.to_jsonable(environment)
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(json.dumps(jsonable, indent=2), encoding="utf-8")
        print(f"Saved to: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
