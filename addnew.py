#!/usr/bin/env python3
# append ADDED_ITEMS snapshots into /tmp/car-site/listings.json (idempotent)
import json, re, html, os, sys

P = '/tmp/car-site/listings.json'
d = json.load(open(P, encoding='utf-8'))
keymap = {"civic": "honda-civic-1995", "e36": "bmw-e36", "astra": "opel-astra"}

items = [
 {"id":"1380984893922735","title":"Honda Civic 1992 — Shebin al-Kom","price":285000,
  "cond":"هوندا سيفيك موديل ١٩٩٢ \nدواخل زيرو \nراشه برا نضافه \nطقم جنط سبور \nتكيف شغال"},
 {"id":"846678185140079","title":"BMW E36 1992 (1800cc auto) — Dumyat","price":300000,
  "cond":"اوتوماتيك مكنه ١٨٠٠ فبريكا دواخل بدون اي ملحوظه العربيه خارجه من شده عفشه وماتور جديد لسه راكب رينجات وليد عالي وطقم سماعات وچي ام رخصه لاخر السنه مرور التجمع الخامس"},
 {"id":"1616979376638554","title":"BMW 1991 manual (2000cc 6-cyl swap) — Giza","price":285000,
  "cond":open('/tmp/car-site/desc_1616979376638554.txt',encoding='utf-8').read().strip()},
 {"id":"1827515691606786","title":"BMW E36 1992 auto — Cairo","price":290000,
  "cond":open('/tmp/car-site/desc_1827515691606786.txt',encoding='utf-8').read().strip()},
 {"id":"1551766360031120","title":"Opel Astra 2004 — Cairo","price":260000,
  "cond":open('/tmp/car-site/desc_1551766360031120.txt',encoding='utf-8').read().strip()},
 {"id":"1571288438059685","title":"Opel Astra 2001 manual 1200cc — 6 October","price":205000,
  "cond":open('/tmp/car-site/desc_1571288438059685.txt',encoding='utf-8').read().strip()},
 {"id":"872387595816189","title":"Opel Astra 2007 auto — El-Bagour","price":225000,
  "cond":open('/tmp/car-site/desc_872387595816189.txt',encoding='utf-8').read().strip()},
]

existing = {l.get('url','').rstrip('/').split('/')[-1] for l in d['listings']}
added = 0
for it in items:
    if it['id'] in existing:
        continue
    t = it['title']
    mk = 'civic' if 'Civic' in t else ('e36' if 'BMW' in t else 'astra')
    d['listings'].append({
        "model_key": mk,
        "platform": "Facebook Marketplace",
        "url": f"https://www.facebook.com/marketplace/item/{it['id']}/",
        "price": it['price'],
        "year": 2004 if '2004' in t else (2001 if '2001' in t else (2007 if '2007' in t else None)),
        "title": t,
        "condition": it['cond'],
        "location": None,
        "transmission": None,
        "km": None,
        "pick": False,
        "bad": False,
        "status": "active",
        "first_seen": "2026-09-22",
        "seller_name": None,
        "seller_phone": None
    })
    added += 1

json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('added', added, 'total', len(d['listings']))
