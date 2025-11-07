
---

### 📄 `docs/specs/streaming.md`

```md
# APS Streaming Runtime Mode

## Mode: B1 (Text Streaming + Final JSON)

Agents may write arbitrary text to stdout.  
Final line must be JSON with status.

### Example

Loading DB...
Embedding...
{"status":"ok","outputs":{"x":1}}


### CLI rules

| Mode | Behavior |
|---|---|
default | buffer output, final JSON only |
--stream | print logs live + emit final JSON |
--debug | print logs + return `{result, logs}` |

### Future Extensions

| Feature | Version target |
|---|---|
JSONL event stream | v0.2 |
Token stream | v0.3 |
Telemetry channel | v0.3 |
