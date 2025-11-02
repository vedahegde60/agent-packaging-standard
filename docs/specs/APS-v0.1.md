Draft v0.1 — Public circulation permitted

# APS v0.1 (working draft)
*(Working title: Agent Packaging Standard — APS)*

## Core ideas
- Manifest file: `aps/agent.yaml`
- Runnable interfaces: local process (stdin/stdout JSON), or remote HTTP (`aps-http-v1`)
- Capability metadata: inputs/outputs schemas + tools
- Adapters: bring-your-own data/vector/cache connectors
- Policies: network egress allowlist, PII, logging/telemetry
- Provenance & signing: optional DSSE/in-toto
- Monetization metadata (optional)
- Versioning: semver; breaking I/O requires MAJOR bump

## Manifest (`aps/agent.yaml`) — minimal example
```yaml
aps: "0.1"
id: "com.example.docqa"
name: "DocQA"
summary: "RAG over your docs."
version: "1.2.0"
runtimes:
  - kind: "python"
    entrypoint: ["python", "-m", "docqa.main"]
capabilities:
  inputs:
    schema: { type: object, properties: { query: { type: string } }, required: ["query"] }
  outputs:
    schema: { type: object, properties: { answer: { type: string } }, required: ["answer"] }
  tools: []
policies:
  network: { egress: [] }

