# APS Signing Model (v0)

## Goals
- Integrity & authenticity of `.aps.tar.gz` artifacts.
- Simple local trust (developer keys), enterprise policy later.

## Artifacts
- dist/<id>.aps.tar.gz
- dist/<id>.aps.tar.gz.sig.json # DSSE-lite: base64(payload) + base64(sig)


**Payload (JSON, then base64 in the .sig.json):**
```json
{ "file": "<filename>.aps.tar.gz", "digest": "sha256:<hex>" }
```
Signature: Ed25519 over the UTF-8 bytes of the payload JSON.

## CLI
```bash
aps keygen                      # creates ~/.aps/keys/{ed25519.key,ed25519.pub}
aps sign dist/pkg.aps.tar.gz    # emits dist/pkg.aps.tar.gz.sig.json
aps verify dist/pkg.aps.tar.gz.sig.json
```
## Trust(v0)
	- Local trust store: ~/.aps/keys/ed25519.pub

	- Policy (future): require signatures from known keys; transparency log optional.

## Supply Chain (future v1)

	- DSSE + in-toto provenance document aps/provenance.json

	- Enterprise policy: block unsigned/unknown keys


