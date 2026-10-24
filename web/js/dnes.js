// Stránka Dnes: hladina teď a za 12, 24 a 36 h z živých dat ČHMÚ, graf posledních 72 hodin, vodočet, průtoky a srážky.
import { typo, cislo, cm, parseIso, posun, datumCas } from "./typo.js";
import { DATA, H, KDE, NAZVY, BARVY, nacti, stav, zapisStav } from "./data.js";
import { $, hlaska, segmenty, naZmenu, oznam, hlava } from "./spolecne.js";
import { prehled, veta, grafSVodoctem } from "./karty.js";
import { vodocet } from "./vodocet.js";
import { graf } from "./graf.js";

const S = { cil: stav().get("cil") || "decin" };
let POV, DNES, prvni = true;
const obsah = $("#obsah");
const spa = () => POV.stanice[S.cil].spa;

async function start() {
  try {
    [POV, DNES] = await Promise.all([nacti(DATA + "povodne.json"), nacti(DATA + "dnesek.json")]);
    if (!DNES.ok) {
      if (!(DNES.posledni && DNES.posledni.ok)) throw new Error(DNES.chyba || "dnesek.json bez předpovědi");
      DNES = { ...DNES.posledni, upozorneni: [DNES.chyba, ...(DNES.posledni.upozorneni || [])].filter(Boolean) };
    }
  } catch (e) {
    obsah.innerHTML = hlaska("Živá předpověď teď není k dispozici. Zkuste to za chvíli, mezitím se můžete podívat na povodně z historie.", "varovani") + upoutavka();
    return;
  }
  if (!POV.stanice[S.cil]) S.cil = "decin";
  $("#stanice").innerHTML = segmenty("cil", Object.entries(POV.stanice).map(([k, v]) => ({ hodnota: k, nazev: v.nazev })), S.cil, "Stanice");
  naZmenu($("#stanice"), "cil", (v) => { S.cil = v; prvni = true; ukaz(); });
  ukaz();
}

// Co ČHMÚ nezveřejnil a není dopočtené: ["Mělník (Labe), průtok"] -> "průtok Mělník (Labe)".
function chybejici() {
  const dopocteno = DNES.dopocteno || [];
  const skupiny = new Map();
  for (const c of DNES.chybi || []) {
    if (dopocteno.includes(c)) continue;
    const k = c.lastIndexOf(", ");
    const [stanice, velicina] = k > 0 ? [c.slice(0, k), c.slice(k + 2)] : [c, "hodnota"];
    skupiny.set(velicina, [...(skupiny.get(velicina) || []), stanice]);
  }
  return [...skupiny].map(([v, s]) => `${v} ${s.join(", ")}`).join("; ");
}

function podrobnosti() {
  const POVODI = { vltava: "Vltava", labe: "Horní Labe", ohre: "Ohře" };
  const srazky = (DNES.srazky || {}).povodi;
  const chybi = chybejici();
  const pozn = (DNES.upozorneni || []).filter((u) => !/^(Dopočteno z bilance|ČHMÚ zatím nezveřejnil)/.test(u));
  if (chybi) pozn.push(`ČHMÚ zatím nezveřejnil všechny hodiny, chybí ${chybi}.`);
  if ((DNES.tabulka || []).some((r) => r.dopocteno)) pozn.push("Mělník a Nymburk ČHMÚ průběžně nezveřejňuje, jejich průtok dopočítáváme z okolních stanic.");
  return `<details class="karta"><summary>Průtoky na stanicích a srážky</summary><div class="podrobnosti">
    <div><h3>Průtok teď</h3><div class="tab-obal"><table class="tab"><thead><tr><th>Stanice</th><th>Řeka</th><th>m³/s</th></tr></thead><tbody>
      ${(DNES.tabulka || []).map((r) => `<tr><th>${typo(r.stanice)}${r.dopocteno ? ' <span class="tlum">dopočteno</span>' : ""}</th><td class="tlum">${typo(r.tok || "")}</td><td>${cislo(r.Q)}</td></tr>`).join("")}
    </tbody></table></div></div>
    <div><h3>Srážky v povodí, příštích 48 h</h3>
      ${srazky ? `<div class="srazky">${Object.entries(srazky).map(([k, p]) => `<div><span>${typo(POVODI[k] || p.nazev)}</span><b>${cislo(p.mm_48)}<small>mm</small></b></div>`).join("")}</div>
      <p class="pozn">Předpověď Open-Meteo, do modelu nevstupuje.</p>` : '<p class="pozn">Předpověď srážek teď není k dispozici.</p>'}
      ${pozn.map((u) => `<p class="pozn">${typo(u)}</p>`).join("")}
    </div>
  </div></details>`;
}

// Most na druhou stránku: povodeň 2013 v mapě.
const upoutavka = () => `<a class="karta upoutavka" href="povodne.html?povoden=2013-06">
    <img src="img/mapbox3_decin_800.webp" alt="" width="800" height="450" loading="lazy" decoding="async">
    <div><span class="popisek">Povodně z historie</span><b>${typo("Jak by model varoval v roce 2013")}</b>
    <p>${typo("Šest skutečných povodní v mapě, hodinu po hodině. Model je při učení neviděl, a přesto hlásil 3. stupeň v Děčíně 18 hodin předem.")}</p></div>
  </a>`;

function ukaz() {
  zapisStav({ cil: S.cil === "decin" ? null : S.cil });
  const st = DNES.stanice[S.cil];
  const t = Date.parse(DNES.cas_utc.endsWith("Z") ? DNES.cas_utc : DNES.cas_utc + "Z");
  const stari = Number.isFinite(t) ? (Date.now() - t) / 3600e3 : DNES.stari_h;
  const kdy = DNES.cas ? datumCas(DNES.cas) : DNES.cas_cesky;
  hlava(`Labe ${KDE[S.cil]} dnes`, typo(`Předpověď vydaná ${kdy} z živých dat ČHMÚ`) +
    (stari > 6 ? ` · <span class="stari">${typo(`data jsou ${cislo(stari)} h stará`)}</span>` : ""));
  const pred = Object.fromEntries(H.map((h) => [h, st.pred[h]]));
  const rozmezi = Object.fromEntries(H.map((h) => [h, st.dolni && st.dolni[h] != null ? [st.dolni[h], st.horni[h]] : null]));
  const chmu = st.chmu || {};
  const hist = DNES.historie && DNES.historie.cas && DNES.historie[`${S.cil}_H`] ? DNES.historie : null;
  const tab = (jmeno) => (DNES.tabulka || []).find((r) => r.stanice.startsWith(jmeno));
  const drive = (k) => hist && hist[k] ? hist[k][Math.max(0, hist[k].length - 7)] : null;
  obsah.innerHTML =
    prehled(spa(), st.ted, pred, rozmezi, Object.fromEntries(H.map((h) => [h, chmu[h] != null ? `ČHMÚ <b>${cm(chmu[h])}</b>` : ""])),
      veta(tab("Praha")?.Q, drive("praha_Q"), tab("Mělník")?.Q, drive("melnik_Q"))) +
    grafSVodoctem(hist ? "Posledních 72 hodin a předpověď" : "Předpověď na 36 hodin") + podrobnosti() + upoutavka();
  oznam(`${NAZVY[S.cil]} dnes, předpověď vydaná ${kdy}: teď ${cm(st.ted)}, za 24 h asi ${cm(pred[24])}.`);
  $(".lat-misto", obsah).innerHTML = vodocet(spa(), st.ted, pred, rozmezi, chmu, prvni, true);
  prvni = false;
  const iso = DNES.cas || new Date().toISOString().slice(0, 16);
  const predX = [0, ...H].map((h) => parseIso(posun(iso, h)));
  const hc = H.filter((h) => chmu[h] != null);
  graf($(".graf-misto", obsah), {
    vyska: hist ? 470 : 380, osaY: "hladina (cm)", spa: spa(), svisla: predX[0],
    popis: `Hladina ${NAZVY[S.cil]} za posledních 72 hodin a předpověď na 12, 24 a 36 hodin.`,
    pas: H.every((h) => rozmezi[h]) ? { x: predX, lo: [st.ted, ...H.map((h) => rozmezi[h][0])], hi: [st.ted, ...H.map((h) => rozmezi[h][1])] } : null,
    serie: [
      ...(hist ? [{ nazev: "změřeno", x: hist.cas.map(parseIso), y: hist[`${S.cil}_H`], barva: BARVY.text, sirka: 2.4 }] : []),
      { nazev: "předpověď", x: predX, y: [st.ted, ...H.map((h) => pred[h])], barva: BARVY.modra, sirka: 2.4, car: "7 5", body: true, prvniMaly: true, stitek: true },
      ...(hc.length ? [{ nazev: "ČHMÚ", x: hc.map((h) => parseIso(posun(iso, h))), y: hc.map((h) => chmu[h]), barva: BARVY.text, jenBody: true, trojuhelnik: true, stitek: true }] : []),
    ],
  });
}

start();
