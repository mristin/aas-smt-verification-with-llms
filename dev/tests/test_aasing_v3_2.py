# SPDX-FileCopyrightText: 2025 aas-smt-verification-with-llms AUTHORS
#
# SPDX-License-Identifier: MIT

import pathlib
import tempfile
import unittest

from aas_core3_2 import types as aas_types, xmlization as aas_xmlization

from aas_smt_verification_with_llms import aasing_v3_2 as aasing


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

        text = aasing.reference_as_text(reference)

        self.assertEqual("something", text)

    def test_model_reference_to_concept_description(self) -> None:
        reference = aas_types.Reference(
            type=aas_types.ReferenceTypes.MODEL_REFERENCE,
            keys=[
                aas_types.Key(
                    value="someConcept", type=aas_types.KeyTypes.CONCEPT_DESCRIPTION
                )
            ],
        )

        text = aasing.reference_as_text(reference)

        self.assertEqual("someConcept", text)

    def test_model_reference_to_nested_element(self) -> None:
        reference = aas_types.Reference(
            type=aas_types.ReferenceTypes.MODEL_REFERENCE,
            keys=[
                aas_types.Key(value="someSubmodel", type=aas_types.KeyTypes.SUBMODEL),
                aas_types.Key(
                    value="someList", type=aas_types.KeyTypes.SUBMODEL_ELEMENT_LIST
                ),
                aas_types.Key(
                    value="2", type=aas_types.KeyTypes.SUBMODEL_ELEMENT_COLLECTION
                ),
                aas_types.Key(value="something", type=aas_types.KeyTypes.PROPERTY),
            ],
        )

        text = aasing.reference_as_text(reference)

        self.assertEqual("someSubmodel.someList[2].something", text)


class TestTextInEnglish(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertIsNone(aasing.text_in_english(None))

    def test_non_english(self) -> None:
        # noinspection SpellCheckingInspection
        self.assertIsNone(
            aasing.text_in_english(
                [aas_types.LangStringTextType(language="de", text="Etwas")]
            )
        )

    def test_english_and_german(self) -> None:
        # noinspection SpellCheckingInspection
        self.assertEqual(
            "water pressure",
            aasing.text_in_english(
                [
                    aas_types.LangStringTextType(language="en", text="water pressure"),
                    aas_types.LangStringTextType(language="de", text="Wasserdruck"),
                ]
            ),
        )


class TestRelevantDetails(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertIsNone(aasing.relevant_details(environment=aas_types.Environment()))

    def test_minimal_property(self) -> None:
        self.assertEqual(
            """\
# Elements

Property at path 'someSubmodel.something' with ID-short 'something' with value type xs:int""",
            aasing.relevant_details(
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
        self.assertEqual(
            """\
# Elements

Property at path 'someSubmodel.something' with ID-short 'something' with value type xs:double and with concept description 'someConcept'

# Concept descriptions

Concept description 'someConcept' means: 'Water pressure'""",
            aasing.relevant_details(
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


# noinspection PyPep8Naming
class Test_load_aas_environment(unittest.TestCase):
    def test_xml_in_own_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = pathlib.Path(tmp_dir) / "environment.xml"
            path.write_text(
                f'<environment xmlns="{aas_xmlization.NAMESPACE}"/>', encoding="utf-8"
            )

            environment, error = aasing.load_aas_environment(path)

        self.assertIsNone(error)
        self.assertIsInstance(environment, aas_types.Environment)

    def test_xml_in_other_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = pathlib.Path(tmp_dir) / "environment.xml"
            path.write_text(
                '<environment xmlns="https://example.com/not-aas"/>', encoding="utf-8"
            )

            environment, error = aasing.load_aas_environment(path)

        self.assertIsNone(environment)
        assert error is not None
        self.assertIn("in the XML namespace 'https://example.com/not-aas'", error)
        self.assertIn("did you specify the correct AAS version?", error)

    def test_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = pathlib.Path(tmp_dir) / "environment.json"
            path.write_text("{}", encoding="utf-8")

            environment, error = aasing.load_aas_environment(path)

        self.assertIsNone(error)
        self.assertIsInstance(environment, aas_types.Environment)


# noinspection PyPep8Naming
class Test_load_relevant_details(unittest.TestCase):
    def test_empty_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = pathlib.Path(tmp_dir) / "environment.json"
            path.write_text("{}", encoding="utf-8")

            relevant_details, error = aasing.load_relevant_details(path)

        self.assertIsNone(relevant_details)
        assert error is not None
        self.assertIn("There are no relevant details", error)


if __name__ == "__main__":
    unittest.main()
