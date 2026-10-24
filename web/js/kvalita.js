// Stránka Přesnost: chyba a předstih varování při povodni proti odhadu beze změny, graf celé povodně a tabulka po dnech.
import { typo, cislo, cm, jedn, parseIso, datum, denMesic } from "./typo.js";
import { DATA, H, NAZVY, BARVY, nacti, stav, zapisStav, odznak } from "./data.js";
import { $, hlaska, dlazdice, segmenty, naZmenu, oznam, hlava } from "./spolecne.js";
import { graf } from "./graf.js";

const q = stav();
const S = { povoden: q.get("povoden") || "2011-01", cil: q.get("cil") || "decin", h: +q.get("h") || 24 };
let POV, MET, RADA;
const obsah = $("#obsah");

const povoden = () => POV.povodne.find((p) => p.slug === S.povoden) || POV.povodne[0];
const spa = () => POV.stanice[S.cil].spa;

async function start() {
  try {
    [POV, MET] = await Promise.all([nacti(DATA + "povodne.json"), nacti(DATA + "metriky.json")]);
  } catch (e) {
    obsah.innerHTML = hlaska("Data se nepodařilo načíst. Zkuste stránku obnovit.", "varovani");
    return;
  }
  if (!POV.povodne.some((p) => p.slug === S.povoden)) S.povoden = POV.povodne[0].slug;
  if (!POV.stanice[S.cil]) S.cil = "decin";
  if (!H.includes(S.h)) S.h = 24;
  $("#povodne").innerHTML = dlazdice("povoden", POV.povodne.map((p) => ({ hodnota: p.slug, nazev: p.klic })), S.povoden, "Povodeň");
  $("#stanice").innerHTML = segmenty("cil", Object.entries(POV.stanice).map(([k, v]) => ({ hodnota: k, nazev: v.nazev })), S.cil, "Stanice");
  $("#horizont").innerHTML = segmenty("h", H.map((h) => ({ hodnota: String(h), nazev: `${h} h` })), String(S.h), "Předpověď vydaná kolik hodin předem");
  const strana = $(".strana");
  naZmenu(strana, "povoden", (v) => { S.povoden = v; ukaz(); });
  naZmenu(strana, "cil", (v) => { S.cil = v; ukaz(); });
  naZmenu(strana, "h", (v) => { S.h = +v; ukaz(); });
  ukaz();
}

// Souhrn je buď po stanicích a horizontech, nebo jedno číslo za celou část (validace / test).
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

async function ukaz() {
  zapisStav({ povoden: S.povoden, cil: S.cil, h: S.h });
  const p = povoden(), h = S.h;
  hlava("Jak přesná je předpověď", typo(`Předpověď vydaná ${h} h předem proti tomu, co opravdu přišlo, a proti odhadu, že hladina zůstane stejná.`));
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
  html += `<section class="karta"><h2>${typo(`${p.nazev} · ${NAZVY[S.cil]}`)}</h2><div id="graf"></div></section>`;
  if (sou) {
    const kde = p.zdroj === "test" ? `Na testu ${sou.roky || ""}` : `Průměr přes ${sou.povodni ? `${sou.povodni} povodně` : "všechny povodně"} z validace`;
    html += `<p class="pozn">${typo(`${kde}: model <b>${cm(sou.chyba_model, 1)}</b>, beze změny <b>${cm(sou.chyba_jako_ted, 1)}</b>.`)}</p>`;
  }
  html += `<details class="karta"><summary>Po dnech</summary><div class="podrobnosti" style="grid-template-columns:1fr"><div class="tab-obal" id="tabulka"></div></div></details>`;
  obsah.innerHTML = html;
  oznam(m ? `${p.nazev} ${NAZVY[S.cil]}, ${h} h předem: chyba modelu ${cm(m.chyba_model, 1)}, beze změny ${cm(m.chyba_jako_ted, 1)}.`
    : `${p.nazev} ${NAZVY[S.cil]}, ${h} h předem: metriky chybí.`);
  try {
    RADA = await nacti(`${DATA}rada_${S.povoden}_${S.cil}.json`);
  } catch (e) {
    $("#graf").innerHTML = hlaska("Průběh povodně se nepodařilo načíst.", "varovani");
    return;
  }
  const n = RADA.cas.length, sk = RADA.skutecnost, pr = RADA.pred[h];
  const model = sk.map((_, j) => (j >= h ? pr[j - h] : null));
  const bezeZmeny = sk.map((_, j) => (j >= h ? sk[j - h] : null));
  const casy = RADA.cas.map(parseIso);
  graf($("#graf"), {
    vyska: 440, osaY: "hladina (cm)", spa: spa(),
    popis: `Povodeň ${p.klic} ${NAZVY[S.cil]}: skutečná hladina, předpověď modelu a odhad beze změny, ${h} h předem.`,
    serie: [
      { nazev: "skutečnost", x: casy, y: sk, barva: BARVY.text, sirka: 2.6, stitek: true },
      { nazev: "beze změny", x: casy, y: bezeZmeny, barva: BARVY.jakoTed, sirka: 2, car: "6 5", stitek: true },
      { nazev: "model", x: casy, y: model, barva: BARVY.modra, sirka: 2.6, stitek: true },
    ],
  });
  const dny = new Map();
  for (let j = 0; j < n; j++) {
    const d = RADA.cas[j].slice(0, 10);
    if (!dny.has(d)) dny.set(d, []);
    dny.get(d).push(j);
  }
  const radky = [...dny].map(([d, idx]) => {
    const max = (a) => { const v = idx.map((j) => a[j]).filter((x) => x != null); return v.length ? Math.max(...v) : null; };
    const chyba = (a) => { const v = idx.filter((j) => a[j] != null && sk[j] != null).map((j) => Math.abs(a[j] - sk[j])); return v.length ? v.reduce((s, x) => s + x, 0) / v.length : null; };
    const ms = max(sk);
    return `<tr><th>${denMesic(d + "T00:00")}</th><td>${ms != null ? cislo(ms) : "–"}</td><td>${ms != null ? odznak(spa(), ms, true) : ""}</td><td>${cislo(max(model))}</td><td>${cislo(chyba(model), 1)}</td><td class="tlum jt">${cislo(chyba(bezeZmeny), 1)}</td></tr>`;
  });
  // Sloupec „beze změny“ (třída jt) se na úzké obrazovce skrývá, srovnání zůstává v kartě nahoře.
  $("#tabulka").innerHTML = `<table class="tab"><thead><tr><th>Den</th><th>Hladina nejvýš (cm)</th><th>Stupeň</th><th>Model nejvýš (cm)</th><th>Chyba modelu (cm)</th><th class="jt">${typo("Chyba beze změny (cm)")}</th></tr></thead><tbody>${radky.join("")}</tbody></table>`;
}

start();
