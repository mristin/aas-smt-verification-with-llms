# SPDX-FileCopyrightText: 2025 aas-smt-verification-with-llms AUTHORS
#
# SPDX-License-Identifier: MIT

import unittest

from aas_smt_verification_with_llms import argparsing, llm


# noinspection PyPep8Naming
class Test_extract_llm_args(unittest.TestCase):
    def test_ollama_model_with_tag(self) -> None:
        parser = argparsing.build()
        args = parser.parse_args(["ollama", "--model", "qwen3:1.7b"])

        llm_args = argparsing.extract_llm_args(args)

        assert isinstance(llm_args, argparsing.OllamaArgs)
        self.assertEqual("qwen3:1.7b", llm_args.model)

        client = llm.create(llm_args)
        self.assertEqual("qwen3:1.7b", client.model)


if __name__ == "__main__":
    unittest.main()
