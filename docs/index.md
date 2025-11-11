---
title: "Agent Packaging Standard (APS)"
description: "An open, vendor-neutral specification for packaging, distributing, and governing AI agents across platforms."
last_updated: 2025-11-09
---

# APS — Agent Packaging Standard

**Portable • Auditable • Governable**

The **Agent Packaging Standard (APS)** defines a vendor-neutral, interoperable way to describe, package, and distribute AI agents.  
It provides a consistent framework for enterprises and developers to publish, inspect, and execute agents across diverse runtime environments with predictable behavior and verifiable provenance. 

APS is intentionally **lightweight and OCI-inspired**: agents become **portable, inspectable, and policy-enforced** across platforms and organizations instead of being locked into a single framework, vendor, or runtime.

---

## 🔍 What is APS?

AI agent ecosystems today lack a unified packaging and execution model.  
Each framework defines its own manifest schema, runtime semantics, and governance process, resulting in fragmentation and limited interoperability.

APS addresses this by defining:

- A consistent **manifest specification** (e.g. `agent.yaml` / `aps.yaml`) that describes the agent’s identity, inputs, outputs, and runtime context.  
- A **portable package format** (e.g. `.aps.tar.gz`) for distributing agents and associated metadata.  
- A **registry API** for discovery, publication, and retrieval of agent packages.  
- Optional **signing and provenance extensions** to establish trust and traceability.  

APS does **not** replace existing agent frameworks or orchestration layers.  
Instead, it serves as a **common substrate** that allows tools, runtimes, and marketplaces to interoperate through a shared packaging and execution contract.

---

## 🧭 Design Principles

APS is guided by a small set of core principles:

- **Minimal, not maximal** – APS defines conventions, not a heavyweight platform.  
- **Framework-agnostic** – Works alongside LangChain, LlamaIndex, MCP, Swarm, custom orchestrators, and internal frameworks.
- **Portable execution** – Agents should run locally, on-prem, in the cloud, or in hybrid environments without repackaging.  
- **Transparent & inspectable** – Human- and machine-readable metadata for capabilities, versions, and dependencies.  
- **Governable & auditable** – Provenance and policy metadata make it possible to enforce enterprise security and compliance.  
- **Simple to adopt** – Minimal friction for wrapping existing agents or building new APS-native ones.

---

## 🧩 Key Components (v0.1 Overview)

| Component              | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| **Manifest (`agent.yaml`)** | Defines the agent’s metadata, interface, runtime, and dependencies.            |
| **Package (`.aps.tar.gz`)** | Bundle of source files, manifest, and metadata; portable unit for distribution. |
| **Registry API**       | REST endpoints for publishing and retrieving APS packages.                 |
| **Runtime Execution**  | How APS-compatible runtimes load and invoke packaged agents.               |
| **Provenance**         | Optional metadata block supporting signature and integrity verification.   | 

A deeper technical specification is available in:  
👉 [APS v0.1 Specification](./specs/APS-v0.1.md)

---

## 🚀 Getting Started

For full installation and setup, see [Getting Started](./getting-started.md).   

**Quick taste from the CLI (example):**

```bash
# Run a simple agent
aps run examples/echo-agent

# Build and publish to a registry
aps build examples/echo-agent -o dist/echo-agent.aps.tar.gz
aps publish dist/echo-agent.aps.tar.gz --registry http://localhost:8080
```

Additional examples demonstrating APS in practice live under:
👉 [`examples/`](./examples/index.md)

---

## 🎯 Goals & Scope

APS focuses specifically on:

* The **core agent package format** and directory structure.
* The **manifest schema** (versioned YAML).
* The **minimum runtime behavior** expected of APS-compliant systems.
* The **registry API** surface for push/pull operations.
* Recommended extensions for **security, provenance, and policy enforcement**. 

It does **not** dictate:

* How agents are trained
* Which models they use
* Where they must be hosted
* Which framework you build them with

APS is a **pluggable interoperability layer**, not a framework.

---

## 📐 Conformance & Versioning

APS follows [Semantic Versioning](https://semver.org/) principles.

* The **spec version** (e.g. `v0.1`) defines which manifest fields and behaviors are valid.
* The **CLI / reference implementation version** may move faster but remains aligned to spec tags.
* Minor spec revisions (e.g. `v0.1 → v0.2`) may introduce additional fields while preserving backward compatibility for existing manifests where practical. 

Conformance requirements for runtimes and registries are described in the main specification and will be extended via proposals/RFCs over time.

---

## 🏛 Governance & Community

The APS project is maintained under an **open governance model**:

* Early on, a small maintainer group stewards direction.
* Over time, governance is expected to evolve toward a working-group or foundation-style structure.
* Decisions are made via open discussion, RFCs, and transparent versioning practices. 

For participation guidelines and process, see:

* [Governance](./standards/governance.md)
* [Contributing](./contributing.md)

---

## 🤝 How to Get Involved

APS welcomes:

* Agent framework and orchestration developers
* Platform and MLOps engineers
* Enterprise AI and security leads
* OSS contributors and standards-minded builders

Ways to participate:

* ⭐ Star and watch the repository
* 💬 Join discussions and propose use cases
* 🧪 Try packaging an existing agent and share feedback
* 📝 Open RFCs for spec extensions, registry behaviors, or provenance features

---

## 📬 Contact

* **General inquiries:** [contact@agentpackaging.org](mailto:contact@agentpackaging.org)
* **Community contributions:** [community@agentpackaging.org](mailto:community@agentpackaging.org)
* **Security and provenance:** [security@agentpackaging.org](mailto:security@agentpackaging.org)

Project repository:
👉 [GitHub Link](https://github.com/vedahegde60/agent-packaging-standard)

---

*© 2025 Agent Packaging Standard (APS) Working Group. All rights reserved.*
