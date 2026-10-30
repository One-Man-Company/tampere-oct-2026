#!/usr/bin/env python3
"""Builds the Tampere family-trip site (single file, static, no API keys)."""
import json, math, pathlib, re, html

ROOT = pathlib.Path(__file__).parent
HOME = (61.5028, 23.7209)          # Tervatehtaanraitti 3 B 32, Santalahti
TITLE = "Perhe-reissu · Tampere"
SUB = "Vilnius → Tallinn → Tampere · 31 Oct – 8 Nov 2026"

def load(p):
    return json.load(open(ROOT / "data" / p, encoding="utf-8"))

places = load("tampere.json") + load("food.json") + load("trips.json") + load("route.json")
days = load("days.json")

# ---- home marker ----
places.append({
    "id": "home", "name": "Tervatehtaanraitti 3 B 32", "cat": "practical",
    "sub": "The flat · Santalahti, Tampere", "area": "Santalahti", "city": "Tampere",
    "lat": HOME[0], "lon": HOME[1], "price": "booked 31 Oct – 2 Nov", "famNum": 0,
    "fam": "2 nights booked", "hours": "checkout 2 Nov", "dur": "—", "indoor": True,
    "kid": 3, "baby": True, "days": [], "rating": None, "web": "",
    "desc": "Two-bedroom flat 2 km west of the centre, 300 m from the Näsijärvi shore, 3 km from K-citymarket Lielahti.",
    "why": "The best thing about it is the location: walkable to Särkänniemi and the lake, a short bus or drive to everything else, and quiet at night.",
    "tip": "Check parking arrangements before arrival — Finnish housing companies often have a permit system, and street parking uses a disc."
})

def hav(a, b):
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    d = 2 * R * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 +
                                    math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
    return d

for p in places:
    km = hav(HOME, (p["lat"], p["lon"]))
    p["km"] = round(km, 1) if km >= 0.1 else 0.1
    mins = max(2, round(km / 68 * 60))
    p["drive"] = f"{mins} min" if km > 0.6 else "walk"
    p["gmaps"] = f"https://www.google.com/maps/search/?api=1&query={p['lat']},{p['lon']}"
    p["dir"] = (f"https://www.google.com/maps/dir/?api=1&origin={HOME[0]},{HOME[1]}"
                f"&destination={p['lat']},{p['lon']}&travelmode=driving")
    p["famNum"] = p.get("famNum", 0)

places.sort(key=lambda p: (p["cat"], p["km"]))

def js(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

# ---- inline formatting: **bold**, [[id|label]] ----
LINK_RE = re.compile(r"\[\[([a-z0-9_]+)(?:\|([^\]]+))?\]\]")

def fmt(text):
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    def rep(m):
        pid, label = m.group(1), m.group(2)
        name = label
        if not name:
            found = next((x["name"] for x in places if x["id"] == pid), pid)
            name = found
        return f'<a href="#r-{pid}" data-row="{pid}">{name}</a>'
    return LINK_RE.sub(rep, t)

# ---- weather strip (Open-Meteo, Tampere, fetched 30 Oct 2026) ----
WX = [
    ("d0", "Sat 31.10", "7° / 5°", "ok", "DRY", "0 mm · sunset 16:25"),
    ("d1", "Sun 1.11", "7° / 5°", "ok", "DRY", "0.5 mm · candles 16:15"),
    ("d2", "Mon 2.11", "6° / 3°", "bad", "WET", "3.7 mm · museums shut"),
    ("d3", "Tue 3.11", "7° / 2°", "ok", "DRY", "0.3 mm · gust 51"),
    ("d4", "Wed 4.11", "6° / 1°", "ok", "DRY", "0 mm · best day"),
    ("d5", "Thu 5.11", "7° / 5°", "mid", "WINDY", "0 mm · gust 55"),
    ("d6", "Fri 6.11", "6° / 1°", "ok", "DRY", "0 mm · free museum"),
    ("d7", "Sat 7.11", "6° / 1°", "ok", "DRY", "0.6 mm · transit"),
    ("d8", "Sun 8.11", "5° / 0°", "mid", "COLD", "0.6 mm · drive home"),
]
wx_html = "".join(
    f'<div class="wxd"><div class="d">{d}</div><div class="t">{t}</div>'
    f'<span class="v {cls}">{tag}</span><div class="n">{n}</div></div>'
    for _, d, t, cls, tag, n in WX
)

# ---- day panels ----
def lightbar(day):
    def pos(hhmm):
        h, m = map(int, hhmm.split(":"))
        return max(0.0, min(100.0, (h + m / 60) / 24 * 100))
    sr, ss = pos(day["sunrise"]), pos(day["sunset"])
    return (f'<div class="lightbar">'
            f'<div class="dark" style="left:0;width:{sr:.1f}%"></div>'
            f'<div class="sun" style="left:{sr:.1f}%;width:{ss-sr:.1f}%"></div>'
            f'<div class="dark" style="left:{ss:.1f}%;right:0"></div>'
            f'<div class="nap" style="left:{pos("11:00"):.1f}%;width:{pos("13:00")-pos("11:00"):.1f}%"></div>'
            f'<div class="nap" style="left:{pos("15:00"):.1f}%;width:{pos("16:30")-pos("15:00"):.1f}%"></div>'
            f'<span class="lbl" style="left:{pos("07:00"):.1f}%">06</span>'
            f'<span class="lbl" style="left:{pos("12:00")-2:.1f}%">12</span>'
            f'<span class="lbl" style="left:{pos("18:00")-2:.1f}%">18</span>'
            f'</div>')

def timeline(day):
    out = ['<div class="tl">']
    for it in day["items"]:
        cls = "tli"
        metas = "".join(
            f'<span class="{"cost" if "€" in m else ""}">{fmt(m)}</span>' for m in it.get("m", []))
        out.append(
            f'<div class="{cls}"><t>{it["t"]}</t><h4>{fmt(it["h"])}</h4>'
            f'<p>{fmt(it["p"])}</p><div class="tm">{metas}</div></div>')
    out.append("</div>")
    return "".join(out)

day_tabs = "".join(
    f'<button class="day{" on" if i == 0 else ""}" data-day="{d["id"]}">'
    f'<b>{d["short"]}</b><span>{d["date"]}</span></button>'
    for i, d in enumerate(days))

panels = []
for i, d in enumerate(days):
    alts = "".join(f"<li>{fmt(a)}</li>" for a in d["alts"])
    panels.append(
        f'<div class="daypanel" data-panel="{d["id"]}"{" style=display:none" if i else ""}>'
        f'<div class="daycard">'
        f'<div class="dayhead"><div class="dateblock"><div class="w">{d["short"].split()[0]}</div>'
        f'<div class="n">{d["date"].split()[0]}</div><div class="m">{d["date"].split()[1]}</div></div>'
        f'<div><h3>{d["title"]}</h3><div class="meta">{d["meta"]}</div></div></div>'
        f'{lightbar(d)}'
        f'<div class="lightlegend">'
        f'<span><i style="background:var(--mustard)"></i>daylight {d["sunrise"]}–{d["sunset"]}</span>'
        f'<span><i style="background:repeating-linear-gradient(135deg,color-mix(in srgb,var(--berry) 45%,transparent) 0 2px,transparent 2px 4px)"></i>nap windows 11–13, 15–16:30</span>'
        f'</div>'
        f'<div class="callout {d["callout"]["type"]}">{fmt(d["callout"]["html"])}</div>'
        f'{timeline(d)}'
        f'<details><summary>If the plan breaks — alternatives for {d["short"]}</summary><ul>{alts}</ul></details>'
        f'<p class="tiny mut" style="margin:8px 0 0">{fmt(d["note"])}</p>'
        f'</div></div>')

# ---- week at a glance ----
GLANCE = [
    ("Sat 31 Oct", "Vilnius 04:00 → Tallinn → ferry → Tampere 17:30", "780 km", "Dry, 7 °C"),
    ("Sun 1 Nov", "Pyynikki tower · Moomin Museum · All Saints' candles", "20 km", "Dry, 7 °C"),
    ("Mon 2 Nov", "Mustamakkara · swimming hall · move flat", "15 km", "Rain 3.7 mm"),
    ("Tue 3 Nov", "Dad works · Vapriikki + library", "5 km", "Dry, windy"),
    ("Wed 4 Nov", "Häme Castle + Aulanko park", "160 km", "Dry, 6 °C"),
    ("Thu 5 Nov", "Kangasala: car museum + ridge", "50 km", "Dry, gusty"),
    ("Fri 6 Nov", "Tallipiha · Vapriikki free 15–18 · pack", "10 km", "Dry"),
    ("Sat 7 Nov", "Tampere → Heureka → ferry → Tallinn", "190 km", "Dry"),
    ("Sun 8 Nov", "Tallinn → Pärnu → Vilnius", "600 km", "Cold, 5 °C"),
]
glance_rows = "".join(
    f'<tr{" class=hi" if i in (0, 8) else ""}><td><b>{a}</b></td><td>{b}</td>'
    f'<td class="num">{c}</td><td class="num">{d}</td></tr>'
    for i, (a, b, c, d) in enumerate(GLANCE))

# ---- place counts for copy ----
n_total = len(places)
n_rated = len([p for p in places if p.get("rating")])
n_free = len([p for p in places if p.get("famNum") == 0])
n_food = len([p for p in places if p["cat"] in ("eat", "cafe")])

PACKING = [
    "Passports for all five (the baby needs her own)",
    "Car documents, insurance, green card, ferry booking reference",
    "Two car seats + one booster (Finnish law: child seat under 135 cm)",
    "Winter jackets, waterproof trousers, gloves for everyone",
    "Baby carrier — buggies fail on cobbles, stairs and forest paths",
    "Buggy with rain cover and a warm footmuff",
    "Nappies for 9 days (Finnish prices are high; Estonian ones are not)",
    "Swim nappies, towels, padlock for the swimming hall",
    "Thermos, sausage sticks, matches for the campfire",
    "Parking disc for the windscreen (pysäköintikiekko)",
    "Reflective vests (dark at 16:00, and required if you stop on a road)",
    "Snacks: a box per child, restocked at every supermarket",
    "Headache pills, children's paracetamol, plasters, thermometer",
    "Chargers, a power bank, and a headphone splitter for the car",
    "One small toy each and one drawing book — not the whole shelf",
    "A thermos of coffee for the 04:00 start",
]

# ---- static sections ----
css = (ROOT / "src/style.css").read_text(encoding="utf-8")
app = (ROOT / "src/app.js").read_text(encoding="utf-8")

NAV = [("plan", "Plan", "plan"), ("route", "Route", "car"), ("map", "Map", "pin"),
       ("places", "Places", "see"), ("kids", "Kids", "play"), ("eat", "Eat", "eat"),
       ("work", "Work", "work"), ("costs", "Costs", "euro"), ("info", "Info", "practical")]
PATHS = {
    "plan": '<path d="M4 5h16M4 12h16M4 19h10"/>',
    "car": '<path d="M5 17h14M6.5 17V13l1.8-4.5h7.4L17.5 13v4M7 17v1.6M17 17v1.6"/><circle cx="8" cy="14.6" r=".8"/><circle cx="16" cy="14.6" r=".8"/>',
    "pin": '<path d="M12 21.4s7-6.6 7-11.4a7 7 0 10-14 0c0 4.8 7 11.4 7 11.4z"/><circle cx="12" cy="10" r="2.5"/>',
    "see": '<path d="M3 21h18M4 21V10m5 11V10m6 11V10m5 11V10M2 10L12 3l10 7"/>',
    "play": '<circle cx="12" cy="7" r="3"/><path d="M6 21v-4a6 6 0 0112 0v4M9.5 4.6L12 7l2.5-2.4"/>',
    "eat": '<path d="M6 3v8a2.4 2.4 0 004.8 0V3M8.4 11v10M16.6 3c-1.6 1.6-2.2 3.3-2.2 5.5s.6 3.9 2.2 5.5V21"/>',
    "work": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 012-2h4a2 2 0 012 2v2M3 12h18"/>',
    "euro": '<path d="M17 6.5A6.5 6.5 0 007.5 12A6.5 6.5 0 0017 17.5M5.5 10.5h7M5.5 13.5h7"/>',
    "practical": '<circle cx="12" cy="12" r="8.5"/><path d="M12 8.5v5M12 16h.01"/>',
}
def navicon(k):
    return ('<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + PATHS[k] + "</svg>")
nav = "".join(
    f'<button class="tab{" on" if k == "plan" else ""}" data-tab="{k}">{navicon(i)}{v}</button>'
    for k, v, i in NAV)

HTML = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{TITLE} · 31 Oct – 8 Nov 2026</title>
<meta name="description" content="A nine-day Tampere trip for two adults and three children (9, 7 and 9 months): driving Vilnius–Tallinn, the ferry, {n_total} places with kid ratings, prices for a family of five, a remote-work week and the drive home.">
<meta name="theme-color" content="#fbf8f2">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Perhe-reissu">
<meta property="og:title" content="{TITLE} · Tampere with three kids">
<meta property="og:description" content="{n_total} places, {n_rated} Google ratings, prices for five, and a plan that fits around a 9-month-old's naps.">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='48' fill='%23254a6b'/%3E%3Ctext x='50' y='70' font-size='52' font-family='Georgia,serif' fill='%23fff' text-anchor='middle'%3ET%3C/text%3E%3C/svg%3E">
<link rel="manifest" href="manifest.json">
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css">
<style>{css}</style>
</head>
<body>
<header>
  <div class="bar">
    <div class="brand"><span class="mark">T</span>
      <span><b>Perhe-reissu</b><span>Tampere · 31 Oct – 8 Nov 2026 · 5 of us</span></span></div>
    <div class="sp"></div>
    <button class="iconbtn" id="theme" aria-label="Toggle theme"></button>
  </div>
</header>
<nav class="tabs"><div class="tscroll">{nav}</div></nav>
<main>

<!-- ============ PLAN ============ -->
<section class="page on" id="plan">
  <div class="wrap">
    <div class="hero">
      <div class="kicker">Vilnius → Tallinn → Tampere · with a 9-month-old</div>
      <h1>Nine days north,<br>built around <em>naps and light</em>.</h1>
      <p class="sub">Two adults, three daughters — 9, 7 and 9 months. A car, one ferry each way, two flats in Tampere, and a working week that still has to feel like a holiday. Sunset on day one is 16:25.</p>
      <div class="chips">
        <span class="chip">{navicon("see")} {n_total} places, {n_rated} rated</span>
        <span class="chip">{navicon("euro")} {n_free} free places</span>
        <span class="chip">{navicon("car")} ≈1,950 km driven</span>
        <span class="chip">{navicon("practical")} 0–7 °C</span>
      </div>
    </div>

    <div class="wx" id="wxstrip">{wx_html}</div>
    <p class="tiny mut" style="margin:7px 0 0">Tampere forecast from Open-Meteo, fetched 30 Oct 2026. Daylight is the real constraint: you lose 45 minutes of it across the week.</p>

    <div class="card tight" style="margin-top:12px">
      <div class="stat">
        <div class="s"><b>16:25</b><span>Sunset on 31 Oct</span></div>
        <div class="s"><b>8 h 35</b><span>Useful daylight</span></div>
        <div class="s"><b>4</b><span>Days below 2 °C</span></div>
      </div>
      <p style="margin:10px 0 0;font-size:13px">
        <b>The shape of the week.</b> Saturday is a 780 km transit with one ferry; Sunday is the gentle family day with the Moomin Museum and the All Saints' candles.
        Monday is wet and every museum is shut, so it is mustamakkara and a swimming pool. Tuesday to Friday your wife runs the days alone while you work —
        one indoor anchor each morning, home before dark. Friday evening you pack, Saturday you drive to Heureka and cross to Tallinn, Sunday you drive home.
      </p>
    </div>

    <div class="days" id="daytabs">{day_tabs}</div>
    {''.join(panels)}

    <h2 style="margin-top:22px">The week at a glance</h2>
    <div class="tw"><table>
      <thead><tr><th>Day</th><th>What happens</th><th>Driving</th><th>Weather</th></tr></thead>
      <tbody>{glance_rows}</tbody>
    </table></div>

    <div class="grid g2" style="margin-top:12px">
      <div class="card tight"><h3>Two flats, not one</h3>
        <p class="small">You have <b>Santalahti until 2 Nov</b>. For 2–7 Nov you need a second base, and this time the requirements change: a desk, reliable wifi, parking, a lift (buggy + shopping), a washing machine, and a kitchen.</p>
        <p class="small" style="margin:0"><b>Best area:</b> Tammela or Kaleva — walkable to the market, the library and Vapriikki, 10 minutes' drive to the flat you have now. Book 5 nights, check out Saturday 7 Nov.</p></div>
      <div class="card tight"><h3>What must be booked now</h3>
        <ul class="small" style="margin:0;padding-left:16px">
          <li><b>Ferry out, 31 Oct, car + 5.</b> Saturday winter sailings sell out.</li>
          <li><b>Ferry back, 7 Nov, car + 5.</b> Book both in one session.</li>
          <li><b>Second flat, 2–7 Nov.</b> Five nights, parking, lift.</li>
          <li><b>Tallinn hotel, 7 Nov.</b> One night near the Old Town, with parking.</li>
          <li><b>Heureka tickets online</b> — €3 cheaper each, and under-5s free.</li>
        </ul></div>
    </div>

    <div class="callout info" style="margin-top:12px"><b>The one thing that ruins this trip:</b> 31 October is All Saints' Day in Finland, and most grocery chains close or run Sunday hours. You arrive at 17:30 with three hungry children. Buy bread, milk, cheese and breakfast <b>in Tallinn or on the ferry</b>, and treat dinner as a takeaway problem, not a cooking problem.</div>
  </div>
</section>

<!-- ============ ROUTE ============ -->
<section class="page" id="route">
  <div class="wrap">
    <h2>Route</h2>
    <p class="small mut">Two drives and two ferries. The outbound day is the only genuinely hard one; everything else is under two hours.</p>

    <h3 style="margin-top:14px">The outbound day, hour by hour</h3>
    <div class="tw"><table>
      <thead><tr><th>Leg</th><th>Distance</th><th>Time</th><th>Note</th></tr></thead>
      <tbody>
        <tr><td><b>Vilnius → Tallinn</b><br><span class="tiny mut">Via Baltica, E67</span></td><td class="num">600 km</td><td class="num">7 h 15</td><td>Four stops, 8 h 45 door to port</td></tr>
        <tr class="hi"><td><b>Tallinn → Helsinki</b><br><span class="tiny mut">Ferry, Terminal D</span></td><td class="num">80 km</td><td class="num">2 h</td><td>Check-in closes 30 min before</td></tr>
        <tr><td><b>Helsinki → Tampere</b></td><td class="num">180 km</td><td class="num">1 h 50</td><td>Motorway E12, no tolls</td></tr>
        <tr><td><b>Total</b></td><td class="num">860 km</td><td class="num">≈11 h</td><td>04:00 → 17:30 with stops</td></tr>
      </tbody></table></div>

    <h3 style="margin-top:18px">Ferry timetable — Saturday 31 October 2026</h3>
    <p class="small mut">Real departures and per-person fares for that date, checked 30 October. A car is charged on top; expect €40–70 each way.</p>
    <div class="tw"><table>
      <thead><tr><th>Depart</th><th>Arrive</th><th>Operator</th><th>Ship</th><th>Per person</th><th>Verdict</th></tr></thead>
      <tbody>
        <tr><td class="num">07:00</td><td class="num">09:30</td><td>Viking</td><td>XPRS</td><td class="num">€18.50</td><td>Too early — you would need to leave Vilnius at 22:00</td></tr>
        <tr><td class="num">10:30</td><td class="num">12:30</td><td>Tallink</td><td>Megastar</td><td class="num">€36.90</td><td><span class="no">Too tight</span> for a 600 km morning</td></tr>
        <tr><td class="num">12:00</td><td class="num">14:15</td><td>Eckerö</td><td>Finlandia</td><td class="num">€23.00</td><td>Possible only if you leave at 03:30</td></tr>
        <tr><td class="num">12:30</td><td class="num">16:00</td><td>Tallink</td><td>Victoria I</td><td class="num">€22.30</td><td>Slow ship, 3.5 h — more space, proper meal</td></tr>
        <tr class="hi"><td class="num">13:30</td><td class="num">15:30</td><td>Tallink</td><td>MyStar</td><td class="num">€34.90</td><td><span class="yes">BEST</span> — the plan works around this one</td></tr>
        <tr><td class="num">16:30</td><td class="num">18:30</td><td>Tallink</td><td>Megastar</td><td class="num">€29.90</td><td>The safety net if the drive slips</td></tr>
        <tr><td class="num">17:00</td><td class="num">19:30</td><td>Viking</td><td>XPRS</td><td class="num">€19.50</td><td>Cheap, but Tampere at 21:30</td></tr>
      </tbody></table></div>
    <div class="callout good"><b>Book the 13:30 MyStar.</b> It gives you 8 h 45 to cover 600 km — enough for four stops and a nappy change every three hours — and lands you in Tampere at 17:30, before the children are destroyed. If the drive goes badly, the 16:30 Megastar is the fallback.</div>

    <h3 style="margin-top:18px">The drive home</h3>
    <div class="tw"><table>
      <thead><tr><th>Leg</th><th>Distance</th><th>Time</th><th>Where to stop</th></tr></thead>
      <tbody>
        <tr><td>Tampere → Vantaa (Heureka)</td><td class="num">165 km</td><td class="num">1 h 45</td><td>Heureka, 10:00–14:00</td></tr>
        <tr><td>Vantaa → West Harbour</td><td class="num">25 km</td><td class="num">30 min</td><td>Fill the car before the ferry</td></tr>
        <tr class="hi"><td>Helsinki → Tallinn</td><td class="num">80 km</td><td class="num">2 h</td><td>Afternoon sailing, arrive Tallinn ≈18:30</td></tr>
        <tr><td>Tallinn → Pärnu</td><td class="num">128 km</td><td class="num">1 h 45</td><td>Pärnu beach, 40 minutes</td></tr>
        <tr><td>Pärnu → Vilnius</td><td class="num">470 km</td><td class="num">5 h 30</td><td>Two fuel stops, no meals</td></tr>
      </tbody></table></div>

    <div class="grid g2" style="margin-top:12px">
      <div class="card tight"><h3>Car and tyres</h3>
        <dl class="kv" style="margin-top:6px">
          <dt>Winter tyres</dt><dd>Mandatory in Lithuania from 10 Nov</dd>
          <dt>Finland</dt><dd>Winter tyres 1 Dec – end Feb</dd>
          <dt>Headlights</dt><dd>Always on, all day</dd>
          <dt>Child seats</dt><dd>Required under 135 cm</dd>
          <dt>Alcohol</dt><dd>0.05 % FI · 0.02 % EE · 0.05 % LV · 0.04 % LT</dd>
          <dt>Fuel</dt><dd>1.60–1.80 €/l, cheapest in Lithuania</dd>
        </dl>
        <p class="tiny mut" style="margin:6px 0 0">You are two weeks inside the legal tyre window — but November in Pirkanmaa can already have ice. Check tread before you leave.</p></div>
      <div class="card tight"><h3>Ferry with a car, practically</h3>
        <ul class="small" style="margin:0;padding-left:16px">
          <li>Tallink sails from <b>Terminal D</b> in Tallinn; Viking and Eckerö from <b>Terminal A</b>. Do not mix them up at 12:45.</li>
          <li>Be at the gate <b>30–45 min</b> before departure; car lanes close earlier than foot passengers.</li>
          <li>Passports for all five, including the baby. Estonia and Finland are both Schengen, but identity checks happen.</li>
          <li>Leave the car last — foot passengers board first, and you will sit in the lane with sleeping children.</li>
          <li>Book a seat or a cabin only if you want one; the 2 h crossing is short and the café deck is enough.</li>
        </ul></div>
    </div>

    <div class="callout warn" style="margin-top:12px"><b>Fuel strategy.</b> Fill up in Lithuania (cheapest), again in Latvia, and once more in Finland before the ferry back. Estonian motorway stations are the most expensive on the route; Finnish stations are cheaper than Estonian ones near the ports. Total fuel for ≈1,950 km at 7 l/100 km: <b>€220–260</b>.</div>

    <h3 style="margin-top:18px">Getting around Tampere without the car</h3>
    <div class="grid g2">
      <div class="card tight"><h3>Bus and tram (Nysse)</h3>
        <dl class="kv" style="margin-top:6px">
          <dt>Single, 2 zones</dt><dd>€2.70 adult</dd>
          <dt>24 h ticket</dt><dd>€7.00 adult</dd>
          <dt>Child 7–16</dt><dd>€1.25 per trip</dd>
          <dt>Under 7</dt><dd>free with an adult</dd>
          <dt>App</dt><dd>Nysse Mobiili</dd>
        </dl>
        <p class="tiny mut" style="margin:6px 0 0">Two zones cover Santalahti, the centre and Kaleva. Buy in the app; the driver takes card but not always cash.</p></div>
      <div class="card tight"><h3>Car in the city</h3>
        <dl class="kv" style="margin-top:6px">
          <dt>Centre parking</dt><dd>€1.20–3.60 / h</dd>
          <dt>Parking disc</dt><dd>required on many streets</dd>
          <dt>K-Citymarket</dt><dd>free 2 h with purchase</dd>
          <dt>Fuel</dt><dd>≈€1.70 / l</dd>
        </dl>
        <p class="tiny mut" style="margin:6px 0 0">Buy a parking disc at any petrol station on day one. Fines are €40 and they are enforced.</p></div>
    </div>
  </div>
</section>

<!-- ============ MAP ============ -->
<section class="page" id="map">
  <div class="wrap">
    <h2>Map</h2>
    <p class="small mut">{n_total} places. Tap a pin for the rating, price and a link; numbered bubbles group places that are close together — tap to zoom in.</p>
    <div class="fbar" id="mapfilters"></div>
    <div class="mapwrap">
      <div id="map"></div>
      <div class="mapbtns">
        <button id="locate" title="Find me" aria-label="Find me">◎</button>
        <button id="fitall" title="Fit all" aria-label="Fit all">⤢</button>
      </div>
    </div>
    <p class="tiny mut" style="margin-top:8px">Pins outside Tampere are the day trips and the drive home — zoom out to see Helsinki, Tallinn, Pärnu and Riga.</p>
  </div>
</section>

<!-- ============ PLACES ============ -->
<section class="page" id="places">
  <div class="wrap">
    <h2>Places</h2>
    <input class="search" id="q" placeholder="Search — moomin, castle, swimming, mustamakkara…" autocomplete="off">
    <div class="fbar" id="catfilters"></div>
    <div class="fbar" id="dayfilters"></div>
    <div class="count" id="count">Loading…</div>
    <div id="list"></div>
    <p class="tiny mut" style="margin-top:10px">Prices are for all five of you (2 adults + 2 children + a baby) unless stated. A rating is shown only where it was read from Google Maps on 30 Oct 2026.</p>
  </div>
</section>

<!-- ============ KIDS ============ -->
<section class="page" id="kids">
  <div class="wrap">
    <h2>Kids</h2>
    <p class="small mut">Ranked by the kid-o-meter: how much a 9- and a 7-year-old will actually enjoy it, not how worthy it is. The baby is a separate problem — look for <b>toddler-proof</b>.</p>
    <div class="fbar" id="kidsfilters"></div>
    <div class="count" id="kidscount"></div>
    <div id="kidslist"></div>

    <div class="card" style="margin-top:16px">
      <h3>The five that will actually be remembered</h3>
      <div class="tw"><table>
        <thead><tr><th>#</th><th>Place</th><th>Why they will talk about it</th><th>Cost for 5</th></tr></thead>
        <tbody>
          <tr class="hi"><td class="num">1</td><td><b>Moomin Museum</b></td><td>The five-storey Moominhouse, and a workshop where you cut and glue</td><td class="num">€36</td></tr>
          <tr><td class="num">2</td><td><b>Kintulammi campfire</b></td><td>A real fire, a sausage on a stick, a forest with no playground</td><td class="num">free</td></tr>
          <tr><td class="num">3</td><td><b>Heureka</b></td><td>Everything can be touched; rats play basketball</td><td class="num">€78</td></tr>
          <tr><td class="num">4</td><td><b>Pyynikki tower</b></td><td>130 steps up, a doughnut at the bottom</td><td class="num">€7</td></tr>
          <tr><td class="num">5</td><td><b>All Saints' candles</b></td><td>A whole hillside of small flames in the dark</td><td class="num">free</td></tr>
        </tbody></table></div>
    </div>

    <div class="grid g2">
      <div class="card tight"><h3>Rainy-day shortlist</h3>
        <ul class="small" style="margin:0;padding-left:16px">
          <li><b>Vapriikki</b> — 3 h, €38, everything indoors</li>
          <li><b>Swimming hall</b> — 2 h, €22, warm water</li>
          <li><b>Metso library</b> — free, warm, sofas</li>
          <li><b>Ideapark</b> — 20 min, free, play area</li>
          <li><b>Heureka</b> — if you are near Helsinki</li>
        </ul></div>
      <div class="card tight"><h3>The 9-month-old's rules</h3>
        <ul class="small" style="margin:0;padding-left:16px">
          <li>Two hours out, then home. Every time.</li>
          <li><b>Nap 1</b> 11:00 in the buggy; <b>nap 2</b> 15:00 in the car.</li>
          <li>Carrier beats buggy: cobbles, castle stairs, forest paths.</li>
          <li>Every museum listed has lifts and a baby-changing room.</li>
          <li>Dark by 16:15 — plan the last stop for 15:30.</li>
        </ul></div>
    </div>
  </div>
</section>

<!-- ============ EAT ============ -->
<section class="page" id="eat">
  <div class="wrap">
    <h2>Eat</h2>
    <p class="small mut">{n_food} places, cheapest first, with the price for all five of you. There is no fine dining on this list — there is a lot of food that three children will eat without negotiation.</p>
    <div class="fbar" id="eatfilters"></div>
    <div class="count" id="eatcount"></div>
    <div id="eatlist"></div>

    <div class="card" style="margin-top:16px">
      <h3>What five people actually spend</h3>
      <div class="tw"><table>
        <thead><tr><th>Meal</th><th>Home-cooked</th><th>Cheap out</th><th>Restaurant</th></tr></thead>
        <tbody>
          <tr><td>Breakfast</td><td class="num">€8</td><td class="num">€20</td><td class="num">€45</td></tr>
          <tr><td>Lunch</td><td class="num">€12</td><td class="num">€30</td><td class="num">€60</td></tr>
          <tr><td>Dinner</td><td class="num">€18</td><td class="num">€40</td><td class="num">€70</td></tr>
          <tr class="hi"><td><b>Day total</b></td><td class="num"><b>€38</b></td><td class="num"><b>€90</b></td><td class="num"><b>€175</b></td></tr>
        </tbody></table></div>
      <p class="small mut" style="margin:8px 0 0">A realistic mix — breakfast and half the dinners at home, lunch out — lands around <b>€95–110 a day for five</b>. That is the single biggest lever on the budget.</p>
    </div>

    <div class="callout good"><b>Three cheap institutions to build the week around:</b> mustamakkara at <b>Tammela market</b> (€12 for five), a lunch plate at the <b>market hall</b> (€25–40), and the <b>Pyynikki doughnut</b> (€2.50). Between them they cost less than one restaurant dinner and they are the food the children will remember.</div>

    <div class="callout warn"><b>Sunday and holiday trap.</b> The market hall is closed on Sundays. Most grocery chains close or shorten hours on All Saints' Day (31 Oct). Alko, the state alcohol shop, stays open. Plan Saturday's dinner before you board the ferry.</div>
  </div>
</section>

<!-- ============ WORK ============ -->
<section class="page" id="work">
  <div class="wrap">
    <h2>Work</h2>
    <p class="small mut">Five working days from a flat in Tampere, with a family out in the city. This is the part of the trip that needs a schedule more than a map.</p>

    <div class="callout info"><b>The rule that keeps the week sane:</b> work 08:00–16:00 Finnish time (EET, one hour behind Vilnius), take lunch at 12:00 with whoever is home, and stop when they come back. Lithuania is one hour ahead — your 09:00 stand-up is their 08:00, so the morning is quiet.</div>

    <h3 style="margin-top:14px">Where to sit</h3>
    <div class="tw"><table>
      <thead><tr><th>Spot</th><th>Cost</th><th>Good for</th><th>Watch out</th></tr></thead>
      <tbody>
        <tr class="hi"><td><b>The flat</b><br><span class="tiny mut">Kitchen table or bedroom</span></td><td class="num">free</td><td>Video calls, deep work</td><td>Children at 15:00; check the wifi on arrival</td></tr>
        <tr><td><b>Metso library</b><br><span class="tiny mut">Pirkankatu 2</span></td><td class="num">free</td><td>Silence, 2 h blocks</td><td>No calls; closes around 20:00</td></tr>
        <tr><td><b>University library, Linna</b><br><span class="tiny mut">Kalevantie 5</span></td><td class="num">free</td><td>Full days, power at every desk</td><td>Guest wifi needs an email login</td></tr>
        <tr><td><b>Kahvila Runo</b><br><span class="tiny mut">Ojakatu 3</span></td><td class="num">€5</td><td>Coffee meetings, 2 h</td><td>Too quiet to take a loud call</td></tr>
        <tr><td><b>Kaffila</b><br><span class="tiny mut">Aleksis Kiven katu 11</span></td><td class="num">€5</td><td>Short sessions near the market</td><td>Few seats, small tables</td></tr>
        <tr><td><b>Ratina mall</b><br><span class="tiny mut">Vuolteenkatu 1</span></td><td class="num">free</td><td>Rainy days, food court</td><td>Noisy; use headphones</td></tr>
      </tbody></table></div>

    <h3 style="margin-top:18px">The working week, planned around the family</h3>
    <div class="tw"><table>
      <thead><tr><th>Day</th><th>You</th><th>They</th><th>Handover</th></tr></thead>
      <tbody>
        <tr><td><b>Tue 3</b></td><td>08:00–16:00, calls in the morning</td><td>Vapriikki + Metso library</td><td>You cook; they are home by 15:30</td></tr>
        <tr><td><b>Wed 4</b></td><td>Deep work, no calls before 11</td><td>Häme Castle + Aulanko (79 km)</td><td>They are out until 15:45 — take the long call today</td></tr>
        <tr><td><b>Thu 5</b></td><td>08:00–15:00, then finish early</td><td>Kangasala car museum + ridge</td><td>Home by 15:00; you take the children for an hour</td></tr>
        <tr><td><b>Fri 6</b></td><td>Half day, log off at 14:00</td><td>Tallipiha, lunch, free Vapriikki 15–18</td><td>You join them at Vapriikki at 15:00</td></tr>
        <tr><td><b>Sat 7</b></td><td>Off</td><td>Heureka, ferry, Tallinn</td><td>Driving day for everyone</td></tr>
      </tbody></table></div>

    <div class="grid g2" style="margin-top:12px">
      <div class="card tight"><h3>Before you fly or drive</h3>
        <ul class="small" style="margin:0;padding-left:16px">
          <li>Ask the host for the <b>wifi speed</b> in writing — 4G in Santalahti is fine, but a 5 Mbit/s flat is not.</li>
          <li>Bring a small <b>USB-C dock or a travel router</b> if you need a wired connection.</li>
          <li>Test your VPN from Finland; some corporate tools block new countries.</li>
          <li>Roam like at home across the EU — your Lithuanian SIM works, with a fair-use cap.</li>
          <li>Book calls in <b>EET</b>, and tell colleagues you are one hour behind Vilnius.</li>
        </ul></div>
      <div class="card tight"><h3>If the flat is too loud</h3>
        <p class="small">Three children in a two-bedroom flat on a wet Tuesday is not a work environment. The escape plan, in order:</p>
        <ol class="small" style="margin:0;padding-left:16px">
          <li><b>Metso library</b> — free, silent, 10 minutes away.</li>
          <li><b>University library Linna</b> — open all day, power at every seat.</li>
          <li><b>Runo</b> — buy two coffees and stay until 16:00.</li>
        </ol></div>
    </div>

    <div class="callout warn"><b>One honest warning.</b> A working week with three children in a small flat is not a holiday for the adult who is alone with them. Book one paid activity per day (swimming, castle, museum), and accept that two of the five days will collapse. The plan above assumes that.</div>
  </div>
</section>

<!-- ============ COSTS ============ -->
<section class="page" id="costs">
  <div class="wrap">
    <h2>Costs</h2>
    <p class="small mut">For all five of you, excluding the two nights you have already booked. Lean = cooking, buses, free sights. Comfortable = restaurants, one paid attraction a day, parking everywhere.</p>

    <div class="tw"><table>
      <thead><tr><th>Item</th><th>Lean</th><th>Comfortable</th><th>Notes</th></tr></thead>
      <tbody>
        <tr><td>Ferry out, car + 5</td><td class="num">€210</td><td class="num">€260</td><td>13:30 MyStar</td></tr>
        <tr><td>Ferry back, car + 5</td><td class="num">€220</td><td class="num">€270</td><td>Saturday afternoon</td></tr>
        <tr><td>Fuel, ≈1,950 km</td><td class="num">€220</td><td class="num">€260</td><td>7 l/100 km</td></tr>
        <tr><td>Roads and vignettes</td><td class="num">€0</td><td class="num">€0</td><td>No tolls on this route</td></tr>
        <tr><td>Second flat, 5 nights</td><td class="num">€500</td><td class="num">€750</td><td>2–7 Nov, parking included</td></tr>
        <tr><td>Tallinn hotel, 1 night</td><td class="num">€70</td><td class="num">€110</td><td>7 Nov, parking</td></tr>
        <tr><td>Food, 9 days</td><td class="num">€600</td><td class="num">€1,000</td><td>Lean = €38/day at home</td></tr>
        <tr><td>Tickets and museums</td><td class="num">€120</td><td class="num">€300</td><td>Moomin €36, Vapriikki free Fri, Heureka €78</td></tr>
        <tr><td>Local transport and parking</td><td class="num">€40</td><td class="num">€90</td><td>Nysse day tickets €7</td></tr>
        <tr><td>Swimming, cafés, small stuff</td><td class="num">€80</td><td class="num">€160</td><td>The doughnuts are not optional</td></tr>
        <tr class="hi"><td><b>Total for five</b></td><td class="num"><b>≈€2,060</b></td><td class="num"><b>≈€3,260</b></td><td>Excluding the 2 nights booked</td></tr>
      </tbody></table></div>
    <p class="small" style="margin-top:8px"><b>Realistic middle: €2,500–2,800 for the family.</b> The three big numbers are the second flat, food, and the two ferries — everything else is noise.</p>

    <div class="grid g2" style="margin-top:10px">
      <div class="card tight"><h3>Price cheat-sheet</h3>
        <dl class="kv" style="margin-top:6px">
          <dt>Coffee</dt><dd>€2.00–3.50</dd><dt>Doughnut (munkki)</dt><dd>€2.50</dd>
          <dt>Mustamakkara portion</dt><dd>€2–4</dd><dt>Market hall lunch</dt><dd>€7–12 pp</dd>
          <dt>Pizza, large</dt><dd>€13–18</dd><dt>Restaurant main</dt><dd>€18–28</dd>
          <dt>Museum, adult</dt><dd>€8–18</dd><dt>Family ticket</dt><dd>€32–40</dd>
          <dt>Swimming, adult</dt><dd>≈€7</dd><dt>Bus single</dt><dd>€2.70</dd>
          <dt>Fuel</dt><dd>€1.60–1.80 / l</dd><dt>Parking, centre</dt><dd>€1.20–3.60 / h</dd>
        </dl></div>
      <div class="card tight"><h3>Free, and good</h3>
        <ul style="margin:0;padding-left:16px;font-size:12.5px">
          <li>Pyynikki ridge, Pispala, the lake shore at Santalahti</li>
          <li>Tampere Cathedral, Kaleva Church</li>
          <li>Metso library and the university library</li>
          <li>Finlayson quarter, Tallipiha yards</li>
          <li>Hatanpää manor park and arboretum</li>
          <li>Kintulammi and Kauppi forests, campfire sites</li>
          <li>All Saints' candles at Kalevankangas</li>
          <li>Suomenlinna, Oodi, Senate Square in Helsinki</li>
          <li>Tallinn Old Town, Kadriorg park, Pirita beach</li>
          <li><b>Vapriikki, Fridays 15:00–18:00</b></li>
        </ul></div>
    </div>

    <div class="callout info"><b>Money.</b> Finland is card-first — buses, museums, markets, even the campfire café. Keep €50 in cash for market stalls and the Pispala kiosk. Estonia and Latvia take cards everywhere; Lithuania mostly. Finland uses the euro, Estonia the euro, Latvia the euro, Lithuania the euro — one currency the whole way, which is one less thing to think about.</div>
  </div>
</section>

<!-- ============ INFO ============ -->
<section class="page" id="info">
  <div class="wrap">
    <h2>Info</h2>

    <h3>Opening hours — the thing that ruins trips</h3>
    <div class="tw"><table>
      <thead><tr><th>Place</th><th>Sat 31</th><th>Sun 1</th><th>Mon 2</th><th>Tue–Fri</th><th>Cost for 5</th></tr></thead>
      <tbody>
        <tr><td>Moomin Museum</td><td>9–17</td><td>9–17</td><td class="no">closed</td><td>10–18</td><td class="num">€36</td></tr>
        <tr><td>Vapriikki</td><td>10–18</td><td>10–18</td><td class="no">closed</td><td>10–18</td><td class="num">€38 / free Fri</td></tr>
        <tr><td>Market hall</td><td>9–16</td><td class="no">closed</td><td>9–18</td><td>9–18</td><td class="num">€30</td></tr>
        <tr><td>Tammela market</td><td class="yes">morning</td><td class="no">closed</td><td class="yes">morning</td><td class="yes">morning</td><td class="num">€12</td></tr>
        <tr><td>Pyynikki tower</td><td class="yes">9–20</td><td class="yes">9–20</td><td class="yes">9–20</td><td class="yes">9–20</td><td class="num">€7</td></tr>
        <tr><td>Näsinneula tower</td><td class="yes">11–</td><td class="no">closed</td><td class="no">closed</td><td class="yes">11–</td><td class="num">≈€28</td></tr>
        <tr><td>Swimming centre</td><td class="yes">open</td><td class="yes">open</td><td class="yes">open</td><td class="yes">open</td><td class="num">€22</td></tr>
        <tr><td>Cathedral</td><td class="yes">10–17</td><td class="yes">after service</td><td class="yes">10–17</td><td class="yes">10–17</td><td class="num">free</td></tr>
        <tr><td>Metso library</td><td class="yes">10–17</td><td class="yes">10–17</td><td class="yes">9–20</td><td class="yes">9–20</td><td class="num">free</td></tr>
        <tr><td>K-Citymarket Lielahti</td><td class="no">holiday hours</td><td class="yes">10–22</td><td class="yes">8–22</td><td class="yes">8–22</td><td class="num">—</td></tr>
        <tr><td>Häme Castle</td><td>11–16</td><td>11–16</td><td class="no">closed</td><td>10–16</td><td class="num">≈€35</td></tr>
        <tr><td>Heureka</td><td class="yes">10–17</td><td class="yes">10–17</td><td class="yes">10–17</td><td class="yes">10–17</td><td class="num">€78</td></tr>
        <tr><td>Lennusadam</td><td class="yes">10–18</td><td class="yes">10–18</td><td class="no">closed</td><td class="yes">10–18</td><td class="num">€40</td></tr>
      </tbody></table></div>
    <p class="tiny mut" style="margin-top:6px">Checked 30 Oct 2026 from the operators' own pages. Winter hours change without warning — re-check the two or three places you are actually going to pay for.</p>

    <div class="grid g2" style="margin-top:10px">
      <div class="card tight"><h3>31 October is All Saints' Day</h3>
        <p class="small">A public holiday in Finland. <b>Most grocery chains close or run Sunday hours</b>, banks and offices shut, and public transport runs a Sunday timetable. Alko stays open. The evening belongs to candles at the cemetery — the most beautiful thing in this whole plan.</p></div>
      <div class="card tight"><h3>Emergency</h3>
        <dl class="kv" style="margin-top:6px"><dt>Emergency, all</dt><dd>112</dd>
          <dt>Health advice</dt><dd>116 117 (FI)</dd><dt>Poison control</dt><dd>0800 147 111</dd>
          <dt>Pharmacy</dt><dd>Yliopiston Apteekki, Hämeenkatu</dd>
          <dt>EU health card</dt><dd>EHIC covers public care</dd></dl>
        <p class="tiny mut" style="margin:6px 0 0">Tap water is excellent everywhere. Pharmacies are closed on Sundays except the duty one.</p></div>
      <div class="card tight"><h3>Ten words that help</h3>
        <ul class="small" style="margin:0;padding-left:16px">
          <li><b>Kiitos</b> — thank you</li><li><b>Hei</b> — hello</li>
          <li><b>Yksi, kaksi, kolme</b> — one, two, three</li>
          <li><b>Maito</b> — milk · <b>Vesi</b> — water</li>
          <li><b>Vessa / WC</b> — toilet</li>
          <li><b>Paljonko?</b> — how much?</li>
          <li><b>Lapsi</b> — child · <b>Vauva</b> — baby</li>
          <li><b>Ei saa</b> — not allowed</li>
          <li><b>Anteeksi</b> — sorry / excuse me</li>
        </ul></div>
      <div class="card tight"><h3>Etiquette and small print</h3>
        <ul class="small" style="margin:0;padding-left:16px">
          <li>Shoes off at the door in Finnish homes and many flats.</li>
          <li>Sauna: swimsuit or towel, no shoes, children welcome.</li>
          <li>Tipping is not expected; round up if you like.</li>
          <li>Prams are left outside cafés — nobody steals them.</li>
          <li>Quiet in libraries and churches; the Finns mean it.</li>
          <li>Reflective vest after dark — it is dark at 16:00.</li>
        </ul></div>
    </div>

    <div class="card" style="margin-top:8px">
      <h3>Packing list</h3>
      <p class="small mut" style="margin-bottom:4px">Ticks are saved on this device. <span id="packcount" class="tiny"></span></p>
      <div class="progress"><i id="packbar"></i></div>
      <div id="packing"></div>
    </div>

    <div class="card tight">
      <h3>Three things that will go wrong</h3>
      <ol class="small" style="margin:0;padding-left:16px">
        <li><b>You will arrive on a public holiday with no food.</b> Most Finnish shops shut on 31 Oct. Buy breakfast in Tallinn or on the ferry, and have a takeaway plan for dinner.</li>
        <li><b>Monday will be dead.</b> Every museum in Tampere closes on Mondays. That is why the plan swims and eats mustamakkara instead — do not fight it.</li>
        <li><b>The 9-month-old will not do three hours in a museum.</b> Split up. One adult takes the big two into Vapriikki, the other walks the baby along the rapids and meets you at the café.</li>
      </ol>
    </div>
    <p class="tiny mut">Places and ratings checked 30 October 2026 (Google Maps, read directly). Prices and hours from the operators' own pages the same day, and marked ≈ where they are seasonal or change often. Weather: Open-Meteo, Tampere, 30 Oct 2026. Map: OpenFreeMap / © OpenStreetMap contributors. Every distance is straight-line from the flat, so the driving time is an estimate, not a route.</p>
  </div>
</section>

</main>
<footer><div class="wrap">
  <b>Perhe-reissu</b> · {n_total} places · {n_rated} Google ratings · prices for five · built 30 Oct 2026.
  Weather: Open-Meteo · Map: OpenFreeMap / © OpenStreetMap contributors.
</div></footer>
<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<script>
const DATA={js({"places": places, "days": [{"id": d["id"], "short": d["short"]} for d in days], "wx": [], "packing": PACKING})};
window.DATA=DATA; window.PLACES=DATA.places;
</script>
<script>{app}</script>
</body>
</html>
"""

(ROOT / "index.html").write_text(HTML, encoding="utf-8")

manifest = {
    "name": "Perhe-reissu — Tampere", "short_name": "Perhe-reissu",
    "start_url": "./index.html", "display": "standalone",
    "background_color": "#fbf8f2", "theme_color": "#254a6b",
    "icons": [{"src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 192 192'%3E%3Ccircle cx='96' cy='96' r='92' fill='%23254a6b'/%3E%3Ctext x='96' y='132' font-size='104' font-family='Georgia,serif' fill='%23fff' text-anchor='middle'%3ET%3C/text%3E%3C/svg%3E",
               "sizes": "192x192", "type": "image/svg+xml", "purpose": "any"}]
}
(ROOT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
print(f"built {len(HTML)/1024:.0f} KB · {n_total} places · {n_rated} rated · {n_free} free")
