..
    NOTE (mristin):
    Please keep this file at 72 line width so that we can copy-paste
    the release logs directly into commit messages.

1.0.0rc4 (2026-11-28)
=====================
* Support AAS versions 3.1 and 3.2 (#57)
* Descend into entities, annotations and operations (#58)

We add the command-line argument ``--aas-version`` so that the users
can verify AAS environments against V3.0, V3.1 or V3.2 of the AAS
meta-model. The default is V3.1, as in aas-smt-lint (#57).

We now also descend into all the containers of submodel elements,
including entities, annotated relationship elements and operations,
which we previously silently skipped (#58).

1.0.0rc3 (2026-11-27)
=====================
* Check types against the running Python in mypy (#54)
* Allow colons in model names (#55)

We now accept model names with colons such as Ollama's ``name:tag``
(*e.g.*, ``qwen3:1.7b``) on the command line. The model names are
escaped reversibly wherever they are used in the paths of the
experiments (#55).

We also fix the type checks in CI on Python 3.11 and 3.12 by letting
mypy check against the running Python (#54).

1.0.0rc2 (2026-11-27)
=====================
* Move development tooling to dev/ and add checks (#51)
* Stringify model references as paths (#52)

We fix the crash on semantic IDs given as model references, which we
now render in the same notation as the element paths (#52).

We also move the development tooling under ``dev/`` and extend the
pre-commit checks with ssort, ruff, test coverage and the REUSE
compliance check (#51).

1.0.0rc1 (2026-11-20)
=====================
This is the first release candidate of 1.0.0.
