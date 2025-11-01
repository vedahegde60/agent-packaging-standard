# APS — Agent Packaging Standard (working title)

Package AI agents once, run them anywhere.  
Open spec + CLI. Apache 2.0. Community-led, foundation-bound later.

## Quick start
```bash
cd cli && pip install -e .
echo '{"aps_version":"0.1","operation":"run","inputs":{"text":"hello"}}' \
  | aps run ../examples/echo-agent
