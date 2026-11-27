..
    NOTE (mristin):
    Please keep this file at 72 line width so that we can copy-paste
    the release logs directly into commit messages.

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
