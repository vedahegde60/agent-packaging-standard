# APS Architecture (draft)

APS defines a portable way to package agents with a manifest and a runtime contract.

## High-level

```mermaid
flowchart LR
  Dev[Developer] --> |publish agent + manifest| Repo[(Git/Registry)]
  User[User / CI] --> |search/install| Repo
  User --> |aps run <agent-root>| CLI[APS CLI]
  CLI --> |stdin JSON| Agent[Agent Entrypoint]
  Agent --> |stdout JSON| CLI
```

```mermaid
graph TD
  A[agent-root] --> B[aps/agent.yaml]
  A --> C[src/...]
  A --> D[assets/models (optional)]
  A --> E[README.md]
```

```mermaid
sequenceDiagram
  participant U as User
  participant CLI as APS CLI
  participant AG as Agent Entrypoint

  U->>CLI: aps run <agent-root> (stdin JSON)
  CLI->>AG: launch entrypoint
  AG-->>CLI: stdout JSON response
  CLI-->>U: prints response
```