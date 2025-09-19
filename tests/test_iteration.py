# pylint: disable=missing-docstring

import unittest

from aas_core3 import types as aas_types

import aas_smt_verification_with_llms.iteration


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

        text = aas_smt_verification_with_llms.iteration.reference_as_text(reference)

        self.assertEqual("something", text)


class Test_concept_description_in_english(unittest.TestCase):
    def test_empty(self) -> None:
        concept_description = aas_types.ConceptDescription(
            id="something", description=None
        )

        self.assertIsNone(
            aas_smt_verification_with_llms.iteration.concept_description_in_english(
                concept_description
            )
        )

    def test_non_english(self) -> None:
        # noinspection SpellCheckingInspection
        concept_description = aas_types.ConceptDescription(
            id="something",
            description=[aas_types.LangStringTextType(language="de", text="etwas")],
        )

        self.assertIsNone(
            aas_smt_verification_with_llms.iteration.concept_description_in_english(
                concept_description
            )
        )

    def test_english_and_german(self) -> None:
        # noinspection SpellCheckingInspection
        concept_description = aas_types.ConceptDescription(
            id="something",
            description=[
                aas_types.LangStringTextType(language="en", text="water pressure"),
                aas_types.LangStringTextType(language="de", text="Wasserdruck"),
            ],
        )

        self.assertEqual(
            "water pressure",
            aas_smt_verification_with_llms.iteration.concept_description_in_english(
                concept_description
            ),
        )


if __name__ == "__main__":
    unittest.main()
