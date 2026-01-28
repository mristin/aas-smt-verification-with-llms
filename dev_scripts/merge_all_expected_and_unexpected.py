"""Merge all the expected and unexpected cases into one big test case."""

import argparse
import itertools
import json
import os
import pathlib
import sys
from typing import List, cast, Iterable

from aas_core3 import (
    types as aas_types,
    jsonization as aas_jsonization,
    verification as aas_verification,
)


def main() -> int:
    """Execute the main routine."""
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.parse_args()

    repo_root = pathlib.Path(os.path.realpath(__file__)).parent.parent

    experiment_data_dir = repo_root / "experiment_data"

    base_case_dirs = [
        experiment_data_dir / "concept_description_to_description",
        experiment_data_dir / "concept_description_to_unit",
        experiment_data_dir / "concept_description_to_value_type",
        experiment_data_dir / "description_to_display_name",
        experiment_data_dir / "description_to_id_short",
    ]

    for base_case_dir in base_case_dirs:
        for expectation in ["expected", "unexpected"]:
            expectation_dir = base_case_dir / expectation

            print(f"Merging all environments in {expectation_dir} ...")
            if not expectation_dir.exists():
                raise FileNotFoundError(
                    f"Expected the base case directory to exist: {expectation_dir}"
                )

            submodels = []  # type: List[aas_types.Submodel]
            concept_descriptions = []  # type: List[aas_types.ConceptDescription]

            model_paths = sorted(
                pth
                for pth in expectation_dir.glob("**/model.json")
                if pth.parent.name != "all_joined_together"
            )

            for model_i, model_pth in enumerate(model_paths):
                try:
                    jsonable = json.loads(model_pth.read_text(encoding="utf-8"))
                    environment = aas_jsonization.environment_from_jsonable(jsonable)
                except Exception as exception:
                    print(
                        f"Failed to read and parse {model_pth}: {exception}",
                        file=sys.stderr,
                    )
                    return 1

                for submodel_i, submodel in enumerate(
                    environment.over_submodels_or_empty()
                ):
                    submodel.id = f"urn:submodel_{model_i}_{submodel_i}"
                    submodels.append(submodel)

                for concept_description_i, concept_description in enumerate(
                    environment.over_concept_descriptions_or_empty()
                ):
                    old_id = concept_description.id
                    new_id = (
                        f"urn:concept_description_{model_i}_{concept_description_i}"
                    )

                    concept_description.id = new_id
                    concept_descriptions.append(concept_description)

                    # NOTE (mristin):
                    # Now we update all the references to this ID as well.

                    for reference in environment.descend():
                        if not isinstance(reference, aas_types.Reference):
                            continue

                        if (
                            reference.type
                            is not aas_types.ReferenceTypes.EXTERNAL_REFERENCE
                        ):
                            raise NotImplementedError(
                                f"We currently expect only external references in "
                                f"experiment data, but we got: {reference.type}"
                            )

                        if len(reference.keys) != 1:
                            raise NotImplementedError(
                                f"We currently expect only external references "
                                f"with a single key in experiment data, "
                                f"but we got: {reference.keys}"
                            )

                        first_key = reference.keys[0]
                        if first_key.value == old_id:
                            first_key.value = concept_description.id

            ids = [
                identifiable.id
                for identifiable in itertools.chain(
                    cast(Iterable[aas_types.Identifiable], submodels),
                    concept_descriptions,
                )
            ]

            assert len(ids) == len(
                set(ids)
            ), f"All IDs must be unique, but got duplicates: {sorted(ids)}."

            big_environment = aas_types.Environment(
                submodels=(submodels if len(submodels) > 0 else None),
                concept_descriptions=(
                    concept_descriptions if len(concept_descriptions) > 0 else None
                ),
            )

            errors = list(aas_verification.verify(big_environment))
            assert len(errors) == 0, f"Unexpected verification errors: {errors}"

            target_path = expectation_dir / "all_joined_together" / "model.json"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(
                json.dumps(
                    aas_jsonization.to_jsonable(big_environment),
                    indent=2,
                )
            )

            print(f"Written to: {target_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
