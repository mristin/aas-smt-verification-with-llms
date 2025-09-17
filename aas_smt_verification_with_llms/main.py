"""Verify AAS Submodel Templates using Large Language Models."""

import argparse
import sys

import aas_smt_verification_with_llms

assert aas_smt_verification_with_llms.__doc__ == __doc__


def main(prog: str) -> int:
    """
    Execute the main routine.

    :param prog: name of the program to be displayed in the help
    :return: exit code
    """
    parser = argparse.ArgumentParser(prog=prog, description=__doc__)
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

    return 0


def entry_point() -> int:
    """Provide an entry point for a console script."""
    return main(prog="aas-smt-verification-with-llms")


if __name__ == "__main__":
    sys.exit(main(prog="aas-smt-verification-with-llms"))
