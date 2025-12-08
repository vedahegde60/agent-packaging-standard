# APS Testing Guide

This document describes how to test APS components: CLI, registry, manifests, and reference agents.

APS emphasizes **predictable behavior**, **reproducibility**, and **spec compliance**, so testing is core to the project.

---

## ⚠️ Required Testing Before Committing Code

**Before committing any code changes, you MUST:**

1. **Run all automated tests** (fast, ~8 seconds):
   ```bash
   cd cli
   pytest tests/ -v
   ```
   All tests must pass (15 passed, 1 skipped).

2. **Run registry integration test manually** (requires setup):
   ```bash
   # One-time setup (if not already done):
   pip install fastapi uvicorn python-multipart
   cd registry && pip install -e . && cd ../cli
   
   # Run registry test:
   RUN_REGISTRY_TEST=1 pytest tests/test_e2e_workflow.py::test_registry_integration -v
   ```
   Registry test must pass with "🎉 Registry integration test passed!"

**Why both?**
- Automated tests catch most issues quickly
- Registry test validates the full publish/pull workflow with a real server
- Both are required to ensure end-to-end functionality

**CI/CD Note:** CI only runs automated tests (no registry). Manual registry testing before commit ensures quality.

---

## 🧠 Testing Philosophy

| Principle | Description |
|---|---|
Spec-driven | Tests verify APS behavior from the spec, not implementation details  
No network | Tests must not require internet or external servers  
Fast & local | Expect all tests to run < 3 seconds  
Isolated | Temporary filesystem + mocked HTTP + local cache only  
Deterministic | No randomness, timestamps ignored unless specified  
Cross-platform | Must work on macOS, Linux, and CI containers  

---

## 🧪 Tools & Conventions

| Item | Value |
|---|---|
Test framework | `pytest`  
Temp files | `tmp_path` fixture  
HTTP mocking | `monkeypatch` replacing `requests.get/post`  
CLI exit checks | Assert return codes  
Streams | Use pipe simulation via `subprocess`  

### Directory Structure

cli/tests/
registry/tests/
examples/tests/ (future)


---

## ▶️ Running Tests

```bash
pytest -q
```
To display print() statements while debugging:
```bash
pytest -s
```

To run only CLI tests:
```bash
pytest cli/tests
```

## Temporary Files & Cache

APS uses $HOME/.aps/cache/ normally.
Tests must not pollute real home.

Use monkeypatch:
```bash
monkeypatch.setattr(app, "CACHE_DIR", tmp_path / ".aps" / "cache")
```

## Mocking Registry HTTP

Example pattern:
```bash
def fake_get(url, timeout=10):
    return DummyResp({"id": "dev.echo", "version": "0.1.0"})

monkeypatch.setattr(app, "requests", types.SimpleNamespace(get=fake_get))
```

DummyResp is a small helper class in tests.
## Stream Run Testing

Streaming agents emit intermediate lines followed by final JSON.

Test strategy:
```bash
proc = subprocess.Popen([...], stdin=PIPE, stdout=PIPE)
out = proc.communicate(b'{"input": "hello"}')[0].decode()
assert '"status": "ok"' in out
```
## Manifest Validation Tests

Validate that:

    - Required fields present

    - APS version correct

    - Runtime entries valid

    - Entrypoint exists

    - Reject invalid keys

Example:
```bash
mf = tmp_path/"aps"/"agent.yaml"
mf.write_text("aps_version: '0.1'\n", encoding="utf-8")
assert validate(str(tmp_path)) == 0
```

## CLI Subparser Tests

Tests guarantee stable CLI behavior.

    - Help prints

    - Unknown commands error

    - Flags resolve correctly

    - Stream flag toggles code path

Example:
```bash
out = subprocess.run(["aps", "--help"], capture_output=True)
assert out.returncode == 0
assert b"Usage:" in out.stdout
```

## Registry Tests

Key API tests:
| Endpoint          | Test                               |
| ----------------- | ---------------------------------- |
| `/v1/search`      | returns IDs + metadata             |
| `/v1/agents/<id>` | returns version / info             |
| `/v1/publish`     | accepts valid tar, rejects invalid |

Use fast in-process server where possible.

## Expected Test Coverage
| Area                 | Status                 |
| -------------------- | ---------------------- |
| CLI manifest parser  | ✅                      |
| Registry resolver    | ✅                      |
| Cache logic          | ✅                      |
| Build & publish      | ✅ basic                |
| Stream mode          | ✅ minimal              |
| Error handling       | ✅ basic                |
| Registry server      | ⏳ expand soon          |
| Security validations | 🚧 future APS versions |
Goal: >80% line coverage before GA (future CI).

## Test Rules Checklist

    - No external network

    - No real home dir modification

    - No long-running subprocesses

    - Deterministic output

    - Mock time when needed

    - Validate APS compliance, not implementation quirks

## CI Roadmap (future)
| Milestone                          | Target        |
| ---------------------------------- | ------------- |
| CI lint + unit tests               | Alpha+2 weeks |
| Integration tests (pull/build/run) | Alpha+1 month |
| Package signing tests              | APS v0.2      |
| Performance regression harness     | APS v0.3      |

## Summary

You now know how to:

    - Run the APS test suite

    - Mock the registry + filesystem

    - Write new tests with pytest

    - Validate real APS specification rules

Want examples? See cli/tests/test_registry_resolver.py.