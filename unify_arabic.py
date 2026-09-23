# -*- coding: utf-8 -*-
"""One-pass: close wrap div, unify language to Arabic outside verbatim blocks,
regenerate all long-row titles per fixed pattern, order tag chips, translate
platform/location/misc chips + buttons. Verbatim blocks left untouched."""
import re, json

d = "/tmp/car-site"
html = open(d + "/index.html", encoding="utf-8").read()
data = json.load(open(d + "/listings.json", encoding="utf-8"))
bykey = {}
for r in data:
    u = r['url']
    if u:
        bykey[u.rstrip('/').rsplit('/', 1)[-1].replace('.html', '')] = r

closes = re.compile(r'(نص البائع حرفياً:</b><br>)(.*?)(</div>)', re.S)
SENT = '__VSLOT%03d__'
sent = []
def protect(m):
    sent.append(m.group(0))
    return SENT % (len(sent) - 1)
stub = closes.sub(protect, html)
# NOTE: stub replaces verbatim blocks with placeholders, then card edits run on stub.

PICK_HDR = {  # featured cards (Arabic already); H4 kept as-is
    '3503590183151155': True,
    'opel-astra-2005-ID209022762': True,
    '994926009578175': True,
}

# Arabic loc names
LOC = {
 'New Cairo':'القاهرة الجديدة','Alexandria':'الإسكندرية','Cairo':'القاهرة',
 'Giza':'الجيزة','Al-Jizah':'الجيزة','Mokattam':'المقطم',
 'Mokattam, Cairo':'المقطم، القاهرة','Alexandria (Camp Caesar)':'الإسكندرية (كامب قيصر)',
 '6th of October (Traffic Dept. التجمع)':'6 أكتوبر (مرور التجمع)',
 '6 October':'6 أكتوبر','6 October City':'مدينة 6 أكتوبر',
 'El-Bagour, Monufia':'الباجور، المنوفية','El-Bagour':'الباجور',
 'Shebin al-Kom, Monufia':'شبين الكوم، المنوفية','Shebin al-Kom':'شبين الكوم',
 'Badr, Cairo':'بدر، القاهرة','Badr City':'مدينة بدر',
 'El Barajil, Alexandria':'البراجيل، الإسكندرية','Heliopolis':'مصر الجديدة',
 'Nasr City, Cairo':'مدينة نصر، القاهرة','Haram, Giza':'الهرم، الجيزة',
 'Faisal, Giza':'فيصل، الجيزة','Mohandessin, Giza':'المهندسين، الجيزة',
 'Tanta':'طنطا','Qalyubia':'قليوبية','10th of Ramadan':'العاشر من رمضان',
 'New Borg El Arab':'برج العرب الجديدة','El Shorouk':'الشروك','Qaha':'قها',
 'Dumyat':'دمياط','Shubra El Kheima':'شبرا الخيمة','Monufia':'المنوفية',
 'القاهرة الجديدة':'القاهرة الجديدة','الإسكندرية':'الإسكندرية','القاهرة':'القاهرة',
}
def loc_ar(x):
    return LOC.get(x, x)

MODEL_AR = {'astra':'أوبل Astra','civic':'هوندا Civic','e36':'BMW E36',
            'cruze':'شيفروليه Cruze','sonic':'شيفروليه Sonic','bmw':'BMW',
            'vectra':'فيكترا','colt':'متسوبيشي كولت'}
PLAT = {'Facebook Marketplace':'فيسبوك ماركت بلاس','dubizzle':'دوبيزل','hatla2ee':'حتلاقي'}

TRANSMAP = [  # (regex-on-chip, replacement)
    (r'(?i)\bFacebook Marketplace\b','فيسبوك ماركت بلاس'),
    (r'\bdubizzle\b','دوبيزل'),
    (r'\bhatla2ee\b','حتلاقي'),
    (r'\bmanual\b(?![^-])','مانيوال'),
    (r'(?<![\w-])auto(?!\w)','أوتوماتيك'),
    (r'\bautomatic\b','أوتوماتيك'),
    (r'— Shebin al-Kom —','— شبين الكوم —'),
    (r'^Shebin al-Kom, Monufia$','شبين الكوم، المنوفية'),
    (r'^Shebin al-Kom$','شبين الكوم'),
    (r'^El-Bagour, Monufia$','الباجور، المنوفية'),
    (r'^(Mokattam)$','المقطم'),
    (r'Alexandria \(Camp Caesar\)','الإسكندرية (كامب قيصر)'),
    (r'^(New Cairo)$','القاهرة الجديدة'),
    (r'^(Alexandria)$','الإسكندرية'),
    (r'^(Cairo)$','القاهرة'),
    (r'^(Al-Jizah|Giza)$','الجيزة'),
    (r'^6th of October \(Traffic Dept\. التجمع\)$','6 أكتوبر (مرور التجمع)'),
    (r'^(6 October)( City)?$','6 أكتوبر'),
    (r'^(Qaha)$','قها'),
    (r'^(Tanta)$','طنطا'),
    (r'^(Qalyubia)$','قليوبية'),
    (r'^(New Borg El Arab)$','برج العرب الجديدة'),
    (r'^(10th of Ramadan)$','العاشر من رمضان'),
    (r'^(El Shorouk)$','الشروق'),
    (r'^(Badr, Cairo)$','بدر، القاهرة'),
    (r'^(El Barajil), Alexandria$','البراجيل، الإسكندرية'),
    (r'^(Heliopolis)$','مصر الجديدة'),
    (r'^(Nasr City), Cairo$','مدينة نصر، القاهرة'),
    (r'^(Haram), Giza$','الهرم، الجيزة'),
    (r'^(Faisal), Giza$','فيصل، الجيزة'),
    (r'^(Mohandessin), Giza$','المهندسين، الجيزة'),
    (r'^(Mokattam), Cairo$','المقطم، القاهرة'),
    ('3503590183151155-placeholder',''),
]

TITLE_FIX = {  # url-key -> full Arabic title (long-row cards only)
 '3503590183151155':'BMW E36 316i 1998 — مالك أول، وارد أمريكا',
 '994926009578175':'Honda Civic 1998 — وارد معاقين، مالك تاني',
 'opel-astra-2005-ID209022762':'Opel Astra 2005 أوتوماتيك',
 'ID208827934':'Chevrolet Sonic 2012 أوتوماتيك — وارد الإمارات، مالك أول',
 'ID208936007':'Chevrolet Sonic 2012 أوتوماتيك',
 '1058523209896512':'BMW E36 316 موديل 1997',
 'bmw-318':'BMW E36 318i 1992 — 1800cc',
 'bmw-325':'BMW 325 موديل 1997',
 'honda-civic-2000-ID208995919':'Honda Civic 2000',
 'astra-2004-brazilian':'Opel Astra 2004 برازيلي',
 'astra-2004-brazilian-2':'Opel Astra 2004 برازيلي أوتوماتيك',
 'astrab-3':'Opel Astra 2003 أوتوماتيك 1600cc',
 '7260683':'Chevrolet Cruze 2014 أوتوماتيك — فوق الميزانية (إثبات سعر السوق)',
 '7283716':'Chevrolet Cruze 2010 أوتوماتيك — فوق الميزانية (صف جيد)',
 'chevrolet-cruze-2010-ID209011080':'Chevrolet Cruze 2010 دواخل فابريكا — فوق الميزانية',
 'cruze-2012-for-sale-ID208151317':'Chevrolet Cruze 2012 رشّة جزئية — فوق الميزانية',
 '7274796':'Opel Astra 2000',
 '7284004':'Opel Astra 2004',
 '7288000':'Opel Astra 2000',
 '7288003':'Opel Astra 2000',
 '7147617':'Opel Astra 2000',
 '7287719':'Opel Astra 2000',
 '7277789':'Opel Astra 2001',
 '7283072':'Opel Astra 2005',
 '7283567':'Opel Astra 2000',
 '7283929':'Opel Astra 2005',
 '7283228':'Opel Astra 2006',
 'ID208921382':'BMW E36 318 موديل 1992 مانيوال',
 'bmw-320-1995-ID208831132':'BMW 320i 1995',
 'ID208860390':'BMW 320 موديل 1994',
 'bmw-318-1992-ID208920402':'BMW E36 318 موديل 1992 — يُقبل البدل',
 '1380984893922735':'Honda Civic 1992 — شبين الكوم',
 '846678185140079':'BMW E36 1992 أوتوماتيك 1800cc — دمياط',
 '1616979376638554':'BMW 1991 مانيوال — موتور 2000cc 6 سلندر (مستبدل) — الجيزة',
 '1827515691606786':'BMW E36 1992 أوتوماتيك — القاهرة',
 '1571288438059685':'Opel Astra 2001 مانيوال 1200cc — 6 أكتوبر',
 '872387595816189':'Opel Astra 2007 أوتوماتيك — الباجور',
 '2104212240310906':'Honda Civic 1992 — القاهرة',
 '2119442688647675':'Honda Civic 92 أوتوماتيك — القاهرة',
 '1794850248200983':'BMW 318i F30 2019 — طُعم تقسيط',
 '1029975739522206':'BMW E36 1992 — الجيزة',
 '1135085155519206':'BMW E34 520i 1992 أوتوماتيك — القاهرة',
 '1044289175173643':'BMW E34 520i 1992 أوتوماتيك — القاهرة',
 '1427108649297020':'BMW E36 1992 وارد معاقين — القاهرة',
 '2225480188297630':'Opel Astra 2001 مانيوال — قها',
 '1718821735684618':'Opel GTC 2008 أوتوماتيك — 6 أكتوبر',
 '1362850595828071':'متسوبيشي كولت 1997 — شبين الكوم',
 '4617614171853998':'BMW 316 E36 موديل 1996 — 6 أكتوبر',
 '2368544463758849':'BMW E36 موديل 97 مانيوال — شبرا الخيمة',
 '1551686706261917':'Opel Vectra 97 أوتوماتيك — القاهرة',
 '1240469888269691':'Opel Astra H 2008 — القاهرة',
 'ID208827934-placeholder':'',
}

CARD = re.compile(
    r'(<div class="card(?: pick| warn)?"><h4>)(.*?)(</h4>\s*<div>)(.*?)(</div>\s*)'
    r'(<a class="btn" href="(?P<URL>[^"]+)"[^>]*>)(?P<LABEL>[^<]*)(</a>)', re.S)

TAGCAP = re.compile(r'<span class="tag">(.*?)</span>', re.S)
cnt = {'title':0,'chip':0,'btn':0}

def fix_chip(t):
    o = t
    for pat, rep in TRANSMAP:
        t2 = re.sub(pat, rep, t)
        if t2 != t:
            cnt['chip'] += 1; t = t2
    return t

def chip_order(tags, rec):
    """Reorder: transmission, year, cc, km, color/body, location, status, extras."""
    def pick(preds):
        for p in preds:
            for i, t in enumerate(tags):
                if p(t):
                    return i
        return None
    def findkw(substr_list):
        return pick([lambda t, s=substr_list: any(k in t for k in s)])
    def fkw(tags, kws):
        for i, t in enumerate(tags):
            if any(k in t for k in kws):
                return i
        return None
    keys = {}
    keys['trans'] = fkw(tags, ['أوتوماتيك','مانيوال'])
    keys['year'] = pick([lambda t: re.fullmatch(r'\d{4}', t)])
    keys['cc'] = pick([lambda t: re.search(r'\d{3,4}cc', t)])
    keys['km'] = pick([lambda t: re.search(r'ألف كم|\d000 км|كم$', t.strip())])
    keys['loc'] = fkw(tags, ['القاهرة','الجيزة','الإسكندرية','أكتوبر','شبين','بدر',
                                'قها','دمياط','المقطم','طنطا','قليوب','الباجور',
                                'برج العرب','رمضان','الشروق','مدينة نصر','الهرم',
                                'فيصل','المهندسين','مصر الجديدة','كامب','برازيلي'])
    keys['plat'] = fkw(tags, ['فيسبوك ماركت بلاس','دوبيزل','حتلاقي'])
    used = set(v for v in keys.values() if v is not None)
    rest = [t for i, t in enumerate(tags) if i not in used]
    order = [keys[k] for k in ('trans','year','cc','km','loc','plat') if keys.get(k) is not None]
    seq = [tags[i] for i in order]
    out = seq + rest
    seen, ded = set(), []
    for t in out:
        if t not in seen:
            seen.add(t); ded.append(t)
    return ded

def findkw(tags, kws):
    for i, t in enumerate(tags):
        if any(k in t for k in kws):
            return i
    return None

def do_card(m):
    pre, h4, mid, tagrow, enddiv, apre, url, label, apost = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6), m.group('URL'), m.group('LABEL'), m.group(9)
    key = url.rstrip('/').rsplit('/', 1)[-1].replace('.html', '')
    r = bykey.get(key)
    # safety: cross-card regex span if preceding card has no anchor
    if '__VSLOT' in m.group(0):
        return m.group(0)
    featured = key in ('3503590183151155', 'opel-astra-2005-ID209022762', '994926009578175')
    if not featured:
        title = TITLE_FIX.get(key)
        if title is None and r:
            brand = MODEL_AR[r['model_key']]
            trans = {'manual':' مانيوال','auto':' أوتوماتيك','':None,None:''}[r.get('transmission') or '']
            y = r.get('year') and f" {r['year']}" or ''
            title = f"{brand}{y}{trans}"
        cnt['title'] += 1
        # rebuild h4 completely: keep medal emoji + price span (+ trailing tag span)
        mm = re.match(r'\s*(?P<medal>🥇|🥈|🥉)?(?P<rest>.*)', h4, re.S)
        medal = mm.group('medal') or ''
        price = re.search(r'<span class="price[^>]*>.*?</span>', h4, re.S)
        tail = re.search(r'</span>\s*(<span class="tag">.*?</span>)\s*$', h4, re.S)
        ps = price.group(0) if price else ''
        ts = (tail.group(1) or '') if tail else ''
        h4 = f'{medal} {title} — {ps}{(" "+ts) if ts else ""}'.replace('  ', ' ')
        h4 = h4 if ps else f'{medal} {title}'.replace('  ',' ')
    else:
        h4 = re.sub(r'تفاوض حتى ~285k', 'تفاوض حتى حوالي 285 ألف', h4)
        if '285 ألف' in h4: cnt['chip'] += 1
    # tags
    tags = TAGCAP.findall(tagrow)
    tags = [fix_chip(t) for t in tags]
    if not featured:
        tags = chip_order(tags, r)
    else:
        tags = [t for t in tags if t]
    taghtml = ''.join(f'<span class="tag">{t}</span>' for t in tags)
    label = label.strip()
    if label == 'افتح: ↔':
        cnt['btn'] += 1; label = 'افتح: المصدر ↗'
    elif label == 'افتح: Dubizzle ↗':
        cnt['btn'] += 1; label = 'افتح: دوبيزل ↗'
    return f'{pre}{h4}{mid}{taghtml}{enddiv}{apre}{label}{apost}'

new = CARD.sub(do_card, stub)

# platform chips in featured cards already Arabic

# restore verbatim
new = re.sub(r'__VSLOT(\d+)__', lambda m: sent[int(m.group(1))], new)

# wrap class div fix (leave <span class="ar"> etc.)
new = new.replace('</body></html>', '</div>\n</body></html>', 1)
# — but only if unbalanced
if new.count('<div') == new.count('</div>'):
    new = new.replace('</div>\n</body></html>', '</body></html>', 1)

# fix warn card "Astra" leftovers
new = new.replace('&quot;Astra 2016–2020', '&quot;Astra 2016–2020')  # brand name OK

open(d + "/index.html", "w", encoding="utf-8").write(new)
print("titles:", cnt['title'], "chips:", cnt['chip'], "buttons:", cnt['btn'])
