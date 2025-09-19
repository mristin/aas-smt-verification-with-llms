"""Handle storage of data and outputs for the experiments."""

import enum
import json
import os
import pathlib
import uuid
from typing import List, Final, Iterator

from aas_core3 import (
    types as aas_types,
    jsonization as aas_jsonization,
    verification as aas_verification,
)
from icontract import require

from aas_smt_verification_with_llms.common import Filenameable

_REPO_ROOT = pathlib.Path(os.path.realpath(__file__)).parent.parent

_EXPERIMENT_DATA_DIR = _REPO_ROOT / "experiment_data"


class Category(enum.Enum):
    """
    Enumerate the anticipated categories of experiment cases.

    The expected cases are expected to pass the linter.

    The unexpected cases are expected to cause warnings and/or errors.
    """

    EXPECTED = "expected"
    UNEXPECTED = "unexpected"


def load_model(
    experiment: Filenameable, category: Category, case: Filenameable
) -> aas_types.Environment:
    """Load the AAS model for the corresponding experiment case."""
    model_path = (
        _EXPERIMENT_DATA_DIR / experiment / category.value / case / "model.json"
    )

    text = model_path.read_text(encoding="utf-8")

    jsonable = json.loads(text)

    environment = aas_jsonization.environment_from_jsonable(jsonable)

    errors = list(aas_verification.verify(environment))
    assert (
        len(errors) == 0
    ), f"Unexpected errors w.r.t. the meta-model in {model_path}: {errors}"

    return environment


def list_cases_for_category(
    experiment: Filenameable,
    category: Category,
) -> List[Filenameable]:
    """List all the case names for the given experiment and category."""
    return sorted(
        Filenameable(path.name)
        for path in (_EXPERIMENT_DATA_DIR / experiment / category.value).iterdir()
        if path.is_dir()
    )


def _experiment_output_dir(
    experiment: Filenameable,
    category: Category,
    case: Filenameable,
    model: Filenameable,
) -> pathlib.Path:
    return _REPO_ROOT / model / experiment / category.value / case


class OutputStore:
    """Handle the output data of an experiment."""

    experiment: Final[Filenameable]
    category: Final[Category]
    case: Final[Filenameable]
    model: Final[Filenameable]

    def __init__(
        self,
        experiment: Filenameable,
        category: Category,
        case: Filenameable,
        model: Filenameable,
    ) -> None:
        self.experiment = experiment
        self.category = category
        self.case = case
        self.model = model

        directory = (
            _REPO_ROOT
            / "experiment_output"
            / model
            / experiment
            / category.value
            / case
        )

        self._prompt_path = directory / "prompt.txt"
        self._response_path = directory / "response.txt"

    def has_response(self) -> bool:
        """
        Check whether the response has been already stored.

        If there is no response, the experiment has not been performed.
        """
        return self._response_path.exists()

    def save_prompt_and_response(self, prompt: str, response: str) -> None:
        """
        Save atomically prompt and response.

        If the response is present in the filesystem, the experiment has been stored
        successfully. Otherwise, the prompt and response data is unrolled.
        """
        assert self._prompt_path.parent == self._response_path.parent, (
            "Prompt and response files must reside in the same directory for "
            "atomicity."
        )

        self._prompt_path.parent.mkdir(parents=True, exist_ok=True)

        tmp_prompt_path = (
            self._prompt_path.parent / f"{self._prompt_path.name}.{uuid.uuid4()}"
        )
        tmp_response_path = (
            self._response_path.parent / f"{self._response_path.name}.{uuid.uuid4()}"
        )

        try:
            tmp_prompt_path.write_text(prompt, encoding="utf-8")
            tmp_response_path.write_text(response, encoding="utf-8")

            tmp_prompt_path.rename(self._prompt_path)
            tmp_response_path.rename(self._response_path)
        finally:
            tmp_prompt_path.unlink(missing_ok=True)
            tmp_response_path.unlink(missing_ok=True)

    @require(lambda self: self.has_response())
    def load_prompt(self) -> str:
        """Load the prompt for the given experiment."""
        return self._prompt_path.read_text(encoding="utf-8")

    @require(lambda self: self.has_response())
    def load_response(self) -> str:
        """Load the response for the given experiment."""
        return self._response_path.read_text(encoding="utf-8")


class Take:
    """Capture all the ingredients for a take at an experiment."""

    experiment: Final[Filenameable]
    category: Final[Category]
    case: Final[Filenameable]
    model: Final[Filenameable]
    output_store: Final[OutputStore]

    def __init__(
        self,
        experiment: Filenameable,
        category: Category,
        case: Filenameable,
        model: Filenameable,
        output_store: OutputStore,
    ) -> None:
        self.experiment = experiment
        self.category = category
        self.case = case
        self.model = model
        self.output_store = output_store


def over_takes(
    experiment: Filenameable,
    model: Filenameable,
) -> Iterator[Take]:
    """Go over all the possible experiment takes for the given model."""
    for category in Category:
        for case in list_cases_for_category(experiment, category):
            output_store = OutputStore(
                experiment=experiment, category=category, case=case, model=model
            )

            yield Take(
                experiment=experiment,
                category=category,
                case=case,
                model=model,
                output_store=output_store,
            )
