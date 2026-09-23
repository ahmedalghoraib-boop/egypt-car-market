# -*- coding: utf-8 -*-
"""chips_fill v2: FB Marketplace cards lack url keys in json? -> they come from data with url but our
key match failed for facebook item ids; add trans/year from title-known mapping instead."""
import re, json
p="/tmp/car-site/index.html"
html=open(p,encoding="utf-8").read()
data=json.load(open("/tmp/car-site/listings.json",encoding="utf-8"))

# Explicit knowledge from json listing rows (fb items, by item id)
FB = {
 '1380984893922735': ('auto', 1992),
 '1616979376638554': (None, 1991),
 '1827515691606786': ('auto', 1992),
 '1571288438059685': ('manual', 2001),
 '872387595816189': ('auto', 2007),
 '2104212240310906': (None, 1992),
 '2119442688647675': ('auto', 1992),
 '1794850248200983': (None, 2019),
 '1029975739522206': (None, 1992),
 '1135085155519206': ('auto', 1992),
 '1044289175173643': ('auto', 1992),
 '1427108649297020': (None, 1992),
 '2225480188297630': ('manual', 2001),
 '1718821735684618': (None, 2008),   # GTC auto box, title says أوتوماتيك
 '1362850595828071': (None, 1997),
 '4617614171853998': (None, 1996),
 '2368544463758849': ('manual', 1997),
 '1551686706261917': (None, 1997),
 '1240469888269691': (None, 2008),
 '1058523209896512': ('manual', 1997),
 '3503590183151155': ('manual', 1998),
 '994926009578175': (None, 1998),
 'ID208995919': ('auto', 2000),
}
# Cruze ref cards metadata
NON_URL = {'Chevrolet Cruze 2014': ('auto', 2014), 'Chevrolet Cruze 2013': ('auto', 2013)}

starts=[m.start() for m in re.finditer(r'<div class="card(?: pick| warn)?"', html)]
ends=starts[1:]+[len(html)]
out=[]; pos=0; ntouched=0
for s,e in zip(starts,ends):
    out.append(html[pos:s]); pos=e
    seg=html[s:e]
    row=re.search(r'</h4>\s*<div>(.*?)</div>', seg, re.S)
    h4=re.search(r'<h4>(.*?)</h4>', seg, re.S)
    if not row or not h4:
        out.append(seg); continue
    htxt=h4.group(1)
    u=re.search(r'<a class="btn" href="([^"]+)"', seg)
    tr=yr=None
    if u:
        key=u.group(1).rstrip('/').rsplit('/',1)[-1].replace('.html','')
        for k,(t,y) in FB.items():
            if k in key: tr,yr = t,y; break
        else:
            rec=next((r for r in data if r['url'] and key in r['url']), None)
            if rec: tr=rec.get('transmission'); yr=rec.get('year')
        if tr is None and yr is None:
            (tr, yr) = FB.get(key, (None, None))
    else:
        for name,(t,y) in NON_URL.items():
            if name in htxt: tr,yr = t,y; break
    tags=[t for t in re.findall(r'<span class="tag">(.*?)</span>', row.group(1)) if t.strip()]
    changed=False
    if tr and 'أوتوماتيك' not in ' '.join(tags) and 'مانيوال' not in ' '.join(tags):
        tr_ar={'manual':'مانيوال','auto':'أوتوماتيك'}[tr]
        tags=[tr_ar]+tags; changed=True
    if yr and not any(re.fullmatch(r'(19|20)\d{2}', t) for t in tags):
        i = 1 if tags and tags[0] in ('مانيوال','أوتوماتيك') else 0
        tags.insert(i, str(yr)); changed=True
    # also remove empty tags
    if changed or len(tags)!=len(re.findall(r'<span class="tag">(.*?)</span>', row.group(1))):
        rownew='<div>'+''.join(f'<span class="tag">{t}</span>' for t in tags)+'</div>'
        seg=seg[:row.start()+6]+rownew+seg[row.end():]
        ntouched+=1
    out.append(seg)
out.append(html[pos:])
new=''.join(out).replace('<span class="tag"></span>','')
open(p,"w",encoding="utf-8").write(new)
print("cards touched:", ntouched)
