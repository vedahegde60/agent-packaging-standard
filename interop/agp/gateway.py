#!/usr/bin/env python3
# FastAPI gateway that maps "AGP-style" JSON to APS execution.
# Endpoints:
#   POST /agp/execute   (json: { "agent": "<path|registry://id>", "inputs": {...}, "timeout": null })
#     -> {"status":"ok","outputs":{...}}
#   GET  /agp/execute/stream?agent=...  (body: same JSON as above, but respond as SSE)
#
# Requires: fastapi, uvicorn, pyyaml, requests (already in your repo/venv)

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, PlainTextResponse
import subprocess, os, json, shlex, time
from pathlib import Path

app = FastAPI(title="APS AGP Gateway", version="0.1")

def _run_aps(agent: str, inputs: dict, stream: bool=False, timeout: int|None=None):
    env = {"aps_version":"0.1","operation":"run","inputs":inputs or {}}
    req = json.dumps(env)
    # Use installed CLI 'aps' so registry:// works and resolver pulls when needed
    cmd = ["aps", "run"]
    if stream: cmd.append("--stream")
    cmd.append(agent)

    child_env = os.environ.copy()
    child_env.setdefault("PYTHONUNBUFFERED", "1")

    if not stream:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=child_env)
        out, _ = p.communicate(input=req, timeout=timeout)
        # extract final JSON line
        final = None
        for line in (out or "").splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    obj = json.loads(line)
                    if "status" in obj: final = obj
                except Exception:
                    pass
        return final or {"status":"error","error":{"code":"NO_FINAL_RESPONSE","message":"Agent produced no final JSON"}}
    else:
        # streaming as SSE
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=child_env, bufsize=1)
        try:
            to_send = req if req.endswith("\n") else req+"\n"
            p.stdin.write(to_send); p.stdin.flush(); p.stdin.close()
        except Exception:
            pass

        def _gen():
            final = None
            start = time.time()
            while True:
                line = p.stdout.readline()
                if not line:
                    if p.poll() is not None: break
                    time.sleep(0.01)
                    if timeout and (time.time()-start)>timeout:
                        p.kill(); break
                    continue
                s = line.strip()
                # Non-JSON lines as log events
                if not (s.startswith("{") and s.endswith("}")):
                    yield f"event: log\ndata: {s}\n\n"
                    continue
                try:
                    obj = json.loads(s)
                    if "status" in obj:
                        final = obj
                        yield f"event: final\ndata: {json.dumps(obj)}\n\n"
                except Exception:
                    yield f"event: log\ndata: {s}\n\n"
            if not final:
                err = {"status":"error","error":{"code":"NO_FINAL_RESPONSE","message":"Agent produced no final JSON"}}
                yield f"event: final\ndata: {json.dumps(err)}\n\n"

        return StreamingResponse(_gen(), media_type="text/event-stream")

@app.post("/agp/execute")
async def agp_execute(req: Request):
    body = await req.json()
    agent = body.get("agent")
    inputs = body.get("inputs", {})
    timeout = body.get("timeout", None)
    if not agent:
        raise HTTPException(400, "missing 'agent'")
    res = _run_aps(agent, inputs, stream=False, timeout=timeout)
    return JSONResponse(res)

@app.post("/agp/execute/stream")
async def agp_execute_stream(req: Request):
    body = await req.json()
    agent = body.get("agent")
    inputs = body.get("inputs", {})
    timeout = body.get("timeout", None)
    if not agent:
        raise HTTPException(400, "missing 'agent'")
    res = _run_aps(agent, inputs, stream=True, timeout=timeout)
    return res

# For local dev:
#   uvicorn interop.agp.gateway:app --reload --port 8090
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090)

