"""Check if the LLM can infer that a value type corresponds to concept description."""

import itertools
import os
import pathlib
import sys
from typing import Iterator, Tuple, List, Union

import tqdm
from aas_core3 import types as aas_types

from aas_smt_verification_with_llms import argparsing, llm, iteration
from aas_smt_verification_with_llms.common import Filenameable

import experiments.storage


def _relevant_details(environment: aas_types.Environment) -> str:
    """
    Translate the elements and their concept descriptions into succinct text.

    Return an emtpy string if there are no relevant elements.
    """
    it: Iterator[Tuple[Union[aas_types.Property, aas_types.Range], iteration.Path]] = (
        iteration.filter_elements_of_type(
            iteration.over_elements(environment),
            element_type=aas_types.Property,
        )
    )

    it = itertools.chain(
        it,
        iteration.filter_elements_of_type(
            iteration.over_elements(environment),
            element_type=aas_types.Range,
        ),
    )

    it = iteration.filter_elements_with_semantic_id(it)

    elements_paths = list(it)

    relevant_concept_descriptions_by_element = (
        iteration.map_relevant_concept_descriptions_by_element(
            environment=environment, elements_paths=elements_paths
        )
    )

    # NOTE (mristin):
    # We only mention the elements with available concept descriptions.
    elements_paths = [
        (element, path)
        for element, path in elements_paths
        if element in relevant_concept_descriptions_by_element
    ]

    if len(elements_paths) == 0:
        return ""

    blocks = ["# Elements"]  # type: List[str]

    for element, path in elements_paths:
        assert element.semantic_id is not None
        semantic_id = iteration.reference_as_text(element.semantic_id)
        blocks.append(
            f"{element.__class__.__name__} at path {str(path)!r} "
            f"with value type: {element.value_type.value} "
            f"and with concept description: {semantic_id}"
        )

    assert len(relevant_concept_descriptions_by_element) is not None
    blocks.append("# Concept descriptions")
    for concept_description in relevant_concept_descriptions_by_element.values():
        description = iteration.concept_description_in_english(concept_description)

        if description is None:
            raise RuntimeError(
                f"Unexpected concept description {concept_description.id} "
                f"without a description in English"
            )

        blocks.append(f"{concept_description.id} means: {description}")

    text = "\n".join(blocks)
    return text


def main() -> int:
    """Execute the main routine."""
    parser = argparsing.build()
    args = parser.parse_args()

    llm_args = argparsing.extract_llm_args(args)

    client = llm.create(llm_args)

    experiment = Filenameable(pathlib.Path(os.path.realpath(__file__)).stem)

    outcomes_cases_output_stores: List[
        Tuple[
            experiments.storage.Outcome,
            Filenameable,
            experiments.storage.ExperimentOutput,
        ]
    ] = [
        (
            outcome,
            case,
            experiments.storage.ExperimentOutput(
                experiment=experiment, outcome=outcome, case=case, model=client.model
            ),
        )
        for outcome in experiments.storage.Outcome
        for case in experiments.storage.list_cases_for_outcome(experiment, outcome)
    ]

    # NOTE (mristin):
    # We only want to process the pending cases.
    outcomes_cases_output_stores = [
        (outcome, case, output_store)
        for outcome, case, output_store in outcomes_cases_output_stores
        if not output_store.has_response()
    ]

    if len(outcomes_cases_output_stores) == 0:
        print("All cases are processed.")
        return 0

    print(f"Running {len(outcomes_cases_output_stores)} pending prompt(s)...")
    for outcome, case, output_store in tqdm.tqdm(outcomes_cases_output_stores):
        environment: aas_types.Environment = experiments.storage.load_model(
            experiment=experiment, outcome=outcome, case=case
        )

        relevant_details: str = _relevant_details(environment)

        if relevant_details == "":
            raise RuntimeError(
                f"Unexpected no relevant details for the experiment "
                f"{outcome=}, {case=}"
            )

        prompt = (
            f"For which of the following elements does the XSD value type "
            f"DOES NOT correspond with its concept description?\n\n"
            f"Output a JSON list of objects with properties 'path', "
            f"'explanation' and 'suggestion' corresponding to the mismatches.\n"
            f"The property 'suggestion' should only indicate "
            f"the more appropriate XSD data type. If you suggest a numeric data type, "
            f"determine the type with an appropriate precision "
            f"(double for sensor data, decimal for financial/legally binding data).\n\n"
            f"{relevant_details}"
        )

        response = client.generate(prompt)

        output_store.save_prompt_and_response(prompt=prompt, response=response)

    return 0


if __name__ == "__main__":
    sys.exit(main())
