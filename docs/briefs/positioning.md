
> **APS = the container/OCI moment for agents.**  
> Other players build catalogs, protocols, or payments. APS standardizes the **package** and **run contract** so agents can move freely across tools, clouds, and enterprises.

**Who we are for**
- **Developers**: ship once, run anywhere  
- **Enterprises/IT**: review once, approve many; policy + provenance  
- **Ecosystem**: unify on one manifest, many runtimes/registries

**What we standardize**
- `aps/agent.yaml` manifest (runtimes, schemas, policies)  
- stdin/stdout JSON envelope (local) and `aps-http-v1` (remote, roadmap)  
- optional signatures/provenance (DSSE/in-toto)  
- open Registry API (search/publish/pull)

**How we interoperate**
- **Agent Card**: human description + compliance claims  
- **MCP**: tools listed in `capabilities.tools` with MCP bindings  
- **AGP**: message endpoints referenced in runtimes/adapters  
- **TDF**: tasks mapped to `inputs/outputs` schemas

**Why now**
- Agents are moving from experiments to production; portability+trust missing.  
- Enterprises need neutral packaging + auditability before adoption.  
- Developers need one manifest to reach any runtime or catalog.

**Proof points**
- Working CLI + examples  
- OpenAPI registry draft  
- Docs site + architecture  
- Security/provenance sketch

**Roadmap (next)**
- `aps sign` / `aps verify` prototype  
- MCP/AGP adapters demo  
- Minimal registry service + `aps publish`  
- Compliance claim conventions (NIST/ISO/EU)
