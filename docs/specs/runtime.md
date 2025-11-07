# APS Runtime Specification (v0.1)

APS defines a portable, streaming-capable execution contract for agents.

## Request Format

Agents receive **one JSON object via stdin**:

```json
{
  "aps_version": "0.1",
  "operation": "run",
  "inputs": { "... user fields …" }
}
```
## Required fields
| Field       | Type   | Description                            |
| ----------- | ------ | -------------------------------------- |
| aps_version | string | APS spec version                       |
| operation   | string | Action (`run`, future: `plan`, `info`) |
| inputs      | object | User request payload                   |

## Response Format

### Agents MUST emit final line JSON:
```json
{
  "status": "ok",
  "outputs": { "... agent result …" }
}
```
### Status Values

| value   | meaning                |
| ------- | ---------------------- |
| `ok`    | Successful execution   |
| `error` | Controlled agent error |


## Streaming Behavior (B1)

Agents MAY print text lines to stdout during execution.

Example:
```bash
Loading model...
Indexing data...
Query='hello'
{"status":"ok","outputs":{"answer":"42"}}
```
The last line must be JSON.
## Error Behavior (E3)
### Early controlled error
```json
{
  "status":"error",
  "error": {
    "code":"RUNTIME_ERROR",
    "message":"Bad input"
  }
}
```
### Implicit error (no final JSON)

CLI returns:
```json
{
  "status":"error",
  "error":{
    "code":"NO_FINAL_RESPONSE",
    "message":"Agent exited without valid JSON"
  }
}
```
## CLI Flags
| Flag           | Behavior                                |
| -------------- | --------------------------------------- |
| `--stream`     | Print logs live, only return final JSON |
| `--debug`      | Print logs + return logs + result       |
| `--input '{}'` | Wrap bare input into APS request        |



