# -*- coding: utf-8 -*-
"""Add transmission / year / cc chips wherever json knows them; drop empty tags."""
import re, json
p="/tmp/car-site/index.html"
html=open(p,encoding="utf-8").read()
data=json.load(open("/tmp/car-site/listings.json",encoding="utf-8"))
starts=[m.start() for m in re.finditer(r'<div class="card(?: pick| warn)?"', html)]
ends=starts[1:]+[len(html)]
out=[]
pos=0
ntrans=nempty=0
for s,e in zip(starts,ends):
    seg=html[s:e]
    u=re.search(r'<a class="btn" href="([^"]+)"', seg)
    out.append(html[pos:s])
    pos=e
    if not u:
        out.append(seg); continue
    key=u.group(1).rstrip('/').rsplit('/',1)[-1].replace('.html','')
    rec=next((r for r in data if r['url'] and key in r['url']), None)
    if rec is None:
        out.append(seg); continue
    row=re.search(r'</h4>\s*<div>(.*?)</div>', seg, re.S)
    if not row:
        out.append(seg); continue
    tags=re.findall(r'<span class="tag">(.*?)</span>', row.group(1), re.S)
    tags=[t for t in tags if t.strip()]
    has_trans=any(('أوتوماتيك' in t or 'مانيوال' in t or '1600cc' in t) for t in tags)
    changed=False
    if not has_trans:
        tr={'manual':'مانيوال','auto':'أوتوماتيك'}.get(rec.get('transmission'))
        if tr:
            tags=[tr]+tags; changed=True; ntrans+=1
    if any('1600cc' in t for t in tags) and rec.get('year') and not any(re.fullmatch(r'\d{4}',t) for t in tags):
        pass
    if not any(re.fullmatch(r'\d{4}',t) for t in tags) and rec.get('year'):
        # insert year after trans if present
        i = 1 if (tags and tags[0] in ('مانيوال','أوتوماتيك')) else 0
        tags.insert(i, str(rec['year'])); changed=True
    if changed:
        nempty+=1
        rownew='<div>'+''.join(f'<span class="tag">{t}</span>' for t in tags)+'</div>'
        seg=seg[:row.start()+6]+rownew+seg[row.end():]
    out.append(seg)
out.append(html[pos:])
new=''.join(out)
open(p,"w",encoding="utf-8").write(new)
print("trans added cards:", ntrans, "cards touched:", nempty)
