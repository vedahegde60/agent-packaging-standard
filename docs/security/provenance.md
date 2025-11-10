---
title: "APS Security and Provenance Specification"
description: "Defines integrity, signing, and provenance mechanisms for APS packages to ensure trust, reproducibility, and governance across environments."
version: "0.1"
last_updated: 2025-11-09
---

# APS Security and Provenance Specification

## 1. Introduction

The **Agent Packaging Standard (APS)** incorporates optional security and provenance extensions that enable participants to verify the origin, authenticity, and integrity of agent packages.

This specification defines the structure, generation, and verification of provenance data for APS packages.  
It draws inspiration from industry standards such as the [Open Container Initiative (OCI)](https://opencontainers.org/), [Sigstore](https://sigstore.dev/), and [SLSA Provenance](https://slsa.dev/).

APS aims to ensure that every packaged agent can be **trusted, auditable, and policy-enforced** across environments and organizations.

---

## 2. Scope

This document specifies:

- The **provenance metadata schema** for APS packages.  
- Requirements for **signing, verifying, and attesting** package integrity.  
- How APS-compliant registries and runtimes handle security metadata.  

Encryption, access control, or runtime sandboxing are outside the scope of this specification.

---

## 3. Provenance Overview

APS provenance provides a cryptographically verifiable record of:

- The **origin** of the agent (author, build process, and repository).  
- The **integrity** of the packaged artifact (hash and signature).  
- The **trust policy** under which it was built and published.

Each APS package may include a provenance block in its manifest (`aps/agent.yaml`) or in an accompanying file (`aps/provenance.json`).

---

## 4. Provenance Metadata Schema

### 4.1 YAML Representation (Inline in Manifest)

```yaml
provenance:
  signer: "aps@agentpackaging.org"
  issued_at: "2025-11-09T08:00:00Z"
  signature: "sha256:ab349..."
  digest: "sha256:f9a0..."
  tool: "cosign"
  build:
    repository: "https://github.com/vedahegde60/agent-packaging-standard"
    commit: "c8f62a1"
    environment: "github-actions"
````

### 4.2 JSON Representation (External File)

```json
{
  "signer": "aps@agentpackaging.org",
  "issued_at": "2025-11-09T08:00:00Z",
  "signature": "sha256:ab349...",
  "digest": "sha256:f9a0...",
  "tool": "cosign",
  "build": {
    "repository": "https://github.com/vedahegde60/agent-packaging-standard",
    "commit": "c8f62a1",
    "environment": "github-actions"
  }
}
```

Both representations are equivalent.
When both are present, the external file **SHALL** take precedence.

---

## 5. Signing Requirements

| Requirement             | Description                                                                                     |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| **Signature Algorithm** | APS-compliant runtimes **MUST** support SHA256 digests; additional algorithms MAY be supported. |
| **Signer Identity**     | The `signer` field **MUST** identify the signing entity (email or certificate subject).         |
| **Immutability**        | Once signed, a package version **MUST NOT** be re-signed with modified contents.                |
| **Tooling Interface**   | Signing and verification **MUST** be accessible via the APS CLI (`aps sign`, `aps verify`).     |

### 5.1 Example Commands

```bash
# Sign package using APS CLI
aps sign examples/echo-agent.aps.tar.gz --key cosign.key
```

```bash
# Verify signature
aps verify examples/echo-agent.aps.tar.gz
```

Example output:

```
Signature verification succeeded
Signer: aps@agentpackaging.org
Digest: sha256:f9a0...
Issued: 2025-11-09T08:00:00Z
Tool: cosign
```

---

## 6. Signing Backends

APS provides a **pluggable signing interface**.
CLI commands (`aps sign`, `aps verify`) may delegate to different cryptographic backends.

### Supported Backends (v0.1)

| Backend    | Description                                                                      |
| ---------- | -------------------------------------------------------------------------------- |
| **cosign** | Uses [Sigstore Cosign](https://sigstore.dev/) for key-based and keyless signing. |
| **gpg**    | Uses OpenPGP for local key signing.                                              |
| **none**   | Disables signing for testing and internal builds.                                |

Example with explicit backend selection:

```bash
aps sign examples/echo-agent.aps.tar.gz --with cosign --key cosign.key
aps verify examples/echo-agent.aps.tar.gz --with cosign
```

Backends **MUST** conform to APS provenance schema output.

---

## 7. Verification Behavior

### 7.1 Registry Responsibilities

* Registries **MUST** store provenance metadata alongside package artifacts.
* Registries **SHOULD** reject unsigned packages if configured to enforce signature policies.
* Provenance data **MUST** be retrievable via the Registry API (`/v1/packages`).

### 7.2 Runtime Responsibilities

* APS runtimes **SHOULD** verify signatures prior to execution.
* Verification failures **SHOULD** emit warnings and MAY block execution based on local policy.
* Verification results **MUST** be logged with signer identity and digest.

---

## 8. Policy Integration

APS supports configurable security policies defining how provenance is enforced.

| Policy Level | Description                                                   |
| ------------ | ------------------------------------------------------------- |
| **lenient**  | Execute unsigned agents but log provenance warnings.          |
| **strict**   | Reject unsigned or unverifiable agents.                       |
| **custom**   | Integrate with external attestation services or trust stores. |

Example configuration (`aps-policy.yaml`):

```yaml
policy:
  mode: strict
  required_fields:
    - signer
    - digest
    - issued_at
```

---

## 9. Relationship to Other Standards

| Standard             | Relationship                                                      |
| -------------------- | ----------------------------------------------------------------- |
| **OCI Image Spec**   | APS adopts digest and descriptor conventions from OCI.            |
| **SLSA Provenance**  | APS provenance blocks can map to SLSA Build Level 2 attestations. |
| **Sigstore**         | APS uses Sigstore Cosign as a reference backend.                  |
| **SPDX / CycloneDX** | Compatible for dependency SBOM tracking.                          |

---

## 10. Example End-to-End Workflow

### Step 1. Build and package the agent

```bash
aps build examples/echo-agent
```

### Step 2. Sign the package

```bash
aps sign examples/echo-agent.aps.tar.gz --key cosign.key
```

### Step 3. Publish to registry

```bash
aps publish examples/echo-agent --registry registry://local
```

### Step 4. Verify provenance before execution

```bash
aps verify examples/echo-agent
```

Expected output:

```
Verification succeeded
Signer: aps@agentpackaging.org
Digest: sha256:f9a0...
Issued: 2025-11-09T08:00:00Z
Tool: cosign
```

---

## 11. Conformance Requirements

An APS implementation is **provenance-compliant** if it:

1. Supports signing and verifying using at least one supported backend.
2. Stores provenance data conforming to the schema defined in this document.
3. Exposes provenance metadata via CLI and registry interfaces.
4. Honors configured trust policies during execution.

---

## 12. References

* [APS Specification v0.1](../specs/APS-v0.1.md)
* [APS Registry API](../registry/api.md)
* [Sigstore Cosign](https://sigstore.dev/)
* [SLSA Provenance](https://slsa.dev/spec/v1.0/)
* [SPDX Specification](https://spdx.dev/specifications/)

---

## 13. Contact

📬 **General inquiries:** [contact@agentpackaging.org](mailto:contact@agentpackaging.org)
🔐 **Security disclosures:** [security@agentpackaging.org](mailto:security@agentpackaging.org)
🧑‍💻 **Community contributions:** [community@agentpackaging.org](mailto:community@agentpackaging.org)

---

*© 2025 Agent Packaging Standard (APS) Working Group. All rights reserved.*