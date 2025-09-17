"""Generate and output a simple submodel to be modified later for test data."""

import json
import sys

from aas_core3 import (
    types as aas_types,
    jsonization as aas_jsonization,
    verification as aas_verification,
)


def main() -> int:
    """Execute the main routine."""
    environment = aas_types.Environment(
        submodels=[
            aas_types.Submodel(
                id="someSubmodel",
                submodel_elements=[
                    aas_types.Property(
                        id_short="something",
                        value_type=aas_types.DataTypeDefXSD.DOUBLE,
                        semantic_id=aas_types.Reference(
                            type=aas_types.ReferenceTypes.EXTERNAL_REFERENCE,
                            keys=[
                                aas_types.Key(
                                    type=aas_types.KeyTypes.GLOBAL_REFERENCE,
                                    value="someConcept",
                                )
                            ],
                        ),
                    )
                ],
            )
        ],
        concept_descriptions=[
            aas_types.ConceptDescription(
                id="someConcept",
                description=[
                    aas_types.LangStringTextType(language="en", text="Water pressure")
                ],
            )
        ],
    )

    errors = list(aas_verification.verify(environment))
    assert len(errors) == 0, f"{errors=}"

    print(json.dumps(aas_jsonization.to_jsonable(environment), indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
