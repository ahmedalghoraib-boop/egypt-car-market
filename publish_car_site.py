#!/usr/bin/env python3
"""publish_car_site.py — single-source publisher: listings.json -> index.html.
Standing rules: hard filters re-verified at publish; Arabic UI; seller text verbatim;
price bands green<=250k/yellow<=300k/red>300k; jeneh after number (dir=rtl);
GLOBAL bidi rule (<bdi> on every Latin/digit run); uniform titles (Latin model+year+transmission);
area + km + cc + seller + source as tag chips; fb [hidden information] stripped;
source of truth listings.json; flexible criteria watch_criteria.json.
"""
import json, re, html, os, datetime, zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(f"{HERE}/listings.json", encoding="utf-8"))
css = open(f"{HERE}/current.css", encoding="utf-8").read()

AR_DIG = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
def esc(x): return html.escape(str(x or ""), quote=False)
def clean_note(s):
    return re.sub(r"\[hidden information\]\s*(\.?\s*وتم)?", "", str(s or "")).strip()

LOC_AR = [("new cairo","التجمع الخامسة"),("mokattam","المقطم"),("alexandria","الإسكندرية"),
 ("faisal","فيصل"),("mohandessin","المهندسين"),("badr city","مدينة بدر"),
 ("nasr city","مدينة نصر"),("new borg el arab","برج العرب الجديدة"),
 ("borg el arab","برج العرب"),("el-bagour","الباجور"),("monufia","المنوفية"),
 ("10th of ramadan","العاشر من رمضان"),("6th of october","أكتوبر السادس"),
 ("6 october","أكتوبر السادس"),("october","أكتوبر"),("shubra el kheima","شبرا الخيمة"),
 ("shubra","شبرا الخيمة"),("haram","الهرم"),("qalyubia","القليوبية"),("qaha","قها"),
 ("dumyat","دمياط"),("cairo","القاهرة"),("giza","الجيزة"),("obour","العبور"),
 ("maadi","المعادي"),("zayed","الشيخ زايد"),("tagamoa","التجمع"),("mansoura","المنصورة"),
 ("tanta","طنطا"),("shorouk","الشروق"),("heliopolis","مصر الجديدة"),("zamalek","الزمالك")]
def arloc(loc):
    s = re.sub(r"\([^)]*\)", "", str(loc or "").strip())
    for k, v in LOC_AR:
        s = re.sub(re.escape(k), v, s, flags=re.I)
    s = re.sub(r"[A-Za-z][A-Za-z .\-]*", "", s)
    s = re.sub(r"\s*,\s*", "، ", s)
    return s.strip(" ،-")

MODEL_AR = {"e36":"BMW E36","bmw":"BMW","civic":"Honda Civic","astra":"Opel Astra",
            "vectra":"Opel Vectra","cruze":"Chevrolet Cruze","sonic":"Chevrolet Sonic",
            "colt":"Mitsubishi Colt"}
MAKE_OF = {"e36":"BMW","bmw":"BMW","civic":"Honda","astra":"Opel","vectra":"Opel",
           "cruze":"Chevrolet","sonic":"Chevrolet","colt":"Mitsubishi"}
def make_of(r): return MAKE_OF.get((r.get("model_key") or "").lower(), "أخرى")

def violates(r):
    mk = (r.get("model_key") or "").lower()
    yr = r.get("year") or 0
    tr = (r.get("transmission") or "").lower()
    if mk == "civic" and yr and yr < 1995: return True
    if mk == "cruze" and yr and yr < 2014: return True
    if mk == "cruze" and tr and tr != "auto": return True
    return False
rows = [r for r in rows if not violates(r)]

def band(n):
    if n <= 250000: return "green"
    if n <= 300000: return "yellow"
    return "red"

def normtitle(r):
    name = MODEL_AR.get((r.get("model_key") or "").lower(), "")
    yr = r.get("year") or ""
    hay = (str(r.get("condition") or "") + " " + str(r.get("title") or "")).translate(AR_DIG).lower()
    tr = str(r.get("transmission") or "").lower()
    if not tr:
        if re.search(r"اوتوماتيك|اتوماتيك", hay): tr = "auto"
        elif re.search(r"مانيوال|عادي", hay): tr = "manual"
    trar = "أوتوماتيك" if tr == "auto" else ("مانيوال" if tr == "manual" else "")
    return " ".join(x for x in [name, str(yr or ""), trar] if x)

STATUS_AR = {"over_budget":"فوق الميزانية — مرجع سعر فقط","reference":"مرجع سعر فقط"}
def status_chip(r):
    lbl = STATUS_AR.get((r.get("status") or "").strip().lower())
    return f'<div><span class="tag">{lbl}</span></div>' if lbl else ""

def card(r):
    n = int(re.sub(r"[^0-9]", "", str(r.get("price") or 0)) or 0)
    cls_extra = " pick" if r.get("pick") else ""
    hay = (str(r.get("condition") or "") + " " + str(r.get("title") or "")).translate(AR_DIG)
    tags = []
    tr = str(r.get("transmission") or "").lower()
    if not tr:
        if re.search(r"اوتوماتيك|اتوماتيك", hay): tr = "auto"
        elif re.search(r"مانيوال|عادي", hay): tr = "manual"
    trar = "أوتوماتيك" if tr == "auto" else ("مانيوال" if tr == "manual" else None)
    yr = r.get("year")
    if not yr:
        my = re.search(r"\b(19[89]\d|20[012]\d)\b", hay)
        yr = int(my.group(1)) if my else None
    kmv = r.get("km")
    if not kmv:
        mkm = (re.search(r"\d{2,3}\s*(?:ألف|الف)", hay)
               or re.search(r"\d{3},\d{3}\s*(?:km|كم)", hay, re.I)
               or re.search(r"\d{6}\s*(?:km|كم)", hay, re.I)
               or re.search(r"عداد\s*\d{5,6}", hay))
        if mkm:
            num = re.sub(r"[^0-9]", "", mkm.group(0))
            if num: kmv = f"{int(num):,}km" if len(num) >= 5 else f"{int(num)}،000km"
    cchips = []
    mcc = re.search(r"(\d{3,4})\s*cc", hay, re.I)
    if mcc: cchips.append(f"{int(mcc.group(1)):,}cc")
    loc = arloc(r.get("location"))
    chips = [trar, yr and f'<bdi>{yr}</bdi>'] + cchips + [
             kmv and f'<bdi>{kmv}</bdi>',
             loc and f'<bdi>{loc}</bdi>',
             (r.get("seller_name") and esc(r.get("seller_name"))) or None,
             r.get("platform") and f'<bdi>{esc(r.get("platform"))}</bdi>']
    tags = "".join(f'<span class="tag">{t}</span>' for t in chips if t)
    note = clean_note(r.get("condition"))
    note_html = f'<div class="note ar" dir="rtl"><b>نص البائع حرفياً:</b><br>{esc(note)}</div>' if note else ""
    contact = (f'<div class="note">📞 {esc(r.get("seller_name") or "")} <bdi>{esc(r.get("seller_phone") or "")}</bdi></div>'
               if (r.get("seller_name") or r.get("seller_phone")) else "")
    price_txt = f"{n:,} جنيه" if n else "السعر غير معلن"
    return (f'<div class="card{cls_extra}" data-make="{esc(make_of(r))}" data-model="{esc(r.get("model_key") or "")}" '
            f'data-source="{esc(r.get("platform") or "")}" data-seller="{esc(r.get("seller_name") or "")}" '
            f'data-price="{n}" data-desc="{esc(note[:120])}">'
            f'<h4><bdi>{normtitle(r)}</bdi> — <bdi class="price {band(n)}" dir="rtl">{price_txt}</bdi></h4>'
            f'<div>{tags}</div>{status_chip(r)}{note_html}{contact}'
            f'<a class="btn" href="{esc(r.get("url") or "#")}" target="_blank" rel="noopener">{esc(r.get("platform") or "المصدر")} ↗</a></div>')

sections_order = ["BMW","Honda","Opel","Chevrolet","Mitsubishi","أخرى"]
by_make = {}
for r in rows: by_make.setdefault(make_of(r), []).append(r)
for k in by_make:
    by_make[k].sort(key=lambda r: int(re.sub(r"[^0-9]", "", str(r.get("price") or 0)) or 0))

cairo = datetime.datetime.now(zoneinfo.ZoneInfo("Africa/Cairo"))
updated = cairo.strftime("%d/%m/%Y %I:%M %p").replace("AM","ص").replace("PM","م")

js_engine = open(f"{HERE}/car_site.js", encoding="utf-8").read()

parts = [f'''<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>سيارات مستعملة في مصر — تقرير وسيط</title><style>
{css}
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
</div>''']

for mk in sections_order:
    if mk not in by_make: continue
    parts.append(f'<h2 data-make="{esc(mk)}"><bdi>{esc(mk)}</bdi> — <bdi>{len(by_make[mk])}</bdi> إعلان</h2>')
    for r in by_make[mk]: parts.append(card(r))

parts.append(f'''</div>
<script>
{js_engine}
</script>
</body></html>''')

out = "\n".join(parts)
open(f"{HERE}/index.html", "w", encoding="utf-8").write(out)
print(f"published: {len(out)} bytes, {sum(len(v) for v in by_make.values())} cards in {len(by_make)} make sections")
