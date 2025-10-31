
---

## `cli/README.md`

```markdown
# APS CLI (working title)

Commands:
- `aps lint <path>` — validate minimal APS manifest structure
- `aps init <path>` — scaffold a new agent from a template
- `aps run <path>` — run an APS agent (stdin/stdout JSON)

> NOTE: `run` invokes the agent’s entrypoint from the manifest.
> Minimal runner to prove the contract; not a production runtime.

