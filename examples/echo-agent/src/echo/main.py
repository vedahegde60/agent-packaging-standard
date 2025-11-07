# examples/echo-agent/src/echo/main.py
import sys, os, json, time

def is_stream():
    return os.environ.get("APS_STREAM") == "1"

def parse_inputs(raw: str):
    try:
        req = json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}
    if isinstance(req, dict) and isinstance(req.get("inputs"), dict):
        return req["inputs"]
    return req if isinstance(req, dict) else {}

def main():
    raw = sys.stdin.read() or ""
    inputs = parse_inputs(raw)
    text = inputs.get("text", "")

    if is_stream():
        acc = ""
        for ch in text:
            acc += ch
            print(f"[stream] {ch}", flush=True)  # logs
            time.sleep(0.01)
        print(json.dumps({"aps_version":"0.1","status":"ok","outputs":{"text": acc}}), flush=True)
    else:
        print(json.dumps({"aps_version":"0.1","status":"ok","outputs":{"text": text}}))

if __name__ == "__main__":
    main()


