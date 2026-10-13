# Contributing to sdl2-game-engine-starter

Thanks for wanting to poke at the engine starter. This repo is the Python
scaffolding + build orchestration layer that wraps a C++/SDL2 custom game
engine skeleton. The C++ side lives under `src/engine_cpp/`; the Python side
drives project generation, asset pipeline checks, and build orchestration.

## Ground rules

- Python 3.11+ for the tooling layer. C++17 + SDL2 2.28+ for the engine layer.
- One logical change per PR. Keep diffs tight.
- New handlers go under `src/handlers/`. New services go under `src/services/`.
- Every public function gets a type hint and a docstring that says what it does,
  what it returns, and what it raises. No exceptions.
- Run `pytest -q` before opening a PR. If a test is flaky, fix the test, don't
  retry it.

## Local setup

```bash
python -m venv .venv
. .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -e .[dev]
pytest -q
python -m src.bootstrap.cli --help
```

## Style

- `ruff` for lint, `black` for format, `mypy --strict` for the tooling package.
- C++ side: `clang-format` with the repo `.clang-format`, warnings-as-errors on.
- Commit messages: `area: short imperative summary` (e.g. `handlers: fix asset
  manifest hash collision on duplicate keys`).

## What we do NOT accept

- Vendored SDL2 binaries. Use the system package or the documented fetch step.
- Generated code checked in without the generator script alongside it.
- Silent `except Exception: pass`. Log it or re-raise it.