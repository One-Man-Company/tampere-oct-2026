/* Perhe-reissu — list-first, map, kid-o-meter, packing list */
(function () {
  "use strict";
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const P = {
    see: '<path d="M3 21h18M4 21V10m5 11V10m6 11V10m5 11V10M2 10L12 3l10 7"/>',
    museum: '<path d="M3 21h18M5 21V9m4 12V9m3 12V9m3 12V9m4 12V9M3 9l9-6 9 6z"/>',
    do: '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3.2"/>',
    nature: '<path d="M12 21v-7M12 14l-4.5-4.5a4.2 4.2 0 116-6L12 5l-1.5-1.5a4.2 4.2 0 016 6L12 14z"/>',
    play: '<circle cx="12" cy="7" r="3"/><path d="M6 21v-4a6 6 0 0112 0v4M9.5 4.6L12 7l2.5-2.4"/>',
    eat: '<path d="M6 3v8a2.4 2.4 0 004.8 0V3M8.4 11v10M16.6 3c-1.6 1.6-2.2 3.3-2.2 5.5s.6 3.9 2.2 5.5V21"/>',
    cafe: '<path d="M4 8h13v5a4 4 0 01-4 4H8a4 4 0 01-4-4V8zM17 9h2a2 2 0 010 4h-2M6 3v2M10 3v2M14 3v2"/>',
    work: '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 012-2h4a2 2 0 012 2v2M3 12h18"/>',
    practical: '<circle cx="12" cy="12" r="8.5"/><path d="M12 8.5v5M12 16h.01"/>',
    trip: '<rect x="4" y="3" width="16" height="14" rx="2.4"/><path d="M4 10h16M8.6 21l2-4M15.4 21l-2-4"/>',
    star: '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2.2M12 19.8V22M2 12h2.2M19.8 12H22M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M19.1 4.9l-1.6 1.6M6.5 17.5l-1.6 1.6"/>',
    moon: '<path d="M20.5 14.4A8.6 8.6 0 019.6 3.5 8.6 8.6 0 1020.5 14.4z"/>',
    pin: '<path d="M12 21.4s7-6.6 7-11.4a7 7 0 10-14 0c0 4.8 7 11.4 7 11.4z"/><circle cx="12" cy="10" r="2.5"/>',
    car: '<path d="M5 17h14M6.5 17V13l1.8-4.5h7.4L17.5 13v4M7 17v1.6M17 17v1.6"/><circle cx="8" cy="14.6" r=".8"/><circle cx="16" cy="14.6" r=".8"/>',
    walk: '<circle cx="13.5" cy="4.4" r="1.9"/><path d="M12 21l1.6-5.6-3.1-3 2.1-5.6 3.6 3 3 1M9.4 9.4L7 14l3 1.6"/>',
    link: '<path d="M10.5 13.5a4.5 4.5 0 006.4 0l1.8-1.8a4.5 4.5 0 00-6.4-6.4l-1 1"/><path d="M13.5 10.5a4.5 4.5 0 00-6.4 0l-1.8 1.8a4.5 4.5 0 006.4 6.4l1-1"/>',
    chev: '<path d="M6 9l6 6 6-6"/>',
    home: '<path d="M3 11l9-7 9 7v9.4a1 1 0 01-1 1h-5.4V15H9.4v6.4H4a1 1 0 01-1-1z"/>',
    clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    trail: '<path d="M4 20c4-1 4-6 8-7s4-6 8-7"/><circle cx="6" cy="20" r="1.5"/><circle cx="18" cy="6" r="1.5"/>',
    beach: '<path d="M2 18c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2M2 22c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2"/><circle cx="17" cy="6" r="3"/>',
    cliff: '<path d="M3 20h18M4 20V9l5-3 4 4 3-2 4 4v8"/>',
    view: '<circle cx="12" cy="12" r="2.8"/><path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6z"/>',
    euro: '<path d="M17 6.5A6.5 6.5 0 007.5 12A6.5 6.5 0 0017 17.5M5.5 10.5h7M5.5 13.5h7"/>'
  };
  const icon = (k, cls) => '<svg class="i ' + (cls || "") + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (P[k] || P.practical) + '</svg>';

  const CAT = {
    see:       { label: "See",       color: "#254a6b" },
    museum:    { label: "Museum",    color: "#3c5f86" },
    do:        { label: "Do",        color: "#c98a1f" },
    nature:    { label: "Nature",    color: "#2f7d63" },
    trail:     { label: "Trail",     color: "#39734f" },
    beach:     { label: "Beach",     color: "#b08d2e" },
    cliff:     { label: "Cliff",     color: "#6f5a45" },
    viewpoint: { label: "Viewpoint", color: "#4b7f9e" },
    play:      { label: "Kids play", color: "#b8445e" },
    eat:       { label: "Eat",       color: "#a9522a" },
    cafe:      { label: "Café",      color: "#8a6330" },
    work:      { label: "Work spot", color: "#5b6b7d" },
    trip:      { label: "Day trip",  color: "#2f6f8f" },
    practical: { label: "Practical", color: "#7d837d" }
  };
  const DATA = window.DATA || { places: [], days: [], wx: [] };
  const PLACES = DATA.places;
  const DAYLBL = {}; DATA.days.forEach(d => DAYLBL[d.id] = d.short);

  /* ---------- theme ---------- */
  const root = document.documentElement;
  const saved = localStorage.getItem("pr-theme");
  if (saved) root.setAttribute("data-theme", saved);
  else if (matchMedia && matchMedia("(prefers-color-scheme: dark)").matches) root.setAttribute("data-theme", "dark");
  const themeBtn = $("#theme");
  const syncTheme = () => { if (themeBtn) themeBtn.innerHTML = icon(root.getAttribute("data-theme") === "dark" ? "sun" : "moon"); };
  if (themeBtn) themeBtn.onclick = () => {
    const dark = root.getAttribute("data-theme") === "dark";
    root.setAttribute("data-theme", dark ? "light" : "dark");
    localStorage.setItem("pr-theme", dark ? "light" : "dark");
    syncTheme();
  };
  syncTheme();

  /* ---------- tabs ---------- */
  const tabs = $$(".tab"), pages = $$("section.page");
  function show(id) {
    const t = document.getElementById(id) || document.getElementById("plan");
    pages.forEach(p => p.classList.toggle("on", p.id === t.id));
    tabs.forEach(b => b.classList.toggle("on", b.dataset.tab === t.id));
    history.replaceState(null, "", "#" + t.id);
    window.scrollTo(0, 0);
    if (t.id === "map") {
      if (!window.__map) initMap();
      if (window.__map) [40, 200, 600].forEach(ms => setTimeout(() => { window.__map.resize(); renderMap(); }, ms));
    }
  }
  tabs.forEach(b => b.onclick = () => show(b.dataset.tab));

  /* ---------- weather strip ---------- */
  const wx = $("#wxstrip");
  if (wx && DATA.wx && DATA.wx.length) wx.innerHTML = DATA.wx.map(w =>
    '<div class="wxd"><div class="d">' + w.d + '</div><div class="t">' + w.t + '</div>' +
    '<span class="v ' + w.cls + '">' + w.tag + '</span><div class="n">' + w.n + '</div></div>').join("");

  /* ---------- day tabs ---------- */
  $$("#daytabs .day").forEach(b => b.onclick = () => {
    $$("#daytabs .day").forEach(x => x.classList.toggle("on", x === b));
    $$(".daypanel").forEach(p => p.style.display = p.dataset.panel === b.dataset.day ? "" : "none");
  });

  /* ---------- row rendering ---------- */
  function kidmeter(n) {
    let s = '<span class="kid">';
    for (let i = 1; i <= 5; i++) s += '<i class="' + (i <= n ? "f" : "") + '"></i>';
    return s + "</span>";
  }
  function row(p) {
    const c = CAT[p.cat] || CAT.practical;
    const rate = p.rating ? '<span class="rate">' + icon("star") + p.rating.toFixed(1) + "</span>" : "";
    const priceTxt = p.price && p.price !== "—" ? p.price.split("·")[0].trim() : "";
    return '<article class="row" id="r-' + p.id + '" data-cat="' + p.cat + '" style="--cat:' + c.color + '">' +
      '<button class="rowhead" aria-expanded="false">' +
        '<span class="rm"><span class="rt">' + esc(p.name) + "</span>" +
        '<span class="rs">' + esc(p.sub) + " · " + esc(p.area) + "</span></span>" +
        '<span class="rr">' + rate + (priceTxt ? '<span class="price">' + esc(priceTxt) + "</span>" : "") + "</span>" +
        icon("chev", "chev") +
      "</button>" +
      '<div class="rowbody">' +
        "<p>" + esc(p.desc) + "</p>" +
        '<p class="why"><b>Why for us:</b> ' + esc(p.why) + "</p>" +
        (p.tip ? '<div class="tip"><b>Tip:</b> ' + esc(p.tip) + "</div>" : "") +
        '<div class="rc">' +
          (p.hours && p.hours !== "—" ? "<span>" + esc(p.hours) + "</span>" : "") +
          (p.dur ? "<span>" + icon("clock") + " " + esc(p.dur) + "</span>" : "") +
          (p.fam ? "<span>" + icon("euro") + " " + esc(p.fam) + "</span>" : "") +
          (p.km != null ? "<span>" + p.km + " km</span>" : "") +
          '<span>' + (p.indoor ? "Inside" : "Outside") + "</span>" +
        "</div>" +
        '<div class="kidwrap" style="margin-top:8px"><b>Kid-o-meter</b>' + kidmeter(p.kid || 3) + "</div>" +
        '<div class="links">' +
          '<a class="btn pri" href="' + p.gmaps + '" target="_blank" rel="noopener">' + icon("pin") + " Maps</a>" +
          '<a class="btn" href="' + p.dir + '" target="_blank" rel="noopener">' + icon("car") + " Drive " + (p.drive || "") + "</a>" +
          (p.web ? '<a class="btn" href="' + p.web + '" target="_blank" rel="noopener">' + icon("link") + " Site</a>" : "") +
        "</div></div></article>";
  }
  const shown = { list: 30, eat: 30, kids: 40, nature: 40, coast: 40 };
  function mount(el, items, key, emptyMsg) {
    if (!el) return;
    const n = shown[key] || 30;
    const slice = items.slice(0, n);
    el.innerHTML = (items.length ? slice.map(row).join("") :
      '<div class="card"><b>Nothing matches.</b><p class="small mut" style="margin:4px 0 0">' +
      (emptyMsg || "Clear the search or pick another filter.") + "</p></div>") +
      (items.length > n ? '<button class="more" data-more="' + key + '">Show ' + Math.min(30, items.length - n) +
        " more · " + (items.length - n) + " left</button>" : "");
  }
  document.addEventListener("click", e => {
    const m = e.target.closest("[data-more]");
    if (!m) return;
    shown[m.dataset.more] = (shown[m.dataset.more] || 30) + 30;
    if (m.dataset.more === "list") renderList();
    if (m.dataset.more === "eat") renderEat();
    if (m.dataset.more === "kids") renderKids();
    if (m.dataset.more === "nature") renderNature();
    if (m.dataset.more === "coast") renderCoast();
  });
  document.addEventListener("click", e => {
    const h = e.target.closest(".rowhead");
    if (!h) return;
    const art = h.closest(".row");
    const open = art.classList.toggle("open");
    h.setAttribute("aria-expanded", open ? "true" : "false");
  });
  document.addEventListener("click", e => {
    const a = e.target.closest("[data-row]");
    if (!a) return;
    e.preventDefault();
    openRow(a.dataset.row);
  });
  function openRow(id) {
    const p = PLACES.find(x => x.id === id);
    if (!p) return;
    listState.cat = "all"; listState.day = "all"; listState.minKid = 0; listState.q = p.name;
    const q = $("#q"); if (q) q.value = p.name;
    buildChips(); renderList(); show("places");
    setTimeout(() => {
      const el = document.getElementById("r-" + id);
      if (!el) return;
      el.classList.add("open");
      el.querySelector(".rowhead").setAttribute("aria-expanded", "true");
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.style.outline = "2px solid var(--indigo)";
      setTimeout(() => el.style.outline = "", 1600);
    }, 80);
  }

  /* ---------- filters ---------- */
  const listState = { cat: "all", day: "all", q: "", minKid: 0, sort: "distance", indoor: "all" };
  const eatState = { kind: "all", maxFam: 0 };
  const kidsState = { indoor: "all", age: "all" };
  const natureState = { region: "all", type: "all" };
  const coastState = { country: "all", type: "all" };
  const REGIONS = { tampere: "Tampere & Häme", pori: "Yyteri & Pori", jyvaskyla: "Jyväskylä",
    savonlinna: "Savonlinna", punkaharju: "Punkaharju", porvoo: "Porvoo",
    hanko: "Tammisaari & Hanko", lappeenranta: "Lappeenranta & Imatra" };
  const COUNTRIES = { ee: "Estonia mainland", saaremaa: "Saaremaa & Muhu", lv: "Latvia", lt: "Lithuania" };
  const NTYPES = { nature: "Parks", trail: "Trails", beach: "Beaches", cliff: "Cliffs & rocks", viewpoint: "Viewpoints" };
  const mapState = { cat: "all" };

  function chip(label, attr, val, on) {
    return '<button class="fchip' + (on ? " on" : "") + '" ' + attr + '="' + val + '">' + label + "</button>";
  }
  function buildChips() {
    const c = $("#catfilters");
    if (c) c.innerHTML = chip("All", "data-fcat", "all", listState.cat === "all") +
      Object.keys(CAT).map(k => chip(icon(k) + " " + CAT[k].label, "data-fcat", k, listState.cat === k)).join("");
    const d = $("#dayfilters");
    if (d) d.innerHTML = chip("Any day", "data-day", "all", listState.day === "all") +
      DATA.days.map(x => chip(x.short, "data-day", x.id, listState.day === x.id)).join("");
    const e = $("#eatfilters");
    if (e) e.innerHTML = chip("All food", "data-ekind", "all", eatState.kind === "all") +
      chip("Restaurant", "data-ekind", "eat", eatState.kind === "eat") +
      chip("Café", "data-ekind", "cafe", eatState.kind === "cafe") +
      chip("Under €30 for 5", "data-emax", "30", eatState.maxFam === 30) +
      chip("Under €60 for 5", "data-emax", "60", eatState.maxFam === 60);
    const k = $("#kidsfilters");
    if (k) k.innerHTML = chip("Everything", "data-kin", "all", kidsState.indoor === "all") +
      chip("Inside", "data-kin", "in", kidsState.indoor === "in") +
      chip("Outside", "data-kin", "out", kidsState.indoor === "out") +
      chip("Free", "data-kage", "free", kidsState.age === "free") +
      chip("Toddler-proof", "data-kage", "baby", kidsState.age === "baby");
    const n = $("#naturefilters");
    if (n) n.innerHTML = chip("Everywhere", "data-nreg", "all", natureState.region === "all") +
      Object.entries(REGIONS).map(([k, v]) => chip(v, "data-nreg", k, natureState.region === k)).join("");
    const nt = $("#naturetypes");
    if (nt) nt.innerHTML = chip("All types", "data-ntype", "all", natureState.type === "all") +
      Object.entries(NTYPES).map(([k, v]) => chip(v, "data-ntype", k, natureState.type === k)).join("");
    const co = $("#coastfilters");
    if (co) co.innerHTML = chip("Whole coast", "data-ccou", "all", coastState.country === "all") +
      Object.entries(COUNTRIES).map(([k, v]) => chip(v, "data-ccou", k, coastState.country === k)).join("");
    const ct = $("#coasttypes");
    if (ct) ct.innerHTML = chip("All types", "data-ctype", "all", coastState.type === "all") +
      Object.entries(NTYPES).map(([k, v]) => chip(v, "data-ctype", k, coastState.type === k)).join("");
    const m = $("#mapfilters");
    if (m) m.innerHTML = chip("All", "data-mcat", "all", mapState.cat === "all") +
      Object.keys(CAT).map(x => chip(icon(x) + " " + CAT[x].label, "data-mcat", x, mapState.cat === x)).join("");
  }
  document.addEventListener("click", e => {
    const t = e.target;
    const c = t.closest("[data-fcat]"), d = t.closest("[data-day]"), k = t.closest("[data-minKid]");
    const ek = t.closest("[data-ekind]"), em = t.closest("[data-emax]");
    const kin = t.closest("[data-kin]"), kage = t.closest("[data-kage]");
    const nreg = t.closest("[data-nreg]"), ntype = t.closest("[data-ntype]");
    const ccou = t.closest("[data-ccou]"), ctype = t.closest("[data-ctype]");
    const mc = t.closest("[data-mcat]"), so = t.closest("[data-sort]");
    if (c) { listState.cat = c.dataset.fcat; buildChips(); renderList(); }
    if (d) { listState.day = d.dataset.day; buildChips(); renderList(); }
    if (k) { listState.minKid = +k.dataset.minKid; buildChips(); renderList(); }
    if (ek) { eatState.kind = ek.dataset.ekind; buildChips(); renderEat(); }
    if (em) { eatState.maxFam = +em.dataset.emax === eatState.maxFam ? 0 : +em.dataset.emax; buildChips(); renderEat(); }
    if (kin) { kidsState.indoor = kin.dataset.kin; buildChips(); renderKids(); }
    if (nreg) { natureState.region = nreg.dataset.nreg; buildChips(); renderNature(); }
    if (ntype) { natureState.type = ntype.dataset.ntype; buildChips(); renderNature(); }
    if (ccou) { coastState.country = ccou.dataset.ccou; buildChips(); renderCoast(); }
    if (ctype) { coastState.type = ctype.dataset.ctype; buildChips(); renderCoast(); }
    if (kage) { kidsState.age = kidsState.age === kage.dataset.kage ? "all" : kage.dataset.kage; buildChips(); renderKids(); }
    if (mc) { mapState.cat = mc.dataset.mcat; buildChips(); renderMap(); fitAll(); }
    if (so) { listState.sort = so.dataset.sort; renderList(); }
  });

  const byKid = (a, b) => (b.kid || 0) - (a.kid || 0) || (a.km || 0) - (b.km || 0);
  function renderList() {
    const q = listState.q.toLowerCase();
    let rows = PLACES.filter(p => {
      if (listState.cat !== "all" && p.cat !== listState.cat) return false;
      if (listState.day !== "all" && !(p.days || []).includes(listState.day)) return false;
      if (listState.minKid && (p.kid || 0) < listState.minKid) return false;
      if (q && !(p.name + " " + p.sub + " " + p.area + " " + p.desc + " " + p.why).toLowerCase().includes(q)) return false;
      return true;
    });
    rows.sort(listState.sort === "kid" ? byKid : (a, b) => a.km - b.km);
    const count = $("#count");
    if (count) count.innerHTML = rows.length + (rows.length === 1 ? " place · " : " places · ") +
      (listState.cat === "all" ? "all categories" : CAT[listState.cat].label) +
      (listState.day !== "all" ? " · " + DAYLBL[listState.day] : "") +
      ' · <button class="sortbtn" data-sort="' + (listState.sort === "kid" ? "distance" : "kid") + '">' +
      (listState.sort === "kid" ? "kid-o-meter ⇄" : "nearest first ⇄") + "</button>";
    mount($("#list"), rows, "list");
  }
  function renderEat() {
    let rows = PLACES.filter(p => {
      if (eatState.kind === "all") return p.cat === "eat" || p.cat === "cafe";
      return p.cat === eatState.kind;
    });
    if (eatState.maxFam) rows = rows.filter(p => (p.famNum || 99) <= eatState.maxFam);
    rows.sort((a, b) => (a.famNum || 99) - (b.famNum || 99) || byKid(a, b));
    const c = $("#eatcount");
    if (c) c.textContent = rows.length + " places · cheapest first, price is for all five of you";
    mount($("#eatlist"), rows, "eat");
  }
  function renderKids() {
    let rows = PLACES.filter(p => ["see", "museum", "do", "nature", "play", "trip"].includes(p.cat));
    if (kidsState.indoor === "in") rows = rows.filter(p => p.indoor);
    if (kidsState.indoor === "out") rows = rows.filter(p => !p.indoor);
    if (kidsState.age === "free") rows = rows.filter(p => (p.famNum || 0) === 0);
    if (kidsState.age === "baby") rows = rows.filter(p => p.baby);
    rows.sort(byKid);
    const c = $("#kidscount");
    if (c) c.textContent = rows.length + " things to do · ranked by how much the 9- and 7-year-old will actually enjoy it";
    mount($("#kidslist"), rows, "kids");
  }
  const q = $("#q");
  if (q) {
    let t;
    q.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { listState.q = q.value.trim(); renderList(); }, 110); });
  }

  /* ---------- nature & coast ---------- */
  function renderNature() {
    let rows = PLACES.filter(p => p.scope === "fi" && NTYPES[p.cat]);
    if (natureState.region !== "all") rows = rows.filter(p => p.region === natureState.region);
    if (natureState.type !== "all") rows = rows.filter(p => p.cat === natureState.type);
    rows.sort((a, b) => a.km - b.km || byKid(a, b));
    const c = $("#naturecount");
    if (c) c.textContent = rows.length + " places · nearest to the flat first · " +
      (natureState.region === "all" ? "all of Finland" : REGIONS[natureState.region]);
    mount($("#naturelist"), rows, "nature");
  }
  const COAST_ORDER = { ee: 0, saaremaa: 1, lv: 2, lt: 3 };
  function renderCoast() {
    let rows = PLACES.filter(p => p.scope === "baltic");
    if (coastState.country !== "all") rows = rows.filter(p => p.region === coastState.country);
    if (coastState.type !== "all") rows = rows.filter(p => p.cat === coastState.type);
    rows.sort((a, b) => (COAST_ORDER[a.region] ?? 9) - (COAST_ORDER[b.region] ?? 9) || b.lat - a.lat);
    const c = $("#coastcount");
    if (c) c.textContent = rows.length + " places · ordered along the drive home, north to south";
    mount($("#coastlist"), rows, "coast");
  }

  /* ---------- map ---------- */
  function initMap() {
    const el = $("#map");
    if (!el || !window.maplibregl) return;
    const map = new maplibregl.Map({
      container: "map", style: "https://tiles.openfreemap.org/styles/liberty",
      center: [23.7600, 61.4980], zoom: 12, attributionControl: false
    });
    window.__map = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-left");
    map.addControl(new maplibregl.AttributionControl({ compact: true }));
    window.__byId = {};
    window.__markers = PLACES.map(p => {
      const size = p.id === "home" ? 26 : 15;
      const d = document.createElement("div");
      d.className = "pin" + (p.id === "home" ? " home" : "");
      d.style.cssText = "width:" + size + "px;height:" + size + "px;background:" + (CAT[p.cat] || CAT.practical).color;
      d.title = p.name;
      if (p.id === "home") d.innerHTML = icon("home");
      const pop = new maplibregl.Popup({ offset: size * 0.7, maxWidth: "250px" }).setHTML(
        '<div class="pop"><h4>' + esc(p.name) + "</h4>" +
        '<div class="m">' + (p.rating ? "★ " + p.rating.toFixed(1) + " · " : "") + esc((p.price || "").split("·")[0].trim()) +
        " · " + esc(p.area) + "</div>" +
        '<div class="tiny mut" style="margin-bottom:5px">' + esc(p.hours || "") + "</div>" +
        '<a href="' + p.gmaps + '" target="_blank" rel="noopener">Maps ↗</a>' +
        (p.web ? '<a href="' + p.web + '" target="_blank" rel="noopener">Site ↗</a>' : "") +
        '<a href="#r-' + p.id + '" data-row="' + p.id + '">Details →</a></div>');
      const mk = new maplibregl.Marker({ element: d, anchor: "center" }).setLngLat([p.lon, p.lat]).setPopup(pop).addTo(map);
      mk.__p = p; window.__byId[p.id] = mk;
      return mk;
    });
    $("#fitall").onclick = fitAll;
    $("#locate").onclick = () => {
      if (!navigator.geolocation) return;
      navigator.geolocation.getCurrentPosition(pos => {
        const ll = [pos.coords.longitude, pos.coords.latitude];
        new maplibregl.Marker({ color: "#b8445e" }).setLngLat(ll).addTo(map);
        map.flyTo({ center: ll, zoom: 14 });
      }, () => alert("Location not available."), { timeout: 8000 });
    };
    map.on("load", () => { map.resize(); renderMap(); });
    map.on("moveend", renderMap);
    renderMap();
  }
  function visible(p) { return mapState.cat === "all" || p.cat === mapState.cat; }
  function renderMap() {
    const map = window.__map;
    if (!map || !window.__markers) return;
    window.__markers.forEach(m => { if (m._map) m.remove(); });
    (window.__clusters || []).forEach(el => el.remove());
    window.__clusters = [];
    const list = PLACES.filter(visible);
    const tol = 38, groups = [];
    list.forEach(p => {
      let pt; try { pt = map.project([p.lon, p.lat]); } catch (e) { return; }
      let g = groups.find(g => Math.hypot(g.x - pt.x, g.y - pt.y) < tol);
      if (!g) groups.push({ x: pt.x, y: pt.y, pts: [p] });
      else { g.pts.push(p); g.x = (g.x * (g.pts.length - 1) + pt.x) / g.pts.length; g.y = (g.y * (g.pts.length - 1) + pt.y) / g.pts.length; }
    });
    groups.forEach(g => {
      if (g.pts.length === 1) { const m = window.__byId[g.pts[0].id]; if (m) m.addTo(map); return; }
      const lon = g.pts.reduce((s, p) => s + p.lon, 0) / g.pts.length;
      const lat = g.pts.reduce((s, p) => s + p.lat, 0) / g.pts.length;
      const sz = Math.round(Math.min(36, 24 + Math.log2(g.pts.length) * 3.4));
      const el = document.createElement("div");
      el.className = "clusters";
      el.style.cssText = "width:" + sz + "px;height:" + sz + "px;font-size:" + (sz > 32 ? 12 : 11) + "px";
      el.textContent = g.pts.length;
      el.title = g.pts.slice(0, 5).map(p => p.name).join(" · ");
      el.onclick = () => map.flyTo({ center: [lon, lat], zoom: Math.min(map.getZoom() + 2, 16), duration: 450 });
      new maplibregl.Marker({ element: el, anchor: "center" }).setLngLat([lon, lat]).addTo(map);
      window.__clusters.push(el);
    });
  }
  function fitAll() {
    const map = window.__map;
    if (!map || !window.maplibregl) return;
    const c = map.getContainer();
    if (!c.clientWidth || !c.clientHeight) return;
    let list = PLACES.filter(visible);
    if (mapState.cat === "all") list = list.filter(p => p.km <= 20);
    if (!list.length) return;
    const b = new maplibregl.LngLatBounds();
    list.forEach(p => b.extend([p.lon, p.lat]));
    map.fitBounds(b, { padding: 30, maxZoom: 12.5, duration: 400 });
  }

  /* ---------- packing ---------- */
  const PACK = (DATA.packing || []);
  const packBox = $("#packing");
  if (packBox) {
    const done = JSON.parse(localStorage.getItem("pr-pack") || "[]");
    packBox.innerHTML = PACK.map((item, i) =>
      '<label class="check' + (done.includes(i) ? " done" : "") + '">' +
      '<input type="checkbox" data-i="' + i + '"' + (done.includes(i) ? " checked" : "") + "><span>" + esc(item) + "</span></label>").join("");
    const bar = $("#packbar");
    const upd = () => {
      const n = packBox.querySelectorAll("input:checked").length;
      if (bar) bar.style.width = Math.round(n / PACK.length * 100) + "%";
      const lbl = $("#packcount");
      if (lbl) lbl.textContent = n + " / " + PACK.length + " packed";
    };
    packBox.addEventListener("change", e => {
      const i = +e.target.dataset.i;
      const cur = JSON.parse(localStorage.getItem("pr-pack") || "[]");
      const next = cur.includes(i) ? cur.filter(x => x !== i) : cur.concat(i);
      localStorage.setItem("pr-pack", JSON.stringify(next));
      e.target.closest(".check").classList.toggle("done", next.includes(i));
      upd();
    });
    upd();
  }

  /* boot */
  buildChips();
  renderList();
  renderEat();
  renderKids();
  renderNature();
  renderCoast();
  const h = location.hash.replace("#", "");
  if (h && document.getElementById(h)) show(h);
  else if (h && h.startsWith("r-")) show("places");
})();
