# Registry Integration Testing

## Overview

The registry integration test (`test_registry_integration`) is **SKIPPED by default** in CI/CD because it requires starting a real registry server. This approach ensures:

- ✅ Normal automated tests complete quickly (15 tests)
- ✅ No blocking on builds/deployments
- ✅ Optional full integration testing when needed

## Automated Registry Tests (Always Run)

The following registry tests run automatically with `pytest tests/`:

- **test_registry_resolver.py**: Tests registry resolution logic with mocked network calls
  - Path resolution (local vs registry)
  - Cache checking
  - Pull triggering
  - Error handling

These tests verify the registry logic **without** requiring a real server.

## Manual Integration Test

To test the **full registry workflow** with a real server:

### Prerequisites

```bash
# Install registry dependencies
pip install fastapi uvicorn python-multipart

# Install registry package (development mode)
cd registry
pip install -e .
cd ../cli
```

### Option 1: Run just the registry integration test

```bash
cd cli
RUN_REGISTRY_TEST=1 pytest tests/test_e2e_workflow.py::test_registry_integration -v
```

### Option 2: Run ALL tests including registry

```bash
cd cli
RUN_REGISTRY_TEST=1 pytest tests/ -v
```

This test validates:
1. Starting registry server on dynamic port
2. Creating and building an agent
3. Publishing package to registry
4. Pulling package from registry
5. Verifying pulled agent structure

### Expected Output

```
tests/test_e2e_workflow.py::test_registry_integration
Starting registry server on port 54321...
✅ Registry server started on port 54321
✅ Created agent
✅ Built package
✅ Published to registry
✅ Pulled from registry

🎉 Registry integration test passed!
✅ Registry server stopped
PASSED
```

## Manual Testing (Without pytest)

For quick manual testing during development:

```bash
# Terminal 1: Start registry server
cd cli
aps registry serve --port 8080 --root ./test-registry

# Terminal 2: Test publish/pull
cd cli
aps init test-agent
aps build test-agent
aps publish test-agent/dist/dev.test-agent.aps.tar.gz --registry http://localhost:8080
aps pull dev.test-agent --registry http://localhost:8080
```

## CI/CD Configuration

For GitHub Actions or other CI systems:

```yaml
# Normal test run (registry test skipped)
- name: Run tests
  run: |
    cd cli
    pytest tests/ -v

# Optional: Extended testing with registry
- name: Run full integration tests
  run: |
    cd cli
    RUN_REGISTRY_TEST=1 pytest tests/ -v
  # This could be a separate workflow or manual trigger
```

## Why This Approach?

1. **Fast CI/CD**: Normal builds take ~8 seconds, no server startup overhead
2. **No Flakiness**: Mocked tests are deterministic
3. **Optional Validation**: Full integration test available when needed
4. **Better Coverage**: Both unit tests (mocked) and integration tests (real server)
5. **No Manual Steps in Automation**: Default pytest run has no manual requirements

## Test Coverage Summary

| Test Type | Coverage | Requires Server | Always Run |
|-----------|----------|-----------------|------------|
| test_registry_resolver.py | Registry logic | ❌ (mocked) | ✅ Yes |
| test_registry_integration | Full workflow | ✅ Yes | ❌ No (opt-in) |
| Manual testing | Interactive | ✅ Yes | ❌ Manual |
