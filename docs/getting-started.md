---
title: "Getting Started with APS"
description: "Instructions for installing, packaging, and executing agents using the Agent Packaging Standard (APS)."
last_updated: 2025-11-09
---

# Getting Started with the Agent Packaging Standard (APS)

## 1. Overview

This guide provides a concise introduction to installing the APS toolchain and creating your first APS-compliant agent package.  
It is intended for developers, platform maintainers, and enterprise users who wish to evaluate or contribute to the **Agent Packaging Standard (APS)**.

APS introduces a simple packaging and execution model that allows AI agents to be **packaged once and run anywhere**, ensuring consistency and interoperability across runtimes.

---

## 2. Prerequisites

Before using APS, ensure that your development environment meets the following requirements:

| Requirement | Description |
|--------------|-------------|
| **Operating System** | Linux, macOS, or Windows with WSL2 |
| **Python** | Version 3.9 or higher |
| **Git** | For cloning repositories and examples |
| **Network access** | Required for pulling packages from registries |

---

## 3. Installation

The APS CLI is distributed as a Python package.  
To install the latest version directly from the project repository:

```bash
# Clone the APS repository
git clone https://github.com/vedahegde60/agent-packaging-standard.git
cd agent-packaging-standard

# Install the APS CLI
pip install -e cli
```

Once installed, verify the CLI:

```bash
aps --version
```

Expected output:

```
APS CLI v0.1.0 — Agent Packaging Standard
```

---

## 4. Creating an APS Agent

An APS-compliant agent consists of:

1. A **manifest file** (`aps/agent.yaml`) describing the agent’s metadata and interface.
2. The **implementation files** (Python, shell, or other executables).
3. An **optional configuration** or dependency declaration.

Example directory structure:

```
examples/echo-agent/
├── aps/
│   └── agent.yaml
└── main.py
```

Sample manifest (`aps/agent.yaml`):

```yaml
id: examples.echo-agent
version: "0.1.0"
name: Echo Agent
description: Simple agent that echoes input text.
runtime: python3
entrypoint: main.py
inputs:
  - name: text
    type: string
outputs:
  - name: text
    type: string
```

---

## 5. Running the Agent

Execute the agent locally using the APS runtime interface:

```bash
echo '{"text": "hello world"}' | aps run examples/echo-agent
```

Expected output:

```json
{
  "status": "ok",
  "outputs": {
    "text": "hello world"
  }
}
```

To stream incremental results:

```bash
echo '{"text": "stream"}' | aps run examples/echo-agent --stream
```

---

## 6. Publishing and Retrieving Packages

APS defines a registry protocol for distributing and retrieving agent packages.

### Publish a package

```bash
aps publish examples/echo-agent --registry registry://local
```

### Retrieve and execute a published package

```bash
aps run registry://local/examples.echo-agent
```

These commands demonstrate how APS enables consistent packaging and execution workflows across environments.

For detailed registry specifications, refer to the [Registry API](./registry/api.md).

---

## 7. Next Steps

| Area                      | Description                                                                               |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| **Specification**         | Review the [APS v0.1 Specification](./specs/APS-v0.1.md) for technical details.           |
| **Examples**              | Explore sample agents in the [Examples](./examples/index.md).                           |
| **Provenance & Security** | Learn about signature and integrity extensions in [Provenance](./security/provenance.md). |
| **Contributing**          | See [Contributing Guidelines](./contributing.md) to participate in standard development.  |

---

## 8. Troubleshooting

| Issue                      | Resolution                                                                       |
| -------------------------- | -------------------------------------------------------------------------------- |
| `aps` command not found    | Ensure Python scripts path is added to your environment variables.               |
| Manifest validation errors | Verify all required fields exist in `agent.yaml` and conform to the v0.1 schema. |
| Registry connection issues | Check network access and registry endpoint configuration.                        |

---

## 9. Contact

📬 **General inquiries:** [contact@agentpackaging.org](mailto:contact@agentpackaging.org)
🧑‍💻 **Community contributions:** [community@agentpackaging.org](mailto:community@agentpackaging.org)

---

*© 2025 Agent Packaging Standard (APS) Working Group. All rights reserved.*