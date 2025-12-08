# APS Publish Workflow

## Build
```bash
aps build my-agent
```

Creates `my-agent/dist/dev.my-agent.aps.tar.gz`

## Sign (optional)

First, generate a keypair (one time):
```bash
aps keygen
```

Then sign your package:
```bash
aps sign my-agent/dist/dev.my-agent.aps.tar.gz --key default
```

## Publish
```bash
aps publish my-agent/dist/dev.my-agent.aps.tar.gz --registry http://localhost:8080
```

## Verify
```bash
aps verify my-agent/dist/dev.my-agent.aps.tar.gz --pubkey ~/.aps/keys.pub/default.pub
```
