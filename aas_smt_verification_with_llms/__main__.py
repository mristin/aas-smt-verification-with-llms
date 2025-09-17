"""Run aas-smt-verification-with-llms as Python module."""

import aas_smt_verification_with_llms.main

if __name__ == "__main__":
    # The ``prog`` needs to be set in the argparse.
    # Otherwise, the program name in the help shown to the user will be ``__main__``.
    aas_smt_verification_with_llms.main.main(prog="aas_smt_verification_with_llms")
