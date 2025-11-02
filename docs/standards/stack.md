
# APS in the Standards Landscape

```mermaid
flowchart TB

  subgraph Human["Human Description"]
    CARD[Agent Card (Markdown)]
  end

  subgraph Packaging["Packaging & Execution"]
    MANIFEST[aps/agent.yaml]
    POLICIES[Policies: network, pii, telemetry]
    PROV[Provenance: signatures, DSSE, in-toto]
  end

  subgraph Interop["Interop Protocols"]
    MCP[MCP: tool APIs]
    AGP[AGP: agent messaging]
    TDF[TDF: task schema]
  end

  subgraph Governance["Governance & Compliance"]
    NIST[NIST AI RMF]
    ISO[ISO/IEC 42001]
    EU[EU AI Act]
    PRIV[GDPR/HIPAA/CCPA]
  end

  REG[APS Registry API]
  RUNTIME[Runtime (local/VPC/hosted)]

  CARD --> MANIFEST
  MANIFEST --> REG
  MANIFEST --> RUNTIME

  MCP --> MANIFEST
  AGP --> MANIFEST
  TDF --> MANIFEST

  PROV --> REG
  POLICIES --> RUNTIME

  NIST --> CARD
  ISO --> CARD
  EU --> CARD
  PRIV --> CARD
