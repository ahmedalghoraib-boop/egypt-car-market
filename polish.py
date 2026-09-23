# -*- coding: utf-8 -*-
import re, json
p = "/tmp/car-site/index.html"
html = open(p, encoding="utf-8").read()
# wrap-div close
if html.count('<div') != html.count('</div>'):
    html = html.replace('</body></html>', '</div>\n</body></html>', 1)
    if html.count('<div') == html.count('</div>'):
        html = html.replace('</div>\n</body></html>', '</body></html>', 1)
    else:
        html = html.replace('</div>\n</body></html>', '</body></html>', 1)  # revert accidental
# simpler: append missing close if short by exactly one at end:
if html.count('<div') == html.count('</div>') + 1 and html.rstrip().endswith('</body></html>'):
    html = html.replace('</body></html>', '</div>\n</body></html>')
REP = [
 (r'<h4>BMW E36 316i — first owner, US import — <span class="price">250,000 جنيه</span></h4>',
  r'<h4>BMW E36 316i 1998 — مالك أول، وارد أمريكا — <span class="price">250,000 جنيه</span></h4>'),
 (r'<h4>Honda Civic 1998 — handicap-import \(معاقين\) — <span class="price">235,000 جنيه</span></h4>',
  r'<h4>Honda Civic 1998 — وارد معاقين، مالك تاني — <span class="price">235,000 جنيه</span></h4>'),
 (r'<h4>Opel Astra 2005 automatic — <span class="price">300,000 جنيه</span></h4>',
  r'<h4>Opel Astra 2005 أوتوماتيك — <span class="price">300,000 جنيه</span></h4>'),
 (r'<h4>Cruze 2014 أوتوماتيك — <span class="price pickover" style="white-space:nowrap">435,000&nbsp;جنيه</span> \(فوق الميزانية، أفضل مرشح من ناحية الحالة\)</h4>',
  r'<h4>Chevrolet Cruze 2014 أوتوماتيك — فوق الميزانية (أفضل مرشح من ناحية الحالة) — <span class="price pickover" style="white-space:nowrap">435,000&nbsp;جنيه</span></h4>'),
 (r'<h4>Cruze 2013 أوتوماتيك — <span class="price pickover" style="white-space:nowrap">350,000&nbsp;جنيه</span></h4>',
  r'<h4>Chevrolet Cruze 2013 أوتوماتيك — <span class="price pickover" style="white-space:nowrap">350,000&nbsp;جنيه</span></h4>'),
]
for a,b in REP:
    html = re.sub(a, b, html)
html = re.sub(r'<h4> ', '<h4>', html)
open(p, "w", encoding="utf-8").write(html)
print("polish done")
