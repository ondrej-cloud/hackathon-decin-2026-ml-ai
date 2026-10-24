// Stránky Mapa povodí a Animace povodně: přehrávač s výběrem povodně (a města), těžká mapa se načte do iframe až na klik.
import { typo, datum } from "./typo.js";
import { DATA, NAZVY, nacti, stav, zapisStav } from "./data.js";
import { $, tiraz, hlaska, dlazdice, segmenty, naZmenu } from "./spolecne.js";

const DRUH = document.body.dataset.druh; // "mapa" nebo "animace"
const q = stav();
const S = { povoden: q.get("povoden") || "2011-01", cil: q.get("cil") || "decin", bezi: false };
let POV;
const prehravac = $("#prehravac"), scena = $("#scena"), ramec = $("#ramec"), obrazek = $("#nahled");

const povoden = () => POV.povodne.find((p) => p.slug === S.povoden) || POV.povodne[0];
const cesta = () => `${DRUH}/${S.povoden}${DRUH === "mapa" ? "_" + S.cil : ""}.html`;

async function start() {
  try {
    POV = await nacti(DATA + "povodne.json");
  } catch (e) {
    prehravac.innerHTML = hlaska("Seznam povodní se nepodařilo načíst (data/povodne.json).", "varovani");
    return;
  }
  if (!POV.povodne.some((p) => p.slug === S.povoden)) S.povoden = POV.povodne[0].slug;
  $("#povodne").innerHTML = dlazdice("povoden", POV.povodne.map((p) => ({ hodnota: p.slug, nazev: p.klic, popis: p.nazev + (p.zdroj === "test" ? ", test" : "") })), S.povoden, "radek", "Povodeň");
  if ($("#mesta")) $("#mesta").innerHTML = segmenty("cil", Object.entries(POV.stanice).map(([k, v]) => ({ hodnota: k, nazev: v.nazev })), S.cil, "Město");
  naZmenu(prehravac, "povoden", (v) => { S.povoden = v; ukaz(); });
  naZmenu(prehravac, "cil", (v) => { S.cil = v; ukaz(); });
  $("#prehrat").addEventListener("click", spust);
  $("#start").addEventListener("click", spust);
  matchMedia("(max-width: 640px)").addEventListener("change", celaObrazovka);
  celaObrazovka();
  ukaz();
}

// 5: bez podpory celé obrazovky (Safari na iPhonu) a na telefonu je místo tlačítka odkaz na mapu v nové záložce
const uzke = () => matchMedia("(max-width: 640px)").matches;
const umiCelou = () => Boolean(document.fullscreenEnabled && scena.requestFullscreen);
function celaObrazovka() {
  const stare = $("#cela"), odkaz = !umiCelou() || uzke();
  if (stare.dataset.hotovo && odkaz === (stare.tagName === "A")) return;
  const nove = document.createElement(odkaz ? "a" : "button");
  nove.id = "cela"; nove.className = "tlacitko druhe"; nove.dataset.hotovo = "1";
  if (odkaz) {
    nove.href = cesta(); nove.target = "_blank"; nove.rel = "noopener";
    nove.textContent = `Otevřít ${DRUH === "mapa" ? "mapu" : "animaci"} na celou obrazovku`;
  } else {
    nove.type = "button"; nove.textContent = "Celá obrazovka";
    nove.addEventListener("click", () => { const cil = S.bezi ? ramec : scena; if (cil.requestFullscreen) cil.requestFullscreen(); });
  }
  stare.replaceWith(nove);
}

function ukaz() {
  zapisStav({ povoden: S.povoden, cil: DRUH === "mapa" ? S.cil : null });
  const p = povoden();
  tiraz({ okamzik: `${datum(p.od)} až ${datum(p.do)}`, model: "ridge", zdroj: "archiv ČHMÚ 2006–2025" });
  const v = p.vrchol && p.vrchol[S.cil];
  $("#popis-vyberu").innerHTML = typo(DRUH === "mapa"
    ? `${p.nazev}, ${NAZVY[S.cil]}${v ? `: vrchol ${v.cm} cm ${datum(v.cas)}` : ""}. Vlevo rozliv z hladiny, kterou model předpověděl 24 h předem, vpravo rozliv ze skutečně naměřené hladiny v tutéž hodinu.`
    : `${p.nazev}${v ? `: vrchol v Děčíně ${v.cm} cm ${datum(v.cas)}` : ""}. Kapky tečou po skutečných řekách a nesou průtok ze stanic proti proudu.`);
  if (obrazek && DRUH === "mapa" && !obrazek.getAttribute("src").endsWith(`mapbox3_${S.cil}.webp`)) {
    obrazek.srcset = `img/mapbox3_${S.cil}_800.webp 800w, img/mapbox3_${S.cil}.webp 1600w`;
    obrazek.src = `img/mapbox3_${S.cil}.webp`;
  }
  if ($("#cela").tagName === "A") $("#cela").href = cesta();
  if (S.bezi) ramec.src = cesta();
}

// 3, 16: na telefonu je rám 4 : 3 pro mapu s vlastním ovládáním malý, mapa se otevře jako celá stránka (zpět vrátí sem)
function spust() {
  if (uzke()) { location.assign(cesta()); return; }
  S.bezi = true;
  scena.classList.add("bezi");
  ramec.addEventListener("load", () => scena.classList.add("nacteno"), { once: true });
  ramec.src = cesta();
  ramec.focus({ preventScroll: true });
  scena.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

start();
