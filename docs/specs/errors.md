# APS Error Model (v0.1)

## Controlled Error Format

```json
{
  "status":"error",
  "error":{
    "code":"INPUT_VALIDATION",
    "message":"Invalid field: name",
    "trace_id":"uuid"
  }
}
```

## Error Codes (initial)
| Code              | Meaning                    |
| ----------------- | -------------------------- |
| INPUT_VALIDATION  | Bad user input             |
| RUNTIME_ERROR     | Agent raised exception     |
| NO_FINAL_RESPONSE | Process ended without JSON |
| TIMEOUT           | Future                     |
| PERMISSION_DENIED | Future                     |

