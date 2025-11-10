---
title: "APS Examples"
description: "Reference examples demonstrating the Agent Packaging Standard (APS) in practice."
last_updated: 2025-11-09
---

# APS Examples

This section lists reference agents packaged using the **Agent Packaging Standard (APS)**.

The example agents live in the main repository under the `examples/` directory:

- Repository: [github.com/vedahegde60/agent-packaging-standard](https://github.com/vedahegde60/agent-packaging-standard/tree/main/examples)

---

## 1. Echo Agent

**Path:** `examples/echo-agent/`  

A minimal agent that echoes its input text.  
Use this example to understand the basic APS package layout and manifest fields.

Key files:

- `aps/agent.yaml` — APS manifest
- `main.py` — implementation

Example usage (from the project root):

```bash
echo '{"text": "hello"}' | aps run examples/echo-agent
````

---

## 2. RAG Agent

**Path:** `examples/rag-agent/`

A retrieval-augmented generation agent showing a richer configuration and dependencies.

Key files:

* `aps/agent.yaml` — APS manifest
* Implementation code under `examples/rag-agent/`

Example usage (from the project root):

```bash
aps run examples/rag-agent --input '{"query": "example question"}'
```

---

For more details, see the `README.md` files in each example directory in the repository.

📬 **Questions or ideas for new examples?**
Open an issue or discussion on GitHub, or contact us at [community@agentpackaging.org](mailto:community@agentpackaging.org).
