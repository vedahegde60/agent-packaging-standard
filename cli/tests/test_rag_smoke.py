# cli/tests/test_rag_smoke.py
import io, types, json
from pathlib import Path
import aps_cli.app as app

def test_rag_local(tmp_path, monkeypatch):
    root = Path("examples/rag-agent").resolve()
    assert (root / "aps" / "agent.yaml").exists()
    req = '{"aps_version":"0.1","operation":"run","inputs":{"query":"APS","top_k":1}}'
    monkeypatch.setattr("sys.stdin", io.StringIO(req))
    ns = types.SimpleNamespace(path=str(root), stream=False, input=None, timeout=10)
    rc = app.cmd_run(ns)
    assert rc == 0
