# Beginner Guide to APS

Welcome to APS — the Agent Packaging Standard.

This guide is for **new developers** who want a fast, hands-on path to creating, packaging, and running agents using APS.

If you've never worked with APS before, start here.

---

## 🎯 What You Will Learn

- What APS is and why it exists
- Install & set up APS locally
- Build your first APS agent
- Run your agent locally
- Publish & pull agents from a local registry
- Troubleshoot common issues

---

## 🤔 What is APS?

APS is a **universal packaging format for AI agents** — similar to:

| APS | Equivalent |
|---|---|
Agent package | Python wheel / Docker image  
Registry | PyPI / OCI Registry  
CLI | `pip` + `docker` hybrid  
Manifest | `package.json` / `Cargo.toml`  

APS goal:  
**Move agents between platforms with zero friction.**

---

## 📦 Install APS (Developer Mode)

Clone the repo:

```bash
git clone https://github.com/YOUR_ORG/agent-packaging-standard
cd agent-packaging-standard
```

## Create & activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
Install CLI & registry:
```bash
pip install -e cli/
pip install -e registry/
```

Verify install:
```bash
aps --help
aps registry serve --help
```
## Quick Test
### Version check
```bash
aps --version
```
### Validate an example agent
```bash
aps validate examples/echo-agent
```
You should see OK or validation warnings.

## Your First Agent (Echo Example)

Directory structure:
```
examples/echo-agent/
 ├─ aps/
 │   └─ agent.yaml
 └─ src/
     └─ main.py
```

aps/agent.yaml
```bash
aps_version: 0.1
id: dev.echo
name: Echo
version: 0.0.1
summary: Echoes text.
runtimes:
  - kind: python
    entrypoint: python src/main.py
inputs:
  text: {type: string}
outputs:
  text: {type: string}
```

src/main.py
```bash
import sys, json
req = json.loads(sys.stdin.read())
print(json.dumps({"status": "ok", "outputs": {"text": req["input"]["text"]}}))
```

## Build the Agent
```bash
aps build examples/echo-agent --dist dist
```

Output:
```bash
dist/dev.echo.aps.tar.gz
```
## Run the Agent Locally
```bash
echo '{"text":"hello"}' | aps run examples/echo-agent
```

Expected:
```bash
{"status":"ok","outputs":{"text":"hello"}}
```
## Run With Streaming Output (Optional)
```bash
echo '{"text":"hi"}' | aps run --stream examples/echo-agent
```

Streaming is useful for chat-style agents.

## Run a Local Registry
Start registry server:
```bash
aps registry serve --root registry_data --port 8080
```

Publish your agent:
```bash

aps publish dist/dev.echo.aps.tar.gz --registry http://localhost:8080
```

Search:
```bash
curl "http://localhost:8080/v1/search?q=echo"

```
Run remotely:
```bash
echo '{"text":"hi"}' | aps run registry://dev.echo
```
## Common Troubleshooting
| Issue                                      | Fix                                 |
| ------------------------------------------ | ----------------------------------- |
| `aps` not found                            | Activate venv or reinstall CLI      |
| Registry crash asking for python-multipart | `pip install python-multipart`      |
| SQLite thread error                        | Update APS registry (fixed in v0.1) |
| Build shows missing `aps_version`          | Add `aps_version: 0.1` to manifest  |


## You're Ready

Next steps:

    - Read CONTRIBUTING.md

    - Explore examples/

    - Join APS dev chat (coming soon)

    - Build your own agent!
You now have a working APS environment and know how to package and share agents.

Welcome to the APS ecosystem

