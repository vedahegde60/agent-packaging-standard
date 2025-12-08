# APS Developer Setup Guide

This guide walks new contributors through installing the APS toolchain, running the registry locally, and validating everything works.

APS is currently reference-implemented in Python.

---

## 🧰 Requirements

| Tool | Version |
|---|---|
Python | 3.10–3.13  
Git | Latest  
OS | macOS / Linux / Windows WSL2  

Optional (recommended):

- `make` (for helper scripts)
- `curl` or `httpie` (API tests)
- `uv` or `pipx` (optional package runner)

---

## 📦 Clone + Configure Environment

```bash
git clone https://github.com/agent-packaging-standard/agent-packaging-standard.git
cd agent-packaging-standard
```
## Create and activate a venv
```bash
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
# or
venv\Scripts\activate          # Windows PowerShell
```

## Install APS CLI + Registry in editable mode
```bash
pip install -e cli/
pip install -e registry/
pip install -r requirements.txt
```

Check install:
```bash
aps --help
```

## Run Tests
```bash
source venv/bin/activate
pytest -q
```

Should end with:

8 passed (or similar)

**Note:** Tests automatically isolate the APS cache and logs to avoid touching your real `~/.aps` directory. BLAS threading is also limited for deterministic CI/test runs.

## Run Local Registry

Start server:
```bash
pip install python-multipart
aps registry serve --root registry_data --port 8080
```

Expected output:

INFO: Uvicorn running at http://127.0.0.1:8080


Leave this terminal open.

## Smoke Test CLI + Registry
### 1) Build example agent
```bash
aps build examples/echo-agent
```

Expected output:
```
examples/echo-agent/dist/dev.echo.aps.tar.gz
```
### 2) Publish
```bash
aps publish examples/echo-agent/dist/dev.echo.aps.tar.gz --registry http://localhost:8080
```

Expected JSON:
```json
{"status": "ok", "agent": {"id": "dev.echo", "version": "0.1.0"}}
```

### 3) Search

```bash
curl "http://localhost:8080/v1/search?q=echo"
```

### Run an agent locally
```bash
echo '{"text":"hello"}' | aps run examples/echo-agent


Expected:

{"status":"ok","outputs":{"text":"hello"}}
```

### Run from registry
```bash
echo '{"text":"hello"}' | aps run registry://dev.echo
```

## Troubleshooting
| Issue                                   | Fix                                        |
| --------------------------------------- | ------------------------------------------ |
| `bash: aps: command not found`          | Activate venv (`source venv/bin/activate`) |
| `Form data requires "python-multipart"` | `pip install python-multipart`             |
| `sqlite3 thread error`                  | Restart registry server                    |
| `pytest fails`                          | Run `pip install -r dev-requirements.txt`  |
| CLI can’t find agent                    | Run `aps pull <id>`                        |


## You're ready to develop APS

Next steps:

  - Read CONTRIBUTING.md

  - Explore cli/src/ and registry/src/

  - Build your own agent in /examples/

  - Thank you for contributing!