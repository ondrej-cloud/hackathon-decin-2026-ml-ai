// Stránka Teď: vodočet, odečty, věta pro laika a graf 72 h kolem zvoleného okamžiku; přepínač Dnešek.
import { typo, cislo, cm, jedn, znamenko, NB, parseIso, posun, datumCas, hodina } from "./typo.js";
import { DATA, H, KDE, NAZVY, STUPNE, BARVY, nacti, stav, zapisStav, stupen, odznak, trend, nejblizsi } from "./data.js";
import { $, tiraz, hlaska, stitek, dlazdice, naZmenu, oznam, posuvnaTabulka } from "./spolecne.js";
import { vodocet } from "./vodocet.js";
import { graf } from "./graf.js";

const q = stav();
// Bez povodně a času v adrese se otevře Dnešek; odkazy s ?povoden=… vedou do historie.
const S = { povoden: q.get("povoden") || "2011-01", cil: q.get("cil") || "decin", cas: q.get("cas"),
  dnesek: q.get("dnesek") === "1" || (q.get("dnesek") !== "0" && !q.has("povoden") && !q.has("cas")) };
let POV, RADA, DNES, ZPRAVA = "", i = 0, prvni = true;
const hlavni = $("#hlavni"), panel = $("#panel");
const kompakt = () => matchMedia("(max-width: 640px)").matches;
const K_PANELU = `<a class="k-panelu" href="#panel">${typo("Změnit stanici, povodeň, čas nebo zapnout Dnešek")}</a>`;

function povoden() {
  return POV.povodne.find((p) => p.slug === S.povoden) || POV.povodne[0];
}
const spa = () => POV.stanice[S.cil].spa;

function vychoziCas() {
  if (S.povoden === "2011-01") return "2011-01-15T09:00";
  const v = povoden().vrchol[S.cil];
  return v ? posun(v.cas, -24) : RADA.cas[Math.floor(RADA.cas.length / 2)];
}

async function start() {
  try {
    POV = await nacti(DATA + "povodne.json");
  } catch (e) {
    hlavni.innerHTML = hlaska("Data se nepodařilo načíst (data/povodne.json). Vyrábí je skript src/export_web.py.", "varovani");
    return;
  }
  if (!POV.stanice[S.cil]) S.cil = "decin";
  if (!POV.povodne.some((p) => p.slug === S.povoden)) S.povoden = POV.povodne[0].slug;
  if (!$("#stanice input")) $("#stanice").innerHTML = dlazdice("cil", Object.entries(POV.stanice).map(([k, v]) =>
    ({ hodnota: k, nazev: v.nazev, popis: `stupně ${v.spa.join(" / ")} cm` })), S.cil, "", "Stanice");
  if (!$("#povodne input")) $("#povodne").innerHTML = dlazdice("povoden", POV.povodne.map((p) =>
    ({ hodnota: p.slug, nazev: p.klic, popis: p.nazev + (p.zdroj === "test" ? ", test" : "") })), S.povoden, "", "Povodeň");
  for (const [jmeno, hodnota] of [["cil", S.cil], ["povoden", S.povoden]]) {
    const el = panel.querySelector(`input[name="${jmeno}"][value="${hodnota}"]`);
    if (el) el.checked = true;
  }
  $("#dnesek").checked = S.dnesek;
  // 6: vodočet má na telefonu kompaktní kresbu; při změně šířky se překreslí
  matchMedia("(max-width: 640px)").addEventListener("change", () => { if (RADA || DNES) ukaz(); });
  naZmenu(panel, "cil", (v) => { S.cil = v; prvni = true; nactiAUkaz(); });
  naZmenu(panel, "povoden", (v) => { S.povoden = v; S.cas = null; prvni = true; nactiAUkaz(); });
  $("#dnesek").addEventListener("change", (e) => { S.dnesek = e.target.checked; ZPRAVA = ""; prvni = true; nactiAUkaz(); });
  $("#den").addEventListener("change", zCasu);
  $("#hodina").addEventListener("input", zCasu);
  nactiAUkaz();
}

function zCasu() {
  const den = $("#den").value, h = +$("#hodina").value;
  if (!den) return;
  $("#hodina-out").textContent = `${h}:00`;
  $("#hodina").style.setProperty("--p", `${(h / 23) * 100}%`);
  S.cas = `${den}T${String(h).padStart(2, "0")}:00`;
  ukaz();
}

async function nactiAUkaz() {
  $("#cas-pole").disabled = S.dnesek;
  $("#povodne-pole").disabled = S.dnesek;
  hlavni.setAttribute("aria-busy", "true");
  try {
    if (S.dnesek) {
      DNES = await nacti(DATA + "dnesek.json");
      if (!DNES.ok) {
        if (!(DNES.posledni && DNES.posledni.ok)) throw new Error(DNES.chyba || "dnesek.json bez předpovědi");
        DNES = { ...DNES.posledni, upozorneni: [DNES.chyba, ...(DNES.posledni.upozorneni || [])].filter(Boolean) };
      }
      if (DNES.cas) {
        $("#den").removeAttribute("min"); $("#den").removeAttribute("max");
        $("#den").value = DNES.cas.slice(0, 10);
        const h = parseIso(DNES.cas).getUTCHours();
        $("#hodina").value = h;
        $("#hodina-out").textContent = `${h}:00`;
        $("#hodina").style.setProperty("--p", `${(h / 23) * 100}%`);
      }
    } else {
      RADA = await nacti(`${DATA}rada_${S.povoden}_${S.cil}.json`);
      if (!S.cas) S.cas = vychoziCas();
      i = nejblizsi(RADA.cas, S.cas);
      S.cas = RADA.cas[i];
      $("#den").min = RADA.cas[0].slice(0, 10);
      $("#den").max = RADA.cas[RADA.cas.length - 1].slice(0, 10);
      $("#den").value = S.cas.slice(0, 10);
      const h = parseIso(S.cas).getUTCHours();
      $("#hodina").value = h;
      $("#hodina-out").textContent = `${h}:00`;
      $("#hodina").style.setProperty("--p", `${(h / 23) * 100}%`);
    }
  } catch (e) {
    if (S.dnesek) {
      S.dnesek = false;
      $("#dnesek").checked = false;
      ZPRAVA = "Živá předpověď teď není k dispozici, ukazuje se přehrávání historie. Zkuste to za chvíli znovu přepínačem Dnešek.";
      return nactiAUkaz();
    }
    hlavni.innerHTML = hlaska(`Chybí data pro tuhle povodeň (data/rada_${S.povoden}_${S.cil}.json).`, "varovani");
    tiraz({ okamzik: "–", model: "ridge", zdroj: "archiv ČHMÚ 2006–2025" });
    hlavni.removeAttribute("aria-busy");
    return;
  }
  hlavni.removeAttribute("aria-busy");
  ukaz();
}

// Pro uživatele je model vždycky „ridge“ a liší se jen tím, do kterého roku se učil; klíče ridge_vse a ridge_test
// zůstávají jen v názvech souborů s daty.
const MODEL_DNES = "ridge, do 2025";
const rokUceni = (p) => (p.ucen || "2006–2020").slice(-4);
const popisModelu = (p) => (p.model && p.model !== "ridge" ? `ridge, do ${rokUceni(p)}` : "ridge");

function ukaz() {
  const pv = povoden();
  $("#model-popis").innerHTML = `<b>ridge</b>` + typo(S.dnesek
    ? "Lineární regrese (ridge), 98 vstupů, učená na všem do roku 2025. Hodí se na dnešek."
    : pv.zdroj === "test"
      ? `Lineární regrese (ridge), 98 vstupů, učená na všem do roku ${rokUceni(pv)}, stejná jako při finálním testu. Tuhle povodeň nikdy neviděla.`
      : "Lineární regrese (ridge), 98 vstupů, učená na letech 2006–2018. Hodí se na přehrávání historie.");
  if (S.dnesek) ukazDnesek(); else ukazHistorii();
}

function ukazHistorii() {
  i = nejblizsi(RADA.cas, S.cas);
  S.cas = RADA.cas[i];
  zapisStav({ povoden: S.povoden, cil: S.cil, cas: S.cas, dnesek: null });
  const ted = RADA.skutecnost[i];
  const pred = Object.fromEntries(H.map((h) => [h, RADA.pred[h][i]]));
  const rozmezi = Object.fromEntries(H.map((h) => [h, RADA.dolni[h][i] != null ? [RADA.dolni[h][i], RADA.horni[h][i]] : null]));
  tiraz({ okamzik: datumCas(S.cas), model: popisModelu(povoden()), zdroj: "archiv ČHMÚ 2006–2025" });
  if (ted == null || H.some((h) => pred[h] == null)) {
    hlavni.innerHTML = `<h2>${typo(`${NAZVY[S.cil]}, ${datumCas(S.cas)} českého času`)}</h2>` +
      hlaska("Pro zvolenou hodinu chybí měření nebo vstupy modelu. Posuňte čas o pár hodin.", "varovani");
    oznam(`${NAZVY[S.cil]}, ${datumCas(S.cas)}: pro zvolenou hodinu chybí měření nebo vstupy modelu.`);
    return;
  }
  oznam(`${NAZVY[S.cil]}, ${datumCas(S.cas)}: teď ${cm(ted)}, za 24 h asi ${cm(pred[24])}.`);
  const v = RADA.vstupy, d = Math.max(0, i - 6);
  const tp = trend(v.praha_Q[i], v.praha_Q[d]), tm = trend(v.melnik_Q[i], v.melnik_Q[d]);
  const veta = `Za 24 h bude ${KDE[S.cil]} asi ${cm(pred[24])}, to je ${STUPNE[stupen(spa(), pred[24])]}; teď je ${cm(ted)}. ` +
    `Vltava v Praze teče ${jedn(v.praha_Q[i], "m³/s")}${tp ? " a " + tp : ""}, ` +
    `Labe v Mělníku ${jedn(v.melnik_Q[i], "m³/s")}${tm ? " a " + tm : ""}. ` +
    `Tahle voda doteče do Ústí a Děčína zhruba za půl dne až den.`;
  hlavni.innerHTML = `
    <h2>${typo(`${NAZVY[S.cil]}, ${datumCas(S.cas)} českého času`)}</h2>
    ${K_PANELU}
    ${ZPRAVA ? hlaska(ZPRAVA, "varovani") : ""}
    <div class="dvojice">
      <section class="karta" aria-label="Vodočet">${stitek(`Vodočet ${NAZVY[S.cil]}`, "hladina v cm")}${vodocet(spa(), ted, pred, rozmezi, {}, prvni, kompakt())}</section>
      <section class="karta" aria-label="Odečet a předpověď">${stitek("Odečet a předpověď", "stupeň povodňové aktivity")}${cteni(ted, pred, rozmezi, {})}</section>
    </div>
    <section class="karta">${stitek("Proč to tak vyšlo")}<p class="citat">${typo(veta)}</p></section>
    <section class="karta">${stitek("Posledních 72 hodin a předpověď", `${NAZVY[S.cil]}, hodinová data`)}<div id="legenda"></div><div id="graf"></div></section>
    <p class="pozn" id="graf-pozn"></p>`;
  prvni = false;
  const od = Math.max(0, i - 72);
  const casy = RADA.cas.slice(od, i + 1).map(parseIso);
  const predX = [0, ...H].map((h) => parseIso(RADA.cas[i + h] || posun(S.cas, h)));
  const ymax = Math.max(...RADA.skutecnost.slice(od, i + 1).filter((x) => x != null), ...H.map((h) => pred[h]), ...H.map((h) => (rozmezi[h] ? rozmezi[h][1] : 0)));
  graf($("#graf"), {
    vyska: 400, osaY: "hladina (cm)", spa: spa(), svisla: parseIso(S.cas), legenda: $("#legenda"),
    popis: `Hladina ${NAZVY[S.cil]} za posledních 72 hodin a předpověď na 12, 24 a 36 hodin.`,
    pas: H.every((h) => rozmezi[h]) ? { x: predX, lo: [ted, ...H.map((h) => rozmezi[h][0])], hi: [ted, ...H.map((h) => rozmezi[h][1])], nazev: `rozmezí (90${NB}% chyb)` } : null,
    serie: [
      { nazev: "hladina změřená", x: casy, y: RADA.skutecnost.slice(od, i + 1), barva: BARVY.text, sirka: 2.2 },
      { nazev: "předpověď", x: predX, y: [ted, ...H.map((h) => pred[h])], barva: BARVY.vodaSvetla, sirka: 2.2, car: "7 5", body: true, prvniMaly: true },
    ],
  });
  $("#graf-pozn").innerHTML = typo("Bílá čára je, co se změřilo do zvoleného okamžiku (svislá čára). Modré body jsou předpověď vydaná v tomhle okamžiku na 12, 24 a 36 hodin dopředu. Modrý pás je rozmezí, do kterého se vešlo 90 % chyb modelu na tréninku; na povodních, které model neviděl, to bylo asi 8 z 10 případů. Tečkované čáry jsou stupně povodňové aktivity."
    + (ymax * 1.6 + 60 < spa()[0] ? ` Hladina je hluboko pod 1. stupněm (${spa()[0]} cm), čáry stupňů se do grafu nevešly.` : ""));
}

function cteni(ted, pred, rozmezi, chmu) {
  const radky = H.map((h) => {
    const pozn = [];
    if (rozmezi[h]) pozn.push(`nejspíš ${cislo(rozmezi[h][0])} až ${cm(rozmezi[h][1])}`);
    if (chmu[h] != null) pozn.push(`ČHMÚ ${cm(chmu[h])}`);
    return `<div><span class="nazev">${typo(`Za ${h} h`)}</span><span class="hodnota">${cm(pred[h])}</span>` +
      `<span class="delta">${typo(`${znamenko(pred[h] - ted)} cm proti teď`)}</span>${odznak(spa(), pred[h])}` +
      `<span class="rozmezi">${typo(pozn.join(" · "))}</span></div>`;
  });
  return `<div class="cteni"><div><span class="nazev">Hladina teď</span><span class="hodnota">${cm(ted)}</span>${odznak(spa(), ted)}` +
    `<span class="rozmezi">${typo("změřeno na stanici ČHMÚ")}</span></div>${radky.join("")}</div>`;
}

// Co ČHMÚ nezveřejnil a není dopočtené: ["Mělník (Labe), průtok"] -> "průtok Mělník (Labe)".
function chybejici() {
  if (!DNES.chybi) return null;
  const dopocteno = DNES.dopocteno || [];
  const skupiny = new Map();
  for (const c of DNES.chybi) {
    if (dopocteno.includes(c)) continue;
    const k = c.lastIndexOf(", ");
    const [stanice, velicina] = k > 0 ? [c.slice(0, k), c.slice(k + 2)] : [c, "hodnota"];
    skupiny.set(velicina, [...(skupiny.get(velicina) || []), stanice]);
  }
  return [...skupiny].map(([v, s]) => `${v} ${s.length <= 2 ? s.join(" a ") : s.join(", ")}`).join("; ");
}

function ukazDnesek() {
  zapisStav({ povoden: null, cas: null, cil: S.cil, dnesek: 1 });
  const st = DNES.stanice[S.cil];
  const t = Date.parse(DNES.cas_utc.endsWith("Z") ? DNES.cas_utc : DNES.cas_utc + "Z");
  const stari = Number.isFinite(t) ? (Date.now() - t) / 3600e3 : DNES.stari_h;
  const stare = stari > 6;
  const kdy = DNES.cas ? datumCas(DNES.cas) : DNES.cas_cesky;
  tiraz({ okamzik: kdy, model: MODEL_DNES, zdroj: `živě ČHMÚ, stáří ${cislo(stari, 1)} h`, zive: !stare });
  // Staré věty o dopočtených stanicích má web v poznámce pod tabulkou; chybějící hodiny se skládají z polí chybi a dopocteno.
  const chybi = chybejici();
  const upozorneni = (DNES.upozorneni || []).filter((u) => chybi == null || !/^(Dopočteno z bilance|ČHMÚ zatím nezveřejnil)/.test(u));
  if (chybi) upozorneni.push(`ČHMÚ zatím nezveřejnil všechny hodiny, chybí ${chybi}.`);
  const pred = Object.fromEntries(H.map((h) => [h, st.pred[h]]));
  const rozmezi = Object.fromEntries(H.map((h) => [h, st.dolni && st.dolni[h] != null ? [st.dolni[h], st.horni[h]] : null]));
  const chmu = st.chmu || {};
  const praha = (DNES.tabulka || []).find((r) => r.stanice.startsWith("Praha")), melnik = (DNES.tabulka || []).find((r) => r.stanice.startsWith("Mělník"));
  const veta = st.veta || `Za 24 h bude ${KDE[S.cil]} asi ${cm(pred[24])}, to je ${STUPNE[stupen(spa(), pred[24])]}; teď je ${cm(st.ted)}. ` +
    (praha ? `Vltava v Praze teče ${jedn(praha.Q, "m³/s")}` : "") + (praha && melnik ? ", " : "") +
    (melnik ? `Labe v Mělníku ${jedn(melnik.Q, "m³/s")}` : "") + (praha || melnik ? ". " : "") +
    `Tahle voda doteče do Ústí a Děčína zhruba za půl dne až den.`;
  const srazky = DNES.srazky || {};
  const POVODI = { vltava: "Vltava", labe: "Horní Labe", ohre: "Ohře" };
  const povodi = srazky.povodi ? Object.entries(srazky.povodi).map(([k, p]) => ({ ...p, nazev: POVODI[k] || p.nazev })) : [];
  const hist = DNES.historie && DNES.historie.cas && DNES.historie[`${S.cil}_H`] ? DNES.historie : null;
  hlavni.innerHTML = `
    <h2>${typo(`${NAZVY[S.cil]} dnes, předpověď vydaná ${kdy} českého času`)}</h2>
    ${K_PANELU}
    ${stare ? hlaska(`Živá data jsou ${cislo(stari, 1)} h stará (hranice je 6 h). Soubor data/dnesek.json se obnovuje každou hodinu skriptem src/dnesek_export.py; do té doby berte předpověď s rezervou.`, "varovani") : ""}
    ${upozorneni.map((u) => hlaska(u)).join("")}
    <div class="dvojice">
      <section class="karta" aria-label="Vodočet">${stitek(`Vodočet ${NAZVY[S.cil]}`, "hladina v cm")}${vodocet(spa(), st.ted, pred, rozmezi, chmu, prvni, kompakt())}</section>
      <section class="karta" aria-label="Odečet a předpověď">${stitek("Odečet a předpověď", "stupeň povodňové aktivity")}${cteni(st.ted, pred, rozmezi, chmu)}</section>
    </div>
    <section class="karta">${stitek("Proč to tak vyšlo")}<p class="citat">${typo(veta)}</p></section>
    <div class="dvojice rovna">
      <section class="karta">${stitek("Náš model vedle oficiální předpovědi ČHMÚ")}
        <dl class="udaje tri">${H.map((h) => `<div><dt>${typo(`Za ${h} h`)}</dt><dd>${cislo(pred[h])}<small>cm</small></dd><dd class="vedle">ČHMÚ <b>${chmu[h] != null ? cm(chmu[h]) : "nezveřejnil"}</b></dd></div>`).join("")}</dl>
        <p class="pozn">${typo("Náš model je jednodušší a nemá počasí, ČHMÚ má srážkovou předpověď.")}</p></section>
      <section class="karta">${stitek("Srážky v povodí, příštích 48 h", "Open-Meteo")}
        ${povodi.length ? `<dl class="udaje tri">${povodi.map((p) => `<div><dt>${typo(p.nazev)}</dt><dd>${cislo(p.mm_48)}<small>mm</small></dd><dd class="vedle">za 24${NB}h <b>${jedn(p.mm_24, "mm")}</b></dd></div>`).join("")}</dl>` : hlaska("Předpověď srážek teď není k dispozici.")}
        <p class="pozn">${typo((srazky.veta ? srazky.veta + " " : "") + "Srážky do modelu nevstupují, na 12 až 36 h nepomohly (voda z deště je už v řekách). Zdroj Open-Meteo (CC BY 4.0).")}</p></section>
    </div>
    <section class="karta">${stitek("Stanice proti proudu", "průtok teď")}
      <div class="tab-obal"><table class="tab"><thead><tr><th style="text-align:left">Stanice</th><th>Průtok (m³/s)</th><th>Zdroj</th></tr></thead><tbody>
      ${(DNES.tabulka || []).map((r) => `<tr${r.dopocteno ? ' class="tlum"' : ""}><th>${typo(r.stanice)}</th><td>${cislo(r.Q)}</td><td class="tlum zal">${r.dopocteno ? "dopočteno" : "ČHMÚ"}</td></tr>`).join("")}
      </tbody></table></div>
      <p class="pozn">${typo(`Živá data ČHMÚ (opendata.chmi.cz), ${cislo(stari, 1)} h stará. Průtoky v Mělníku a Nymburce ČHMÚ operativně nezveřejňuje, jsou dopočtené z bilance vody.`)}</p></section>
    <section class="karta">${stitek(hist ? "Posledních 72 hodin a předpověď" : "Předpověď na 36 hodin", `${NAZVY[S.cil]}, ${hist ? "hodinová data ČHMÚ" : "od " + kdy}`)}<div id="legenda"></div><div id="graf"></div></section>`;
  prvni = false;
  posuvnaTabulka($(".tab-obal", hlavni));
  oznam(`${NAZVY[S.cil]} dnes, předpověď vydaná ${kdy}: teď ${cm(st.ted)}, za 24 h asi ${cm(pred[24])}.`);
  const zacatek = DNES.cas_cesky.replace(/\s/g, "");
  const m = zacatek.match(/(\d{1,2})\.(\d{1,2})\.(\d{4})(\d{1,2}):(\d{2})/);
  const iso = DNES.cas || (m ? `${m[3]}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}T${m[4].padStart(2, "0")}:${m[5]}` : new Date().toISOString().slice(0, 16));
  const predX = [0, ...H].map((h) => parseIso(posun(iso, h)));
  const hc = H.filter((h) => chmu[h] != null);
  graf($("#graf"), {
    vyska: hist ? 400 : 320, osaY: "hladina (cm)", spa: spa(), svisla: predX[0], legenda: $("#legenda"),
    popis: `Předpověď hladiny ${NAZVY[S.cil]} na 12, 24 a 36 hodin.`,
    pas: H.every((h) => rozmezi[h]) ? { x: predX, lo: [st.ted, ...H.map((h) => rozmezi[h][0])], hi: [st.ted, ...H.map((h) => rozmezi[h][1])], nazev: `rozmezí (90${NB}% chyb)` } : null,
    serie: [
      ...(hist ? [{ nazev: "hladina změřená", x: hist.cas.map(parseIso), y: hist[`${S.cil}_H`], barva: BARVY.text, sirka: 2.2 }] : []),
      { nazev: "předpověď", x: predX, y: [st.ted, ...H.map((h) => pred[h])], barva: BARVY.vodaSvetla, sirka: 2.2, car: "7 5", body: true, prvniMaly: true },
      ...(hc.length ? [{ nazev: "ČHMÚ", x: hc.map((h) => parseIso(posun(iso, h))), y: hc.map((h) => chmu[h]), barva: BARVY.text, jenBody: true, trojuhelnik: true }] : []),
    ],
  });
}

start();
