# Scrapes every item from the Vicky store into items.jsonl. Gets its own visitor token.
import json, time, urllib.request, sys, ssl, threading, calendar, datetime, http.cookiejar
ALBUM='A201804151243384880035925'
HOST=f'https://{ALBUM.lower()}.wecatalog.cn'
CTX=ssl.create_default_context()
try:
    urllib.request.urlopen('https://www.google.com', timeout=5, context=CTX)
except Exception:
    CTX=ssl._create_unverified_context()
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
jar=http.cookiejar.CookieJar()
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), urllib.request.HTTPSHandler(context=CTX))
opener.addheaders=[('User-Agent',UA),('Referer',f'{HOST}/weshop/store/{ALBUM}')]
opener.open(f'{HOST}/weshop/store/{ALBUM}', timeout=30).read()
if not any(c.name=='token' for c in jar): print('no visitor token issued', file=sys.stderr); sys.exit(2)
P='https://xcimg.szwego.com/'
lock=threading.Lock(); out=open('items.jsonl','w'); total=[0]
def work(y,m):
    last=calendar.monthrange(y,m)[1]
    base=f'{HOST}/album/personal/all?&albumId={ALBUM}&startDate={y}-{m:02d}-01&endDate={y}-{m:02d}-{last}&auditPassword=&requestDataType=&transLang=en'
    ts=None; n=0; fails=0; buf=[]
    while True:
        url=base+(f'&slipType=1&timestamp={ts}' if ts else '')
        try:
            req=urllib.request.Request(url,data=b'',method='POST')
            d=json.load(opener.open(req,timeout=40)); r=d['result']; its=r['items']
        except Exception as e:
            fails+=1; time.sleep(2)
            if fails>20: print('GIVEUP',y,m,e,file=sys.stderr); break
            continue
        fails=0
        for i in its:
            buf.append(json.dumps({'id':i.get('goods_id'),'t':(i.get('title') or '').strip(),'s':(i.get('subTitle') or '').strip(),'tags':[t['tagName'] for t in (i.get('tags') or [])],'imgs':[u.replace(P,'') for u in (i.get('imgsSrc') or [])],'vt':(i.get('videoThumbImg') or '').replace(P,''),'v':(i.get('videoUrl') or '').replace(P,''),'ts':i.get('time_stamp')},ensure_ascii=False))
        n+=len(its)
        if len(buf)>=320:
            with lock: out.write('\n'.join(buf)+'\n')
            buf=[]
        nts=r.get('pagination',{}).get('pageTimestamp')
        if not its or not nts or nts==ts: break
        ts=nts
    with lock:
        if buf: out.write('\n'.join(buf)+'\n')
        total[0]+=n
    print('month',y,m,'items',n,file=sys.stderr,flush=True)
today=datetime.date.today()
months=[]; y,m=2025,5
while (y,m)<=(today.year,today.month):
    months.append((y,m)); m+=1
    if m>12: y,m=y+1,1
ths=[threading.Thread(target=work,args=a) for a in months]
for t in ths: t.start()
for t in ths: t.join()
out.close()
print('TOTAL',total[0],file=sys.stderr)
if total[0]<1000: print('too few items, refusing to publish', file=sys.stderr); sys.exit(3)
