# Security & Provenance (draft)

APS aims to be “trustable by default”.

## Goals
- Identify who built and published the agent
- Bind manifest to a content hash
- Support signatures (DSSE) and provenance (in-toto/SLSA)

## Minimal approach (v0.x)
1. Compute a content digest of the agent package (tar/zip or git commit).
2. Create a DSSE envelope with the digest + manifest id/version.
3. Sign with ed25519 (age/SSH/mini-sign keys acceptable).
4. Publish manifest + signature + optional provenance.

## Example DSSE-like payload
```json
{
  "payloadType": "application/vnd.aps.manifest.v0+json",
  "payload": {
    "id": "dev.rag",
    "version": "0.0.1",
    "digest": "sha256:abcd...1234"
  },
  "signatures": [
    { "keyid": "pubkey:...base64...", "sig": "base64..." }
  ]
}

