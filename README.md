# 🧩 Agent Packaging Standard (APS)

[![PyPI version](https://badge.fury.io/py/apstool.svg)](https://badge.fury.io/py/apstool)
[![PyPI downloads](https://img.shields.io/pypi/dm/apstool.svg)](https://pypi.org/project/apstool/)
[![Python versions](https://img.shields.io/pypi/pyversions/apstool.svg)](https://pypi.org/project/apstool/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](https://github.com/vedahegde60/agent-packaging-standard/blob/main/LICENSE)

**Agent Packaging Standard (APS)** defines a **lightweight, vendor-neutral format** for packaging, sharing, and executing AI agents across runtimes and platforms.

> _Portable. Inspectable. Policy-enforced._  
> Build once, run anywhere — with confidence.

---

## 🌍 Overview

Modern AI agents are locked into proprietary formats and execution models.  
Each platform defines its own way to describe capabilities, dependencies, and trust boundaries — creating fragmentation and limiting adoption.

APS provides a **common foundation** so that agents can move seamlessly between ecosystems.

### Core Goals

| Principle | Description |
|------------|--------------|
| **Portability** | Agents can be packaged once and executed anywhere that supports APS. |
| **Inspectability** | All components (manifest, policy, code) are transparent and verifiable. |
| **Governance** | Built-in signing, provenance, and trust policies ensure enterprise compliance. |
| **Interoperability** | Designed to complement — not replace — existing frameworks and runtimes. |

---

## 📦 What’s Inside an APS Package

An APS package (`.aps.tar.gz`) contains everything required to describe, run, and verify an agent:

```

aps/
├── agent.yaml        # Manifest — entrypoint, metadata, and runtime interface
├── provenance.json   # Optional signature and provenance data
├── LICENSE
└── src/              # Agent code, configuration, and assets

````

Agents can be published and pulled from registries just like container images.

---

## 🧠 Why It Matters

APS makes agents:
- **Portable** across tools, clouds, and organizations.  
- **Composable** via shared metadata and runtime descriptors.  
- **Auditable** with signed manifests and provenance attestations.  
- **Extensible** so future frameworks can plug into a shared ecosystem.

---

## 🧰 Quick Start

### 1. Package an Agent

```bash
aps build examples/echo-agent
```

This creates `examples/echo-agent/dist/dev.echo.aps.tar.gz``

### 2. Sign and Verify

```bash
# Generate keypair (first time)
aps keygen

# Sign the package
aps sign examples/echo-agent/dist/dev.echo.aps.tar.gz --key default

# Verify signature
aps verify examples/echo-agent/dist/dev.echo.aps.tar.gz --pubkey ~/.aps/keys.pub/default.pub
```

### 3. Publish to a Registry

```bash
aps publish examples/echo-agent/dist/dev.echo.aps.tar.gz --registry http://localhost:8080
```

### 4. Run Anywhere

```bash
aps run examples/echo-agent --input '{"text": "hello"}'
```

---

## 🧩 Specification & Docs

| Document                                             | Purpose                                          |
| ---------------------------------------------------- | ------------------------------------------------ |
| [APS Specification v0.1](docs/specs/APS-v0.1.md)     | Core manifest and runtime model                  |
| [Registry API](docs/registry/api.md)                 | How agents are published, discovered, and pulled |
| [Security & Provenance](docs/security/provenance.md) | Signing, verification, and trust policies        |
| [Governance](docs/standards/governance.md)           | Maintainers, process, and community rules        |
| [Contributing](docs/contributing.md)                 | How to join and participate                      |
| [Examples](docs/examples/index.md)                   | Reference agent packages                         |

Full documentation and site: **[agentpackaging.org](https://agentpackaging.org)**

---

## 🧪 Example Agents

| Example                             | Description                                                                 |
| ----------------------------------- | --------------------------------------------------------------------------- |
| [`echo-agent`](examples/echo-agent) | Minimal agent that echoes input (hello world of APS).                       |
| [`rag-agent`](examples/rag-agent)   | Retrieval-augmented generation agent with richer manifest and dependencies. |

---

## 🤝 Get Involved

APS is open to developers, researchers, and organizations who want to build a more interoperable agent ecosystem.

| Type            | How to Participate                                                                               |
| --------------- | ------------------------------------------------------------------------------------------------ |
| **Contribute**  | Fork the repo and submit improvements or examples.                                               |
| **Discuss**     | Open a [GitHub Discussion](https://github.com/vedahegde60/agent-packaging-standard/discussions). |
| **Collaborate** | Reach out to align on registry, runtime, or signing integrations.                                |

See [CONTRIBUTING.md](docs/contributing.md) for full details.

---

## 🧭 Roadmap (30-Day Pilot)

| Phase        | Focus                                                 | Status         |
| ------------ | ----------------------------------------------------- | -------------- |
| **Week 1–2** | Packaging format and manifest model                   | ✅ Completed    |
| **Week 3**   | Interop tests + test-release                          | ✅ Completed    |
| **Week 4**   | Signing, provenance, governance, and community launch | 🚀 In progress |

Next milestones:

* Formalize **`aps` CLI** reference implementation
* Extend **registry protocol** for discovery and version negotiation
* Publish **APS v0.2** based on community feedback

---

## 🤝 Contributing

We welcome contributions! Before submitting code changes:

1. **Run the pre-commit test suite:**
   ```bash
   ./scripts/pre_commit_tests.sh
   ```
   This runs both automated tests (~8s) and registry integration tests (~5s).

2. **Follow the guidelines** in [CONTRIBUTING.md](CONTRIBUTING.md)

See [Testing Guide](docs/testing.md) for detailed testing instructions.

---

## 🔒 Security

APS supports optional signing and verification of all packages.
See the [Security and Provenance Specification](docs/security/provenance.md) for details.

For confidential reports:
📧 **[security@agentpackaging.org](mailto:security@agentpackaging.org)**

---

## 🪴 License

This project is licensed under the **Apache 2.0 License**.
See [LICENSE](LICENSE) for details.

---

## ✉️ Contact

| Purpose                 | Email                                                               |
| ----------------------- | ------------------------------------------------------------------- |
| General inquiries       | [contact@agentpackaging.org](mailto:contact@agentpackaging.org)     |
| Community contributions | [community@agentpackaging.org](mailto:community@agentpackaging.org) |
| Security disclosures    | [security@agentpackaging.org](mailto:security@agentpackaging.org)   |

---

*© 2025 Agent Packaging Standard (APS) Working Group. All rights reserved.*

