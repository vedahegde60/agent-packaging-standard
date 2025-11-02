# APS Publish Workflow

## Build
```bash
aps build

Creates a .aps.tar.gz

##Sign (optional)

aps sign dist/myagent.aps.tar.gz


##PUblish

aps publish --registry=https://registry.aps.dev \
  dist/myagent.aps.tar.gz

## Verify
aps verify dist/myagent.aps.tar.gz

