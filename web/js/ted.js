// Stránka Předpověď: hladina teď a za 12, 24 a 36 h, graf a vodočet. Dnes z živých dat ČHMÚ, nebo přehrání povodně z historie.
import { typo, cislo, cm, jedn, znamenko, parseIso, posun, datumCas } from "./typo.js";
import { DATA, H, KDE, NAZVY, BARVY, nacti, stav, zapisStav, stupen, odznak, trend, nejblizsi } from "./data.js";
import { $, hlaska, dlazdice, segmenty, naZmenu, oznam, hlava } from "./spolecne.js";
import { vodocet } from "./vodocet.js";
import { graf } from "./graf.js";

const q = stav();
// Bez povodně a času v adrese se otevře Dnes; odkazy s ?povoden=… vedou do historie.
const S = { povoden: q.get("povoden") || "2011-01", cil: q.get("cil") || "decin", cas: q.get("cas"),
  dnesek: q.get("dnesek") === "1" || (q.get("dnesek") !== "0" && !q.has("povoden") && !q.has("cas")) };
let POV, RADA, DNES, ZPRAVA = "", prvni = true;
const obsah = $("#obsah"), posuvnik = $("#cas"), vystup = $("#cas-out");

const povoden = () => POV.povodne.find((p) => p.slug === S.povoden) || POV.povodne[0];
const spa = () => POV.stanice[S.cil].spa;

function vychoziCas() {
  // stejné okamžiky jako v prezentaci
  if (S.povoden === "2011-01") return "2011-01-15T09:00";
  if (S.povoden === "2024-09" && S.cil === "decin") return "2024-09-14T11:00";
  const v = povoden().vrchol[S.cil];
  return v ? posun(v.cas, -24) : RADA.cas[Math.floor(RADA.cas.length / 2)];
}

async function start() {
  try {
    POV = await nacti(DATA + "povodne.json");
  } catch (e) {
    obsah.innerHTML = hlaska("Data se nepodařilo načíst. Zkuste stránku obnovit.", "varovani");
    return;
  }
  if (!POV.stanice[S.cil]) S.cil = "decin";
  if (!POV.povodne.some((p) => p.slug === S.povoden)) S.povoden = POV.povodne[0].slug;
  $("#rezim").innerHTML = segmenty("rezim", [{ hodnota: "dnes", nazev: "Dnes" }, { hodnota: "historie", nazev: "Povodně z historie" }],
    S.dnesek ? "dnes" : "historie", "Co ukázat");
  $("#stanice").innerHTML = segmenty("cil", Object.entries(POV.stanice).map(([k, v]) => ({ hodnota: k, nazev: v.nazev })), S.cil, "Stanice");
  $("#povodne").innerHTML = dlazdice("povoden", POV.povodne.map((p) => ({ hodnota: p.slug, nazev: p.klic })), S.povoden, "Povodeň");
  const strana = $(".strana");
  naZmenu(strana, "rezim", (v) => { S.dnesek = v === "dnes"; ZPRAVA = ""; prvni = true; nactiAUkaz(); });
  naZmenu(strana, "cil", (v) => { S.cil = v; prvni = true; nactiAUkaz(); });
  naZmenu(strana, "povoden", (v) => { S.povoden = v; S.cas = null; prvni = true; nactiAUkaz(); });
  posuvnik.addEventListener("input", () => { S.cas = RADA.cas[+posuvnik.value]; ukaz(); });
  nactiAUkaz();
}

async function nactiAUkaz() {
  $("#historie").hidden = S.dnesek;
  obsah.setAttribute("aria-busy", "true");
  try {
    if (S.dnesek) {
      DNES = await nacti(DATA + "dnesek.json");
      if (!DNES.ok) {
        if (!(DNES.posledni && DNES.posledni.ok)) throw new Error(DNES.chyba || "dnesek.json bez předpovědi");
        DNES = { ...DNES.posledni, upozorneni: [DNES.chyba, ...(DNES.posledni.upozorneni || [])].filter(Boolean) };
      }
    } else {
      RADA = await nacti(`${DATA}rada_${S.povoden}_${S.cil}.json`);
      if (!S.cas) S.cas = vychoziCas();
      posuvnik.max = RADA.cas.length - 1;
    }
  } catch (e) {
    obsah.removeAttribute("aria-busy");
    if (S.dnesek) {
      S.dnesek = false;
      $('input[name="rezim"][value="historie"]').checked = true;
      ZPRAVA = "Živá předpověď teď není k dispozici, ukazuje se povodeň z historie.";
      return nactiAUkaz();
    }
    obsah.innerHTML = hlaska("Data pro tuhle povodeň se nepodařilo načíst.", "varovani");
    return;
  }
  obsah.removeAttribute("aria-busy");
  ukaz();
}

function ukaz() {
  if (S.dnesek) ukazDnes(); else ukazHistorii();
  prvni = false;
}

// Karta nahoře: teď vlevo, 12, 24 a 36 h vpravo; pod každou předpovědí rozmezí a srovnání (ČHMÚ, nebo co opravdu přišlo).
function prehled(ted, pred, rozmezi, srovnani, veta) {
  const sloupce = H.map((h) => {
    const d = pred[h] - ted;
    const smer = d >= 5 ? " roste" : d <= -5 ? " klesa" : "";
    const pod = [rozmezi[h] ? `nejspíš ${cislo(rozmezi[h][0])}–${cm(rozmezi[h][1])}` : "", srovnani[h] || ""].filter(Boolean);
    return `<div><span class="popisek">Za ${h} h</span><span class="stredni">${cislo(pred[h])}<small>cm</small></span>` +
      `<span class="zmena${smer}">${znamenko(d)} cm</span>${stupen(spa(), pred[h]) ? odznak(spa(), pred[h], true) : ""}` +
      pod.map((r) => `<span class="drobne">${typo(r)}</span>`).join("") + "</div>";
  });
  return `<section class="karta prehled" aria-label="Hladina teď a předpověď">
    <div><span class="popisek">Teď</span><span class="velke">${cislo(ted)}<small>cm</small></span>${odznak(spa(), ted)}</div>
    <div class="prehled-pred">${sloupce.join("")}</div>
    ${veta ? `<p class="prehled-veta">${typo(veta)}</p>` : ""}
  </section>`;
}

// Proč to tak vyšlo: co teče Prahou a Mělníkem a jestli to stoupá.
function veta(praha, prahaDrive, melnik, melnikDrive) {
  const kus = (kde, q, drive) => q == null ? "" : `${kde} ${jedn(q, "m³/s")}${trend(q, drive) ? " a " + trend(q, drive) : ""}`;
  const casti = [kus("Vltava v Praze teče", praha, prahaDrive), kus("Labe v Mělníku", melnik, melnikDrive)].filter(Boolean);
  return casti.length ? `${casti.join(", ")}. Tahle voda doteče do Ústí a Děčína zhruba za půl dne až den.` : "";
}

const mrizka = (nazevGrafu) => `<div class="mrizka">
    <section class="karta"><h2>${typo(nazevGrafu)}</h2><div id="graf"></div></section>
    <section class="karta"><h2>Vodočet</h2><div id="lat"></div></section>
  </div>`;

function ukazHistorii() {
  const i = nejblizsi(RADA.cas, S.cas);
  S.cas = RADA.cas[i];
  zapisStav({ povoden: S.povoden, cil: S.cil, cas: S.cas, dnesek: null });
  posuvnik.value = i;
  posuvnik.style.setProperty("--p", `${(i / Math.max(1, RADA.cas.length - 1)) * 100}%`);
  vystup.textContent = typo(datumCas(S.cas));
  const p = povoden();
  hlava(`Hladina Labe ${KDE[S.cil]}`, typo(`${p.nazev} · předpověď vydaná ${datumCas(S.cas)}`));
  const ted = RADA.skutecnost[i];
  const pred = Object.fromEntries(H.map((h) => [h, RADA.pred[h][i]]));
  if (ted == null || H.some((h) => pred[h] == null)) {
    obsah.innerHTML = (ZPRAVA ? hlaska(ZPRAVA, "varovani") : "") +
      hlaska("Pro tuhle hodinu chybí měření nebo vstupy modelu. Posuňte čas o pár hodin.", "varovani");
    return;
  }
  const rozmezi = Object.fromEntries(H.map((h) => [h, RADA.dolni[h][i] != null ? [RADA.dolni[h][i], RADA.horni[h][i]] : null]));
  const skutecne = Object.fromEntries(H.map((h) => [h, RADA.skutecnost[i + h] != null ? `skutečně <b>${cm(RADA.skutecnost[i + h])}</b>` : ""]));
  const v = RADA.vstupy, d = Math.max(0, i - 6);
  obsah.innerHTML = (ZPRAVA ? hlaska(ZPRAVA, "varovani") : "") +
    prehled(ted, pred, rozmezi, skutecne, veta(v.praha_Q[i], v.praha_Q[d], v.melnik_Q[i], v.melnik_Q[d])) +
    mrizka("Před a po okamžiku předpovědi");
  oznam(`${NAZVY[S.cil]}, ${datumCas(S.cas)}: teď ${cm(ted)}, za 24 h asi ${cm(pred[24])}.`);
  $("#lat").innerHTML = vodocet(spa(), ted, pred, rozmezi, {}, prvni, true);
  const od = Math.max(0, i - 72), konec = Math.min(RADA.cas.length - 1, i + 36);
  const predX = [0, ...H].map((h) => parseIso(RADA.cas[i + h] || posun(S.cas, h)));
  graf($("#graf"), {
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

function ukazDnes() {
  zapisStav({ povoden: null, cas: null, cil: S.cil, dnesek: null });
  const st = DNES.stanice[S.cil];
  const t = Date.parse(DNES.cas_utc.endsWith("Z") ? DNES.cas_utc : DNES.cas_utc + "Z");
  const stari = Number.isFinite(t) ? (Date.now() - t) / 3600e3 : DNES.stari_h;
  const kdy = DNES.cas ? datumCas(DNES.cas) : DNES.cas_cesky;
  hlava(`Hladina Labe ${KDE[S.cil]}`, typo(`Předpověď vydaná ${kdy} z živých dat ČHMÚ`) +
    (stari > 6 ? ` · <span class="stari">${typo(`data jsou ${cislo(stari)} h stará`)}</span>` : ""));
  const pred = Object.fromEntries(H.map((h) => [h, st.pred[h]]));
  const rozmezi = Object.fromEntries(H.map((h) => [h, st.dolni && st.dolni[h] != null ? [st.dolni[h], st.horni[h]] : null]));
  const chmu = st.chmu || {};
  const hist = DNES.historie && DNES.historie.cas && DNES.historie[`${S.cil}_H`] ? DNES.historie : null;
  const tab = (jmeno) => (DNES.tabulka || []).find((r) => r.stanice.startsWith(jmeno));
  const drive = (k) => hist && hist[k] ? hist[k][Math.max(0, hist[k].length - 7)] : null;
  obsah.innerHTML = (ZPRAVA ? hlaska(ZPRAVA, "varovani") : "") +
    prehled(st.ted, pred, rozmezi, Object.fromEntries(H.map((h) => [h, chmu[h] != null ? `ČHMÚ <b>${cm(chmu[h])}</b>` : ""])),
      veta(tab("Praha")?.Q, drive("praha_Q"), tab("Mělník")?.Q, drive("melnik_Q"))) +
    mrizka(hist ? "Posledních 72 hodin a předpověď" : "Předpověď na 36 hodin") + podrobnosti();
  oznam(`${NAZVY[S.cil]} dnes, předpověď vydaná ${kdy}: teď ${cm(st.ted)}, za 24 h asi ${cm(pred[24])}.`);
  $("#lat").innerHTML = vodocet(spa(), st.ted, pred, rozmezi, chmu, prvni, true);
  const iso = DNES.cas || new Date().toISOString().slice(0, 16);
  const predX = [0, ...H].map((h) => parseIso(posun(iso, h)));
  const hc = H.filter((h) => chmu[h] != null);
  graf($("#graf"), {
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
