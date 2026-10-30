# Perhe-reissu — Vilnius → Tampere, 31 Oct – 8 Nov 2026

A nine-day family trip for two adults and three daughters (9, 7 and 9 months), as a single static page.
Same architecture and depth as the Gdańsk trip, different visual language: paper, birch and berry, serif headlines, a daylight bar on every day.

- **197 places** — sights, museums, indoor play, day trips, cheap food, work spots, and the drive home through Estonia, Latvia and Lithuania
- **85 live Google Maps ratings**, read directly on 30 Oct 2026
- **Nature tab** — 43 trails, national parks, cliffs and beaches around the seven Finnish towns on the wish list (Yyteri, Jyväskylä, Savonlinna, Punkaharju, Porvoo, Tammisaari & Hanko, Lappeenranta & Imatra), filterable by region
- **Coast tab** — 39 cliffs, boulders, dunes and beaches from Tallinn to Klaipėda, including Saaremaa and Muhu, ordered along the drive home
- **Cost for all five** on every row, not a per-person guess
- **Kid-o-meter** (1–5) instead of a generic star rating: how much a 9- and a 7-year-old actually enjoy it
- **Nine day cards** with real sunrise/sunset, a daylight bar and the baby's nap windows
- **Real 31 October ferry timetable** (Tallink / Viking / Eckerö) with per-person fares for that date
- **Remote-work tab**: where to sit, how to plan calls around a family that is out without you
- **Opening-hours matrix** for the actual dates, including the traps (Monday closures, All Saints' Day, Sunday market hall)
- **Interactive packing list** that saves ticks in `localStorage`

Single `index.html`, no build step needed to read it. MapLibre + OpenFreeMap, no API keys.

**Live:** https://one-man-company.github.io/tampere-oct-2026/ — GitHub Pages, built from `main` / root.
Also on the tailnet at https://zoltanas.tail4bbf34.ts.net:8099/ (local copy, not public).

## Build

```
python3 build.py        # data/*.json + src/* → index.html, manifest.json
python3 -m http.server 8099
```

## Structure

```
build.py            generates the whole page
data/tampere.json   Tampere core (museums, nature, play, practical)
data/food.json      restaurants, cafés, market counters
data/trips.json     day trips from Tampere
data/route.json     Helsinki, Tallinn, Pärnu, Riga, Lithuania
data/nature_finland.json  trails, parks, cliffs, beaches near the seven Finnish towns
data/coast_baltic.json    Baltic coast: klint cliffs, boulders, dunes, beaches, Saaremaa
data/days.json      the nine-day itinerary, timeline by timeline
data/raw/           raw sources: OSM POIs and the geocoded place list
src/style.css       the design system
src/app.js          tabs, filters, map, packing list
```

## Facts and sources

- Weather: Open-Meteo, Tampere 61.5028 / 23.7209, hourly + daily, fetched 30 Oct 2026.
- Ferry times and fares: Laivaliput (Estravel) timetable for 31 Oct 2026, checked 30 Oct 2026.
- Prices and hours: Moomin Museum, Vapriikki, Häme Castle, Heureka, Kauppahalli, Pyynikki, Kaleva Church, Nysse, Heureka, Lennusadam, PROTO — from the operators' own pages on 30 Oct 2026.
- Ratings: Google Maps place panels, read 30 Oct 2026.
- Distances are straight-line from the flat; driving times are estimates, not routed.
- Values marked **≈** are seasonal or change often. Re-check anything you are about to pay for.

## Known constraints baked into the plan

- **Särkänniemi's season ended 17 October 2026** — rides, aquarium and Doghill are shut.
- **Every museum in Tampere closes on Mondays.** 2 November is a move day for that reason.
- **31 October is All Saints' Day in Finland** — most grocery chains close or run Sunday hours.
- **Näsinneula and its restaurant are closed Sunday–Monday** out of season.
- **Sunset is 16:25 on day one and 16:03 by the drive home.** Daylight, not temperature, sets the schedule.
