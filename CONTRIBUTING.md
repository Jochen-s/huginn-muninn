# Contributing

Thank you for considering a contribution. Please open an issue to discuss a change before you start on it, so we can agree on the approach first.

## Ground rules

- The [Anti-Weaponization Charter](ANTI-WEAPONIZATION-CHARTER.md) applies to every change. Features that profile individuals, act as persuasion engines or manufacture consensus will not be merged, however useful they look.
- Rejected ideas and the evidence that would change the decision are listed in [REJECTIONS.md](REJECTIONS.md). Please check there before proposing one again.
- Claims about research need a citation the reviewer can check. Use "the design calls for" for anything that is not built.

## Development setup

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/), and Node.js (one test builds the gallery). [Ollama](https://ollama.ai) is needed only to run the tool itself, not the tests.

```bash
uv sync --extra dev
uv run pytest -m "not e2e"
```

The `e2e` tests need a running Ollama instance and are skipped in CI.

**Note:** running the test suite rebuilds `gallery/dist/` from the scenario results in `tests/results/`. This repository ships only one of them, so discard that output before committing (`git checkout -- gallery/dist`).

Please also run `uv run pytest tests/test_docs_language.py` after editing the README, the charter or research documents; it checks for pathologising language.

## Pull requests

- Keep each pull request focused on one change, with tests for any behaviour change.
- CI runs the full suite; it must pass.
- By contributing, you agree that your contribution is licensed under the [MIT License](LICENSE).

## Reporting problems

- Security issues: see [SECURITY.md](SECURITY.md).
- Errors in published scenarios or research: see [CORRECTIONS.md](CORRECTIONS.md).
