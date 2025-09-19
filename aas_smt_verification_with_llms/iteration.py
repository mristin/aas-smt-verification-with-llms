"""Iterate over AAS elements."""

import json
from typing import (
    Sequence,
    Union,
    Final,
    TypeVar,
    Type,
    Iterator,
    Tuple,
    get_args,
    List,
    Iterable,
    MutableMapping,
    Optional,
)

from aas_core3 import types as aas_types, jsonization as aas_jsonization

from aas_smt_verification_with_llms.common import assert_never


class Path:
    """Represent a value-only path."""

    fragments: Final[Sequence[Union[str, int]]]

    def __init__(self, fragments: Sequence[Union[str, int]]) -> None:
        self.fragments = fragments

    def __str__(self) -> str:
        if len(self.fragments) == 0:
            return ""

        parts = []  # type: List[str]

        iterator = iter(self.fragments)

        first = next(iterator)
        assert first is not None

        parts.append(str(first))

        for fragment in iterator:
            if isinstance(fragment, str):
                parts.append(f".{fragment}")
            elif isinstance(fragment, int):
                parts.append(f"[{fragment}]")
            else:
                assert_never(fragment)

        return "".join(parts)


SubmodelElementT = TypeVar("SubmodelElementT", bound=aas_types.SubmodelElement)

_Collection = Union[
    aas_types.Submodel,
    aas_types.SubmodelElementList,
    aas_types.SubmodelElementCollection,
]

_CollectionAsTuple = (
    aas_types.Submodel,
    aas_types.SubmodelElementList,
    aas_types.SubmodelElementCollection,
)

assert _CollectionAsTuple == get_args(_Collection)


def map_relevant_concept_descriptions_by_element(
    environment: aas_types.Environment,
    elements_paths: Iterable[Tuple[SubmodelElementT, Path]],
) -> MutableMapping[SubmodelElementT, aas_types.ConceptDescription]:
    """Go over the elements and extract the concept descriptions referenced by them."""
    concept_description_map = {
        concept_description.id: concept_description
        for concept_description in environment.over_concept_descriptions_or_empty()
    }

    result: MutableMapping[SubmodelElementT, aas_types.ConceptDescription] = dict()

    for element, _ in elements_paths:
        if element.semantic_id is None:
            continue

        semantic_id = reference_as_text(element.semantic_id)

        if semantic_id is None:
            continue

        concept_description = concept_description_map.get(semantic_id, None)

        if concept_description is not None:
            result[element] = concept_description

    return result


def filter_elements_with_semantic_id(
    iterator: Iterator[Tuple[SubmodelElementT, Path]],
) -> Iterator[Tuple[SubmodelElementT, Path]]:
    """Filter the elements with defined semantic ID attribute."""
    for element, path in iterator:
        if element.semantic_id is None:
            continue

        yield element, path


def filter_elements_of_type(
    iterator: Iterator[Tuple[aas_types.SubmodelElement, Path]],
    element_type: Type[SubmodelElementT],
) -> Iterator[Tuple[SubmodelElementT, Path]]:
    """Filter the elements with the given runtime types."""
    for element, path in iterator:
        if isinstance(element, element_type):
            yield element, path


def _over_elements(
    collection: _Collection, prefix: Path
) -> Iterator[Tuple[aas_types.SubmodelElement, Path]]:
    if isinstance(collection, aas_types.Submodel):
        for element in collection.over_submodel_elements_or_empty():
            assert (
                element.id_short is not None
            ), "All submodel elements must have an ID-short."
            path = Path(fragments=list(prefix.fragments) + [element.id_short])

            yield element, path

            if isinstance(element, _CollectionAsTuple):
                yield from _over_elements(collection=element, prefix=path)
    elif isinstance(collection, aas_types.SubmodelElementList):
        for i, element in enumerate(collection.over_value_or_empty()):
            path = Path(fragments=list(prefix.fragments) + [i])

            yield element, path

            if isinstance(element, _CollectionAsTuple):
                yield from _over_elements(collection=element, prefix=path)
    elif isinstance(collection, aas_types.SubmodelElementCollection):
        for element in collection.over_value_or_empty():
            assert (
                element.id_short is not None
            ), "All elements of a Submodel Element Collection must have an ID-short."
            path = Path(fragments=list(prefix.fragments) + [element.id_short])

            yield element, path

            if isinstance(element, _CollectionAsTuple):
                yield from _over_elements(collection=element, prefix=path)
    else:
        assert_never(collection)


def over_elements(
    environment: aas_types.Environment,
) -> Iterator[Tuple[aas_types.SubmodelElement, Path]]:
    """Iterate over all the submodel elements contained in the environment."""
    for submodel in environment.over_submodels_or_empty():
        prefix = Path(fragments=[])

        yield from _over_elements(collection=submodel, prefix=prefix)


def reference_as_text(reference: aas_types.Reference) -> str:
    """
    Convert the AAS reference into a string identifier.

    This is necessary since the reference is given as a list of keys.
    """
    assert len(reference.keys) > 0

    if reference.type is aas_types.ReferenceTypes.EXTERNAL_REFERENCE:
        assert len(reference.keys) == 1, "Expected only one key for external references"
        return reference.keys[0].value

    elif reference.type is aas_types.ReferenceTypes.MODEL_REFERENCE:
        jsonable = aas_jsonization.to_jsonable(reference)
        jsonable_str = json.dumps(jsonable, indent=2)

        raise NotImplementedError(
            f"We have not implemented the stringification of model references. "
            f"If you need this feature, please contact the developers. "
            f"The model reference was: {jsonable_str}"
        )

    else:
        assert_never(reference.type)


def concept_description_in_english(
    concept_description: aas_types.ConceptDescription,
) -> Optional[str]:
    """
    Try to extract the contained description in English.

    If there are no descriptions, or no descriptions in English, return None.
    """
    description = None  # type: Optional[str]
    if (
        concept_description.description is None
        or len(concept_description.description) == 0
    ):
        return None

    for lang_string in concept_description.over_description_or_empty():
        lang = lang_string.language.lower()
        if lang == "en" or lang.startswith("en-"):
            description = lang_string.text
            break

    return description
