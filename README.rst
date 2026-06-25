******************************
aas-smt-verification-with-llms
******************************

.. image:: https://github.com/mristin/aas-smt-verification-with-llms/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/mristin/aas-smt-verification-with-llms/actions/workflows/ci.yml
    :alt: Continuous integration

Verify AAS Submodel Templates using Large Language Models.

Installation
============
Check out the repository and change to its directory.

Create a virtual environment:

.. code-block::

    python -m venv venv

Activate it (on Windows):

.. code-block::

    venv/Scripts/activate

... or on Unix:

.. code-block::

    source venv/bin/activate

Install the dependencies:

.. code-block::

    pip3 install .

You can now run ``aas-smt-verification-with-llms`` (see ``--help`` section below).

``--help``
==========

.. Help starts: aas-smt-verification-with-llms --help
.. code-block::

    usage: aas-smt-verification-with-llms [-h] --aas_environment_path
                                          AAS_ENVIRONMENT_PATH [--version]
                                          {openai,ollama} ...

    Verify AAS Submodel Templates using Large Language Models.

    positional arguments:
      {openai,ollama}       Choose the LLM backend
        openai              Use OpenAI (ChatGPT) models
        ollama              Use a local Ollama model

    options:
      -h, --help            show this help message and exit
      --aas_environment_path AAS_ENVIRONMENT_PATH
                            Path to the AAS environment which should be verified
      --version             show the current version and exit

.. Help ends: aas-smt-verification-with-llms --help

Contributing
============
See `CONTRIBUTING.rst`_.

.. _CONTRIBUTING.rst: https://github.com/mristin/aas-smt-verification-with-llms/tree/main/CONTRIBUTING.rst

Experiments
===========
For experiment set up, see `EXPERIMENTS.rst`_.

.. _EXPERIMENTS.rst: https://github.com/mristin/aas-smt-verification-with-llms/tree/main/EXPERIMENTS.rst

The datasheet to the dataset is available at `DATASHEET.md`_.

.. _DATASHEET.md: https://github.com/mristin/aas-smt-verification-with-llms/tree/main/DATASHEET.rst
