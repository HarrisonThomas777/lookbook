# One-off: build codes.json (goods id -> product code) from the catalogue that is already live,
# so the automated rebuilds keep every existing product code unchanged.
import json, sys, os
D = sys.argv[1]  # folder holding items.jsonl and data-plain/
key2id = {}
for line in open(os.path.join(D, 'items.jsonl')):
    i = json.loads(line)
    key2id[(i['ts'], i['imgs'][0] if i['imgs'] else i['vt'])] = i['id']
codes = {'next': {}, 'items': {}}
miss = 0
for f in os.listdir(os.path.join(D, 'data-plain')):
    if f == 'index.json' or not f.endswith('.json'):
        continue
    for r in json.load(open(os.path.join(D, 'data-plain', f))):
        gid = key2id.get((r['ts'], r['im'][0] if r['im'] else r['vt']))
        if not gid:
            miss += 1
            continue
        codes['items'][gid] = r['c']
        pf, n = r['c'].split('-')
        codes['next'][pf] = max(codes['next'].get(pf, 0), int(n))
json.dump(codes, open('codes.json', 'w'), separators=(',', ':'))
print('seeded', len(codes['items']), 'codes, unmatched', miss, codes['next'])
