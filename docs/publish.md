# APS Publish Workflow

## Build
```bash
aps build

Creates a .aps.tar.gz
```
##Sign (optional)
```bash
aps sign dist/myagent.aps.tar.gz
```

##PUblish
```bash
aps publish --registry=https://registry.aps.dev \
  dist/myagent.aps.tar.gz
```
## Verify
```bash
aps verify dist/myagent.aps.tar.gz
```
