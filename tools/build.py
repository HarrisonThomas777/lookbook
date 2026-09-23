# Turns items.jsonl into per-category data files, keeping product codes stable via codes.json.
import json, os, re, collections, sys, datetime
from brands import brand
PFX={'belt':'BT','dishes':'DS','hat':'HT','jewelry':'JW','lady bag':'LB','lady clothes':'LC','lady shoes':'LS','luggage':'LG','man clothes':'MC','man shoes':'MS','men bag':'MB','scarf':'SC','sunglasses':'SG','tie':'TI','wallets':'WL','watches':'WT'}
NAMES={'jewelry':'Jewellery','men bag':"Men's bags",'lady bag':"Ladies' bags",'lady clothes':"Ladies' clothing",'lady shoes':"Ladies' shoes",'man clothes':"Men's clothing",'man shoes':"Men's shoes",'wallets':'Wallets','watches':'Watches','sunglasses':'Sunglasses','scarf':'Scarves','hat':'Hats','belt':'Belts','tie':'Ties','luggage':'Luggage','dishes':'Homeware'}
ORDER=['lady bag','lady clothes','lady shoes','man clothes','man shoes','men bag','wallets','luggage','belt','scarf','hat','sunglasses','jewelry','watches','tie','dishes','other']
src, codes_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
codes=json.load(open(codes_path)) if os.path.exists(codes_path) else {'next':{},'items':{}}
items=[]; seen=set()
for line in open(src):
    line=line.strip()
    if not line: continue
    try: i=json.loads(line)
    except: continue
    if i['id'] in seen: continue
    seen.add(i['id']); items.append(i)
items.sort(key=lambda i:i['ts'])
cats=collections.OrderedDict()
for i in items:
    k=i['tags'][0] if i['tags'] else 'other'
    cats.setdefault(k,[]).append(i)
os.makedirs(out,exist_ok=True)
for f in os.listdir(out): os.remove(os.path.join(out,f))
index=[]; total=0; new=0
for k in ORDER:
    if k not in cats: continue
    pf=PFX.get(k,'MX'); rows=[]
    for i in cats[k]:
        c=codes['items'].get(i['id'])
        if not c:
            n=codes['next'].get(pf,0)+1; codes['next'][pf]=n; c=f'{pf}-{n:05d}'; codes['items'][i['id']]=c; new+=1
        rows.append({'c':c,'t':i['t'],'s':i['s'],'g':[NAMES.get(t,t) for t in i['tags']],'b':brand(i['t']),'im':i['imgs'],'vt':i['vt'],'v':i['v'],'ts':i['ts']})
    rows.reverse()
    key=re.sub(r'[^a-z]+','-',k); fn=f'{key}.json'
    json.dump(rows,open(os.path.join(out,fn),'w'),ensure_ascii=False,separators=(',',':'))
    bc=collections.Counter(r['b'] for r in rows)
    index.append({'key':key,'name':NAMES.get(k,'Other'),'code':pf,'count':len(rows),'file':fn,'brands':sorted(bc.items(),key=lambda x:(-x[1],x[0]))})
    total+=len(rows)
json.dump({'total':total,'categories':index,'generated':datetime.date.today().isoformat()},open(os.path.join(out,'index.json'),'w'))
json.dump(codes,open(codes_path,'w'),separators=(',',':'))
print('total',total,'new codes',new)
