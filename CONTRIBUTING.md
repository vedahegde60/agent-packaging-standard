# Contributing

Thank you for considering a contribution!

## Getting started

```bash
git clone <your-repo-url>
cd agent-packaging-standard/cli
python -m venv .venv && source .venv/bin/activate
pip install -e .
```
## Development areas

    - Spec (specs/) — propose fields, schemas, examples
    - CLI (cli/) — lint, init, run stubs, validators
    - Examples (examples/) — minimal agents using the spec

## Guidelines

    - Small, focused PRs
    - Add tests where practical (schema validation, CLI exit codes)
    - Keep docs updated (README, examples)
    - Be kind in code reviews

## Commit message convention

    - Use clear, conventional messages, e.g.:
    - spec: clarify policies.network semantics
    - cli: add runtime check for entrypoint existence
    - examples: add python summarizer agent

## Code style

    - Python: standard library + pyyaml
    - Avoid heavy deps in the CLI
    - Prefer clarity over cleverness