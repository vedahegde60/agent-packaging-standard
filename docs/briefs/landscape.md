
**Executive Summary**  
Current “agent marketplaces” are **platform-locked catalogs** (Microsoft, Google/Oracle), **governance-first registries** (Covasavant), **protocol-centric hosts** (TrueFoundry with MCP/A2A), and **payment rails** (Skyfire). None provides a **neutral packaging + execution** standard. APS fills the gap as **OCI-like** packaging for agents.

**Players & Angles**
- **TrueFoundry / Agent Protocols (MCP/A2A)**: strong tool interop; less emphasis on portable packaging.
- **Covasavant**: governance catalog; good enterprise fit; unclear packaging portability.
- **Microsoft Marketplace**: robust commerce + compliance; proprietary offer model; not agent-native packaging.
- **Google/Oracle Marketplaces**: mature listing/commerce; lacks agent packaging contract.
- **Skyfire**: agent payments & identity; assumes an execution substrate elsewhere.

**Risks of today’s landscape**
- Vendor lock-in on run formats and catalogs  
- Weak portability into enterprise VPCs  
- Fragmented “capability” descriptions (no shared schema)  
- Compliance claims not machine-verifiable

**APS Advantages**
- **Run anywhere**: local, VPC, hosted, or hybrid  
- **Open manifest**: inputs/outputs/tools policy defined  
- **Trust**: signatures + provenance hooks  
- **Composable with others**: Card for humans, MCP/AGP/TDF for interop, compliance claims for governance  
- **Registry protocol**: Search, publish, pull; monetization pluggable

**Go-to-Market**
1) Win developers with spec + CLI + examples  
2) Land enterprise pilots (policy + provenance)  
3) Bridge to protocols (MCP/AGP) via adapters  
4) Minimal registry → federation → foundation governance

**Adoption Signals to Watch**
- Framework support (LangChain/LlamaIndex/etc.) announcing APS template generators  
- Cloud vendors acknowledging APS manifests in their catalogs  
- Security teams referencing APS policy/provenance in reviews