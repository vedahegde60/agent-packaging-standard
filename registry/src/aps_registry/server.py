# registry/src/aps_registry/server.py
# FastAPI app factory for the APS Registry (no globals)
from __future__ import annotations
import os
from fastapi import FastAPI, Request, UploadFile, File, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from .store import Store

def create_app(root: str) -> FastAPI:
    app = FastAPI(title="APS Registry", version="0.1")
    app.state.store = Store(root)

    @app.get("/healthz")
    def healthz():
        return {"status":"ok"}

    @app.post("/v1/publish")
    def publish(request: Request, file: UploadFile = File(...)):
        # Read whole file in memory for simplicity; you can stream to disk if needed
        data = file.file.read()
        store: Store = request.app.state.store
        tmp = store.save_upload(file.filename, data)
        agent = store.index_package(tmp)
        return {"status":"ok","agent":agent}

    @app.get("/v1/search")
    def search(request: Request, q: str = Query("")):
        store: Store = request.app.state.store
        return {"agents": store.search(q)}

    @app.get("/v1/agents/{agent_id}")
    def get_agent(request: Request, agent_id: str):
        store: Store = request.app.state.store
        meta = store.get_agent(agent_id)
        if "error" in meta:
            raise HTTPException(status_code=404, detail="not found")
        return meta

    @app.get("/v1/agents/{agent_id}/download")
    def download_agent(request: Request, agent_id: str, version: str | None = None):
        store: Store = request.app.state.store
        ver = version or store.latest_version(agent_id)
        if not ver:
            raise HTTPException(status_code=404, detail="agent not found")
        pkg = store.package_path(agent_id, ver)
        if not os.path.exists(pkg):
            raise HTTPException(status_code=404, detail="package file not found")
        return FileResponse(pkg, media_type="application/gzip", filename=f"{agent_id}-{ver}.aps.tar.gz")

    return app
