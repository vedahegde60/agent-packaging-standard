
## ✅ `docs/standards/mapping.md`

```md
# APS ↔ Agent Card ↔ Ecosystem Mapping

## Overview

APS = **machine-readable packaging + execution contract**  
Agent Card = **human-readable capability & trust profile**

APS does **what OCI did for containers**, Agent Card is like **PyPI package page + model card**.

---

## Field Mapping

| Concept | Agent Card (human) | APS Manifest (machine) | Notes |
|---------|--------------------|------------------------|-------|
Identity  | name, version, publisher | id, name, version, summary | Human vs system identifiers |
Purpose | description, use cases | summary | Card has richer narrative |
Inputs/Outputs | prose + examples | JSON schema in `capabilities.inputs/outputs` | APS ensures runtime contract |
Execution | narrative | `runtimes`, `entrypoint` | APS enforces portability |
Tools | list, links | (future) `tools[]` mapped to MCP | APS formalizes tool interface |
Security & Trust | safety notes, risks | `policies`, signatures | APS enables enterprise gating |
Compliance | human claims | (future) structured claims | Card cites; APS verifies artifacts |
Monetization | price, model | (future) monetization block | Optional, marketplace-friendly |
Support | maintainer | N/A | Operational, not spec concern |

---

## Standards Position

| Layer | Standard |
|---|---|
Human metadata | **Agent Card** |
Packaging & run | **APS Manifest** |
Tools / Capabilities | **MCP** |
Agent-to-Agent messaging | **AGP** |
Tasks / Workflows | **TDF** |
Governance / Risk | **NIST AI RMF**, **ISO/IEC 42001** |
Regulation | **EU AI Act**, **GDPR/HIPAA/CCPA** |

---

## Architecture

```mermaid
flowchart TB
  CARD[Agent Card] --> MANIFEST[APS Manifest]
  MANIFEST --> REG[APS Registry]
  MANIFEST --> RUNTIME[APS Runtime]

  MCP[MCP Tools] --> MANIFEST
  AGP[AGP Messaging] --> MANIFEST
  TDF[TDF Tasks] --> MANIFEST

  NIST[NIST RMF] --> CARD
  ISO[ISO 42001] --> CARD
  EU[EU AI Act] --> CARD
  PRIV[GDPR/HIPAA] --> CARD

