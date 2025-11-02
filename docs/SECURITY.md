# APS Security Policy

## Threat Model
- Local execution by trusted user
- No remote code or networks unless declared in manifest
- Strict stdin/stdout interface

## Security Controls
- No network access (default)
- Optional signature + provenance files
- Secrets never bundled inside agent

## Reporting Vulnerabilities
Email: security@yourorg.com  
PGP Key: *optional*

## Best Practices for APS Agents
- Avoid uncontrolled subprocess launches
- Validate input schemas
- Log to stderr only, never stdout

## Known Risks
- Misuse if agent claims are inaccurate
- Developer trust required until signing pipeline enabled

