# cli/tests/conftest.py
import os
import io
import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_aps_dirs(tmp_path, monkeypatch):
    """
    Ensure tests never touch the user's real ~/.aps.
    """
    monkeypatch.setenv("APS_CACHE_DIR", str(tmp_path / ".cache"))
    monkeypatch.setenv("APS_LOGS_DIR", str(tmp_path / ".logs"))
    # Keep registry default unless the test overrides
    yield


class DummyResp:
    """
    Tiny stand-in for requests.Response for GETs returning JSON.
    """
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status
        self.text = json.dumps(payload) if isinstance(payload, (dict, list)) else str(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


@pytest.fixture
def dummy_resp():
    return DummyResp


def make_cached_agent(cache_dir: Path, agent_id="dev.echo", version="0.0.3"):
    """
    Create a minimal agent in the APS cache shape:
      <cache>/<id>/<version>/aps/agent.yaml
                                /src/echo/main.py
    Uses a file-based entrypoint so PYTHONPATH isn't required.
    """
    root = cache_dir / agent_id / version
    (root / "aps").mkdir(parents=True, exist_ok=True)
    (root / "src" / "echo").mkdir(parents=True, exist_ok=True)

    (root / "aps" / "agent.yaml").write_text(
        """aps_version: 0.1
id: dev.echo
name: Echo
version: %s
summary: Echo test agent
runtimes:
  - kind: python
    entrypoint: python src/echo/main.py
inputs:
  text: {type: string}
outputs:
  text: {type: string}
""" % version,
        encoding="utf-8",
    )

    (root / "src" / "echo" / "main.py").write_text(
        r"""import sys, json, os, time

def parse_inputs(raw: str):
    try:
        obj = json.loads(raw) if raw.strip() else {}
    except Exception:
        obj = {}
    if isinstance(obj, dict) and isinstance(obj.get("inputs"), dict):
        return obj["inputs"]
    return obj if isinstance(obj, dict) else {}

def main():
    raw = sys.stdin.read() or ""
    inputs = parse_inputs(raw)
    text = inputs.get("text", "")

    if os.environ.get("APS_STREAM") == "1":
        acc = ""
        for ch in text:
            acc += ch
            print(f"[stream] {ch}", flush=True)
            time.sleep(0.005)
        print(json.dumps({"aps_version":"0.1","status":"ok","outputs":{"text":acc}}), flush=True)
    else:
        print(json.dumps({"aps_version":"0.1","status":"ok","outputs":{"text":text}}))

if __name__ == "__main__":
    main()
""",
        encoding="utf-8",
    )
    return root


@pytest.fixture
def fabricate_cached_agent(tmp_path):
    """
    Helper fixture: returns (agent_id, version, root_path) after creating the cached agent.
    """
    cache_dir = tmp_path / ".cache"
    agent_id = "dev.echo"
    version = "0.0.9"
    root = make_cached_agent(cache_dir, agent_id=agent_id, version=version)
    return agent_id, version, root


@pytest.fixture
def stdin_json(monkeypatch):
    """
    Helper to inject JSON text into sys.stdin.
    Usage:
       stdin_json('{"inputs":{"text":"hi"}}')
    """
    def _inject(s: str):
        monkeypatch.setattr("sys.stdin", io.StringIO(s))
    return _inject
