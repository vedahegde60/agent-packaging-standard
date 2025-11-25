---
title: "Getting Started with APS"
description: "Beginner-friendly walkthrough for installing, initializing, and running agents with the Agent Packaging Standard (APS)."
last_updated: 2025-11-25
---

# Getting Started with the Agent Packaging Standard (APS)

## 1. Overview

This guide provides a simple walkthrough for new contributors to install the APS CLI, create their first agent, run an example, and modify its logic.  

APS introduces a packaging and execution model that allows AI agents to be **packaged once and run anywhere**, ensuring consistency and interoperability across runtimes.

---

## 2. Prerequisites

Before you begin, make sure your environment meets these requirements:

| Requirement        | Description                                |
|--------------------|--------------------------------------------|
| **Operating System** | Linux, macOS, or Windows with WSL2        |
| **Python**          | Version 3.9 or higher                     |
| **Git**             | For cloning repositories and examples     |
| **Network Access**  | Required for pulling packages from registries |

---

## 3. Install the APS CLI

Clone the repository and install the CLI:

```bash
# Clone the APS repository
git clone https://github.com/vedahegde60/agent-packaging-standard.git
cd agent-packaging-standard

# Install the APS CLI
pip install -e cli
```

Verify installation:

```bash
aps --version
```

Expected output:

```
APS CLI v0.1.0 — Agent Packaging Standard
```

---

## 4. Initialize Your First Agent

Use the CLI to scaffold a new agent:

```bash
aps init my-first-agent
```

This creates a directory with:

- `aps/agent.yaml` → manifest describing metadata and inputs/outputs  
- `main.py` → default implementation file  

Example structure:

```
my-first-agent/
├── aps/
│   └── agent.yaml
└── main.py
```

---

## 5. Run the Example Agent

Try running the provided **echo agent**:

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

To stream results:

```bash
echo '{"text": "stream"}' | aps run examples/echo-agent --stream
```

---

## 6. Modify Agent Logic

Open `main.py` in your agent folder and change the behavior. For example:

```python
def run(inputs):
    text = inputs.get("text", "")
    return {"text": text.upper()}
```

Re-run the agent:

```bash
echo '{"text": "hello world"}' | aps run my-first-agent
```

Output:

```json
{
  "status": "ok",
  "outputs": {
    "text": "HELLO WORLD"
  }
}
```

---

## 7. Publishing and Retrieving Packages

APS supports registries for sharing agents.

**Publish:**

```bash
aps publish my-first-agent --registry registry://local
```

**Retrieve and run:**

```bash
aps run registry://local/my-first-agent
```

---

## 8. Next Steps

| Area              | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| **Specification** | Review the [APS v0.1 Specification](./specs/APS-v0.1.md).                   |
| **Examples**      | Explore sample agents in [Examples](./examples/index.md).                   |
| **Security**      | Learn about provenance and integrity in [Provenance](./security/provenance.md). |
| **Contributing**  | See [Contributing Guidelines](./contributing.md).                           |

---

## 9. Troubleshooting

| Issue                        | Resolution                                                         |
|------------------------------|---------------------------------------------------------------------|
| `aps` command not found      | Ensure Python scripts path is added to your environment variables. |
| Manifest validation errors   | Verify required fields in `agent.yaml` match the schema.           |
| Registry connection issues   | Check network access and registry endpoint configuration.          |

---

## 10. Contact

📬 **General inquiries:** [contact@agentpackaging.org](mailto:contact@agentpackaging.org)  
🧑‍💻 **Community contributions:** [community@agentpackaging.org](mailto:community@agentpackaging.org)

---

*© 2025 Agent Packaging Standard (APS) Working Group. All rights reserved.*
```

---

### 🔑 Key Updates Made
- Added **`aps init`** step to scaffold a new agent (your original doc skipped this).  
- Simplified flow: **Install → Init → Run Example → Modify Logic → Publish**.  
- Made troubleshooting and next steps more concise for beginners.  
- Updated `last_updated` date to today (2025‑11‑25).  

This version now matches the GitHub issue requirements and is beginner‑friendly.  

Would you like me to also **draft a shorter “Quickstart” section** (like a 10‑line minimal workflow) at the top for contributors who just want commands without explanations?
