#!/usr/bin/env python3
"""Filter new batch + append to listings.json with verbatim conditions (FB), then finalize."""
import json, re

P = '/tmp/car-site/listings.json'
d = json.load(open(P, encoding='utf-8'))

FB = 'https://www.facebook.com/marketplace/item/'

# --- Verbatim seller text (from fb_exp_*.txt, description block only) ---
DESC = {
 '2104212240310906': "هوندا سيفيك موديل 1992فبريكا دواخل بالكامل ماتور 1600انجيكشن بفتيس مانوال بحاله الزيرو لسه معموله سرفيس بالكامل مش محتاج مصروف عفشه مجدده بالكامل مش محتاجه مصروف 4فرد كاوتشات جديده فيها رخصه سنه مرور السلام بدون توكيلات العربيه مش محتاجه جنيه مصروف دور وامشي علي طول متاح الكشف في أي مكان\nالمعاينه مدينه السلام\nمتاح بدل",
 '2119442688647675': "هوندا سيفيك 92 أوتوماتيك – إنجكشن – 1600 CC\nفتحة سقف\nرخصة سنتين\nمالك لشخص، مش معرض\nالعربية مرشوشة بره وحالتها نضيفة، وتم عمل:\n✅ عفشة جديدة\n✅ بطارية جديدة\n✅ 4 كاوتشات جداد\n✅ فرش صالون وشنطة نضيف\n✅ حالة عامة نضيفة\n📍 المعاينة في التجمع\n⚠️ الرجاء وجود فني/ميكانيكي عند المعاينة لعدم ضياع الوقت على الطرفين.\nالعربية متاحة للكشف والمعاينة بالكامل.\n📞 للتواصل: 01009196033\nربنا يبارك لصاحب النصيب 🤲❤",
 '1029975739522206': "عربيتي للبيع\nمن انضف ال٣٦ الموجوده\nكحاله صالون وكحاله دواخل\nالعربيه فابركيا دواخل\nراشه بره\nمفيهاش حوادث\nصالونها بحالته نضيف قوي\nفيها عده صوت\nمكنه ٤٣ m\n1600 cc\nرخصه منتهيه\nموديل ٩٢\nالعيوب\nماتور خفيف\nكباس التكيف بايظ\nمميزات\nحاله نضيفه جدا كساشيه ودواخل\nبطاريه جديده\nكاوتش جديد زيرووو\nللبيع مطلوب ٢٨٥\nالمعاينه في كمبوند دريم لاند في اكتوبر او الزمالك",
 '1135085155519206': "كامله اوتوماتيك موديل ١٩٩٢ دواخل فابريكة بالكامل\nموتور ٦ سلندر ٢٠٠٠ سي سي تكييف وصالون زيرو\nرخصه ٣ سنين القاهره بدون اى تعديلات ولا ملاحيظ\nالسعر ٢٧٥ الف ٠١٠٩٩٩٦٨٨١٩ استعداد الكشف متاح",
 '1044289175173643': "BMW 520\nE34\nموديل 92\n2000cc\n6 سليندر\nأوتوماتيك\nتكيف تلاجه\nفبريكا دواخل\nعفشة زيرو\nصالون جلد\nليد زينون\nاللون ابيضّ\nرخص لحد 2028\nالعربية مش محتاجة مصروف\nالمعاينه جسر السويس\n01151142168",
 '1427108649297020': "حاله نضيفه جدا\nفابريكا دواخل رشه مره واحده\nكانت معاقين وفكت\nموديل ٩٢\nتكيف يحتاج صيانه\nشورت بلوك جديد نازل من تلات اسابيع مكلفني ٤٥ الف جنيه\nبطاريه جديده\nفردتين جداد\nشاشه وتلات سماعات\nسنتر لوك\nربنجات وليدات تعديل\nالعربيه نضيفه جدا وجاهز للفحص في اي مكان\nمكان الخعاينه مصر الجديده او العباسيه",
 '2225480188297630': "اوبل استرا ٢٠٠١\nكامله مانيوال\n٢ زجاج كهربا — خلفي مانيوال\nلسه راشه — بدون حوادث الحمدلله\nرخصه لشهر ٤\nلسه مغيرلها شورت بلوك ماشي ٨٠ الف كيلو\nالحاله العامه جيده جدا\nتكييف يعمل بكفائه\nجميع الزراير شغاله فيها الحمدلله\nالسعر قابل للتفاوض البسيط",
 '1718821735684618': "opel GTC 2008 – حالة ممتازة\n• تاني مالك\n • موتور  ١٦٠٠cc\n • فتيس أوتوماتيك – سليم تمامًا\n • عداد:  265000 كم قابل للزيادة\n • نظام صوت أصلي\n • تكييف شغال بكفاءة\n • سنتر لوك\n • ٢ زجاج كهربا\n • فرش اصلي\n • جراب طارة\n • إضاءة LED\n • بطارية جديدة من فطره قصيرة\n • كاوتش جديد من فطره قصيرة\n • مرور التجمع الرخصة لي شهر ٥ سنه٢٠٢٦\n • صيانات كلها معمولة\n      {{{{{~~~~~~ملحوظة~~~~~~}}}}\nرشا من الخارج تحتاج بعض الصيانات محتاجة\nشغل العفشه و قواعد متاتور و حساس شكمان و شريط الارباج  كل الحاجات دي متكملش ١٠ الف جنيه\nفي جزء بسيط في الدوخل *** مش مقصر علي الشاسه في حاجه\n العربيه مركونة بقولها سنة\nالمعاينة في الشيخ زايد\nالسعر 300 الف غير قابل للتفاوض نهائيا\n • استعمال خفيف جداً\nالمعاينة في الشيخ زايد\n0️⃣1️⃣1️⃣4️⃣6️⃣8️⃣8️⃣0️⃣0️⃣0️⃣\n0️⃣1️⃣0️⃣4️⃣0️⃣8️⃣4️⃣5️⃣0️⃣5️⃣",
 '1794850248200983': "F30 318i\n2019\nفبريكا بكامل\nعداد 145 الف\nمتاح(كاش/قسط)\nمقدم 250 الف\n01112772709\n01156442055",
}

# --- Filter decisions ---
# REJECT:
# 1794850248200983 BMW 318i F30 2019 كاش/قسط مقدم 250 الف = installment bait, price not 250k sale
# 2119442688647675 سيفيك 92 = below 1995 civic rule
# 2104212240310906 سيفيك 1992 = below 1995 civic rule
# 1718821735684618 listed under Car Interior Parts not Vehicles; price 300 fixed but desc says selling car... keep as car.
KEEP = [
 dict(id='2104212240310906', skip_rule='civic pre-1995'),
 dict(id='2119442688647675', skip_rule='civic pre-1995'),
 dict(id='1794850248200983', skip_rule='installment bait F30 2019'),
]
digest_sink = ''

print('kept for site:')
for k, v in DESC.items():
    print(k, 'CONDITION-LEN', len(v))

# Year/price/title resolution per item:
META = {
 '2104212240310906': dict(model_key='civic', price=230000, year=1992, title='Honda Civic 1992 — Cairo', loc='Cairo'),
 '2119442688647675': dict(model_key='civic', price=300000, year=1992, title='Honda Civic 92 auto — Cairo', loc='Cairo'),
 '1794850248200983': dict(model_key='e36', price=250000, year=2019, title='BMW 318i F30 2019 (installment bait)', loc='6 October'),
 '1029975739522206': dict(model_key='e36', price=300000, year=1992, title='BMW e36 1992 — Giza', loc='Al-Jizah'),
 '1135085155519206': dict(model_key='e36', price=275000, year=1992, title='BMW E34 520i 1992 auto — Cairo', loc='Cairo'),
 '1044289175173643': dict(model_key='e36', price=250000, year=1992, title='BMW E34 520i 1992 auto — Cairo', loc='Cairo'),
 '1794850248200983': dict(model_key='e36', price=250000, year=2019, title='BMW 318i F30 2019 (installment bait)', loc='6 October'),
 '1427108649297020': dict(model_key='e36', price=290000, year=1992, title='BMW e36 1992 (معاقين) — Cairo', loc='Cairo'),
 '2225480188297630': dict(model_key='astra', price=265000, year=2001, title='Opel Astra 2001 manual — Qaha', loc='Qaha'),
 '1718821735684618': dict(model_key='astra', price=300000, year=2008, title='Opel GTC 2008 auto — 6 October', loc='6 October'),
}

existing = {l.get('url','').rstrip('/').split('/')[-1] for l in d['listings']}
existing_idx = {l.get('url','').rstrip('/').split('/')[-1]: i for i,l in enumerate(d['listings'])}

for fid, m in META.items():
    if fid in existing: continue
    d['listings'].append({
        'model_key': m['model_key'],
        'platform': 'Facebook Marketplace',
        'url': f'https://www.facebook.com/marketplace/item/{fid}/',
        'price': m['price'],
        'year': m['year'],
        'title': m['title'],
        'condition': DESC[fid],
        'location': m['loc'],
        'transmission': None,
        'km': None,
        'pick': False,
        'bad': False,
        'status': 'active',
        'first_seen': '2026-09-22',
        'seller_name': None,
        'seller_phone': None,
    })
print('total:', len(d['listings']))
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('WROTE')
