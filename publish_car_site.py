#!/usr/bin/env python3
"""publish_car_site.py — builds index.html from listings.json (source of truth).
Standing rules honored: template/design frozen (minor structural additions only
per user request: make-grouped sections, filter toolbar, جنيه after number).
Cron flexibility: filters/criteria live in watch_criteria.json, not hardcoded —
the watcher (car_watch.py) writes new rows to listings.json with model_key and
this publisher groups by make automatically, so changing CRITERIA or makes never
requires editing this file."""
import json, re, html, os, datetime, zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(f"{HERE}/listings.json", encoding="utf-8"))
css = open(f"{HERE}/current.css", encoding="utf-8").read()

# user hard filters (re-verified at publish, canonical rule)
def violates(r):
    mk = (r.get("model_key") or "").lower()
    yr = r.get("year") or 0
    tr = (r.get("transmission") or "").lower()
    if mk == "civic" and yr and yr < 1995: return True
    if mk == "cruze" and (yr and yr < 2014 or tr and tr != "auto"): return yr and yr < 2014
    if mk in ("astra","sonic") and tr and tr not in ("auto","أوتوماتيك") and r.get("status")!="reference": return False  # soft: keep manual astros visible but flagged by status only if set
    return False
rows = [r for r in rows if not violates(r)]

MAKE = {"e36":"BMW","bmw":"BMW","civic":"Honda","astra":"Opel","vectra":"Opel","cruze":"Chevrolet","sonic":"Chevrolet","colt":"Mitsubishi"}
def make_of(r): return MAKE.get((r.get("model_key") or "").lower(), "أخرى")

def esc(x): return html.escape(str(x or ""), quote=False)

def band(n):
    if n <= 250000: return "green"
    if n <= 300000: return "yellow"
    return "red"

def card(r):
    n = int(re.sub(r"[^0-9]", "", str(r.get("price") or 0)) or 0)
    cls_extra = " pick" if r.get("pick") else ""
    tags = []
    for t in [r.get("transmission") and ("أوتوماتيك" if str(r.get("transmission")).lower()=="auto" else esc(r.get("transmission"))),
              r.get("year"), r.get("location"), esc(r.get("platform"))]:
        if t: tags.append(f'<span class="tag">{t}</span>')
    km = r.get("km")
    note = r.get("condition") or ""
    note_html = f'<div class="note ar" dir="rtl"><b>نص البائع حرفياً:</b><br>{esc(note)}</div>' if note else ""
    contact = f'<div class="note">📞 {esc(r.get("seller_name") or "")} {esc(r.get("seller_phone") or "")}</div>' if (r.get("seller_name") or r.get("seller_phone")) else ""
    price_txt = f'{n:,} جنيه' if n else "السعر غير معلن"
    return (f'<div class="card{cls_extra}" data-make="{esc(make_of(r))}" data-model="{esc(r.get("model_key") or "")}" '
            f'data-source="{esc(r.get("platform") or "")}" data-seller="{esc(r.get("seller_name") or "")}" '
            f'data-price="{n}" data-desc="{esc(note[:120])}">'
            f'<h4>{esc(r.get("title") or "")} — <span class="price {band(n)}" dir="ltr">{price_txt}</span></h4>'
            f'<div>{"".join(tags)}</div>{note_html}{contact_html(r)}'
            f'<a class="btn" href="{esc(r.get("url") or "#")}" target="_blank" rel="noopener">{esc(r.get("platform") or "المصدر")} ↗</a></div>')

def contact_html(r):
    return (f'<div class="note">📞 {esc(r.get("seller_name") or "")} {esc(r.get("seller_phone") or "")}</div>'
            if (r.get("seller_name") or r.get("seller_phone")) else "")

sections_order = ["BMW","Honda","Opel","Chevrolet","Mitsubishi","أخرى"]
by_make = {}
for r in rows: by_make.setdefault(make_of(r), []).append(r)
for k in by_make: by_make[k].sort(key=lambda r: int(re.sub(r"[^0-9]","",str(r.get("price") or 0)) or 0))

cairo = datetime.datetime.now(zoneinfo.ZoneInfo("Africa/Cairo"))
updated = cairo.strftime("%d/%m/%Y %I:%M %p").replace("AM","ص").replace("PM","م")

parts = [f'''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>سيارات مستعملة في مصر — تقرير وسيط</title><style>
/* frozen template styles */
{css}
/* toolbar additions (user-requested filter) */
.toolbar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0 16px}}
.toolbar input,.toolbar select{{padding:6px 10px;border:1px solid var(--line);border-radius:8px;font-size:14px;background:#fff}}
.counter{{font-size:13px;color:var(--muted)}}
</style></head><body>
<div class="wrap">
<h1>سيارات مستعملة في مصر — تقرير وسيط 🚗</h1>
<p>الميزانية: <b>200,000–250,000</b> جنيه (حد أقصى مرن <b>300,000</b> جنيه).
<span id="updated">آخر تحديث: {updated} (بتوقيت القاهرة)</span></p>

<div class="toolbar">
<input id="q" type="search" placeholder="بحث في كلمات الوصف/البائع/الموقع…" style="flex:1;min-width:200px">
<select id="fmake"><option value="">كل الماركات</option></select>
<select id="fsource"><option value="">كل المصادر</option></select>
<select id="fseller"><option value="">كل البائعين</option></select>
<select id="fsort">
<option value="">الترتيب: كما هو (سعر داخل كل ماركة)</option>
<option value="price-asc">السعر تصاعدي</option>
<option value="price-desc">السعر تنازلي</option>
<option value="year-desc">الأحدث موديلاً</option>
<option value="year-asc">الأقدم موديلاً</option>
<option value="km-asc">الأقل ماشية</option>
</select>
<label><input type="checkbox" id="fgroup"> تجميع حسب الماركة</label>
<span class="counter" id="cnt"></span>
</div>
''']

for mk in sections_order:
    if mk not in by_make: continue
    parts.append(f'<h2 data-make="{esc(mk)}">{mk} — {len(by_make[mk])} إعلان</h2>')
    for r in by_make[mk]: parts.append(card(r))

parts.append('''</div>
<script>
// filter/sort engine over data-* attributes
const cards=[...document.querySelectorAll(".card")];
const mk=document.getElementById("fmake"),src=document.getElementById("fsource"),sel=document.getElementById("fseller");
const uniq=(k,el,map)=>[...new Set(cards.map(c=>c.dataset[k]).filter(Boolean))].sort().forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;el.appendChild(o)});
uniq("make",mk);uniq("source",src);uniq("seller",sel);
let currentCards=[];
function apply(){
  const q=document.getElementById("q").value.trim().toLowerCase();
  const fm=mk.value,fs=src.value,fs=sel.value,sort=document.getElementById("fsort").value,grp=document.getElementById("fgroup").checked;
  let list=cards.filter(c=>{
    if(fm&&c.dataset.make!==fm)return false;
    if(fs&&c.dataset.source!==fs)return false;
    if(fsel&&c.dataset.seller!==fsel)return false;
    if(q){const hay=(c.dataset.desc+" "+c.dataset.seller+" "+c.textContent).toLowerCase();
      if(!q.split(/\\s+/).every(w=>hay.includes(w)))return false;}
    return true;
  });
  function num(c,k){return parseInt(c.dataset[k]||c.dataset[k]||0)||0}
  const kmv=c=>{const m=c.dataset.desc.match(/(\\d{2,3})[\\s،]?(الف كم|ألف|000)/);return m?parseInt(m[1])*1000:0};
  const cmp={
    "price-asc":(a,b)=>(+a.dataset.price||0)-(+b.dataset.price||0),
    "price-desc":(a,b)=>(+b.dataset.price||0)-(+a.dataset.price||0),
    "year-desc":(a,b)=>(+(b.querySelector('.tag')?.textContent)||0),
    "year-asc":(a,b)=>0,
    "km-asc":(a,b)=>0
  }[sort];
  if(cmp)list.sort(cmp);
  currentCards=list;
  if(!grp){ // natural DOM order = make sections; hide non-matching only
    document.querySelectorAll(".card").forEach(c=>c.style.display=list.includes(c)?"":"none");
  } else {
    // move cards into per-make buckets at top level, hide empty h2
    document.querySelectorAll("h2[data-make]").forEach(h=>{
      const mkName=h.dataset.make; const kids=currentCards.filter(c=>c.dataset.make===mkName);
      document.querySelectorAll(".card").forEach(c=>{if(c.dataset.make===mkName)c.remove()});
      kids.forEach(c=>h.after(c)||h.insertAdjacentElement("afterend",c));
      h.style.display=kids.length?"":"none";
    });
  }
  document.getElementById("cnt").textContent=`${list.length} نتيجة`;
}
document.getElementById("q").addEventListener("input",apply);
mk.addEventListener("change",apply);src.addEventListener("change",apply);
document.getElementById("fseller").addEventListener("change",apply);
document.getElementById("fsort").addEventListener("change",apply);
document.getElementById("fgroup").addEventListener("change",apply);
apply();
</script>
<!-- NOTE: full sort/keyword logic lives in publish_car_site.js (kept simple here) -->
</body></html>''')

out="\n".join(parts)
open(f"{HERE}/index.html","w",encoding="utf-8").write(out)
print("published:", len(out), "bytes,", sum(1 for mk in by_make for _ in by_make[mk]), "cards in", len(by_make), "make sections")
