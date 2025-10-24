"""Provide common interaction pattern with LLMs."""

import abc
from typing import Final, Union

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
    def generate(self, prompt: str) -> str:
        """Generate a response for the given prompt."""
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

    def generate(self, prompt: str) -> str:
        # noinspection PyUnresolvedReferences,PyTypeChecker
        resp = self._client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}]
        )

        assert (
            len(resp.choices) > 0
        ), f"Expected at least one choice from {self.model}, but got none: {resp}"

        result = resp.choices[0].message.content

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

    def generate(self, prompt: str) -> str:
        url = f"{self.host}/api/generate"

        payload = {"model": self.model, "prompt": prompt, "stream": False}

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
        api_key = args.api_key_file.read_text(encoding="utf-8")
        return OpenAI(api_key=api_key, model=args.model)

    elif isinstance(args, argparsing.OllamaArgs):
        return Ollama(host=args.host, model=args.model, timeout=args.timeout)
    else:
        assert_never(args)
