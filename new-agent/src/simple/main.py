import sys, json
raw=sys.stdin.read()
req=json.loads(raw)
text=(req.get('inputs') or {}).get('text','')
print(json.dumps({'status':'ok','outputs':{'text':text.upper()}}))
