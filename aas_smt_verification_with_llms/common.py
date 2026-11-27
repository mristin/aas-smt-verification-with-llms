# SPDX-FileCopyrightText: 2025 aas-smt-verification-with-llms AUTHORS
#
# SPDX-License-Identifier: MIT

"""Provide common data structures used both in the program and the experiments."""

import re
from typing import cast, NoReturn

from icontract import require


class NonEmptyStr(str):
    """Represent a string with at least one character."""

    __slots__ = ()

    @require(lambda value: len(value) > 0)
    def __new__(cls, value: str) -> "NonEmptyStr":
        return cast(NonEmptyStr, value)


FILENAMEABLE_RE = re.compile("[^/;:]+")


class Filenameable(str):
    """Represent an immutable string appropriate as a filename."""

    __slots__ = ()

    @require(lambda value: FILENAMEABLE_RE.fullmatch(value) is not None)
    def __new__(cls, value: str) -> "Filenameable":
        return cast(Filenameable, value)


def assert_never(value: NoReturn) -> NoReturn:
    """
    Signal to mypy to perform an exhaustive matching.

    Please see the following page for more details:
    https://hakibenita.com/python-mypy-exhaustive-checking
    """
    raise AssertionError(f"Unhandled value: {value} ({type(value).__name__})")
