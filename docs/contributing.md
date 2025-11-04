# Contributing to APS (Agent Packaging Standard)

Welcome! APS is an open standard and community-driven initiative to enable a universal agent packaging + registry ecosystem.

We welcome contributions across:
- Core standard (specs, manifests)
- CLI tooling
- Registry service
- SDKs
- Examples + docs
- Security extensions
- Compliance & ecosystem alignment (MCP, AGP, TDF, NIST AI RMF, ISO 42001, EU AI Act, GDPR)

---

## 🚀 Quick Start (for contributors)

### 1) Fork + clone
```bash
git clone https://github.com/<your-username>/agent-packaging-standard.git
cd agent-packaging-standard
```
### 2) Set up virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e cli/
pip install -e registry/
```
### 3) Run tests
```bash
pytest -q
```
### 4) Verify CLI works
```bash
echo '{"text":"hello"}' | aps run examples/echo-agent
```

## Project Structure
```bash
/cli         → APS CLI
/registry    → APS local registry server
/specs       → Standard and drafts
/examples    → Runnable example agents
/docs        → Documentation site
```
## Development Workflow
### Branch strategy
```bash
feature/<area>-<short-name>
fix/<bug>
docs/<doc>
```
PR checklist:

    - Tests added or updated

    - Code is formatted (ruff + black)

    - Docs updated if needed

    - No failing lint/test jobs

## Commit Style (Conventional)
```bash
feat: add streaming mode
fix: solve registry thread issue
docs: add developer onboarding
test: add pytest resolver tests
refactor: split registry handler
```

## Design Principles
    - Simple first

    - Spec > Code

    - Security & Trust by design

    - Open, modular, portable

    - No cloud lock-in

## Communication
Discussion channels TBD — until then:

    - Use GitHub Issues & PRs

    - Add RFC: for large proposals

## Code of Conduct
Be civil. No harassment. No trolling.
APS is a professional standards effort.
Thank you for contributing to the future of open agents!