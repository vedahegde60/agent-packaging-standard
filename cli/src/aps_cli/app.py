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

def _run_python_entry(entry, extra_env=None, stdin_text=None):
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    proc = subprocess.Popen(
        entry,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    out, err = proc.communicate(input=stdin_text)
    if err:
        print(err, file=sys.stderr)
    if out:
        sys.stdout.write(out)
    return proc.returncode

def lint_manifest(agent_dir: Path) -> int:
    try:
        manifest = load_manifest(agent_dir)
    except Exception as e:
        print(f"[lint] ERROR: {e}", file=sys.stderr)
        return 2

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

def cmd_lint(args):
    return lint_manifest(Path(args.path).resolve())

def cmd_validate(args):  # alias of lint
    return lint_manifest(Path(args.path).resolve())

def cmd_init(args):
    target = Path(args.path).resolve()
    template = Path(__file__).parent / "templates" / "echo_agent"
    if target.exists() and any(target.iterdir()):
        print(f"[init] ERROR: target directory not empty: {target}", file=sys.stderr)
        return 2
    os.makedirs(target, exist_ok=True)
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

def cmd_run(args):
    agent_dir = Path(args.path).resolve()
    try:
        manifest = load_manifest(agent_dir)
    except Exception as e:
        print(f"[run] ERROR: {e}", file=sys.stderr)
        return 2

    # Auto-prepend <agent_root>/src to PYTHONPATH
    extra_env = {}
    src_dir = agent_dir / "src"
    if src_dir.exists():
        existing = os.environ.get("PYTHONPATH", "")
        extra_env["PYTHONPATH"] = f"{src_dir}{os.pathsep}{existing}" if existing else str(src_dir)

    for rt in manifest.get("runtimes", []):
        if rt.get("kind") in ("python", "container") and rt.get("entrypoint"):
            entry = rt["entrypoint"]
            stdin_text = sys.stdin.read()
            return _run_python_entry(entry, extra_env=extra_env, stdin_text=stdin_text)

    print("[run] ERROR: no supported local runtime found in this skeleton (remote not implemented)", file=sys.stderr)
    return 2

def cmd_shell(args):
    """Simple interactive loop: each line you paste must be a full JSON request. """
    agent_dir = Path(args.path).resolve()
    try:
        manifest = load_manifest(agent_dir)
    except Exception as e:
        print(f"[shell] ERROR: {e}", file=sys.stderr)
        return 2

    extra_env = {}
    src_dir = agent_dir / "src"
    if src_dir.exists():
        existing = os.environ.get("PYTHONPATH", "")
        extra_env["PYTHONPATH"] = f"{src_dir}{os.pathsep}{existing}" if existing else str(src_dir)

    chosen = None
    for rt in manifest.get("runtimes", []):
        if rt.get("kind") in ("python", "container") and rt.get("entrypoint"):
            chosen = rt["entrypoint"]
            break
    if not chosen:
        print("[shell] ERROR: no supported local runtime found", file=sys.stderr)
        return 2

    print("APS shell: paste one JSON request per line; Ctrl+C to exit.")
    while True:
        try:
            line = input("> ").strip()
        except KeyboardInterrupt:
            print()
            return 0
        if not line:
            continue
        rc = _run_python_entry(chosen, extra_env=extra_env, stdin_text=line)
        if rc != 0:
            print(f"[shell] WARN: child exit code {rc}", file=sys.stderr)

def main(argv=None):
    parser = argparse.ArgumentParser(prog="aps", description="APS CLI (working title)")
    sub = parser.add_subparsers(dest="cmd")

    p_lint = sub.add_parser("lint", help="Validate an APS agent directory")
    p_lint.add_argument("path", help="Path to agent root (contains aps/agent.yaml)")
    p_lint.set_defaults(func=cmd_lint)

    p_validate = sub.add_parser("validate", help="Alias of lint")
    p_validate.add_argument("path", help="Path to agent root")
    p_validate.set_defaults(func=cmd_validate)

    p_init = sub.add_parser("init", help="Scaffold a new APS agent directory")
    p_init.add_argument("path", help="Target directory to create")
    p_init.set_defaults(func=cmd_init)

    p_run = sub.add_parser("run", help="Run an APS agent locally (stdin->stdout JSON)")
    p_run.add_argument("path", help="Path to agent root")
    p_run.set_defaults(func=cmd_run)

    p_shell = sub.add_parser("shell", help="Interactive: send JSON requests repeatedly")
    p_shell.add_argument("path", help="Path to agent root")
    p_shell.set_defaults(func=cmd_shell)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
