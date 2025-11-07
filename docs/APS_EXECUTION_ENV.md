# APS Execution Environment

APS defines **how agents execute**, independent of runtime, OS, or host platform.

Goal: **Run any APS agent anywhere.**

## Execution Modes

| Mode | Description | Use Case |
|---|---|---|
Local | Execute on host | Dev, prototyping |
Sandbox | Execute inside isolated container | Security, enterprise |
Remote | Execute via APS executor service | Cloud/hybrid Orchestration |

APS does **not** mandate sandboxing — but provides hooks for it.

aps run <path> # local
aps exec docker <path> # future
aps exec remote <agent-id> # future


---

## Core Contract

### Inputs
- `stdin`: JSON request
- `env`: runtime variables
- `cwd`: agent root
- `$PYTHONPATH` or language equivalent auto-set

### Outputs
- `stdout`: streaming or final JSON
- `stderr`: logs only (never protocol)

---

## Environment Variables

| Variable | Purpose |
|---|---|
`APS_AGENT_ROOT` | Path to unpacked agent |
`APS_AGENT_ID` | `id` from manifest |
`APS_AGENT_VERSION` | `version` |
`APS_RUNTIME_KIND` | `python`, `node`, etc |
`APS_STREAM_MODE` | `true/false` |
`APS_TEMP_DIR` | Ephemeral workspace |

---

## Runtime Rules

| Rule | Required |
|---|---|
No network unless policy allows | ✅ future policy file |
Agent cannot modify its package | ✅ required |
Working dir = agent root | ✅ enforced |
All state in temp dir | ✅ future |
Final stdout must contain JSON frame | ✅ |

---

## Streaming Protocol (preview)

Lines until final JSON response:

<log or partial> <log> { "status": "...", "outputs": {...} } ```

Future extension: APS-FRAME: JSON\n<data>


