# SPDX-FileCopyrightText: 2025 aas-smt-verification-with-llms AUTHORS
#
# SPDX-License-Identifier: MIT

"""Provide common data structures used both in the program and the experiments."""

import io
import re
import xml.etree.ElementTree
from typing import cast, NoReturn, Final, Sequence, Union, List, Optional

from icontract import ensure, require


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


@ensure(lambda result: FILENAMEABLE_RE.fullmatch(result) is not None)
def escape_for_filename(text: str) -> Filenameable:
    """
    Escape the ``text`` so that it can be used as a filename.

    We percent-encode only the characters forbidden in :py:class:`Filenameable`
    and the percent sign itself, so that the escaping is reversible and
    the common names remain unchanged.

    >>> escape_for_filename("gpt-5-2025-08-07")
    'gpt-5-2025-08-07'

    >>> escape_for_filename("qwen3:1.7b")
    'qwen3%3A1.7b'

    >>> escape_for_filename("hf.co/org/model:Q4_K_M")
    'hf.co%2Forg%2Fmodel%3AQ4_K_M'
    """
    return Filenameable(
        text.replace("%", "%25")
        .replace("/", "%2F")
        .replace(";", "%3B")
        .replace(":", "%3A")
    )


def assert_never(value: NoReturn) -> NoReturn:
    """
    Signal to mypy to perform an exhaustive matching.

    Please see the following page for more details:
    https://hakibenita.com/python-mypy-exhaustive-checking
    """
    raise AssertionError(f"Unhandled value: {value} ({type(value).__name__})")


class Path:
    """Represent an ID-short path."""

    fragments: Final[Sequence[Union[str, int]]]

    def __init__(self, fragments: Sequence[Union[str, int]]) -> None:
        self.fragments = fragments

    def __str__(self) -> str:
        if len(self.fragments) == 0:
            return ""

        parts: List[str] = []

        iterator = iter(self.fragments)

        first = next(iterator)
        assert first is not None

        parts.append(str(first))

        for fragment in iterator:
            if isinstance(fragment, str):
                parts.append(f".{fragment}")
            elif isinstance(fragment, int):
                parts.append(f"[{fragment}]")
            else:
                assert_never(fragment)

        return "".join(parts)


def sniff_xml_namespace(text: str) -> Optional[str]:
    """
    Determine the XML namespace of the root element in ``text``.

    Return None if the root element has no namespace or ``text`` could not be parsed.
    Only the beginning of ``text`` is parsed, up to the start of the root element.

    >>> sniff_xml_namespace('<environment xmlns="https://admin-shell.io/aas/3/1"/>')
    'https://admin-shell.io/aas/3/1'

    >>> sniff_xml_namespace('<environment/>') is None
    True

    >>> sniff_xml_namespace('<broken') is None
    True
    """
    try:
        for _, element in xml.etree.ElementTree.iterparse(
            io.StringIO(text), events=("start",)
        ):
            tag: str = element.tag
            if tag.startswith("{"):
                return tag[1 : tag.index("}")]

            return None
    except xml.etree.ElementTree.ParseError:
        return None

    return None
