
---

# 3) Registry API (paste to `docs/registry/api.md`)
```md
# APS Registry API (Draft v0.1)

Base URL: `/v1`

## Publish
`POST /v1/publish` (multipart form)

- field `file`: `.aps.tar.gz`

**200**
```json
{"status":"ok","agent":{"id":"dev.echo","name":"Echo","version":"0.0.1","summary":"Echoes the input text."}}
```
## Raw Publish (optional)
```bash
POST /v1/publish/raw (body: application/gzip)
```
200 Response
```json
{"status":"ok","agent":{"id":"dev.echo","name":"Echo","version":"0.0.1","summary":"..."}} 
```

## Search
```bash
GET /v1/search?q=<text>
```
200 Response
```json
{"agents":[{"id":"dev.echo","name":"Echo","version":"0.0.1","summary":"..."}]}
```
## Get Agent
```bash
GET /v1/agents/{id}
```
200 Response
```json
{"id":"dev.echo","name":"Echo","version":"0.0.1","summary":"..."}
```
## Pull Artifact
```bash
GET /v1/pull?id=<id>
```
Response: application/gzip stream of the .aps.tar.gz

## Health (optional)
```bash
GET /healthz → {"status":"ok"}
```
Notes

Index: SQLite (dev), Postgres (prod)

Auth: none (dev), token (future)

Signatures: served alongside artifacts (future endpoint /v1/signatures/{id})