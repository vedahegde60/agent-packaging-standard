---
title: "Agent Packaging Standard (APS) — Specification v0.1"
description: "Technical specification defining the manifest schema, package format, and runtime behavior for the Agent Packaging Standard (APS)."
version: "0.1"
last_updated: 2025-12-07
---

# Agent Packaging Standard (APS) — Specification v0.1

## 1. Introduction

The **Agent Packaging Standard (APS)** defines an interoperable format for describing, packaging, and distributing AI agents.  
This specification establishes the canonical structure of an APS package, the required metadata schema, and the minimum expectations for the APS-compliant runtimes and registries.

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
| `dependencies` | map | Optional runtime dependencies or requirements. |
| `environment` | map | Optional environment variable declarations. |
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
### 4.4. Dependencies

Agents MAY declare dependencies to describe what they require from the execution environment.
These are **descriptive hints**, not installation instructions, in APS v0.1.

#### 4.4.1 Runtime Dependencies

Runtime dependencies describe the execution environment (Python version, OS packages, etc.):

```yaml
dependencies:
  python: ">=3.10"
  packages:
    - "scikit-learn>=1.3"
    - "requests>=2.31"
  system:
    - "tesseract"
    - "ffmpeg"
```
- python (string) — minimum required interpreter version.
- packages (list of strings) — language-level dependencies (e.g., pip packages).
- system (list of strings) — system-level tools or libraries the agent expects.

APS v0.1 does not define auto-install behavior. Runtimes MAY use this information for validation or environment provisioning.

#### 4.4.2 Model Dependencies
Agents MAY declare which models they depend on (LLMs, embedding models, etc.):
```yaml
dependencies:
  models:
    - id: "openai:gpt-4o-mini"
      provider: "openai"
      family: "gpt-4"
      purpose: "llm"
      required: true

    - id: "openai:text-embedding-3-small"
      provider: "openai"
      purpose: "embeddings"
      required: false
```

Recommended fields:
- id (required, string)
  Opaque identifier for the model, such as:

  - openai:gpt-4o-mini
  - bedrock:anthropic.claude-3.5
  - local:my-custom-model

- provider (optional, string)
  Logical provider name (e.g., openai, bedrock, vertex).
- family (optional, string)
  Model family name (e.g., gpt-4, llama-3).
- purpose (optional, string)
  High-level role, e.g. llm, embeddings, reranker, classifier.
- required (optional, boolean, default: true)
  Indicates whether this model must be available for the agent to function.
Runtimes and policy engines MAY use dependencies.models to:
- Validate whether a deployment environment can satisfy the agent,
- Route agents to appropriate backends (e.g., an OpenAI-capable runtime),

- Enforce governance around which models are allowed.
APS v0.1 does not prescribe how models are provisioned.

#### 4.4.3 Dataset/Index Dependencies
Agents MAY declare external datasets, indexes, or other data resources they require:
```yaml
dependencies:
  datasets:
    - id: "registry://datasets/resume-ingestion-index"
      kind: "vector_index"
      required: true

    - id: "s3://my-bucket/resume-schema.json"
      kind: "schema"
      required: false
```
Recommended fields:
- id (required, string)
  URI or identifier for the dataset or resource, e.g.:
  - registry://datasets/resume-ingestion-index
  - s3://my-bucket/resume-schema.json
  - https://example.com/knowledge-base.json

- kind (optional, string)
  Logical type such as vector_index, corpus, schema, config.
- required (optional, boolean, default: true)
  Indicates whether this resource is required for the agent to function.

Runtimes SHOULD treat these values as declarative metadata:
they MAY validate presence or reachability, but APS does not dictate fetching or mounting behavior in v0.1.

### 4.5 Relationship to Environment Configuration

dependencies describe what an agent needs conceptually.

Concrete configuration for accessing models and datasets (e.g., API keys, endpoints, regions) SHOULD be declared under environment, for example:
```yaml
environment:
  required:
    - name: OPENAI_API_KEY
      description: "API key for model dependencies under dependencies.models"
  optional:
    - name: RAG_INDEX_URI
      default: "registry://datasets/resume-ingestion-index"
      description: "Override default dataset index location"
```
This separation allows APS manifests to remain portable while deployment-specific details are provided via environment variables or runtime configuration.
---


## 5. Runtime Behavior

A compliant APS runtime **MUST**:

1. Accept an APS package (local path or registry reference).
2. Validate the manifest schema and structure.
3. Resolve dependencies defined in `agent.yaml`.
4. Execute the declared entrypoint according to the specified runtime.
5. Capture and return outputs in JSON format.

### 5.1 Entrypoint Invocation

The runtime **MUST** invoke the entrypoint by prepending the appropriate interpreter command based on the `runtime` field:

- `runtime: python3` → execute as `python <entrypoint>`
- `runtime: nodejs` → execute as `node <entrypoint>`
- `runtime: bash` → execute as `bash <entrypoint>`

The working directory **MUST** be set to the package root, and the `src/` directory (if present) **SHOULD** be added to the language-specific module path (e.g., `PYTHONPATH` for Python).

### 5.2 Example Invocation

```bash
echo '{"text": "hello"}' | aps run examples/echo-agent
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
