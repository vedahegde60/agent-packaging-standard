---
title: "Agent Packaging Standard (APS)"
description: "An open, vendor-neutral specification for packaging, distributing, and governing AI agents across platforms."
last_updated: 2025-11-09
---

# Agent Packaging Standard (APS)

## Abstract

The **Agent Packaging Standard (APS)** defines a vendor-neutral, interoperable format for describing, packaging, and distributing AI agents.  
It provides a consistent framework for enterprises and developers to publish, inspect, and execute agents across diverse runtime environments with predictable behavior and verifiable provenance.

APS introduces a lightweight, OCI-inspired model for agents—enabling them to be **portable, inspectable, and policy-enforced** across platforms and organizations.

---

## 1. Introduction

AI agent ecosystems today lack a unified packaging and execution model.  
Each framework defines its own manifest schema, runtime semantics, and governance process, resulting in fragmentation and limited interoperability.

The **Agent Packaging Standard (APS)** addresses this gap by defining:

- A consistent **manifest specification** (`agent.yaml`) that describes the agent’s identity, inputs, outputs, and runtime context.  
- A **portable package format** (`.aps.tar.gz`) for distributing agents and associated metadata.  
- A **registry API** for discovery, publication, and retrieval of agent packages.  
- Optional **signing and provenance extensions** to establish trust and traceability.

APS does not replace existing agent frameworks or orchestration layers.  
Instead, it serves as a **common substrate** that allows tools, runtimes, and marketplaces to interoperate through a shared packaging and execution protocol.

---

## 2. Scope

The APS specification defines:

- The **core agent package format** and directory structure.  
- The **manifest schema** (versioned YAML format).  
- The **minimum runtime behavior** expected of APS-compliant systems.  
- The **registry API** endpoints for push/pull operations.  
- Recommended extensions for **security, provenance, and policy enforcement**.

This standard does **not** prescribe how agents are implemented, trained, or hosted.  
It focuses solely on packaging, metadata, and interoperability primitives.

---

## 3. Design Goals

| Goal | Description |
|------|--------------|
| **Portability** | Enable any APS-compliant runtime to execute an agent without modification. |
| **Transparency** | Allow human and machine inspection of agent metadata, dependencies, and versions. |
| **Verifiability** | Support signatures and provenance statements to ensure build integrity. |
| **Compatibility** | Complement, not replace, existing frameworks (e.g., MCP, LangChain, Swarm). |
| **Simplicity** | Maintain minimal friction for developers adopting APS for new or existing agents. |

---

## 4. Specification Overview

| Component | Description |
|------------|-------------|
| **Manifest (`agent.yaml`)** | Defines the agent’s metadata, interface, runtime, and dependencies. |
| **Package (`.aps.tar.gz`)** | Bundle of source files, manifest, and metadata; portable unit for distribution. |
| **Registry API** | REST endpoints for publishing and retrieving APS packages. |
| **Runtime Execution** | Defines how APS-compatible runtimes load and invoke packaged agents. |
| **Provenance** | Optional metadata block supporting signature and integrity verification. |

A full technical specification is provided in [APS v0.1 Specification](./specs/APS-v0.1.md).

---

## 5. Getting Started

For quick installation and usage instructions, see [Getting Started](./getting-started.md).

```bash
# Example: run a simple agent
aps run examples/echo-agent

# Example: publish to registry
aps publish examples/echo-agent
````

Additional examples demonstrating APS interoperability are available under [Examples](./examples/).

---

## 6. Conformance and Versioning

APS follows [Semantic Versioning](https://semver.org/) principles.
Conformance requirements for runtimes and registries are defined in the specification.
Minor revisions (e.g., `v0.1 → v0.2`) may introduce additional fields but will not break backward compatibility.

---

## 7. Governance

The APS project is maintained under an open governance model.
Decisions are made by consensus among maintainers and community contributors, following transparent review and versioning practices.

For participation guidelines, see [Governance](./standards/governance.md) and [Contributing](./contributing.md).

---

## 8. Contact

📬 **General inquiries:** [contact@agentpackaging.org](mailto:contact@agentpackaging.org)
🧑‍💻 **Community contributions:** [community@agentpackaging.org](mailto:community@agentpackaging.org)
🔐 **Security and provenance:** [security@agentpackaging.org](mailto:security@agentpackaging.org)

Project repository: [github.com/vedahegde60/agent-packaging-standard](https://github.com/vedahegde60/agent-packaging-standard)

---

*© 2025 Agent Packaging Standard (APS) Working Group. All rights reserved.*

