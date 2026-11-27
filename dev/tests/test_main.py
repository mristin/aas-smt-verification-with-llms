# SPDX-FileCopyrightText: 2025 aas-smt-verification-with-llms AUTHORS
#
# SPDX-License-Identifier: MIT

import pathlib
import tempfile
import unittest

import aas_smt_verification_with_llms.main
from aas_smt_verification_with_llms.main import AasVersion

_NAMESPACE_BY_VERSION = {
    AasVersion.V3_0: "https://admin-shell.io/aas/3/0",
    AasVersion.V3_1: "https://admin-shell.io/aas/3/1",
    AasVersion.V3_2: "https://admin-shell.io/aas/3/2",
}

_ENVIRONMENT_XML_FORMAT = """\
<environment xmlns="{namespace}">
  <conceptDescriptions>
    <conceptDescription>
      <id>someConcept</id>
    </conceptDescription>
  </conceptDescriptions>
</environment>"""


def _write_xml_environment(directory: pathlib.Path, namespace: str) -> pathlib.Path:
    path = directory / "environment.xml"
    path.write_text(
        _ENVIRONMENT_XML_FORMAT.format(namespace=namespace), encoding="utf-8"
    )
    return path


# noinspection PyPep8Naming
class Test_load_relevant_details(unittest.TestCase):
    def test_default_is_v3_1(self) -> None:
        self.assertIs(
            AasVersion.V3_1, aas_smt_verification_with_llms.main.DEFAULT_AAS_VERSION
        )

    def test_xml_in_namespace_of_version(self) -> None:
        for aas_version, namespace in _NAMESPACE_BY_VERSION.items():
            with self.subTest(aas_version=aas_version):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    path = _write_xml_environment(pathlib.Path(tmp_dir), namespace)
                    relevant_details, error = (
                        aas_smt_verification_with_llms.main.load_relevant_details(
                            path, aas_version
                        )
                    )

                self.assertIsNone(error)
                self.assertEqual(
                    "# Concept descriptions\n\nConcept description 'someConcept'",
                    relevant_details,
                )

    def test_xml_in_namespace_of_other_version(self) -> None:
        for aas_version in AasVersion:
            for other_version, namespace in _NAMESPACE_BY_VERSION.items():
                if other_version is aas_version:
                    continue

                with self.subTest(aas_version=aas_version, other_version=other_version):
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        path = _write_xml_environment(pathlib.Path(tmp_dir), namespace)
                        relevant_details, error = (
                            aas_smt_verification_with_llms.main.load_relevant_details(
                                path, aas_version
                            )
                        )

                    self.assertIsNone(relevant_details)
                    assert error is not None
                    self.assertIn(f"in the XML namespace {namespace!r}", error)
                    self.assertIn("did you specify the correct AAS version?", error)


class TestPrompts(unittest.TestCase):
    def test_prompts_for_every_version(self) -> None:
        for aas_version in AasVersion:
            with self.subTest(aas_version=aas_version):
                prompts = aas_smt_verification_with_llms.main._PROMPTS_BY_VERSION[
                    aas_version
                ]

                value_type_prompt = next(
                    prompt
                    for prompt in prompts
                    if prompt.name == "concept_description_to_value_type"
                )
                self.assertIn("xs:double", value_type_prompt.format_str)


if __name__ == "__main__":
    unittest.main()
