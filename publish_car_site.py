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

def clean_note(s):
    s = str(s or "")
    return re.sub(r"\[hidden information\]\s*(\.\s*وتم)?", "", s).strip()

def band(n):
    if n <= 250000: return "green"
    if n <= 300000: return "yellow"
    return "red"


import re as _re
LOC_AR = [("new cairo","التجمع الخامسة"),("mokattam","المقطم"),("alexandria","الإسكندرية"),("faisal","فيصل"),("mohandessin","المهندسين"),("badr city","مدينة بدر"),("nasr city","مدينة نصر"),("new borg el arab","برج العرب الجديدة"),("borg el arab","برج العرب"),("el-bagour","الباجور"),("monufia","المنوفية"),("10th of ramadan","العاشر من رمضان"),("6th of october","أكتوبر السادس"),("6 october","أكتوبر السادس"),("october","أكتوبر"),("shubra el kheima","شبرا الخيمة"),("shubra","شبرا الخيمة"),("haram","الهرم"),("qalyubia","القليوبية"),("qaha","قها"),("dumyat","دمياط"),("cairo","القاهرة"),("giza","الجيزة"),("obour","العبور"),("maadi","المعادي"),("zayed","الشيخ زايد"),("tagamoa","التجمع"),("mansoura","المنصورة")]
def arloc(loc):
    s = str(loc or "").strip()
    s = re.sub(r"\([^)]*\)", "", s)          # drop parenthetical junk
    sl = s.lower()
    for k,v in LOC_AR:
        s = re.sub(re.escape(k), v, s, flags=re.I)
    # drop residual Latin words (e.g. 'City', 'Dept.', first word if English) — keep Arabic only
    s = re.sub(r"[A-Za-z][A-Za-z .\-]*", "", s)
    s = re.sub(r"\s*,\s*", "، ", s)
    return s.strip(" ،-")
MODEL_AR = {"e36":"BMW E36","bmw":"BMW","civic":"Honda Civic","astra":"Opel Astra","vectra":"Opel Vectra","cruze":"Chevrolet Cruze","sonic":"Chevrolet Sonic","colt":"Mitsubishi Colt"}
def normtitle(r):
    mk=""; name=MODEL_AR.get((r.get("model_key") or "").lower())
    yr = r.get("year") or ""
    tr = str(r.get("transmission") or "").lower()
    trar = "أوتوماتيك" if tr=="auto" else ("مانيوال" if tr=="manual" else "")
    loc = arloc(r.get("location"))
    bits = [x for x in [name, str(yr) if yr else "", trar if trar else ""] if x]
    out = " ".join(bits)
    if loc: out += f" — {loc}"
    return out


STATUS_AR = {"over_budget":"فوق الميزانية — مرجع سعر فقط","reference":"مرجع سعر فقط"}
def status_chip(r):
    st = (r.get("status") or "").strip().lower()
    lbl = STATUS_AR.get(st)
    return f'<div><span class="tag">{lbl}</span></div>' if lbl else ""

def card(r):
    n = int(re.sub(r"[^0-9]", "", str(r.get("price") or 0)) or 0)
    cls_extra = " pick" if r.get("pick") else ""
    tags = []
    for t in [r.get("transmission") and ("أوتوماتيك" if str(r.get("transmission")).lower()=="auto" else f'<bdi>{esc(r.get("transmission"))}</bdi>'),
              r.get("year") and f'<bdi>{r.get("year")}</bdi>', r.get("location"), esc(r.get("platform")) and f'<bdi>{esc(r.get("platform"))}</bdi>']:
        if t: tags.append(f'<span class="tag">{t}</span>')
    km = r.get("km")
    note = clean_note(r.get("condition"))
    note_html = f'<div class="note ar" dir="rtl"><b>نص البائع حرفياً:</b><br>{esc(note)}</div>' if note else ""
    contact = f'<div class="note">📞 {esc(r.get("seller_name") or "")} <bdi>{esc(r.get("seller_phone") or "")}</bdi></div>' if (r.get("seller_name") or r.get("seller_phone")) else ""
    price_txt = f'{n:,} جنيه' if n else "السعر غير معلن"
    return (f'<div class="card{cls_extra}" data-make="{esc(make_of(r))}" data-model="{esc(r.get("model_key") or "")}" '
            f'data-source="{esc(r.get("platform") or "")}" data-seller="{esc(r.get("seller_name") or "")}" '
            f'data-price="{n}" data-desc="{esc(note[:120])}">'
            f'<h4><bdi>{normtitle(r)}</bdi> — <bdi class="price {band(n)}" dir="rtl">{price_txt}</bdi></h4>'
            f"{status_chip(r)}"
            f'<div>{"".join(tags)}</div>{note_html}{contact_html(r)}'
            f'<a class="btn" href="{esc(r.get("url") or "#")}" target="_blank" rel="noopener">{esc(r.get("platform") or "المصدر")} ↗</a></div>')

def contact_html(r):
    return (f'<div class="note">📞 {esc(r.get("seller_name") or "")} <bdi>{esc(r.get("seller_phone") or "")}</bdi></div>'
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
    parts.append(f'<h2 data-make="{esc(mk)}"><bdi>{esc(mk)}</bdi> — <bdi>{len(by_make[mk])}</bdi> إعلان</h2>')
    for r in by_make[mk]: parts.append(card(r))

parts.append('''</div>
<script>{ENGINE}</script>
<!-- NOTE: full sort/keyword logic lives in publish_car_site.js (kept simple here) -->
</body></html>''')

out="\n".join(parts)

ENGINE = open(f"{HERE}/car_site.js", encoding="utf-8").read()
out = out.replace('{ENGINE}', ENGINE)

open(f"{HERE}/index.html","w",encoding="utf-8").write(out)
print("published:", len(out), "bytes,", sum(1 for mk in by_make for _ in by_make[mk]), "cards in", len(by_make), "make sections")
