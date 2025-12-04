"""Check if the LLM can infer that a value type corresponds to concept description."""

import os
import pathlib
import sys
from typing import Optional

import tqdm
from aas_core3 import types as aas_types

import experiments.common
import experiments.storage
from aas_smt_verification_with_llms import argparsing, llm, aasing
from aas_smt_verification_with_llms.common import Filenameable


def main() -> int:
    """Execute the main routine."""
    parser = argparsing.build()
    args = parser.parse_args()

    llm_args = argparsing.extract_llm_args(args)

    client = llm.create(llm_args)

    experiment = Filenameable(pathlib.Path(os.path.realpath(__file__)).stem)

    takes = [
        take
        for take in experiments.storage.over_takes(
            experiment=experiment, model=client.model
        )
    ]

    pending_takes = [take for take in takes if not take.output_store.has_response()]

    if len(pending_takes) == 0:
        print("All experiment takes are processed.")
        return 0

    print(f"Running {len(pending_takes)} pending experiment take(s)...")
    for take in tqdm.tqdm(pending_takes):
        environment: aas_types.Environment = experiments.storage.load_model(
            experiment=experiment, category=take.category, case=take.case
        )

        relevant_details: Optional[str] = aasing.relevant_details(environment)

        if relevant_details is None:
            raise RuntimeError(
                f"Unexpected no relevant details for the experiment "
                f"{take.category=}, {take.case=}"
            )

        prompt = (
            f"For which of the following elements does the ID-short "
            f"DOES NOT correspond with its description?\n\n"
            f"Note, that there are cases where there is no mismatch and "
            f"return this as well.\n\n"
            f"Output any possible semantic improvement following the JSON schema:\n"
            f"{experiments.common.JSONSCHEMA}\n\n"
            f"Here is the data to be analyzed:\n"
            f"{relevant_details}"
        )

        response = client.generate(prompt)

        take.output_store.save_prompt_and_response(prompt=prompt, response=response)

    return 0


if __name__ == "__main__":
    sys.exit(main())
