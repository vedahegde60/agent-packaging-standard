import argparse, sys, os, tarfile, tempfile, json, subprocess, shutil, hashlib, base64
from pathlib import Path
import requests
import yaml
from .signing import (
    ensure_keypair, load_pubkey, load_privkey,
    ed25519_sign, ed25519_verify
)

def agent_root(p: str) -> Path:
    root = Path(p).resolve()
    mf = root / "aps" / "agent.yaml"
    if not mf.exists(): raise FileNotFoundError(f"Missing manifest: {mf}")
    return root

def load_manifest(root: Path) -> dict:
    with open(root/"aps"/"agent.yaml","r",encoding="utf-8") as f:
        return yaml.safe_load(f)

def tarball_build(root: Path, outdir: Path) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    name = load_manifest(root).get("id","agent").replace("/", ".")
    out = outdir / f"{name}.aps.tar.gz"
    with tarfile.open(out, "w:gz") as tar:
        for item in ["aps","src","AGENT_CARD.md","README.md","requirements.txt"]:
            p = root/item
            if p.exists():
                tar.add(p, arcname=str(item))
    return out

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
    return "sha256:" + h.hexdigest()

def cmd_build(args):
    root = agent_root(args.path)
    out = tarball_build(root, Path(args.dist))
    print(str(out))
    return 0

def cmd_run(args):
    root = agent_root(args.path)
    mf = load_manifest(root)
    # auto PYTHONPATH for src
    env = os.environ.copy()
    src_dir = root/"src"
    if src_dir.exists():
        env["PYTHONPATH"] = str(src_dir) + os.pathsep + env.get("PYTHONPATH","")
    # pick first python runtime
    rt = None
    for r in mf.get("runtimes", []):
        if r.get("kind") == "python" and r.get("entrypoint"): rt = r; break
    if not rt: print("[run] ERROR: no python runtime", file=sys.stderr); return 2
    entry = rt["entrypoint"]
    # read stdin fully, pass to child
    req = sys.stdin.read()
    proc = subprocess.Popen(entry, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, cwd=str(root))
    out, err = proc.communicate(input=req)
    if err: print(err, file=sys.stderr)
    if out: print(out, end="")
    return proc.returncode

def cmd_shell(args):
    root = agent_root(args.path)
    print("APS shell: paste one JSON request per line. Ctrl+C to exit.")
    while True:
        try: line = input("> ").strip()
        except KeyboardInterrupt: print(); return 0
        if not line: continue
        p = subprocess.Popen([sys.executable,"-m","aps_cli.app","run",str(root)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out,_ = p.communicate(input=line)
        print(out, end="")

def cmd_validate(args):
    try:
        root = agent_root(args.path)
        mf = load_manifest(root)
    except Exception as e:
        print(f"[validate] ERROR: {e}", file=sys.stderr)
        return 2

    missing = [k for k in ("id","name","version","runtimes","capabilities") if k not in mf]
    if missing:
        print(f"[validate] ERROR: missing keys: {missing}", file=sys.stderr)
        return 2

    rts = mf.get("runtimes") or []
    ok = any(isinstance(rt, dict) and rt.get("kind") == "python" and rt.get("entrypoint") for rt in rts)
    if not ok:
        print("[validate] ERROR: no python runtime with entrypoint", file=sys.stderr)
        return 2

    print("[validate] OK")
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

# --- Registry client
def cmd_publish(args):
    pkg = Path(args.package).resolve()
    url = args.registry.rstrip("/") + "/v1/publish"
    with open(pkg, "rb") as f:
        r = requests.post(url, files={"file": ("package.tar.gz", f, "application/gzip")})
    if r.status_code not in (200,201): print(r.text, file=sys.stderr); return 2
    print(r.json()); return 0

def cmd_pull(args):
    url = args.registry.rstrip("/") + f"/v1/pull?id={args.id}"
    r = requests.get(url, stream=True)
    if r.status_code!=200: print(r.text, file=sys.stderr); return 2
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        shutil.copyfileobj(r.raw, f)
    print(str(out)); return 0

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
    # run the local registry server (uvicorn) without extra deps if possible
    return subprocess.call([sys.executable, "-m", "aps_registry.server", "--root", args.root, "--port", str(args.port)])

def main(argv=None):
    # Create top-level parser
    parser = argparse.ArgumentParser(
        prog="aps",
        description="APS CLI — Agent Packaging Standard"
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    sub = parser.add_subparsers(dest="cmd")

    #
    # validate
    #
    s = sub.add_parser("validate", help="Validate an APS agent directory")
    s.add_argument("path")
    s.set_defaults(func=cmd_validate)

    #
    # build
    #
    s = sub.add_parser("build", help="Build .aps.tar.gz for an agent")
    s.add_argument("path")
    s.add_argument("--dist", default="dist")
    s.set_defaults(func=cmd_build)

    #
    # run
    #
    s = sub.add_parser("run", help="Run an APS agent (stdin->stdout JSON)")
    s.add_argument("path")
    s.set_defaults(func=cmd_run)

    #
    # shell
    #
    s = sub.add_parser("shell", help="Interactive test shell")
    s.add_argument("path")
    s.set_defaults(func=cmd_shell)

    #
    # init
    #
    s = sub.add_parser("init", help="Create a new APS agent scaffold")
    s.add_argument("path")
    s.set_defaults(func=cmd_init)

    #
    # publish
    #
    s = sub.add_parser("publish", help="Publish agent package to registry")
    s.add_argument("package")
    s.add_argument("--registry", required=True)
    s.set_defaults(func=cmd_publish)

    #
    # pull
    #
    s = sub.add_parser("pull", help="Pull agent from registry")
    s.add_argument("--registry", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--out", default="dist/pulled.aps.tar.gz")
    s.set_defaults(func=cmd_pull)

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
    # registry server
    #
    s = sub.add_parser("registry", help="Local registry operations")
    ss = s.add_subparsers(dest="sub")
    r = ss.add_parser("serve", help="Run local registry server")
    r.add_argument("--root", default="registry_data")
    r.add_argument("--port", type=int, default=8080)
    r.set_defaults(func=cmd_registry_serve)

    #
    # Parse + dispatch
    #
    args = parser.parse_args(argv)

    # Show version
    if getattr(args, "version", False) and args.cmd is None:
        print("aps-cli 0.1.0")
        return 0

    # If no subcommand: show help
    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    # Execute command handler
    return args.func(args)



if __name__ == "__main__":
    raise SystemExit(main())
