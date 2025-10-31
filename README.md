Draft v0.1 — Public circulation permitted

# (Working title) Agent Packaging Standard (APS)

**Goal:** an open spec + tooling to publish an AI **agent** once and run it anywhere (local, VPC, or remote), with a standard manifest for capabilities, adapters, policies, provenance, and optional monetization.

This repo contains:
- `specs/APS-v0.1.md` — working draft of the spec
- `cli/` — the `aps` CLI (init, lint, run stub)
- `examples/` — reference agents packaged with APS

## Quick start

```bash
# 1) Install CLI (editable)
cd cli && pip install -e .

# 2) Validate the example agent
aps lint ../examples/echo-agent

# 3) Run the example agent (stdin → stdout contract)
echo '{"aps_version":"0.1","operation":"run","inputs":{"text":"hello"}}' \
  | aps run ../examples/echo-agent

# agent-packaging-standard
