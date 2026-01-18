"""Verify AAS Submodel Templates using Large Language Models."""

import collections.abc
import json
import pathlib
import sys
from typing import Optional, Final, List, Sequence, Any, Tuple, Iterator

from aas_core3 import (
    jsonization as aas_jsonization,
    types as aas_types,
    xmlization as aas_xmlization,
)
from icontract import require

import aas_smt_verification_with_llms
from aas_smt_verification_with_llms import argparsing, llm, aasing
from aas_smt_verification_with_llms.common import Filenameable

assert aas_smt_verification_with_llms.__doc__ == __doc__


class Prompt:
    """Define the prompt of a check."""

    format_str: Final[str]
    name: Final[Filenameable]

    @require(lambda format_str: "{relevant_details}" in format_str)
    def __init__(self, name: Filenameable, format_str: str) -> None:
        self.name = name
        self.format_str = format_str


def _list_prompts() -> List[Prompt]:
    """Generate the list of available prompts."""
    jsonschema = """\
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Improvement Suggestion",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["path", "explanation", "suggestion"],
    "properties": {
      "path": {
        "type": "string",
        "description": "ID-short path to the offending element",
        "examples": [
          "https://example.com/something",
          "urn:example.com:something"
        ]
      },
      "explanation": {
        "type": "string",
        "description": "Explanation of the semantic mismatch",
        "examples": [
          "Semantic mismatch between the concept description and unit. Length should be given in meters, while J (Joule) was indicated."
        ]
      },
      "suggestion": {
        "type": "string",
        "description": "How the semantic mismatch can be fixed",
        "examples": ["m"]
      }
    },
    "additionalProperties": false
  }
}
"""

    available_xsd_types = [data_type.value for data_type in aas_types.DataTypeDefXSD]
    available_xsd_types_joined = ", ".join(available_xsd_types)

    escaped_jsonschema = jsonschema.replace("{", "{{").replace("}", "}}")

    return [
        Prompt(
            name=Filenameable("concept_description_to_description"),
            format_str=(
                "For which of the following elements does the description "
                "DOES NOT correspond with its concept description? "
                "Consider the fact that the description can include more "
                "specific information about a particular instance "
                "that the concept description "
                "should be able to capture semantically.\n\n"
                "Output any possible semantic improvement following the JSON schema:\n"
                f"{escaped_jsonschema}\n\n"
                "Here is the data to be analyzed:\n"
                "{relevant_details}"
            ),
        ),
        Prompt(
            name=Filenameable("concept_description_to_unit"),
            format_str=(
                "For which of the following concept descriptions does the unit "
                "DOES NOT correspond with its definition?\n\n"
                "Output any possible semantic improvement following the JSON schema:\n"
                f"{escaped_jsonschema}\n\n"
                "Here is the data to be analyzed:\n"
                "{relevant_details}"
            ),
        ),
        Prompt(
            name=Filenameable("concept_description_to_value_type"),
            format_str=(
                "For which of the following elements does the XSD value type "
                "DOES NOT correspond with its concept description?\n\n"
                f"The available XSD value types are: {available_xsd_types_joined}.\n\n"
                "Output any possible semantic improvement following the JSON schema:\n"
                f"{escaped_jsonschema}\n\n"
                "The property 'suggestion' should only indicate "
                "the more appropriate XSD data type. If you suggest a numeric data type, "
                "determine the type with an appropriate precision "
                "(double for sensor data, decimal for financial/legally binding data). "
                "Also consider value types such as xs:gMonth and ilks for recurrent "
                "events.\n\n"
                "Here is the data to be analyzed:\n"
                "{relevant_details}"
            ),
        ),
        Prompt(
            name=Filenameable("description_to_display_name"),
            format_str=(
                "For which of the following elements does its description "
                "DOES NOT correspond with its display name?\n\n"
                "Only compare the description with the display name and ignore the ID-short!\n"
                "Note, that there are cases where there is no mismatch and return this "
                "as well.\n\n"
                "Output any possible semantic improvement following the JSON schema:\n"
                f"{escaped_jsonschema}\n\n"
                "Here is the data to be analyzed:\n"
                "{relevant_details}"
            ),
        ),
        Prompt(
            name=Filenameable("description_to_id_short"),
            format_str=(
                "For which of the following elements does the ID-short "
                "DOES NOT correspond with its description?\n\n"
                "Note, that there are cases where there is no mismatch and "
                "return this as well.\n\n"
                "Output any possible semantic improvement following the JSON schema:\n"
                f"{escaped_jsonschema}\n\n"
                "Here is the data to be analyzed:\n"
                "{relevant_details}"
            ),
        ),
    ]


_PROMPTS: Final[Sequence[Prompt]] = _list_prompts()


class Suggestion:
    """Represent an improvement suggested by an LLM."""

    path: Final[str]
    explanation: Final[str]
    suggestion: Final[str]

    def __init__(self, path: str, explanation: str, suggestion: str) -> None:
        self.path = path
        self.explanation = explanation
        self.suggestion = suggestion


def _parse_response(response: Any) -> Optional[List[Suggestion]]:
    """Parse the LLM response as list of improvement suggestions."""
    # NOTE (mristin):
    # We do not include Pydantic here to keep the dependencies minimal.

    if not isinstance(response, (list, tuple)):
        return None

    result = []  # type: List[Suggestion]

    for item in response:
        if not isinstance(item, collections.abc.Mapping):
            return None

        path = item.get("path", None)
        if not isinstance(path, str):
            return None

        explanation = item.get("explanation", None)
        if not isinstance(explanation, str):
            return None

        suggestion = item.get("suggestion", None)
        if not isinstance(suggestion, str):
            return None

        result.append(
            Suggestion(path=path, explanation=explanation, suggestion=suggestion)
        )

    return result


class PromptResponse:
    """Represent an LLM prompt and its response."""

    name: Final[Filenameable]
    prompt: Final[str]
    response: Final[str]

    def __init__(self, name: Filenameable, prompt: str, response: str) -> None:
        self.name = name
        self.prompt = prompt
        self.response = response


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
        try:
            environment = aas_xmlization.environment_from_str(text)
        except Exception as exception:
            return None, f"Failed to parse the AAS environment as XML: {exception}"
    else:
        return None, "Unrecognized format"

    return environment, None


def request_over_prompts(
    client: llm.Client, environment: aas_types.Environment
) -> Iterator[Tuple[Optional[PromptResponse], Optional[str]]]:
    """
    Run all the checks on the given environment.

    Yield the inputs and outputs of the LLM, or an error, if any.

    In case of error, the iterator will be closed and no further checks will be
    performed.
    """
    relevant_details: Optional[str] = aasing.relevant_details(environment)
    if relevant_details is None:
        yield None, (
            "There are no relevant details for the AAS environment, "
            "so no request to LLM could be made."
        )
        return

    for prompt in _PROMPTS:
        try:
            formatted_prompt = prompt.format_str.format(
                relevant_details=relevant_details
            )
        except Exception as exception:
            raise AssertionError(
                f"Invalid format string for {prompt.name}:\n{prompt.format_str}"
            ) from exception

        try:
            response = client.generate(formatted_prompt)
        except Exception as exception:
            yield None, (
                f"Failed to make the request to the LLM for {prompt.name}: {exception}"
            )
            return

        yield PromptResponse(
            name=prompt.name, prompt=formatted_prompt, response=response
        ), None


def main(prog: str) -> int:
    """
    Execute the main routine.

    :param prog: name of the program to be displayed in the help
    :return: exit code
    """
    parser = argparsing.build(prog=prog, description=__doc__)
    parser.add_argument(
        "--aas_environment_path",
        help="Path to the AAS environment which should be verified",
        required=True,
    )
    parser.add_argument(
        "--version", help="show the current version and exit", action="store_true"
    )

    # NOTE (mristin):
    # The module ``argparse`` is not flexible enough to understand special options such
    # as ``--version`` so we manually hard-wire.
    if "--version" in sys.argv and "--help" not in sys.argv:
        print(aas_smt_verification_with_llms.__version__)
        return 0

    args = parser.parse_args()  # pylint: disable=unused-variable
    aas_environment_path = pathlib.Path(args.aas_environment_path)

    llm_args = argparsing.extract_llm_args(args)

    client = llm.create(llm_args)

    environment, error = load_aas_environment(aas_environment_path)
    if error is not None:
        print(
            f"Failed to read and parse --aas_environment_path: {error}", file=sys.stderr
        )
        return 1

    assert environment is not None

    print("[")

    suggestion_count = 0

    for prompt_response, error in request_over_prompts(client, environment):
        if error is not None:
            print(
                f"The request failed: {error}",
                file=sys.stderr,
            )
            return 1

        assert prompt_response is not None

        # NOTE (mristin):
        # We separate the de-serialization logic from the request/receive function
        # so that we can use the function in the experiments as well.

        try:
            response_json = json.loads(prompt_response.response)
        except json.JSONDecodeError as exception:
            print(
                f"Failed to parse the response from LLM as JSON :{exception}; "
                f"the response was:\n{prompt_response.response}\n\n"
                f"The prompt was:\n{prompt_response.prompt}",
                file=sys.stderr,
            )
            continue

        maybe_suggestions = _parse_response(response_json)
        if maybe_suggestions is None:
            print(
                f"Failed to parse the response from LLM as JSON array "
                f"for check {prompt_response.name}; "
                f"the response was:\n{prompt_response.response}\n\n"
                f"The prompt was:\n{prompt_response.prompt}",
                file=sys.stderr,
            )
            continue

        for suggestion in maybe_suggestions:
            suggestion_json = collections.OrderedDict(
                [
                    ("check", prompt_response.name),
                    ("path", suggestion.path),
                    ("explanation", suggestion.explanation),
                    ("suggestion", suggestion.suggestion),
                ]
            )

            suggestion_json_text = json.dumps(suggestion_json, indent=2)

            if suggestion_count > 0:
                print(",")

            print(suggestion_json_text)

            suggestion_count += 1

    print("]")

    return 0


def entry_point() -> int:
    """Provide an entry point for a console script."""
    return main(prog="aas-smt-verification-with-llms")


if __name__ == "__main__":
    sys.exit(main(prog="aas-smt-verification-with-llms"))
