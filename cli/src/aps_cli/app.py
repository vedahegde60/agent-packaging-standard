# cli/src/aps_cli/app.py
# APS CLI – clean baseline
# ------------------------------------------------------------
# Features:
# - validate | build | publish | pull | run (sync/--stream) | logs | inspect | registry serve
# - Self-healing registry:// resolver with cache verification
# - Robust streaming (write->flush->close stdin BEFORE reading)
# - Sync path merges stderr->stdout to avoid 3.13 pipe race
# - Log persistence under ~/.aps/logs
# - Clear stderr logging for all non-JSON chatter
# ------------------------------------------------------------

from __future__ import annotations
import os, sys, json, argparse, tarfile, shutil, subprocess, threading, time, shlex
from pathlib import Path
from typing import Any, Dict, Optional

from .signing import (
    ensure_keypair, load_pubkey, load_privkey,
    ed25519_sign, ed25519_verify
)

# 3rd party (ensure installed in venv for CLI usage)
import requests
try:
    import yaml
except ImportError:
    print("[init] ERROR: PyYAML not installed. pip install pyyaml", file=sys.stderr)
    raise

# ------------------------------ Constants / Paths

HOME = Path.home()
CACHE_DIR = Path(os.environ.get("APS_CACHE_DIR", str(HOME / ".aps" / "cache")))
LOGS_DIR  = Path(os.environ.get("APS_LOGS_DIR",  str(HOME / ".aps" / "logs")))
DEFAULT_REGISTRY = os.environ.get("APS_REGISTRY", "http://localhost:8080")

# ------------------------------ Helpers

def eprint(*a, **k):
    print(*a, file=sys.stderr, **k)

def _now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())

def _logs_dir_for(agent_id: str, version: str) -> Path:
    return LOGS_DIR / agent_id / version

def _write_log(agent_root: Path, manifest: Dict[str, Any], stderr_lines: list[str], final_json: Optional[dict]):
    """Persist a run log. Enabled when APS_SAVE_LOGS in {"1","true"} (default: on)."""
    if os.environ.get("APS_SAVE_LOGS", "1") not in ("1", "true", "True"):
        return
    agent_id = manifest.get("id", "unknown")
    version  = manifest.get("version", "unknown")
    d = _logs_dir_for(agent_id, version)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{_now_ts()}.log"
    with p.open("w", encoding="utf-8") as f:
        f.write(f"# APS LOG\nid: {agent_id}\nversion: {version}\n")
        f.write(f"time: {_now_ts()}\n\n")
        f.write("## STDERR/LOGS\n")
        for line in stderr_lines:
            f.write(line.rstrip("\n") + "\n")
        f.write("\n## RESULT\n")
        f.write(json.dumps(final_json if final_json else {
            "status":"error","error":{"code":"NO_FINAL_RESPONSE","message":"Agent exited without valid JSON"}
        }))
    eprint(f"[logs] wrote {p}")

def agent_root(p: str | Path) -> Path:
    """Return the agent root Path (dir containing aps/agent.yaml)."""
    p = Path(p)
    if p.is_file() and p.suffixes[-2:] == [".tar", ".gz"]:
        # tarball is treated in inspect/build/publish paths; run expects a dir
        raise FileNotFoundError(f"Run expects directory, got tar: {p}")
    if (p / "aps" / "agent.yaml").exists():
        return p
    raise FileNotFoundError(f"Missing manifest: {p}/aps/agent.yaml")

def load_manifest(root: Path) -> Dict[str, Any]:
    with (root / "aps" / "agent.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f.read())

def cached_agent_dir(agent_id: str, version: str) -> Path:
    return CACHE_DIR / agent_id / version

def _is_json_status_line(line: str) -> Optional[dict]:
    """Heuristic: parse if dict and has 'status' key."""
    if not line or line[0] != "{" or line[-1] != "}":
        return None
    try:
        obj = json.loads(line)
        if isinstance(obj, dict) and "status" in obj:
            return obj
    except Exception:
        return None
    return None

def _emit_implicit_error() -> int:
    print(json.dumps({"status":"error","error":{"code":"NO_FINAL_RESPONSE","message":"Agent produced no final JSON"}}))
    return 1

def _wrap_request(stdin_raw: str, single_input: Optional[str]) -> str:
    """
    Accepts either:
      - Full envelope: {"aps_version": "...", "operation": "run", "inputs": {...}}
      - Raw inputs object or a primitive under --input key.
    Always returns a full envelope string.
    """
    # DEBUG hooks (you can comment out later)
    eprint("In _wrap_request function")
    eprint("Trying to parse stdin_raw",stdin_raw)

    # If user passed raw, but also provided --input key, wrap as {"inputs": {key: raw}}
    if single_input:
        try:
            raw = json.loads(stdin_raw) if stdin_raw.strip() else None
        except Exception:
            raw = stdin_raw if stdin_raw.strip() else None
        payload = {"aps_version":"0.1","operation":"run","inputs":{single_input: raw}}
        eprint(f"Detected single_input wrap -> {payload}")
        return json.dumps(payload)


    # Already an envelope?
    try:
        print("Trying to parse stdin_raw as JSON envelope...", file=sys.stderr)
        obj = json.loads(stdin_raw) if stdin_raw.strip() else {}
    except Exception:
        obj = {}
    if isinstance(obj, dict) and "inputs" in obj and "operation" in obj:
        eprint(f"Detected full APS envelope {obj}")
        return json.dumps(obj)

    print("Wrapping entire stdin_raw as inputs.text", file=sys.stderr)
    # Treat entire obj as inputs
    env = {"aps_version":"0.1","operation":"run","inputs": (obj if isinstance(obj, dict) else {"text": str(obj)})}
    return json.dumps(env)

# ------------------------------ Tar extraction (flatten if nested)

def _extract_agent_pkg(pkg_path: str, target: Path):
    """
    Extract tar.gz into `target`. Supports both:
      - Flat tars: aps/..., src/...
      - Nested tars: <name>/aps/..., <name>/src/...
    """
    import tempfile
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpd:
        with tarfile.open(pkg_path, "r:gz") as tf:
            # NOTE: For demo/dev we trust packages; add safe_member checks if needed
            tf.extractall(path=tmpd)

        tmp_root = Path(tmpd)
        # Case A: flat
        if (tmp_root / "aps" / "agent.yaml").exists():
            for item in tmp_root.iterdir():
                shutil.move(str(item), str(target / item.name))
            return

        # Case B: nested – find directory that contains aps/agent.yaml
        cand = None
        for p in tmp_root.rglob("aps/agent.yaml"):
            cand = p.parent.parent  # .../<cand>/aps/agent.yaml
            break
        if cand:
            for item in cand.iterdir():
                shutil.move(str(item), str(target / item.name))
            return

    raise FileNotFoundError("package missing aps/agent.yaml")

# ------------------------------ Registry resolution / Pull

def _resolve_registry_path_if_needed(path: str) -> str:
    """Resolve registry://ID to local cache path (and self-heal incomplete cache)."""
    if not path.startswith("registry://"):
        return path

    agent_id = path.replace("registry://", "")
    reg = DEFAULT_REGISTRY

    # Get metadata (latest version)
    r = requests.get(f"{reg}/v1/agents/{agent_id}", timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"failed to resolve {agent_id}: HTTP {r.status_code}")
    meta = r.json()
    version = meta["version"]
    target = cached_agent_dir(agent_id, version)

    # Self-heal if cache is missing
    if not (target / "aps" / "agent.yaml").exists():
        eprint(f"[run] cache incomplete for {agent_id}@{version}; pulling…")
        ns = argparse.Namespace(agent=agent_id, registry=reg, version=version)
        rc = cmd_pull(ns)
        if rc != 0 or not (target / "aps" / "agent.yaml").exists():
            raise FileNotFoundError(f"Missing manifest after pull: {target}/aps/agent.yaml")

    eprint(f"[run] resolved registry://{agent_id} -> {target}")
    return str(target)

# ------------------------------ Commands

def cmd_validate(args):
    root = agent_root(args.path)
    mf = load_manifest(root)
    required = ["aps_version","id","name","version","runtimes"]
    missing = [k for k in required if k not in mf]
    if missing:
        print(json.dumps({"status":"error","error":{"code":"MISSING_KEYS","missing":missing}}))
        return 1
    print(json.dumps({"status":"ok"}))
    return 0

def cmd_build(args):
    root = Path(args.path).resolve()
    dist_dir = Path(args.dist or (root / "dist"))
    dist_dir.mkdir(parents=True, exist_ok=True)

    mf = load_manifest(root)
    agent_id = mf["id"]; version = mf["version"]
    out_path = dist_dir / f"{agent_id}.aps.tar.gz"

    eprint(f"[build] packaging {agent_id}@{version} -> {out_path}")
    with tarfile.open(out_path, "w:gz") as tf:
        # Add select paths at top-level; avoid nesting (no arcname=root.name)
        for rel in ["aps", "src", "README.md", "assets","LICENSE"]:
            p = root / rel
            if p.exists():
                tf.add(p, arcname=rel)
    print(str(out_path))
    return 0

def cmd_init(args):
    tgt = Path(args.path).resolve()
    if tgt.exists() and any(tgt.iterdir()):
        print("[init] ERROR: target not empty", file=sys.stderr); return 2
    (tgt/"aps").mkdir(parents=True, exist_ok=True)
    (tgt/"src"/"simple").mkdir(parents=True, exist_ok=True)
    (tgt/"aps"/"agent.yaml").write_text(
        'aps: "0.1"\nid: "dev.simple"\nname: "Simple"\nversion: "0.0.1"\nsummary: "Echo upper."\n'
        'runtimes:\n  - kind: "python"\n    entrypoint: ["python","-m","simple.main"]\n'
        'capabilities:\n  inputs:\n    schema:\n      type: object\n      properties:\n        text: {type: string}\n      required: ["text"]\n'
        '  outputs:\n    schema:\n      type: object\n      properties:\n        text: {type: string}\n      required: ["text"]\n'
        'policies:\n  network: { egress: [] }\n'
    , encoding="utf-8")
    (tgt/"src"/"simple"/"main.py").write_text(
        "import sys, json\nraw=sys.stdin.read()\nreq=json.loads(raw)\ntext=(req.get('inputs') or {}).get('text','')\n"
        "print(json.dumps({'status':'ok','outputs':{'text':text.upper()}}))\n", encoding="utf-8")
    (tgt/"AGENT_CARD.md").write_text("# Agent Card\n", encoding="utf-8")
    print(f"[init] Created {tgt}"); return 0

def cmd_publish(args):
    pkg = Path(args.package).resolve()
    reg = args.registry or DEFAULT_REGISTRY
    files = {"file": open(pkg, "rb")}
    eprint(f"[publish] -> {reg} ({pkg.name})")
    r = requests.post(f"{reg}/v1/publish", files=files, timeout=60)
    if r.status_code >= 400:
        eprint(f"[publish] ERROR {r.status_code}: {r.text}")
        r.raise_for_status()
    print(json.dumps(r.json()))
    return 0

def cmd_pull(args):
    agent_id = args.agent
    reg = args.registry or DEFAULT_REGISTRY

    # Resolve version
    r = requests.get(f"{reg}/v1/agents/{agent_id}", timeout=10)
    r.raise_for_status()
    meta = r.json()
    version = args.version if getattr(args, "version", None) and args.version != "latest" else meta["version"]

    # Download
    url = f"{reg}/v1/agents/{agent_id}/download?version={version}"
    eprint(f"[pull] GET {url}")
    rd = requests.get(url, stream=True, timeout=60)
    rd.raise_for_status()

    target = cached_agent_dir(agent_id, version)
    target.mkdir(parents=True, exist_ok=True)
    tmp_pkg = target.parent / f"{agent_id}-{version}.tmp.tar.gz"
    with open(tmp_pkg, "wb") as f:
        for chunk in rd.iter_content(8192):
            if chunk:
                f.write(chunk)

    # Extract (flatten if needed)
    _extract_agent_pkg(str(tmp_pkg), target)
    tmp_pkg.unlink(missing_ok=True)
    eprint(f"[pull] ready: {target}")
    return 0

def helper_run_agent(path: str, req: str, timeout_s=None) -> int:
    """
    SYNC path:
      - Merge stderr -> stdout to avoid Python 3.13 dual-pipe races.
      - Only print final JSON line to stdout.
      - Persist logs separate from final JSON.
    """
    root = agent_root(path)
    mf = load_manifest(root)

    env = os.environ.copy()
    src_dir = root / "src"
    if src_dir.exists():
        env["PYTHONPATH"] = str(src_dir) + os.pathsep + env.get("PYTHONPATH", "")
    env.setdefault("PYTHONUNBUFFERED", "1")
    env["APS_AGENT_ROOT"] = str(root)

    # Select python runtime
    rt = next((r for r in mf.get("runtimes", []) if r.get("kind") == "python" and r.get("entrypoint")), None)
    if not rt:
        eprint("[run] ERROR: no python runtime")
        return 2
    entry = rt["entrypoint"]
    if isinstance(entry, str):
        entry = shlex.split(entry)

    proc = subprocess.Popen(
        entry,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # merged to avoid 3.13 EBADF race
        text=True,
        env=env,
        cwd=str(root)
    )

    try:
        out, _ = proc.communicate(input=req, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            out, _ = proc.communicate(timeout=1)
        except Exception:
            out = out or ""
        err_obj = {"status":"error","error":{"code":"TIMEOUT","message":f"Agent exceeded timeout ({timeout_s}s)"}}
        _write_log(root, mf, (out.splitlines() if out else []), err_obj)
        print(json.dumps(err_obj))
        return 124

    lines = out.splitlines() if out else []
    final_json, final_idx = None, -1
    for i, line in enumerate(lines):
        obj = _is_json_status_line(line)
        if obj:
            final_json, final_idx = obj, i

    logs_lines = lines[:final_idx] + lines[final_idx+1:] if final_idx >= 0 else lines
    _write_log(root, mf, logs_lines, final_json)

    if final_json:
        print(json.dumps(final_json))
        return 0 if final_json.get("status") == "ok" else 1
    return _emit_implicit_error()

def cmd_run_stream(args):
    """
    STREAM path:
      - Set APS_STREAM=1 for agent behavior switch
      - Write -> flush -> close stdin BEFORE reading any output
      - Drain stderr concurrently; mirror non-JSON stdout lines to stderr
      - Persist logs; print final JSON once to stdout
    """
    root = agent_root(args.path)
    mf = load_manifest(root)

    env = os.environ.copy()
    src_dir = root / "src"
    if src_dir.exists():
        env["PYTHONPATH"] = str(src_dir) + os.pathsep + env.get("PYTHONPATH", "")
    env.setdefault("PYTHONUNBUFFERED", "1")
    env["APS_STREAM"] = "1"
    env["APS_AGENT_ROOT"] = str(root)
    rt = next((r for r in mf.get("runtimes", []) if r.get("kind") == "python" and r.get("entrypoint")), None)
    if not rt:
        eprint("[run] ERROR: no python runtime")
        return 2
    entry = rt["entrypoint"]
    if isinstance(entry, str):
        entry = shlex.split(entry)

    # Read + wrap user stdin first
    raw = sys.stdin.read() or ""
    req = _wrap_request(raw, getattr(args, "input", None))

    proc = subprocess.Popen(
        entry, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env=env, cwd=str(root), bufsize=1
    )

    # Strict ordering: write->flush->close BEFORE reads
    try:
        to_send = req if req.endswith("\n") else req + "\n"
        proc.stdin.write(to_send)
        proc.stdin.flush()
    except BrokenPipeError:
        pass
    finally:
        try: proc.stdin.close()
        except Exception: pass

    collected_stderr: list[str] = []

    def _drain_err(pipe):
        for line in iter(pipe.readline, ''):
            if not line:
                break
            collected_stderr.append(line)
            eprint(line.rstrip("\n"))
        try: pipe.close()
        except Exception: pass

    t = threading.Thread(target=_drain_err, args=(proc.stderr,), daemon=True)
    t.start()

    final_json = None
    for line in iter(proc.stdout.readline, ''):
        s = line.rstrip("\n")
        if not s:
            continue
        obj = _is_json_status_line(s)
        if obj:
            final_json = obj
            if obj.get("status") == "error":
                break
        else:
            # Non-JSON stdout is treated as log; mirror to stderr
            eprint(s)

    try: proc.stdout.close()
    except Exception: pass
    proc.wait()

    _write_log(root, mf, collected_stderr, final_json)
    if final_json:
        print(json.dumps(final_json))
        return 0 if final_json.get("status") == "ok" else 1
    return _emit_implicit_error()

def cmd_run(args):
    path = _resolve_registry_path_if_needed(args.path)
    if getattr(args, "stream", False):
        # stream mode uses its own runner (already reads stdin internally)
        args.path = path
        return cmd_run_stream(args)
    else:
        # sync mode reads stdin here then calls helper
        raw = sys.stdin.read() or ""
        req = _wrap_request(raw, getattr(args, "input", None))
        args.path = path
        return helper_run_agent(args.path, req, timeout_s=args.timeout)

def cmd_logs(args):
    resolved = _resolve_registry_path_if_needed(args.path)
    root = agent_root(resolved)
    mf = load_manifest(root)
    d = _logs_dir_for(mf.get("id","unknown"), mf.get("version","unknown"))
    if not d.exists():
        eprint(f"[logs] no logs for {mf.get('id')}@{mf.get('version')} in {d}")
        return 1
    files = sorted(d.glob("*.log"))
    if not files:
        eprint(f"[logs] no log files found in {d}")
        return 1
    if args.latest:
        print(files[-1].read_text(encoding="utf-8"), end="")
        return 0
    for f in files:
        print(f.name)
    return 0

def cmd_inspect(args):
    p = Path(args.path)
    if p.is_file() and p.suffixes[-2:] == [".tar", ".gz"]:
        try:
            with tarfile.open(p, "r:gz") as tf:
                m = tf.getmember("aps/agent.yaml")
                with tf.extractfile(m) as f:
                    manifest = yaml.safe_load(f.read().decode("utf-8"))
        except Exception as e:
            eprint(f"[inspect] ERROR: {e}")
            return 1
    else:
        manifest = load_manifest(agent_root(p))
    print(json.dumps(manifest, indent=2))
    return 0

    # --- Signing
def cmd_keygen(_):
    ensure_keypair()
    print("[keys] ready at ~/.aps/keys"); return 0

def cmd_sign(args):
    pkg = Path(args.package).resolve()
    digest = sha256_file(pkg)
    sk = load_privkey()
    payload = json.dumps({"file": pkg.name, "digest": digest}).encode()
    sig = ed25519_sign(sk, payload)
    out = pkg.with_suffix(pkg.suffix + ".sig.json")
    out.write_text(json.dumps({"payload": base64.b64encode(payload).decode(), "sig": base64.b64encode(sig).decode()}))
    print(str(out)); return 0

def cmd_verify(args):
    sigf = Path(args.signature).resolve()
    sigobj = json.loads(sigf.read_text())
    payload = base64.b64decode(sigobj["payload"])
    sig = base64.b64decode(sigobj["sig"])
    pk = load_pubkey()
    ok = ed25519_verify(pk, payload, sig)
    print("OK" if ok else "INVALID"); return 0 if ok else 2


def cmd_registry_serve(args):
    # Launch FastAPI registry in-process
    import uvicorn
    from aps_registry.server import create_app
    app = create_app(args.root)
    eprint(f"[registry] serving at 0.0.0.0:{args.port} (root={args.root})")
    uvicorn.run(app, host="0.0.0.0", port=int(args.port), log_level="info")

# ------------------------------ Argparse / Main

def main(argv=None):
    parser = argparse.ArgumentParser(prog="aps", add_help=True)
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    sub = parser.add_subparsers(dest="cmd")
    import sys, os
    print("DBG sys.path[0]:", sys.path[0], file=sys.stderr, flush=True)
    print("DBG PYTHONPATH:", os.environ.get("PYTHONPATH"), file=sys.stderr, flush=True)

    p = sub.add_parser("validate", help="Validate an agent manifest")
    p.add_argument("path")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("build", help="Build an APS package (.aps.tar.gz)")
    p.add_argument("path")
    p.add_argument("--dist", default=None)
    p.set_defaults(func=cmd_build)

    #
    # init
    #
    s = sub.add_parser("init", help="Create a new APS agent scaffold")
    s.add_argument("path")
    s.set_defaults(func=cmd_init)
    
    p = sub.add_parser("publish", help="Publish a built package to a registry")
    p.add_argument("package")
    p.add_argument("--registry", default=DEFAULT_REGISTRY)
    p.set_defaults(func=cmd_publish)

    p = sub.add_parser("pull", help="Pull an agent from registry into local cache")
    p.add_argument("agent")
    p.add_argument("--version", default="latest")
    p.add_argument("--registry", default=DEFAULT_REGISTRY)
    p.set_defaults(func=cmd_pull)

    p = sub.add_parser("run", help="Run an agent (dir or registry://id)")
    p.add_argument("path")
    p.add_argument("--stream", action="store_true", help="Enable streaming mode")
    p.add_argument("--input", default=None, help="When raw input, wrap under inputs.{key}")
    p.add_argument("--timeout", type=int, default=None, help="Timeout seconds (sync only)")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("logs", help="Show saved logs for an agent")
    p.add_argument("path")
    p.add_argument("--latest", action="store_true")
    p.set_defaults(func=cmd_logs)

    p = sub.add_parser("inspect", help="Inspect manifest from dir or tarball")
    p.add_argument("path")
    p.set_defaults(func=cmd_inspect)

    #
    # signing
    #
    s = sub.add_parser("keygen", help="Generate signing keys")
    s.set_defaults(func=cmd_keygen)

    s = sub.add_parser("sign", help="Sign an APS package")
    s.add_argument("package")
    s.set_defaults(func=cmd_sign)

    s = sub.add_parser("verify", help="Verify APS signature")
    s.add_argument("signature")
    s.set_defaults(func=cmd_verify)

    #
    # registry serve
    #

    p = sub.add_parser("registry", help="Registry commands")
    s = p.add_subparsers(dest="subcmd")
    r = s.add_parser("serve", help="Start a local APS registry")
    r.add_argument("--root", default="registry_data")
    r.add_argument("--port", type=int, default=8080)
    r.set_defaults(func=cmd_registry_serve)

    args = parser.parse_args(argv)

    # Show version
    if getattr(args, "version", False) and args.cmd is None:
        print("aps-cli 0.1.0")
        return 0
    
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
