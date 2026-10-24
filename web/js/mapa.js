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
  $("#povodne").innerHTML = dlazdice("povoden", POV.povodne.map((p) => ({ hodnota: p.slug, nazev: p.klic })), S.povoden, "radek", "Povodeň");
  if ($("#mesta")) $("#mesta").innerHTML = segmenty("cil", Object.entries(POV.stanice).map(([k, v]) => ({ hodnota: k, nazev: v.nazev })), S.cil, "Město");
  naZmenu(prehravac, "povoden", (v) => { S.povoden = v; ukaz(); });
  naZmenu(prehravac, "cil", (v) => { S.cil = v; ukaz(); });
  $("#start").addEventListener("click", spust);
  ukaz();
}

const uzke = () => matchMedia("(max-width: 640px)").matches;

function ukaz() {
  zapisStav({ povoden: S.povoden, cil: DRUH === "mapa" ? S.cil : null });
  const p = povoden();
  tiraz({ okamzik: `${datum(p.od)} až ${datum(p.do)}` });
  const v = p.vrchol && p.vrchol[S.cil];
  $("#popis-vyberu").innerHTML = typo(DRUH === "mapa"
    ? `${p.nazev}, ${NAZVY[S.cil]}${v ? `: vrchol ${v.cm} cm ${datum(v.cas)}` : ""}.`
    : `${p.nazev}${v ? `: vrchol v Děčíně ${v.cm} cm ${datum(v.cas)}` : ""}.`);
  if (obrazek && DRUH === "mapa" && !obrazek.getAttribute("src").endsWith(`mapbox3_${S.cil}.webp`)) {
    obrazek.srcset = `img/mapbox3_${S.cil}_800.webp 800w, img/mapbox3_${S.cil}.webp 1600w`;
    obrazek.src = `img/mapbox3_${S.cil}.webp`;
  }
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
