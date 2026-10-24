// Stránka Povodně: jedna povodeň v mapě, jak přesná byla předpověď a co model hlásil v kterékoli hodině. Jeden výběr
// povodně a města řídí všechny tři části.
import { typo, cislo, cm, jedn, parseIso, posun, datum, datumCas, denMesic } from "./typo.js";
import { DATA, H, KDE, NAZVY, BARVY, nacti, stav, zapisStav, odznak, nejblizsi } from "./data.js";
import { $, hlaska, dlazdice, segmenty, naZmenu, oznam } from "./spolecne.js";
import { prehled, veta, grafSVodoctem } from "./karty.js";
import { vodocet } from "./vodocet.js";
import { graf } from "./graf.js";

const q = stav();
const S = { povoden: q.get("povoden") || "2013-06", cil: q.get("cil") || "decin", h: +q.get("h") || 24, cas: q.get("cas"),
  vrstva: q.get("vrstva") === "animace" ? "animace" : "mapa", bezi: false };
let POV, MET, RADA, prvni = true;
const scena = $("#scena"), ramec = $("#ramec"), nahled = $("#nahled"), posuvnik = $("#cas"), vystup = $("#cas-out");

const povoden = () => POV.povodne.find((p) => p.slug === S.povoden) || POV.povodne[0];
const spa = () => POV.stanice[S.cil].spa;

async function start() {
  try {
    [POV, MET] = await Promise.all([nacti(DATA + "povodne.json"), nacti(DATA + "metriky.json")]);
  } catch (e) {
    $("#presnost-obsah").innerHTML = hlaska("Data se nepodařilo načíst. Zkuste stránku obnovit.", "varovani");
    return;
  }
  if (!POV.povodne.some((p) => p.slug === S.povoden)) S.povoden = POV.povodne[0].slug;
  if (!POV.stanice[S.cil]) S.cil = "decin";
  if (!H.includes(S.h)) S.h = 24;
  $("#povodne").innerHTML = dlazdice("povoden", POV.povodne.map((p) => ({ hodnota: p.slug, nazev: p.klic })), S.povoden, "Povodeň");
  $("#stanice").innerHTML = segmenty("cil", Object.entries(POV.stanice).map(([k, v]) => ({ hodnota: k, nazev: v.nazev })), S.cil, "Město");
  $("#vrstva").innerHTML = segmenty("vrstva", [{ hodnota: "mapa", nazev: "Rozliv v mapě" }, { hodnota: "animace", nazev: "Voda v řekách" }], S.vrstva, "Co ukázat v mapě");
  $("#horizont").innerHTML = segmenty("h", H.map((h) => ({ hodnota: String(h), nazev: `${h} h předem` })), String(S.h), "Předpověď vydaná kolik hodin předem");
  const strana = $(".strana");
  naZmenu(strana, "povoden", (v) => { S.povoden = v; S.cas = null; prvni = true; nactiAUkaz(); });
  naZmenu(strana, "cil", (v) => { S.cil = v; prvni = true; nactiAUkaz(); });
  naZmenu(strana, "vrstva", (v) => { S.vrstva = v; ukazMapu(); });
  naZmenu(strana, "h", (v) => { S.h = +v; ukazPresnost(); });
  posuvnik.addEventListener("input", () => { S.cas = RADA.cas[+posuvnik.value]; ukazOkamzik(); });
  $("#start").addEventListener("click", spustMapu);
  nactiAUkaz();
}

async function nactiAUkaz() {
  const p = povoden();
  $("#nadpis").textContent = typo(p.nazev.replace(/, model ji neviděl$/, ""));
  const v = p.vrchol && p.vrchol[S.cil];
  $("#podtitul").innerHTML = typo(`${v ? `Vrchol ${KDE[S.cil]} ${v.cm} cm ${datum(v.cas)}. ` : ""}${popisModelu(p)}`);
  ukazMapu();
  $("#okamzik").setAttribute("aria-busy", "true");
  try {
    RADA = await nacti(`${DATA}rada_${S.povoden}_${S.cil}.json`);
  } catch (e) {
    $("#presnost-obsah").innerHTML = hlaska("Průběh téhle povodně se nepodařilo načíst.", "varovani");
    $("#okamzik-obsah").innerHTML = "";
    return;
  } finally {
    $("#okamzik").removeAttribute("aria-busy");
  }
  if (!S.cas) S.cas = vychoziCas();
  posuvnik.max = RADA.cas.length - 1;
  ukazPresnost();
  ukazOkamzik();
  // kotva ze staré adresy (#presnost, #okamzik): obsah se dokreslil až po načtení, posunout znovu
  if (location.hash && !S.posunuto) { S.posunuto = true; document.querySelector(location.hash)?.scrollIntoView(); }
}

// Kterým modelem se povodeň přehrává, aby ji při učení neviděl.
function popisModelu(p) {
  if (p.zdroj === "test") return "Povodeň z testu: model ji poprvé viděl až při jediném finálním ověření.";
  if (p.zdroj === "trenink") return "Přehráváme ji modelem, který se učil bez téhle povodně.";
  return `Povodeň z validace: model učený ${p.ucen || "do roku 2018"} ji při učení neviděl.`;
}

function vychoziCas() {
  // stejné okamžiky jako v prezentaci
  if (S.povoden === "2011-01") return "2011-01-15T09:00";
  if (S.povoden === "2024-09" && S.cil === "decin") return "2024-09-14T11:00";
  const v = povoden().vrchol[S.cil];
  return v ? posun(v.cas, -24) : RADA.cas[Math.floor(RADA.cas.length / 2)];
}

function zapis() {
  zapisStav({ povoden: S.povoden, cil: S.cil === "decin" ? null : S.cil, h: S.h === 24 ? null : S.h, cas: S.cas,
    vrstva: S.vrstva === "mapa" ? null : S.vrstva });
}

// ---------- mapa: náhled s tlačítkem, těžká stránka mapy se načte do iframe až na klik ----------
const cestaMapy = () => S.vrstva === "animace" ? `animace/${S.povoden}.html` : `mapa/${S.povoden}_${S.cil}.html`;

function ukazMapu() {
  zapis();
  const obr = S.vrstva === "animace" ? "animace" : S.cil;
  if (!nahled.getAttribute("src").endsWith(`mapbox3_${obr}.webp`)) {
    nahled.srcset = `img/mapbox3_${obr}_800.webp 800w, img/mapbox3_${obr}.webp 1600w`;
    nahled.src = `img/mapbox3_${obr}.webp`;
  }
  $("#popis-mapy").innerHTML = typo(S.vrstva === "animace"
    ? "Kapky po řekách nesou průtok ze stanic proti proudu, hodinu po hodině."
    : `Rozliv ze změřené hladiny ${KDE[S.cil]} na výškovém modelu terénu, hodinu po hodině.`);
  if (S.bezi) {
    scena.classList.remove("nacteno");
    ramec.addEventListener("load", () => scena.classList.add("nacteno"), { once: true });
    ramec.src = cestaMapy();
  }
}

// Na telefonu je rám pro mapu s vlastním ovládáním malý, mapa se otevře jako celá stránka (zpět vrátí sem).
function spustMapu() {
  if (matchMedia("(max-width: 640px)").matches) { location.assign(cestaMapy()); return; }
  S.bezi = true;
  scena.classList.add("bezi");
  ramec.addEventListener("load", () => scena.classList.add("nacteno"), { once: true });
  ramec.src = cestaMapy();
  ramec.focus({ preventScroll: true });
}

// ---------- přesnost: čtyři čísla, graf celé povodně, tabulka po dnech ----------
function souhrn(zdroj) {
  const s = (MET.souhrn || {})[zdroj];
  if (!s) return null;
  if (s[S.cil] && s[S.cil][S.h]) return s[S.cil][S.h];
  if (s[S.h]) return s[S.h];
  return s.chyba_model != null ? s : null;
}

function varovani(m) {
  if (m.predstih_3_stupen_h != null) {
    return ["Varování před 3. stupněm", `${cislo(m.predstih_3_stupen_h)}<small>h předem</small>`,
      m.predstih_2_stupen_h != null ? `2. stupeň <b>${jedn(m.predstih_2_stupen_h, "h")} předem</b>` : ""];
  }
  const v = m.predstih_2_stupen_h != null ? `${cislo(m.predstih_2_stupen_h)}<small>h předem</small>`
    : `<small>${m.propasnute ? "propásnuto" : "nenastal"}</small>`;
  return ["Varování před 2. stupněm", v, "3. stupeň nenastal"];
}

function ukazPresnost() {
  zapis();
  const p = povoden(), h = S.h, el = $("#presnost-obsah");
  $("#presnost-popis").innerHTML = typo(`Předpověď vydaná ${h} h předem proti tomu, co opravdu přišlo, a proti odhadu, že hladina zůstane stejná.`);
  const m = ((MET[S.povoden] || {})[S.cil] || {})[h];
  const sou = souhrn(p.zdroj);
  let html = "";
  if (m) {
    const mene = m.chyba_jako_ted ? Math.round((1 - m.chyba_model / m.chyba_jako_ted) * 100) : null;
    const [varNazev, varCislo, varVedle] = varovani(m);
    const udaje = [
      ["Průměrná chyba", `${cislo(m.chyba_model, 1)}<small>cm</small>`, `beze změny <b>${cm(m.chyba_jako_ted, 1)}</b>${mene != null ? `, model o&nbsp;${mene}&nbsp;% méně` : ""}`],
      [varNazev, varCislo, varVedle],
      ...(m.vrchol_cm != null ? [["Vrchol povodně", `${cislo(m.vrchol_cm)}<small>cm</small>`, `model nejvýš <b>${m.vrchol_model_cm != null ? cm(m.vrchol_model_cm) : "–"}</b>`]] : []),
      ["Plané poplachy", cislo(m.plane), `propásnuté povodně <b>${cislo(m.propasnute)}</b>`],
    ];
    html += `<dl class="karta udaje">${udaje.map(([dt, dd, vedle]) =>
      `<div><dt>${typo(dt)}</dt><dd class="stredni">${dd}</dd>${vedle ? `<dd class="vedle">${typo(vedle)}</dd>` : ""}</div>`).join("")}</dl>`;
  } else {
    html += hlaska(`Pro ${p.klic}, ${NAZVY[S.cil]} a ${h} h chybí metriky.`, "varovani");
  }
  html += `<section class="karta"><h3>${typo(`Celá povodeň ${KDE[S.cil]}`)}</h3><div class="graf-misto"></div></section>`;
  if (sou) {
    const kde = p.zdroj === "test" ? `Na testu ${sou.roky || ""}` : `Průměr přes ${sou.povodni ? `${sou.povodni} povodně` : "všechny povodně"} z validace`;
    html += `<p class="pozn">${typo(`${kde}: model <b>${cm(sou.chyba_model, 1)}</b>, beze změny <b>${cm(sou.chyba_jako_ted, 1)}</b>.`)}</p>`;
  }
  html += `<details class="karta"><summary>Tabulka po dnech</summary><div class="podrobnosti jeden"><div class="tab-obal">${tabulka()}</div></div></details>`;
  el.innerHTML = html;
  const sk = RADA.skutecnost, pr = RADA.pred[h];
  const model = sk.map((_, j) => (j >= h ? pr[j - h] : null));
  const bezeZmeny = sk.map((_, j) => (j >= h ? sk[j - h] : null));
  const casy = RADA.cas.map(parseIso);
  graf($(".graf-misto", el), {
    vyska: 440, osaY: "hladina (cm)", spa: spa(),
    popis: `Povodeň ${p.klic} ${NAZVY[S.cil]}: skutečná hladina, předpověď modelu a odhad beze změny, ${h} h předem.`,
    serie: [
      { nazev: "skutečnost", x: casy, y: sk, barva: BARVY.text, sirka: 2.6, stitek: true },
      { nazev: "beze změny", x: casy, y: bezeZmeny, barva: BARVY.jakoTed, sirka: 2, car: "6 5", stitek: true },
      { nazev: "model", x: casy, y: model, barva: BARVY.modra, sirka: 2.6, stitek: true },
    ],
  });
}

function tabulka() {
  const h = S.h, sk = RADA.skutecnost, pr = RADA.pred[h];
  const model = sk.map((_, j) => (j >= h ? pr[j - h] : null));
  const bezeZmeny = sk.map((_, j) => (j >= h ? sk[j - h] : null));
  const dny = new Map();
  RADA.cas.forEach((c, j) => dny.set(c.slice(0, 10), [...(dny.get(c.slice(0, 10)) || []), j]));
  const radky = [...dny].map(([d, idx]) => {
    const max = (a) => { const v = idx.map((j) => a[j]).filter((x) => x != null); return v.length ? Math.max(...v) : null; };
    const chyba = (a) => { const v = idx.filter((j) => a[j] != null && sk[j] != null).map((j) => Math.abs(a[j] - sk[j])); return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null; };
    const ms = max(sk);
    return `<tr><th>${denMesic(d + "T00:00")}</th><td>${ms != null ? cislo(ms) : "–"}</td><td>${ms != null ? odznak(spa(), ms, true) : ""}</td><td>${cislo(max(model))}</td><td>${cislo(chyba(model), 1)}</td><td class="tlum jt">${cislo(chyba(bezeZmeny), 1)}</td></tr>`;
  });
  // Sloupec „beze změny“ (třída jt) se na úzké obrazovce skrývá, srovnání zůstává v kartě nahoře.
  return `<table class="tab"><thead><tr><th>Den</th><th>Hladina nejvýš (cm)</th><th>Stupeň</th><th>Model nejvýš (cm)</th><th>Chyba modelu (cm)</th><th class="jt">${typo("Chyba beze změny (cm)")}</th></tr></thead><tbody>${radky.join("")}</tbody></table>`;
}

// ---------- okamžik: co model hlásil v jedné hodině a co pak přišlo ----------
function ukazOkamzik() {
  const i = nejblizsi(RADA.cas, S.cas), el = $("#okamzik-obsah");
  S.cas = RADA.cas[i];
  zapis();
  posuvnik.value = i;
  posuvnik.style.setProperty("--p", `${(i / Math.max(1, RADA.cas.length - 1)) * 100}%`);
  vystup.textContent = typo(datumCas(S.cas));
  const ted = RADA.skutecnost[i];
  const pred = Object.fromEntries(H.map((h) => [h, RADA.pred[h][i]]));
  if (ted == null || H.some((h) => pred[h] == null)) {
    el.innerHTML = hlaska("Pro tuhle hodinu chybí měření nebo vstupy modelu. Posuňte čas o pár hodin.", "varovani");
    return;
  }
  const rozmezi = Object.fromEntries(H.map((h) => [h, RADA.dolni[h][i] != null ? [RADA.dolni[h][i], RADA.horni[h][i]] : null]));
  const skutecne = Object.fromEntries(H.map((h) => [h, RADA.skutecnost[i + h] != null ? `skutečně <b>${cm(RADA.skutecnost[i + h])}</b>` : ""]));
  const v = RADA.vstupy, d = Math.max(0, i - 6);
  el.innerHTML = prehled(spa(), ted, pred, rozmezi, skutecne, veta(v.praha_Q[i], v.praha_Q[d], v.melnik_Q[i], v.melnik_Q[d])) +
    grafSVodoctem("Před a po okamžiku předpovědi");
  oznam(`${NAZVY[S.cil]}, ${datumCas(S.cas)}: teď ${cm(ted)}, za 24 h asi ${cm(pred[24])}.`);
  $(".lat-misto", el).innerHTML = vodocet(spa(), ted, pred, rozmezi, {}, prvni, true);
  prvni = false;
  const od = Math.max(0, i - 72), konec = Math.min(RADA.cas.length - 1, i + 36);
  const predX = [0, ...H].map((h) => parseIso(RADA.cas[i + h] || posun(S.cas, h)));
  graf($(".graf-misto", el), {
    vyska: 470, osaY: "hladina (cm)", spa: spa(), svisla: parseIso(S.cas),
    popis: `Hladina ${NAZVY[S.cil]} 72 hodin před okamžikem předpovědi, předpověď na 12, 24 a 36 hodin a co pak opravdu přišlo.`,
    pas: H.every((h) => rozmezi[h]) ? { x: predX, lo: [ted, ...H.map((h) => rozmezi[h][0])], hi: [ted, ...H.map((h) => rozmezi[h][1])] } : null,
    serie: [
      { nazev: "změřeno", x: RADA.cas.slice(od, i + 1).map(parseIso), y: RADA.skutecnost.slice(od, i + 1), barva: BARVY.text, sirka: 2.4 },
      { nazev: "co pak přišlo", x: RADA.cas.slice(i, konec + 1).map(parseIso), y: RADA.skutecnost.slice(i, konec + 1), barva: BARVY.text3, sirka: 2, stitek: true },
      { nazev: "předpověď", x: predX, y: [ted, ...H.map((h) => pred[h])], barva: BARVY.modra, sirka: 2.4, car: "7 5", body: true, prvniMaly: true, stitek: true },
    ],
  });
}

start();
