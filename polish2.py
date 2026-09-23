# -*- coding: utf-8 -*-
"""Final polish pass #2: tag/btn leftovers in cards that the VSlot guard skipped."""
import re
p="/tmp/car-site/index.html"
html=open(p,encoding="utf-8").read()
reps=[
 # card3 (E36 long-row twin)
 ('<span class="tag">1998</span><span class="tag">New Cairo</span><span class="tag">Facebook Marketplace</span>',
  '<span class="tag">1998</span><span class="tag">القاهرة الجديدة</span><span class="tag">فيسبوك ماركت بلاس</span>'),
 ('<span class="tag">1998</span><span class="tag">Alexandria</span><span class="tag">Facebook Marketplace</span>',
  '<span class="tag">1998</span><span class="tag">الإسكندرية</span><span class="tag">فيسبوك ماركت بلاس</span>'),
 ('<span class="tag">2005</span><span class="tag">Mokattam, Cairo</span><span class="tag">dubizzle</span>',
  '<span class="tag">2005</span><span class="tag">المقطم، القاهرة</span><span class="tag">دوبيزل</span>'),
 # BMW 316 1997
 ('<h4>BMW E36 316 1997 — <span class="price">260,000 جنيه</span></h4>',
  '<h4>BMW E36 316 موديل 1997 — <span class="price">260,000 جنيه</span></h4>'),
 ('<div><span class="tag">1997</span><span class="tag">Cairo</span><span class="tag">Facebook Marketplace</span></div>\n<a class="btn" href="https://www.facebook.com/marketplace/item/1058523209896512/">افتح: ↔</a>',
  '<div><span class="tag">1997</span><span class="tag">القاهرة</span><span class="tag">فيسبوك ماركت بلاس</span></div>\n<a class="btn" href="https://www.facebook.com/marketplace/item/1058523209896512/">افتح: المصدر ↗</a>'),
 # BMW e36 97 location chip
 ('<span class="tag">Shubra El Kheima</span>', '<span class="tag">شبرا الخيمة</span>'),
]
n=0
for a,b in reps:
    while a in html:
        html=html.replace(a,b); n+=1
# leftover 'افتح: ↔' and 'افتح: Dubizzle ↗' anywhere
html=html.replace('>افتح: ↔<','>افتح: المصدر ↗<')
html=html.replace('>افتح: Dubizzle ↗<','>افتح: دوبيزل ↗<')
open(p,"w",encoding="utf-8").write(html)
print("polish2 replacements:", n)
