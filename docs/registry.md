# APS Registry Service

The APS Registry is a lightweight local or self-hosted service used to store and distribute APS agent packages (`.aps.tar.gz`).

It supports:
- Publishing agents
- Searching agents
- Retrieving metadata
- Serving cached packages for execution

This is NOT a model-hosting service. It is a metadata + tarball distribution layer.

---

## 🎯 Goals

| Goal | Description |
|---|---|
Local-first | Works offline on developer machines  
Simple | SQLite + tar storage  
Predictable | No background jobs or workers  
Secure by design | No arbitrary code execution on server  

---

## 🚀 Running the Registry

### Start

```bash
aps registry serve --root registry_data --port 8080
```
Stop

Use Ctrl-C or kill the process.
(Graceful stop endpoint will be added in APS v0.2.)

Default directory structure
