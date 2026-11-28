# SPDX-FileCopyrightText: 2025 aas-smt-verification-with-llms AUTHORS
#
# SPDX-License-Identifier: MIT

"""
Translate AAS environments into the input of the LLM for one version of the meta-model.

The version of the meta-model is given by the imported aas-core SDK. The modules
for the different versions are kept identical apart from the SDK imports and
the explicitly listed exceptions, see ``dev/tests/test_version_modules_in_sync.py``.
"""

import itertools
import json
import pathlib
from typing import (
    Sequence,
    Union,
    Iterable,
    Iterator,
    Tuple,
    List,
    Optional,
)

from aas_core3_1 import (
    jsonization as aas_jsonization,
    types as aas_types,
    xmlization as aas_xmlization,
)

from aas_smt_verification_with_llms.common import (
    assert_never,
    Path,
    sniff_xml_namespace,
)


def load_aas_environment(
    path: pathlib.Path,
) -> Tuple[Optional[aas_types.Environment], Optional[str]]:
    """
    Read the AAS environment from the file.

    Return the parsed AAS environment, or an error, if any.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exception:
        return None, str(exception)

    if len(text) == 0:
        return None, "Empty file"

    text = text.strip()

    environment: aas_types.Environment
    if text[0] == "{":
        try:
            jsonable = json.loads(text)
        except Exception as exception:
            return None, f"Failed to parse the AAS environment as JSON: {exception}"

        try:
            environment = aas_jsonization.environment_from_jsonable(jsonable)
        except Exception as exception:
            return None, f"Failed to parse the AAS environment as JSON: {exception}"

    elif text[0] == "<":
        # NOTE (mristin):
        # The XML namespace tells us the version of the meta-model, so we can give
        # a clear message instead of a confusing de-serialization error if the user
        # selected the wrong version.
        namespace = sniff_xml_namespace(text)
        if namespace is not None and namespace != aas_xmlization.NAMESPACE:
            return None, (
                f"The root element is in the XML namespace {namespace!r}, "
                f"but expected the namespace {aas_xmlization.NAMESPACE!r}; "
                f"did you specify the correct AAS version?"
            )

        try:
            environment = aas_xmlization.environment_from_str(text)
        except Exception as exception:
            return None, f"Failed to parse the AAS environment as XML: {exception}"
    else:
        return None, "Unrecognized format"

    return environment, None


def list_xsd_value_types() -> List[str]:
    """List the XSD value types available in this version of the meta-model."""
    return [data_type.value for data_type in aas_types.DataTypeDefXSD]


def _over_nested_elements(
    container: Union[aas_types.Submodel, aas_types.SubmodelElement],
) -> Iterator[Tuple[aas_types.SubmodelElement, Union[str, int]]]:
    """
    Iterate over the immediate children of the container with their path fragments.

    Items of a submodel element list are identified by their index, all the other
    children by their ID-short. Elements which can not contain other submodel
    elements yield nothing.
    """
    if isinstance(container, aas_types.SubmodelElementList):
        for i, item in enumerate(container.over_value_or_empty()):
            yield item, i
        return

    children: Iterable[aas_types.SubmodelElement]
    if isinstance(container, aas_types.Submodel):
        children = container.over_submodel_elements_or_empty()
    elif isinstance(container, aas_types.SubmodelElementCollection):
        children = container.over_value_or_empty()
    elif isinstance(container, aas_types.Entity):
        children = container.over_statements_or_empty()
    elif isinstance(container, aas_types.AnnotatedRelationshipElement):
        children = container.over_annotations_or_empty()
    elif isinstance(container, aas_types.Operation):
        children = (
            variable.value
            for variable in itertools.chain(
                container.over_input_variables_or_empty(),
                container.over_output_variables_or_empty(),
                container.over_inoutput_variables_or_empty(),
            )
        )
    else:
        return

    for child in children:
        assert child.id_short is not None, (
            f"Expected all children of {container.__class__.__name__} "
            f"to have an ID-short."
        )
        yield child, child.id_short


def _over_nested_elements_recursively(
    container: Union[aas_types.Submodel, aas_types.SubmodelElement], prefix: Path
) -> Iterator[Tuple[aas_types.SubmodelElement, Path]]:
    for element, fragment in _over_nested_elements(container):
        path = Path(fragments=list(prefix.fragments) + [fragment])

        yield element, path

        yield from _over_nested_elements_recursively(container=element, prefix=path)


def over_elements(
    environment: aas_types.Environment,
) -> Iterator[Tuple[aas_types.SubmodelElement, Path]]:
    """Iterate over all the submodel elements contained in the environment."""
    for submodel in environment.over_submodels_or_empty():
        prefix = Path(fragments=[submodel.id])

        yield from _over_nested_elements_recursively(container=submodel, prefix=prefix)


def reference_as_text(reference: aas_types.Reference) -> str:
    """
    Convert the AAS reference into a string identifier.

    This is necessary since the reference is given as a list of keys.

    Model references are rendered in the same notation as :py:class:`Path`, *i.e.*,
    the ID of the first (identifiable) key followed by ``.idShort`` for nested
    elements and ``[index]`` for items of a submodel element list. A model
    reference with a single key (*e.g.*, pointing to a concept description) is
    thus simply rendered as the identifier of the referred identifiable.
    """
    assert len(reference.keys) > 0

    if reference.type is aas_types.ReferenceTypes.EXTERNAL_REFERENCE:
        assert len(reference.keys) == 1, "Expected only one key for external references"
        return reference.keys[0].value

    elif reference.type is aas_types.ReferenceTypes.MODEL_REFERENCE:
        fragments: List[Union[str, int]] = [reference.keys[0].value]

        for parent_key, key in itertools.pairwise(reference.keys):
            if (
                parent_key.type is aas_types.KeyTypes.SUBMODEL_ELEMENT_LIST
                and key.value.isdigit()
            ):
                fragments.append(int(key.value))
            else:
                fragments.append(key.value)

        return str(Path(fragments=fragments))

    else:
        # noinspection PyTypeChecker
        assert_never(reference.type)


def text_in_english(
    lang_strings: Optional[Sequence[aas_types.AbstractLangString]],
) -> Optional[str]:
    """
    Try to extract the contained text in English.

    If there is no language string at all or no text in English, return None.
    """
    if lang_strings is None:
        return None

    for lang_string in lang_strings:
        lang = lang_string.language.lower()
        if lang == "en" or lang.startswith("en-"):
            return lang_string.text

    return None


def relevant_details(environment: aas_types.Environment) -> Optional[str]:
    """
    Translate the elements and the concept descriptions into succinct text.

    Return None if there is nothing relevant.
    """
    # fmt: off
    elements_paths: Sequence[
        Tuple[
            Union[
                aas_types.Property,
                aas_types.Range,
                aas_types.MultiLanguageProperty
            ],
            Path
        ]
    ] = [
        (element, path)
        for element, path in over_elements(environment)
        if isinstance(
            element,
            (aas_types.Property, aas_types.Range, aas_types.MultiLanguageProperty)
        )
    ]
    # fmt: on

    if len(elements_paths) == 0 and (
        environment.concept_descriptions is None
        or len(environment.concept_descriptions) == 0
    ):
        return None

    blocks: List[str] = []

    if len(elements_paths) > 0:
        blocks.append("# Elements")

        for element, path in elements_paths:
            element_parts: List[str] = [
                f"{element.__class__.__name__} at path {str(path)!r}"
            ]

            if element.id_short is not None:
                element_parts.append(f" with ID-short {element.id_short!r}")

            description_in_en = text_in_english(element.description)
            if description_in_en is not None:
                element_parts.append(f" with description {description_in_en!r}")

            display_name_in_en = text_in_english(element.display_name)
            if display_name_in_en is not None:
                element_parts.append(f" with display name {display_name_in_en!r}")

            if isinstance(element, (aas_types.Property, aas_types.Range)):
                element_parts.append(f" with value type {element.value_type.value}")

            if element.semantic_id is not None:
                semantic_id_as_text = reference_as_text(element.semantic_id)

                element_parts.append(
                    f" and with concept description {semantic_id_as_text!r}"
                )

            block = "".join(element_parts)
            blocks.append(block)

    if (
        environment.concept_descriptions is not None
        and len(environment.concept_descriptions) > 0
    ):
        blocks.append("# Concept descriptions")
        for concept_description in environment.over_concept_descriptions_or_empty():
            concept_description_parts = [
                f"Concept description {concept_description.id!r}"
            ]

            description_in_en = text_in_english(concept_description.description)
            if description_in_en is not None:
                concept_description_parts.append(f" means: {description_in_en!r}")

            unit_parts: List[str] = []

            definition_parts: List[str] = []

            for (
                data_specification
            ) in concept_description.over_embedded_data_specifications_or_empty():
                content = data_specification.data_specification_content

                if isinstance(content, aas_types.DataSpecificationIEC61360):
                    if content.unit is not None:
                        unit_parts.append(content.unit)

                    if content.definition is not None:
                        definition_in_en = text_in_english(content.definition)

                        if definition_in_en is not None:
                            definition_parts.append(definition_in_en)

            if len(unit_parts) > 0:
                units_str = ", ".join(unit_parts)

                if len(unit_parts) == 1:
                    concept_description_parts.append(f" with unit {units_str}")
                else:
                    concept_description_parts.append(f" with units {units_str}")

            if len(definition_parts) > 0:
                definitions_str = ", ".join(f"'{part}'" for part in definition_parts)
                if len(definition_parts) == 1:
                    concept_description_parts.append(
                        f" with definition {definitions_str}"
                    )
                else:
                    concept_description_parts.append(
                        f" with definitions {definitions_str}"
                    )

            block = "".join(concept_description_parts)
            blocks.append(block)

    text = "\n\n".join(blocks)
    return text


def load_relevant_details(path: pathlib.Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Load the AAS environment and translate it into the relevant details for the LLM.

    Return the relevant details, or an error, if any.
    """
    environment, error = load_aas_environment(path)
    if error is not None:
        return None, f"Failed to read and parse the AAS environment: {error}"

    assert environment is not None

    text = relevant_details(environment)
    if text is None:
        return None, (
            "There are no relevant details for the AAS environment, "
            "so no request to LLM could be made."
        )

    return text, None
