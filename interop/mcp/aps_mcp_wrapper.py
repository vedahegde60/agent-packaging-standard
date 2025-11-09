#!/usr/bin/env python3
# Minimal MCP-compatible JSON-RPC 2.0 wrapper for APS agents (stdio transport).
# - Exposes "agent.run" method
# - Params: {"path": "<agent-root>", "inputs": {...}, "stream": false, "timeout": null}
# - Returns: {"status":"ok","outputs":{...}} (agent's final line)
#
# NOTE: This is a minimal, dependency-free shim that follows MCP's JSON-RPC
#       shape over stdio. It is *not* a full MCP session manager, but it's
#       sufficient for testing tool invocation workflows.

import sys, json, os, subprocess, shlex, argparse, time
from pathlib import Path

def _jsonrpc(id=None, result=None, error=None, method=None, params=None):
    obj = {"jsonrpc":"2.0"}
    if id is not None: obj["id"] = id
    if result is not None: obj["result"] = result
    if error is not None: obj["error"] = error
    if method is not None: obj["method"] = method
    if params is not None: obj["params"] = params
    return obj

def _final_json_from_output(text: str):
    # Find last JSON line with "status"
    final = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and "status" in obj:
                    final = obj
            except Exception:
                pass
    return final

def _run_aps(path: str, inputs: dict, stream: bool=False, timeout: int|None=None):
    # Build APS envelope
    env = {"aps_version":"0.1","operation":"run","inputs": inputs or {}}
    req = json.dumps(env)

    # We will execute the agent's runtime directly (like your CLI), but without importing aps_cli.
    root = Path(path).resolve()
    # discover entrypoint: read manifest
    import yaml
    mf = yaml.safe_load((root/"aps"/"agent.yaml").read_text(encoding="utf-8"))
    rt = next((r for r in mf.get("runtimes", []) if r.get("kind")=="python" and r.get("entrypoint")), None)
    if not rt:
        return {"status":"error","error":{"code":"NO_RUNTIME","message":"No python runtime in manifest"}}

    entry = rt["entrypoint"]
    if isinstance(entry, str): entry = shlex.split(entry)

    child_env = os.environ.copy()
    src_dir = root / "src"
    if src_dir.exists():
        existing = child_env.get("PYTHONPATH")
        child_env["PYTHONPATH"] = str(src_dir) if not existing else str(src_dir)+os.pathsep+existing
    child_env.setdefault("PYTHONUNBUFFERED", "1")
    if stream:
        child_env["APS_STREAM"] = "1"

    if not stream:
        # sync: merge stderr to stdout
        p = subprocess.Popen(entry, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(root), env=child_env)
        out, _ = p.communicate(input=req, timeout=timeout)
        final = _final_json_from_output(out or "")
        return final or {"status":"error","error":{"code":"NO_FINAL_RESPONSE","message":"Agent produced no final JSON"}}
    else:
        # stream: write->flush->close then capture lines
        p = subprocess.Popen(entry, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=str(root), env=child_env, bufsize=1)
        try:
            to_send = req if req.endswith("\n") else req+"\n"
            p.stdin.write(to_send); p.stdin.flush(); p.stdin.close()
        except Exception:
            pass
        final = None
        start = time.time()
        while True:
            line = p.stdout.readline()
            if not line:
                if p.poll() is not None: break
                time.sleep(0.01)
                if timeout and (time.time()-start) > timeout:
                    p.kill(); break
                continue
            obj = _final_json_from_output(line)
            if obj: final = obj
        if final: return final
        return {"status":"error","error":{"code":"NO_FINAL_RESPONSE","message":"Agent produced no final JSON"}}

def main():
    # Read JSON-RPC messages from stdin; respond on stdout.
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw: continue
        try:
            msg = json.loads(raw)
        except Exception:
            # Ignore non-JSON noise
            continue

        if msg.get("method") == "initialize":
            # Minimal handshake
            resp = _jsonrpc(id=msg.get("id"), result={"capabilities":{"tools":True}})
            print(json.dumps(resp), flush=True)
            continue

        if msg.get("method") == "tools/list":
            # Advertise a single tool "agent.run"
            resp = _jsonrpc(id=msg.get("id"), result=[{
                "name":"agent.run",
                "description":"Run APS agent with inputs",
                "input_schema":{"type":"object","properties":{
                    "path":{"type":"string"},
                    "inputs":{"type":"object"},
                    "stream":{"type":"boolean"},
                    "timeout":{"type":["integer","null"]}
                }, "required":["path"]}}
            ])
            print(json.dumps(resp), flush=True)
            continue

        if msg.get("method") == "tools/call":
            params = msg.get("params") or {}
            name = params.get("name")
            args  = params.get("arguments") or {}
            if name != "agent.run":
                err = {"code": -32601, "message": "Method not found"}
                print(json.dumps(_jsonrpc(id=msg.get("id"), error=err)), flush=True); continue

            path = args.get("path")
            inputs = args.get("inputs", {})
            stream = bool(args.get("stream", False))
            timeout = args.get("timeout", None)
            result = _run_aps(path, inputs, stream=stream, timeout=timeout)
            print(json.dumps(_jsonrpc(id=msg.get("id"), result=result)), flush=True)
            continue

        # Default: respond with method not found
        err = {"code": -32601, "message": "Method not found"}
        print(json.dumps(_jsonrpc(id=msg.get("id"), error=err)), flush=True)

if __name__ == "__main__":
    main()

