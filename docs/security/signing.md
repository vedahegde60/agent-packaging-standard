# APS Signing & Provenance

## Goal
Assure authenticity + integrity of agent packages.

## Format
- DSSE envelopes (in-toto compatible)
- Sign: `aps sign`
- Verify: `aps verify`

## Artifacts
agent/
aps/agent.yaml
aps/provenance.json
aps/signature.sig


## Trust Model
- Local key config
- Future: public key registry / transparency log

