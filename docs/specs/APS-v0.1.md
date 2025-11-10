---
title: "Agent Packaging Standard (APS) — Specification v0.1"
description: "Technical specification defining the manifest schema, package format, and runtime behavior for the Agent Packaging Standard (APS)."
version: "0.1"
last_updated: 2025-11-09
---

# Agent Packaging Standard (APS) — Specification v0.1

## 1. Introduction

The **Agent Packaging Standard (APS)** defines an interoperable format for describing, packaging, and distributing AI agents.  
This specification establishes the canonical structure of an APS package, the required metadata schema, and the minimum expectations for APS-compliant runtimes and registries.

APS is **vendor-neutral** and is intended to complement existing agent frameworks and orchestration systems.  
It focuses solely on portability, reproducibility, and governance of agent artifacts.

---

## 2. Terminology

| Term | Definition |
|------|-------------|
| **Agent** | An executable AI component that performs a defined task through one or more models, tools, or workflows. |
| **Manifest** | YAML-formatted file describing an agent’s metadata, interface, and runtime requirements. |
| **Package** | Compressed tarball (`.aps.tar.gz`) containing the manifest, source, and metadata files. |
| **Registry** | A service implementing the APS Registry API for publishing and retrieving agent packages. |
| **Runtime** | Execution environment capable of loading and invoking APS packages according to this specification. |

---

## 3. Package Structure

An APS package is a compressed tar archive (`.aps.tar.gz`) with the following canonical layout:

```

<agent-name>/
├── aps/
│   ├── agent.yaml          # Required manifest
│   ├── README.md           # Optional documentation
│   └── LICENSE             # Optional license information
├── src/                    # Implementation files
└── assets/                 # Optional models, configs, or data

```

All paths are relative to the package root.  
The manifest file (`aps/agent.yaml`) **MUST** exist and conform to the schema defined in Section 4.

---

## 4. Manifest Specification

The manifest is a **YAML-encoded document** that declares an agent’s identity, version, runtime, and I/O schema.

### 4.1 Required Fields

| Field | Type | Description |
|--------|------|-------------|
| `id` | string | Globally unique identifier using reverse-DNS or dotted naming convention (e.g., `examples.echo-agent`). |
| `version` | string | Semantic version (`MAJOR.MINOR.PATCH`). |
| `name` | string | Human-readable agent name. |
| `description` | string | Concise summary of the agent’s purpose. |
| `runtime` | string | Target execution runtime (e.g., `python3`, `nodejs`, `bash`). |
| `entrypoint` | string | Relative path to the executable script or module. |

### 4.2 Optional Fields

| Field | Type | Description |
|--------|------|-------------|
| `author` | string | Author or maintainer name/email. |
| `license` | string | SPDX identifier or license reference. |
| `dependencies` | list | Optional runtime dependencies or requirements. |
| `inputs` | list | Input parameter definitions. |
| `outputs` | list | Output field definitions. |
| `provenance` | map | Optional metadata block for signatures or build provenance. |

### 4.3 Example Manifest

```yaml
id: examples.echo-agent
version: "0.1.0"
name: Echo Agent
description: Simple agent that echoes its input text.
runtime: python3
entrypoint: main.py
inputs:
  - name: text
    type: string
outputs:
  - name: text
    type: string
license: MIT
author: "APS Working Group <contact@agentpackaging.org>"
```

---

## 5. Runtime Behavior

A compliant APS runtime **MUST**:

1. Accept an APS package (local path or registry reference).
2. Validate the manifest schema and structure.
3. Resolve dependencies defined in `agent.yaml`.
4. Execute the declared entrypoint according to the specified runtime.
5. Capture and return outputs in JSON format.

Example invocation:

```bash
aps run examples/echo-agent --input '{"text": "hello"}'
```

Expected output:

```json
{
  "status": "ok",
  "outputs": {
    "text": "hello"
  }
}
```

---

## 6. Registry Specification (Summary)

APS registries provide push/pull capabilities for agents.
Registries **SHALL** expose endpoints compatible with the [APS Registry API](../registry/api.md).

| Operation    | Method | Path            | Description                            |
| ------------ | ------ | --------------- | -------------------------------------- |
| **Publish**  | `POST` | `/v1/push`      | Upload a signed APS package.           |
| **Retrieve** | `GET`  | `/v1/pull/{id}` | Download an APS package by identifier. |
| **List**     | `GET`  | `/v1/packages`  | Enumerate available packages.          |

All registry responses **MUST** include standard JSON metadata (id, version, digest).

---

## 7. Provenance and Signing

APS supports optional provenance blocks to verify artifact integrity.

### 7.1 Provenance Block

```yaml
provenance:
  signature: "sha256:abc123..."
  signer: "aps@agentpackaging.org"
  issued_at: "2025-11-09T10:00:00Z"
  tool: "cosign"
```

### 7.2 Verification Requirements

* Runtimes and registries **SHOULD** verify package signatures.
* Provenance data **MUST NOT** modify package execution semantics.
* Invalid signatures **SHOULD** raise warnings but not block execution unless policy dictates.

---

## 8. Versioning and Compatibility

| Version Component | Meaning                                     | Compatibility Rule |
| ----------------- | ------------------------------------------- | ------------------ |
| **MAJOR**         | Incompatible changes to schema or behavior. | Breaking           |
| **MINOR**         | Backward-compatible additions.              | Non-breaking       |
| **PATCH**         | Bug fixes or clarifications.                | Non-breaking       |

Backward compatibility applies to manifests and registry operations within a major version.

---

## 9. Conformance Requirements

An implementation is considered **APS-compliant** if it:

1. Validates manifests according to this specification.
2. Can execute at least one agent conforming to the manifest schema.
3. Supports registry operations defined in Section 6.
4. Produces deterministic outputs for valid inputs.
5. Optionally supports provenance verification.

---

## 10. References

* [APS Registry API](../registry/api.md)
* [Security and Provenance](../security/provenance.md)
* [Governance](../standards/governance.md)
* [Semantic Versioning](https://semver.org/)
* [Open Container Initiative (OCI) Image Spec](https://opencontainers.org/)

---

## 11. Contact

📬 **General inquiries:** [contact@agentpackaging.org](mailto:contact@agentpackaging.org)
🧑‍💻 **Community contributions:** [community@agentpackaging.org](mailto:community@agentpackaging.org)

---

*© 2025 Agent Packaging Standard (APS) Working Group. All rights reserved.*
