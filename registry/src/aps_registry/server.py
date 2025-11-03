# registry/src/aps_registry/server.py

import argparse
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

from .store import Store

app = FastAPI()
STORE: Store | None = None

@app.post("/v1/publish")
async def publish(file: UploadFile = File(...)):
    data = await file.read()
    pkg_path = STORE.save_upload(file.filename, data)
    try:
        row = STORE.index_package(pkg_path)
    except Exception as e:
        pkg_path.unlink(missing_ok=True)
        raise HTTPException(400, f"Invalid package: {e}")
    return {"status": "ok", "agent": row}

@app.get("/v1/search")
def search(q: str = ""):
    return {"agents": STORE.search(q)}

@app.get("/v1/agents/{id}")
def get_agent(id: str):
    row = STORE.get_agent(id)
    if not row:
        raise HTTPException(404, "not found")
    return row

@app.get("/v1/pull")
def pull(id: str):
    pkg = STORE.get_package_path(id)
    if not pkg:
        raise HTTPException(404, "not found")
    def gen():
        with open(pkg, "rb") as f:
            yield from iter(lambda: f.read(65536), b"")
    return StreamingResponse(gen(), media_type="application/gzip")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="registry_data")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    global STORE
    STORE = Store(Path(args.root))

    uvicorn.run(app, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()
