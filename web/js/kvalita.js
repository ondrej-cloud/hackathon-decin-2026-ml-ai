// Stránka Jak dobře to funguje: souhrn chyby a předstihu proti „bude jako teď“, graf celé povodně a tabulka po dnech.
import { typo, cislo, cm, jedn, NB, parseIso, datum, denMesic } from "./typo.js";
import { DATA, H, NAZVY, BARVY, nacti, stav, zapisStav, stupen, odznak } from "./data.js";
import { $, tiraz, hlaska, stitek, dlazdice, segmenty, naZmenu, oznam, posuvnaTabulka } from "./spolecne.js";
import { graf } from "./graf.js";

const q = stav();
const S = { povoden: q.get("povoden") || "2011-01", cil: q.get("cil") || "decin", h: +q.get("h") || 24 };
let POV, MET, RADA;
const volby = $("#volby"), hlavni = $("#hlavni");

const povoden = () => POV.povodne.find((p) => p.slug === S.povoden) || POV.povodne[0];
const spa = () => POV.stanice[S.cil].spa;

async function start() {
  try {
    [POV, MET] = await Promise.all([nacti(DATA + "povodne.json"), nacti(DATA + "metriky.json")]);
  } catch (e) {
    hlavni.innerHTML = hlaska("Data se nepodařilo načíst (data/povodne.json, data/metriky.json). Vyrábí je skript src/export_web.py.", "varovani");
    return;
  }
  if (!POV.povodne.some((p) => p.slug === S.povoden)) S.povoden = POV.povodne[0].slug;
  if (!POV.stanice[S.cil]) S.cil = "decin";
  if (!H.includes(S.h)) S.h = 24;
  volby.innerHTML = `
    <div><span class="popisek">Povodeň</span>${dlazdice("povoden", POV.povodne.map((p) => ({ hodnota: p.slug, nazev: p.klic, popis: p.nazev + (p.zdroj === "test" ? ", test" : "") })), S.povoden, "radek", "Povodeň")}</div>
    <div><span class="popisek">Stanice</span>${segmenty("cil", Object.entries(POV.stanice).map(([k, v]) => ({ hodnota: k, nazev: v.nazev })), S.cil, "Stanice")}</div>
    <div><span class="popisek">${typo("Předpověď vydaná … hodin předem")}</span>${segmenty("h", H.map((h) => ({ hodnota: String(h), nazev: String(h) })), String(S.h), "Předpověď vydaná kolik hodin předem")}</div>`;
  naZmenu(volby, "povoden", (v) => { S.povoden = v; ukaz(); });
  naZmenu(volby, "cil", (v) => { S.cil = v; ukaz(); });
  naZmenu(volby, "h", (v) => { S.h = +v; ukaz(); });
  ukaz();
}

// Souhrn je buď po stanicích a horizontech, nebo jedno číslo za celou část (validace / test).
function souhrn(zdroj) {
  const s = (MET.souhrn || {})[zdroj];
  if (!s) return null;
  if (s[S.cil] && s[S.cil][S.h]) return { ...s[S.cil][S.h], presne: true };
  if (s[S.h]) return { ...s[S.h], presne: true };
  if (s.chyba_model != null) return { ...s, presne: false };
  return null;
}

async function ukaz() {
  zapisStav({ povoden: S.povoden, cil: S.cil, h: S.h });
  const p = povoden(), h = S.h;
  tiraz({ okamzik: `${datum(p.od)} až ${datum(p.do)}` });
  const m = ((MET[S.povoden] || {})[S.cil] || {})[h];
  const sou = souhrn(p.zdroj);
  let html = `<h2 class="nadpis">${typo(`${p.nazev} · ${NAZVY[S.cil]} · ${h} h předem`)}</h2>`;
  if (m) {
    const mene = m.chyba_jako_ted ? (1 - m.chyba_model / m.chyba_jako_ted) * 100 : null;
    html += `<section class="pas">
      <dl class="udaje">
        <div><dt>Chyba při povodni</dt><dd>${cislo(m.chyba_model, 1)}<small>cm</small></dd><dd class="vedle">${typo(`bude jako teď <b>${cm(m.chyba_jako_ted, 1)}</b>${mene != null ? `, o ${cislo(mene)} % méně` : ""}`)}</dd></div>
        <div><dt>${typo("Varování před 2. stupněm")}</dt><dd>${m.predstih_2_stupen_h != null ? `${cislo(m.predstih_2_stupen_h)}<small>h předem</small>` : `<small>${m.propasnute ? "propásnuto" : "2. stupeň nenastal"}</small>`}</dd><dd class="vedle">${typo(m.predstih_3_stupen_h != null ? `3. stupeň <b>${jedn(m.predstih_3_stupen_h, "h")} předem</b>` : "3. stupeň nenastal")}</dd></div>
        <div><dt>Propásnuté povodně</dt><dd>${cislo(m.propasnute)}</dd><dd class="vedle">${typo("model 2. stupeň vůbec nehlásil")}</dd></div>
        <div><dt>Plané poplachy</dt><dd>${cislo(m.plane)}</dd><dd class="vedle">${typo("model hlásil 2. stupeň, voda nepřišla")}</dd></div>
        ${m.vrchol_cm != null ? `<div><dt>Vrchol povodně</dt><dd>${cislo(m.vrchol_cm)}<small>cm</small></dd><dd class="vedle">${typo(`model nejvýš <b>${m.vrchol_model_cm != null ? cm(m.vrchol_model_cm) : "–"}</b>`)}</dd></div>` : ""}
      </dl></section>`;
  } else {
    html += hlaska(`Pro ${p.klic}, ${NAZVY[S.cil]} a ${h} h chybí metriky (data/metriky.json).`, "varovani");
  }
  if (sou) {
    const mene = sou.chyba_jako_ted ? (1 - sou.chyba_model / sou.chyba_jako_ted) * 100 : null;
    const kolik = sou.povodni ? `${sou.povodni} povodně` : "všechny povodně";
    html += `<p class="pozn">${typo(`Průměr přes ${kolik}: model <b>${cm(sou.chyba_model, 1)}</b>, bude jako teď <b>${cm(sou.chyba_jako_ted, 1)}</b>${mene != null ? `, o ${cislo(mene)} % méně` : ""}.`)}</p>`;
  }
  html += `<section class="karta">${stitek(`Celá povodeň ${p.klic}`, NAZVY[S.cil])}<div id="graf"></div></section>
    <section class="karta">${stitek("Po dnech", `${NAZVY[S.cil]}, ${h} h předem`)}<div class="tab-obal" id="tabulka"></div></section>`;
  hlavni.innerHTML = html;
  oznam(m ? `${p.nazev} ${NAZVY[S.cil]}, ${h} h předem: chyba modelu ${cm(m.chyba_model, 1)}, bude jako teď ${cm(m.chyba_jako_ted, 1)}.`
    : `${p.nazev} ${NAZVY[S.cil]}, ${h} h předem: metriky chybí.`);
  try {
    RADA = await nacti(`${DATA}rada_${S.povoden}_${S.cil}.json`);
  } catch (e) {
    $("#graf").innerHTML = hlaska(`Chybí řada (data/rada_${S.povoden}_${S.cil}.json).`, "varovani");
    return;
  }
  const n = RADA.cas.length, sk = RADA.skutecnost, pr = RADA.pred[h];
  const model = sk.map((_, j) => (j >= h ? pr[j - h] : null));
  const jakoTed = sk.map((_, j) => (j >= h ? sk[j - h] : null));
  const casy = RADA.cas.map(parseIso);
  graf($("#graf"), {
    vyska: 440, osaY: "hladina (cm)", spa: spa(),
    popis: `Povodeň ${p.klic} ${NAZVY[S.cil]}: skutečná hladina, předpověď modelu a bude jako teď, ${h} h předem.`,
    serie: [
      { nazev: "skutečnost", x: casy, y: sk, barva: BARVY.text, sirka: 2.6, stitek: true },
      { nazev: "bude jako teď", x: casy, y: jakoTed, barva: BARVY.jakoTed, sirka: 2, car: "6 5", stitek: true },
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
    return `<tr><th>${denMesic(d + "T00:00")}</th><td>${ms != null ? cislo(ms) : "–"}</td><td>${ms != null ? odznak(spa(), ms, true) : ""}</td><td>${cislo(max(model))}</td><td class="tlum jt">${cislo(max(jakoTed))}</td><td>${cislo(chyba(model), 1)}</td><td class="tlum jt">${cislo(chyba(jakoTed), 1)}</td></tr>`;
  });
  // Sloupce „bude jako teď“ (třída jt) se na úzké obrazovce skrývají, srovnání zůstává v souhrnu nahoře.
  $("#tabulka").innerHTML = `<table class="tab"><thead><tr><th style="text-align:left">Den</th><th>Hladina nejvýš (cm)</th><th>Stupeň</th><th>Model nejvýš (cm)</th><th class="jt">${typo("Bude jako teď nejvýš (cm)")}</th><th>Chyba modelu (cm)</th><th class="jt">${typo("Chyba bude jako teď (cm)")}</th></tr></thead><tbody>${radky.join("")}</tbody></table>`;
  posuvnaTabulka($("#tabulka"));
}

start();
