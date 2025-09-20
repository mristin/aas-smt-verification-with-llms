# pylint: disable=missing-docstring

import unittest

from aas_core3 import types as aas_types

import aas_smt_verification_with_llms.aasing


# noinspection PyPep8Naming
class Test_reference_as_text(unittest.TestCase):
    def test_external(self) -> None:
        reference = aas_types.Reference(
            type=aas_types.ReferenceTypes.EXTERNAL_REFERENCE,
            keys=[
                aas_types.Key(
                    value="something", type=aas_types.KeyTypes.GLOBAL_REFERENCE
                )
            ],
        )

        text = aas_smt_verification_with_llms.aasing.reference_as_text(reference)

        self.assertEqual("something", text)


class TestTextInEnglish(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertIsNone(aas_smt_verification_with_llms.aasing.text_in_english(None))

    def test_non_english(self) -> None:
        # noinspection SpellCheckingInspection
        self.assertIsNone(
            aas_smt_verification_with_llms.aasing.text_in_english(
                [aas_types.LangStringTextType(language="de", text="Etwas")]
            )
        )

    def test_english_and_german(self) -> None:
        # noinspection SpellCheckingInspection
        self.assertEqual(
            "water pressure",
            aas_smt_verification_with_llms.aasing.text_in_english(
                [
                    aas_types.LangStringTextType(language="en", text="water pressure"),
                    aas_types.LangStringTextType(language="de", text="Wasserdruck"),
                ]
            ),
        )


class TestRelevantDetails(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertIsNone(
            aas_smt_verification_with_llms.aasing.relevant_details(
                environment=aas_types.Environment()
            )
        )

    def test_minimal_property(self) -> None:
        self.assertEqual(
            """\
# Elements

Property at path 'something' with ID-short 'something' with value type xs:int""",
            aas_smt_verification_with_llms.aasing.relevant_details(
                environment=aas_types.Environment(
                    submodels=[
                        aas_types.Submodel(
                            id="someSubmodel",
                            submodel_elements=[
                                aas_types.Property(
                                    id_short="something",
                                    value_type=aas_types.DataTypeDefXSD.INT,
                                )
                            ],
                        )
                    ]
                )
            ),
        )

    def test_property_and_concept_description(self) -> None:
        # pylint: disable=line-too-long
        self.assertEqual(
            """\
# Elements

Property at path 'something' with ID-short 'something' with value type xs:double and with concept description 'someConcept'

# Concept descriptions

Concept description 'someConcept' means: 'Water pressure'""",
            aas_smt_verification_with_llms.aasing.relevant_details(
                aas_types.Environment(
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
                                aas_types.LangStringTextType(
                                    language="en", text="Water pressure"
                                )
                            ],
                        )
                    ],
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
