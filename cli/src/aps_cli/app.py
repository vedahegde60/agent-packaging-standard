import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

from .schema_min import REQUIRED_TOP_LEVEL, REQUIRED_CAPABILITIES

def load_manifest(agent_dir: Path):
    manifest_path = agent_dir / "aps" / "agent.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest: {manifest_path}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def cmd_lint(args):
    agent_dir = Path(args.path).resolve()
    try:
        manifest = load_manifest(agent_dir)
    except Exception as e:
        print(f"[lint] ERROR: {e}", file=sys.stderr)
        return 2

    # Basic shape checks
    missing = [k for k in REQUIRED_TOP_LEVEL if k not in manifest]
    if missing:
        print(f"[lint] ERROR: missing top-level keys: {missing}", file=sys.stderr)
        return 2

    caps = manifest.get("capabilities", {})
    for k in REQUIRED_CAPABILITIES:
        if k not in caps:
            print(f"[lint] ERROR: capabilities missing '{k}'", file=sys.stderr)
            return 2

    runtimes = manifest.get("runtimes", [])
    if not isinstance(runtimes, list) or not runtimes:
        print("[lint] ERROR: runtimes must be a non-empty list", file=sys.stderr)
        return 2

    # Check at least one runtime has an entrypoint or endpoint
    ok = False
    for rt in runtimes:
        kind = rt.get("kind")
        entry = rt.get("entrypoint")
        if kind in ("python", "container") and entry:
            ok = True
            break
        if kind == "remote" and rt.get("endpoint"):
            ok = True
            break
    if not ok:
        print("[lint] ERROR: no runnable runtime found (entrypoint or endpoint)", file=sys.stderr)
        return 2

    print("[lint] OK")
    return 0

def cmd_init(args):
    target = Path(args.path).resolve()
    template = Path(__file__).parent / "templates" / "echo_agent"
    if target.exists() and any(target.iterdir()):
        print(f"[init] ERROR: target directory not empty: {target}", file=sys.stderr)
        return 2
    os.makedirs(target, exist_ok=True)

    # Copy minimal template
    for root, _, files in os.walk(template):
        rel = Path(root).relative_to(template)
        dest_dir = target / rel
        os.makedirs(dest_dir, exist_ok=True)
        for fn in files:
            src = Path(root) / fn
            dst = dest_dir / fn
            with open(src, "rb") as rf, open(dst, "wb") as wf:
                wf.write(rf.read())

    print(f"[init] Created agent scaffold at {target}")
    return 0

def _run_python_entry(entry):
    """
    Entry is a list, e.g. ["python","-m","echo.main"] or ["python","path/to/file.py"].
    We pipe stdin (JSON) to the child and stream stdout back.
    """
    proc = subprocess.Popen(entry, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        req = sys.stdin.read()
        out, err = proc.communicate(input=req)
    except KeyboardInterrupt:
        proc.terminate()
        raise
    if err:
        print(err, file=sys.stderr)
    sys.stdout.write(out)
    return proc.returncode

def cmd_run(args):
    agent_dir = Path(args.path).resolve()
    try:
        manifest = load_manifest(agent_dir)
    except Exception as e:
        print(f"[run] ERROR: {e}", file=sys.stderr)
        return 2

    # Choose first non-remote runtime with entrypoint
    for rt in manifest.get("runtimes", []):
        if rt.get("kind") in ("python", "container") and rt.get("entrypoint"):
            entry = rt["entrypoint"]
            return _run_python_entry(entry)

    print("[run] ERROR: no supported local runtime found in this skeleton (remote not implemented)", file=sys.stderr)
    return 2

def main(argv=None):
    parser = argparse.ArgumentParser(prog="aps", description="APS CLI (working title)")
    sub = parser.add_subparsers(dest="cmd")

    p_lint = sub.add_parser("lint", help="Validate an APS agent directory")
    p_lint.add_argument("path", help="Path to agent root (contains aps/agent.yaml)")
    p_lint.set_defaults(func=cmd_lint)

    p_init = sub.add_parser("init", help="Scaffold a new APS agent directory")
    p_init.add_argument("path", help="Target directory to create")
    p_init.set_defaults(func=cmd_init)

    p_run = sub.add_parser("run", help="Run an APS agent locally (stdin->stdout JSON)")
    p_run.add_argument("path", help="Path to agent root")
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())

