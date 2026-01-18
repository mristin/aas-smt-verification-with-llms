"""Run our main program with full stack of checks on the ``complex/`` cases."""

import os
import pathlib
import sys

import tqdm

import aas_smt_verification_with_llms.main
from aas_smt_verification_with_llms import argparsing, llm


def main() -> int:
    """Execute the main routine."""
    parser = argparsing.build(description=__doc__)
    args = parser.parse_args()

    llm_args = argparsing.extract_llm_args(args)

    client = llm.create(llm_args)

    repo_root = pathlib.Path(os.path.realpath(__file__)).parent.parent

    experiment_data_dir = repo_root / "experiment_data"
    if not experiment_data_dir.exists():
        raise FileNotFoundError(
            f"Experiment data directory not found: {experiment_data_dir}"
        )

    experiment_output_dir = repo_root / "experiment_output"

    for model_path in tqdm.tqdm(
        sorted((experiment_data_dir / "complex").glob("**/model.json"))
    ):
        print(f"Processing {model_path} ...")
        target_dir = (
            experiment_output_dir
            / client.model
            / (model_path.parent.relative_to(experiment_data_dir))
        )

        target_dir.mkdir(parents=True, exist_ok=True)
        done_path = target_dir / "done"

        if done_path.exists():
            print(f"The marker file {done_path} exists, skipping.")
            continue

        environment, error = aas_smt_verification_with_llms.main.load_aas_environment(
            model_path
        )
        if error is not None:
            print(
                f"Failed to read and parse the model path {model_path}: {error}",
                file=sys.stderr,
            )
            return 1

        assert environment is not None

        for (
            prompt_response,
            error,
        ) in aas_smt_verification_with_llms.main.request_over_prompts(
            client, environment
        ):
            if error is not None:
                print(f"The request on {model_path} failed: {error}", file=sys.stderr)
                return 1

            assert prompt_response is not None

            prompt_path = target_dir / f"prompt_{prompt_response.name}.txt"
            prompt_path.write_text(prompt_response.prompt, encoding="utf-8")
            print(f"Written to: {prompt_path}")

            response_path = target_dir / f"response_{prompt_response.name}.txt"
            response_path.write_text(prompt_response.response, encoding="utf-8")
            print(f"Written to: {response_path}")

        done_path.write_text("yes", encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
