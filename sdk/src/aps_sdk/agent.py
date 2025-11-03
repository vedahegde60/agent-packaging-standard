import json, sys

def handler(fn):
    def _main():
        raw = sys.stdin.read().strip()
        if not raw:
            print(json.dumps({"status":"error","message":"empty"})); return
        try:
            req = json.loads(raw)
        except Exception as e:
            print(json.dumps({"status":"error","message":f"invalid json: {e}"})); return
        try:
            out = fn(req.get("inputs") or {})
            print(json.dumps({"status":"ok","outputs": out}))
        except Exception as e:
            print(json.dumps({"status":"error","message":str(e)}))
    return _main

