# Echo Agent (example)

This mirrors the template agent under the CLI. It echoes `inputs.text`.

Quick test:

```bash
# Install CLI
pip install apstool

# Run the agent
echo '{"text":"hello"}' | aps run examples/echo-agent

