# APS Runtime Extensions

APS agents are **language-agnostic**.  
A runtime defines **how to execute an agent’s entrypoint**.

This document explains how runtimes plug into APS.

---

## Goals

| Requirement | Why |
|---|---|
Language-agnostic | Python, JS, Go, Rust, Bash, JVM |
Deterministic contract | Same I/O everywhere |
Simple extension | Add a runtime without patching APS core |
Secure execution path | Upgrade to sandbox/container mode |

---

## Runtime Definition in Manifest

```yaml
runtimes:
  - kind: python
    entrypoint: "python main.py"
  - kind: node
    entrypoint: "node index.js"
```
## Rules
| Field             | Meaning                       |
| ----------------- | ----------------------------- |
| `kind`            | runtime identifier string     |
| `entrypoint`      | command or array              |
| (optional) `env`  | runtime-specific env vars     |
| (optional) `args` | static args passed to process |

APS selects the first matching runtime.
---
## I/O Contract (Universal)
| Channel | Usage                      |
| ------- | -------------------------- |
| STDIN   | Full JSON request          |
| STDOUT  | Logs + final JSON response |
| STDERR  | Logs only (never protocol) |

Example final frame:
```json
{"status":"ok","outputs":{"text":"hello"}}
```
---
## Runtime Loading Logic
1. APS CLI detects runtime by:

2. Checking manifest runtimes list

3. Validating entrypoint exists in agent root

4. Injecting runtime env vars

5. Launching entrypoint as subprocess

## Environment Variables
APS injects:
| Var                 | Purpose                    |
| ------------------- | -------------------------- |
| `APS_AGENT_ROOT`    | root dir                   |
| `APS_AGENT_VERSION` | package version            |
| `APS_RUNTIME_KIND`  | `python`, `node`, etc      |
| `APS_STREAM_MODE`   | `"true"` if streaming mode |
| `APS_TEMP_DIR`      | scratch space              |

Language runtimes must not depend on host global state.
---
## Runtime Extension API (Conceptual)
To add a new runtime, you implement:
```rust
runtime = {
  detect(agent_dir) -> bool
  command(agent_dir) -> [cmd tokens]
  prepare_env(agent_dir) -> env dict
}
```
## Example: Python Runtime
### Manifest
```yaml
runtimes:
  - kind: python
    entrypoint: "python main.py"
```
### Launch behavior
```bash
PYTHONPATH=<agent>/src:$PYTHONPATH python main.py
```
---
## Example: Node Runtime
### Manifest
```yaml
runtimes:
  - kind: node
    entrypoint: "node index.js"
```
### Launch behavior
```bash
NODE_PATH=<agent>/src:$NODE_PATH node index.js
```
## Minimal Runtime Checklist
| Feature                         | Required |
| ------------------------------- | -------- |
| Reads JSON from STDIN           | ✅        |
| Writes JSON to STDOUT           | ✅        |
| Supports streaming lines        | ✅        |
| No global state                 | ✅        |
| No network unless agent chooses | ✅        |
| Final JSON frame ends process   | ✅        |

Summary

Runtimes in APS:

  - Declare entrypoints

  - Follow I/O contract

  - Are isolated by design

  - Are extensible without central control

  - Make APS portable across ecosystems

You can now write agents in any language that speaks streams + JSON.