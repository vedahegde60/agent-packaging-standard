
---
````
card_version: 0.1
id: your.agent.id
name: Your Agent Name
version: 0.1.0
publisher:
    name: Your Name / Org
    url: https://your.site
links:
  repo: https://github.com/your/repo
  docs: ./README.md
tags: [agent, template]
license: Apache-2.0

compliance:
  claims:
    - nist_ai_rmf: "profile: low-risk"
    - iso_42001: "process: documented"
    - eu_ai_act: "category: minimal-risk"
  evidence:
    - threat_model: ./SECURITY.md
    - data_privacy: "see privacy notes below"

safety:
  known_limitations:
    - "May hallucinate"
    - "Not suitable for sensitive data without review"

monetization:
  model: free   # free | one-time | subscription | usage | BYOL | external
  url: ""       # if payment external

runtime:
  language: "Python 3.11"
  platform: "Linux/macOS/Windows"
  network: "none"   # none | outbound | restricted | full
````

---

# Agent Card — Your Agent Name

## 🧠 Summary
Short human-readable description of the agent.

Example: This agent answers questions over local documents using RAG and runs fully offline.

---

## 🎯 Use Cases
- Use case 1  
- Use case 2  

---

## 📥 Inputs (example)
```json
{
  "query": "string",
  "top_k": 1
}
