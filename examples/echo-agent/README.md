# Echo Agent (example)

This mirrors the template agent under the CLI. It echoes `inputs.text`.

Quick test:

```bash
cd cli && pip install -e .
echo '{"aps_version":"0.1","operation":"run","inputs":{"text":"hello"}}' \
  | aps run ../examples/echo-agent

