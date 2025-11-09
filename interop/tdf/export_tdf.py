#!/usr/bin/env python3
# Convert aps/agent.yaml -> TDF JSON
# Usage:
#   python interop/tdf/export_tdf.py examples/rag-agent > tdf.json

import sys, json
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

def to_tdf(mf: dict) -> dict:
    # Minimal, stable schema for "Task Definition Format"
    # Feel free to extend with governance, risk tags, etc.
    inputs = []
    for k, v in (mf.get("inputs") or {}).items():
        inputs.append({"name": k, "type": v.get("type","string"), "required": v.get("required", False), "default": v.get("default", None)})

    outputs = []
    for k, v in (mf.get("outputs") or {}).items():
        outputs.append({"name": k, "type": v.get("type","string")})

    runtimes = []
    for rt in mf.get("runtimes", []):
        runtimes.append({
            "kind": rt.get("kind"),
            "entrypoint": rt.get("entrypoint"),
        })

    tdf = {
        "tdf_version": "0.1",
        "task": {
            "id": mf.get("id"),
            "name": mf.get("name"),
            "version": mf.get("version"),
            "summary": mf.get("summary", ""),
            "labels": mf.get("labels", []),
            "inputs": inputs,
            "outputs": outputs,
            "runtimes": runtimes,
            "security": {
                "signing": mf.get("signing", {}).get("required", False),
                "provenance": mf.get("provenance", {}).get("level", "none")
            },
            "interop": {
                "aps_manifest": True,
                "mcp_tool": "agent.run",
                "agp_gateway": True
            }
        }
    }
    return tdf

def main():
    if len(sys.argv) < 2:
        print("usage: export_tdf.py <agent-root>", file=sys.stderr)
        sys.exit(2)
    root = Path(sys.argv[1]).resolve()
    mf = yaml.safe_load((root/"aps"/"agent.yaml").read_text(encoding="utf-8"))
    print(json.dumps(to_tdf(mf), indent=2))

if __name__ == "__main__":
    main()

