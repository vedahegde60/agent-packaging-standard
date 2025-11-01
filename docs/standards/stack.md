
---

# C) Architecture Diagram Showing APS in the Standards Landscape

Drop this into `docs/standards/stack.md`:

```md
# APS in the Standards Landscape

```mermaid
flowchart TB
  subgraph Human
    CARD[Agent Card (Markdown)]
  end

  subgraph Package["Packaging & Execution (APS)"]
    MANIFEST[aps/agent.yaml]
    POLICIES[Policies (network, pii, telemetry)]
    PROV[Signatures + Provenance (DSSE/in-toto)]
  end

  subgraph Interop["Interoperability Protocols"]
    MCP[MCP (tools/capabilities)]
    AGP[AGP (agent↔agent messaging)]
    TDF[TDF (task/workflow schema)]
  end

  subgraph Gov["Governance & Compliance"]
    NIST[NIST AI RMF]
    ISO[ISO/IEC 42001]
    EU[EU AI Act]
    PRIV[GDPR/HIPAA/CCPA]
  end

  REG[APS Registry API]:::reg
  RUNTIME[Runtime (local/VPC/hosted)]

  CARD --> MANIFEST
  MANIFEST --> REG
  MANIFEST --> RUNTIME
  MCP -.tools mapping.-> MANIFEST
  AGP -.endpoints.-> MANIFEST
  TDF -.inputs/outputs.-> MANIFEST
  PROV --> REG
  POLICIES --> RUNTIME
  NIST -.claims/evidence.-> CARD
  ISO -.process claims.-> CARD
  EU -.risk class.-> CARD
  PRIV -.data handling.-> CARD

classDef reg fill:#e8f2ff,stroke:#3b82f6,color:#111;

