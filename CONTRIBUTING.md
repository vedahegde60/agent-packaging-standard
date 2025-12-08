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

## Pre-Commit Checklist ✅

**Before committing any code changes, complete this checklist:**

- [ ] **Run automated tests:**
  ```bash
  cd cli
  pytest tests/ -v
  ```
  Verify: `15 passed, 1 skipped` (should take ~8 seconds)

- [ ] **Run registry integration test:**
  ```bash
  # One-time setup (if needed):
  pip install fastapi uvicorn python-multipart
  cd registry && pip install -e . && cd ../cli
  
  # Run test:
  RUN_REGISTRY_TEST=1 pytest tests/test_e2e_workflow.py::test_registry_integration -v
  ```
  Verify: Test passes with "🎉 Registry integration test passed!"

- [ ] **Update documentation** if you changed:
  - CLI commands → Update `cli/README.md` and `docs/cli/reference.md`
  - Spec fields → Update `docs/specs/APS-v0.1.md`
  - Testing → Update `docs/testing.md`

- [ ] **Update CHANGELOG** (if applicable)

- [ ] **Git commit** with conventional message:
  ```bash
  git add .
  git commit -m "type: description"
  ```

**Why manual registry testing?**
- CI only runs fast automated tests (no server dependencies)
- Registry test validates full publish/pull workflow
- Catches integration issues before they reach production

## Commit message convention

    - Use clear, conventional messages, e.g.:
    - spec: clarify policies.network semantics
    - cli: add runtime check for entrypoint existence
    - examples: add python summarizer agent

## Code style

    - Python: standard library + pyyaml
    - Avoid heavy deps in the CLI
    - Prefer clarity over cleverness