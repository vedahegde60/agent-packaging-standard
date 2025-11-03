# APS Developer Setup Guide (step-by-step)

This guide gets a new contributor from zero → running APS locally.

## 0) Prerequisites

Git (latest)

Python 3.10+ (3.11 recommended)

macOS/Linux (Windows users: use WSL or PowerShell; notes included)

Verify:
```bash
git --version
python3 --version
```
---

## 1) GitHub access (SSH)

Generate an ed25519 SSH key (recommended):

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# press Enter to accept default (~/.ssh/id_ed25519) and add a passphrase
```

Add your public key to GitHub:
```bash
pbcopy < ~/.ssh/id_ed25519.pub   # macOS (copies to clipboard)
# Linux:
cat ~/.ssh/id_ed25519.pub
```

GitHub → Settings → SSH and GPG keys → New SSH key → paste

Test:
```bash
ssh -T git@github.com
# You should see: "Hi <username>! You've successfully authenticated…"
```

Alt (HTTPS + token): create a fine-grained PAT on GitHub and use https://github.com/<you>/agent-packaging-standard.git with the token as password.

---
## 2) Clone the repo
```bash
cd ~/Documents   # or wherever you keep code
git clone git@github.com:vedahegde60/agent-packaging-standard.git
cd agent-packaging-standard
git remote -v
```
## 3) Create and activate a virtual environment

Recommended: repo-local .venv at the root.

macOS/Linux (bash/zsh):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Confirm:
```bash
which python
python -V
```

You can activate this venv in multiple terminals simultaneously.

## 4) Install APS components (editable)

From repo root:
```bash
pip install --upgrade pip
pip install -e cli -e registry -e sdk

# Runtime deps used by CLI/registry:
pip install cryptography requests PyYAML fastapi uvicorn python-multipart
```

Smoke tests:
```bash
which aps
aps --help
aps --version
```

If aps --help prints nothing, reinstall: pip install -e cli and ensure which aps points to .venv/bin/aps.

## 5) Run the local registry

Terminal A (keep running):
```bash
aps registry serve --root registry_data --port 8080
# Stop with CTRL+C
```

Optional health checks:
```bash
curl 'http://localhost:8080/v1/search?q='
```
## 6) Build & publish an example agent

Terminal B (new window/tab, same venv):
```bash
# Validate example agent
aps validate examples/echo-agent

# Build (artifact lands in ./dist by default)
aps build examples/echo-agent --dist dist

# Publish to local registry
aps publish dist/dev.echo.aps.tar.gz --registry http://localhost:8080

# Search
curl 'http://localhost:8080/v1/search?q=echo'
```

Expected search result:
```bash
{"agents":[{"id":"dev.echo","name":"Echo","version":"0.0.1","summary":"Echoes the input text."}]}
```
## 7) Run an agent locally
```bash
echo '{"aps_version":"0.1","operation":"run","inputs":{"text":"hello"}}' \
  | aps run examples/echo-agent
# -> {"status":"ok","outputs":{"text":"HELLO"}}
```

(Coming soon: aps pull + aps run registry://<id>.)

## 8) Common tasks

Activate venv quickly (alias):
```bash
# add to ~/.zshrc or ~/.bashrc
alias apsenv='cd ~/Documents/agent-packaging-standard && source .venv/bin/activate'
```

Stop registry: press CTRL+C in the window where it runs.
(Planned: aps registry stop using a PID file.)

Reinstall after code changes:
```bash
pip install -e cli
pip install -e registry
pip install -e sdk
```

Lint/format (optional):
```bash
pip install black ruff
black .
ruff check .
```
## 9) Troubleshooting
```bash
aps not found / wrong venv

which aps               # should resolve to .../.venv/bin/aps
pip install -e cli      # reinstall in the active venv
```

FastAPI upload error: python-multipart
```bash
pip install python-multipart
```

SQLite thread error on search
Fixed by using check_same_thread=False + a lock (already in store.py).

Mermaid diagrams not rendering (MkDocs)

Ensure pymdownx.superfences is in mkdocs.yml

Use fenced blocks with ```mermaid (no nesting)

## 10) Suggested dev workflow

Terminal A: registry (aps registry serve …)

Terminal B: build/validate/publish agents

Terminal C: docs (mkdocs serve)

Terminal D: git (branches, commits, PRs)

## 11) Contributing (short)

Fork → create a branch (feat/<topic>)

Write code + tests (examples if user-facing)

Run black + ruff

Commit, push, open a PR

Link issues / add context in PR body

Full details: CONTRIBUTING.md.

## 12) Quick verification checklist

  - aps --help prints

  - aps validate examples/echo-agent prints [validate] OK

  - aps build examples/echo-agent emits dist/<id>.aps.tar.gz

  - Registry serves on http://localhost:8080

  - aps publish … returns {'status': 'ok', ...}

  - curl /v1/search?q=echo returns one result

  - aps run examples/echo-agent echoes/uppercases input

Appendix: Windows (WSL) notes

Use WSL2 with Ubuntu for best results.

Install Python via sudo apt install python3-venv python3-pip.

Activate venv: source .venv/bin/activate.

Use curl via WSL or PowerShell (Invoke-WebRequest).
