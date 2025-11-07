
### 🧪 `examples/stream-agent/main.py`

import json, sys, time

req = json.load(sys.stdin)
text = req["inputs"]["text"]

for ch in text:
    print(ch, flush=True)
    time.sleep(0.1)

print(json.dumps({
    "status":"ok",
    "outputs": {"reverse": text[::-1]}
}))

