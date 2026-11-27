# SPDX-FileCopyrightText: 2025 aas-smt-verification-with-llms AUTHORS
#
# SPDX-License-Identifier: MIT

import unittest

from aas_smt_verification_with_llms.common import FILENAMEABLE_RE, escape_for_filename


# noinspection PyPep8Naming
class Test_escape_for_filename(unittest.TestCase):
    def test_unchanged(self) -> None:
        self.assertEqual("gpt-5-2025-08-07", escape_for_filename("gpt-5-2025-08-07"))

    def test_ollama_tag(self) -> None:
        self.assertEqual("qwen3%3A1.7b", escape_for_filename("qwen3:1.7b"))

    def test_all_forbidden_characters(self) -> None:
        escaped = escape_for_filename("a/b;c:d%e")

        self.assertEqual("a%2Fb%3Bc%3Ad%25e", escaped)
        self.assertIsNotNone(FILENAMEABLE_RE.fullmatch(escaped))

    def test_no_collisions(self) -> None:
        # NOTE (mristin):
        # The percent sign must be escaped as well, or the two names would end up
        # in the same directory.
        self.assertNotEqual(
            escape_for_filename("model:tag"), escape_for_filename("model%3Atag")
        )


if __name__ == "__main__":
    unittest.main()
