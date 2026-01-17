"""Merge all the expected and unexpected cases into one big test case."""

import argparse
import hashlib
import itertools
import json
import os
import pathlib
import sys
from typing import Iterator, List, MutableMapping, cast, Iterable, Set

from aas_core3 import (
    types as aas_types,
    jsonization as aas_jsonization,
    verification as aas_verification,
)


def _make_ids_unique_in_situ(environment: aas_types.Environment) -> None:
    """
    Make all the IDs unique in the given environment by adding a hash suffix.

    We make sure that the references are updated as well.
    """
    old_to_new_id = dict()  # type: MutableMapping[str, str]

    for identifiable in itertools.chain(
        cast(Iterator[aas_types.Identifiable], environment.over_submodels_or_empty()),
        environment.over_concept_descriptions_or_empty(),
    ):
        identifiable_hash = hashlib.md5(
            json.dumps(aas_jsonization.to_jsonable(identifiable)).encode("utf-8")
        ).hexdigest()

        short_hash = identifiable_hash[:8]

        old_id = identifiable.id
        new_id = f"{identifiable.id}_{short_hash}"

        old_to_new_id[old_id] = new_id
        identifiable.id = new_id

    for instance in environment.descend():
        if not isinstance(instance, aas_types.Key):
            continue

        assert instance.type is aas_types.KeyTypes.GLOBAL_REFERENCE

        if instance.value is not None:
            maybe_new_id = old_to_new_id.get(instance.value, None)
            if maybe_new_id is None:
                # NOTE (mristin):
                # There are some references outside the environment. For example,
                # the reference to the external data specification.
                continue

            instance.value = maybe_new_id


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

            set_of_observed_submodel_ids = set()  # type: Set[str]
            set_of_observed_concept_description_ids = set()  # type: Set[str]

            for model_pth in sorted(
                pth
                for pth in expectation_dir.glob("**/model.json")
                if pth.parent.name != "all_joined_together"
            ):
                try:
                    jsonable = json.loads(model_pth.read_text(encoding="utf-8"))
                    environment = aas_jsonization.environment_from_jsonable(jsonable)
                except Exception as exception:
                    print(
                        f"Failed to read and parse {model_pth}: {exception}",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    _make_ids_unique_in_situ(environment)
                except Exception as exception:
                    raise AssertionError(
                        f"Failed to make the IDs unique in {model_pth}"
                    ) from exception

                # NOTE (mristin):
                # The ID of the submodels and concept descriptions will depend on their
                # content due to the call to ``_make_ids_unique_in_situe``, so we can use
                # the ID to de-duplicate them.

                for submodel in environment.over_submodels_or_empty():
                    if submodel.id in set_of_observed_submodel_ids:
                        continue

                    set_of_observed_submodel_ids.add(submodel.id)
                    submodels.append(submodel)

                for (
                    concept_description
                ) in environment.over_concept_descriptions_or_empty():
                    if (
                        concept_description.id
                        in set_of_observed_concept_description_ids
                    ):
                        continue

                    set_of_observed_concept_description_ids.add(concept_description.id)
                    concept_descriptions.append(concept_description)

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
