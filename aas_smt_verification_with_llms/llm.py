"""Provide common interaction pattern with LLMs."""

import abc
import json
from typing import Final, Union, Optional, Mapping, Any, MutableMapping

import openai  # pylint: disable=import-error
import requests

from aas_smt_verification_with_llms.common import Filenameable, assert_never
from aas_smt_verification_with_llms import argparsing


class Client(abc.ABC):
    """Talk to an LLM."""

    # NOTE (mristin):
    # The model names should be globally unique.
    model: Final[Filenameable]

    @abc.abstractmethod
    def generate(
            self,
            prompt: str,
            json_schema: Optional[Mapping[str, Any]] = None
    ) -> str:
        """
        Generate a response for the given prompt.

        If the JSON schema is supplied, the LLM is tasked to generate the response
        following the schema.
        """
        raise NotImplementedError()

    def __init__(self, model: Filenameable) -> None:
        self.model = model


class OpenAI(Client):
    """Talk to the OpenAI server."""

    def __init__(
            self, api_key: str, model: Filenameable = Filenameable("gpt-5-2025-08-07")
    ) -> None:
        super().__init__(model)

        self._client = openai.OpenAI(api_key=api_key)

    def generate(
            self,
            prompt: str,
            json_schema: Optional[Mapping[str, Any]] = None
    ) -> str:
        kwargs: MutableMapping[str, Any] = {
            "model": str(self.model),
            "messages": [{"role": "user", "content": prompt}]
        }

        if json_schema is not None:
            kwargs["response_format"] = {
                "type": "json_schema",
                # NOTE (mristin):
                # We have to adapt the schema so that OpenAI can handle it -- OpenAI
                # is quite restricted what it accepts as schema.
                "json_schema": {
                    "name": "response_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "response": json_schema
                        },
                        "required": ["response"]
                    }
                }
            }

        # noinspection PyUnresolvedReferences,PyTypeChecker
        resp = self._client.chat.completions.create(**kwargs)

        assert (
                len(resp.choices) > 0
        ), f"Expected at least one choice from {self.model}, but got none: {resp}"

        content = resp.choices[0].message.content

        if json_schema is None:
            result = content
        else:
            try:
                jsonable = json.loads(content)
            except json.JSONDecodeError as exception:
                raise RuntimeError(
                    f"Expected the OpenAI to return a valid JSON if json_schema "
                    f"was specified, but it returned:\n{content}"
                ) from exception

            try:
                # NOTE (mristin):
                # We had to massage the expected schema for OpenAI as it generates
                # only objects and not array and other types, so we have to unpack
                # that here.
                response_jsonable = jsonable["response"]
            except KeyError as exception:
                raise RuntimeError(
                    f"Expected OpenAI to return a response conforming to the supplied "
                    f"JSON schema, but it returned something else:\n{content}"
                ) from exception

            result = json.dumps(response_jsonable, indent=2)

        assert isinstance(
            result, str
        ), f"Expected the answer to be a string, but got: {type(result)} {result}"

        return result


class Ollama(Client):
    """Talk to the local Ollama server."""

    host: Final[str]
    timeout: float

    def __init__(
            self,
            host: str = "http://localhost:11434",
            model: Filenameable = Filenameable("llama3.1"),
            timeout: float = 60.0,
    ) -> None:
        super().__init__(model)

        self.host = host
        self.timeout = timeout

    def generate(
            self,
            prompt: str,
            json_schema: Optional[Mapping[str, Any]] = None
    ) -> str:
        url = f"{self.host}/api/generate"

        payload: MutableMapping[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        if json_schema is not None:
            payload["format"] = json_schema

        resp = requests.post(url, json=payload, stream=False, timeout=self.timeout)
        resp.raise_for_status()

        data = resp.json()

        result = data.get("response", "")
        assert isinstance(
            result, str
        ), f"Expected the answer to be a string, but got: {type(result)} {result}"
        return result


def create(
        args: Union[
            argparsing.OpenAIArgs,
            argparsing.OllamaArgs,
        ],
) -> Client:
    """Produce a client with dispatch based on the supplied arguments."""
    if isinstance(args, argparsing.OpenAIArgs):
        api_key = args.api_key_file.read_text(encoding="utf-8").strip()
        return OpenAI(api_key=api_key, model=args.model)

    elif isinstance(args, argparsing.OllamaArgs):
        return Ollama(host=args.host, model=args.model, timeout=args.timeout)
    else:
        # noinspection PyTypeChecker
        assert_never(args)
