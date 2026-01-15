"""Provide common parsers of command-line arguments."""

import argparse
import os
import pathlib
from typing import Final, Union, Optional

from aas_smt_verification_with_llms.common import Filenameable


def build(
    prog: Optional[str] = None, description: Optional[str] = None
) -> argparse.ArgumentParser:
    """
    Construct the basic command-line argument parser.

    The parser includes the arguments shared across different experiments. Each
    experiment script is expected to add more arguments if necessary.
    """
    parser = argparse.ArgumentParser(prog=prog, description=description)
    sub = parser.add_subparsers(
        dest="llm", required=True, help="Choose the LLM backend"
    )

    parser_openai = sub.add_parser("openai", help="Use OpenAI (ChatGPT) models")
    parser_openai.add_argument(
        "--model", default="gpt-5-2025-08-07", help="OpenAI model name"
    )
    parser_openai.add_argument(
        "--api-key-file",
        required=True,
        help="Path to the file containing OpenAI API key",
    )

    parser_ollama = sub.add_parser("ollama", help="Use a local Ollama model")
    parser_ollama.add_argument("--model", default="llama3.1", help="Ollama model name")
    parser_ollama.add_argument(
        "--host",
        default=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        help="Ollama host URL",
    )
    parser_ollama.add_argument(
        "--timeout", type=float, default=60.0, help="HTTP timeout in seconds"
    )

    return parser


class OpenAIArgs:
    """Capture the arguments necessary for OpenAI client."""

    api_key_file: Final[pathlib.Path]
    model: Final[Filenameable]

    def __init__(self, api_key_file: pathlib.Path, model: Filenameable) -> None:
        self.api_key_file = api_key_file
        self.model = model


class OllamaArgs:
    """Capture the arguments necessary for Ollama client."""

    model: Final[Filenameable]
    host: Final[str]
    timeout: Final[float]

    def __init__(self, model: Filenameable, host: str, timeout: float) -> None:
        self.model = model
        self.host = host
        self.timeout = timeout


def extract_llm_args(args: argparse.Namespace) -> Union[OpenAIArgs, OllamaArgs]:
    """Extract the arguments from the parsed command-line arguments."""
    if args.llm == "openai":
        return OpenAIArgs(
            api_key_file=pathlib.Path(args.api_key_file), model=Filenameable(args.model)
        )

    elif args.llm == "ollama":
        return OllamaArgs(
            model=Filenameable(args.model), host=args.host, timeout=float(args.timeout)
        )

    else:
        raise NotImplementedError(f"Unhandled llm: {args.llm}")
