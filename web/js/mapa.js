// Stránky Mapa a Animace: výběr povodně (a města), těžká mapa se načte do iframe až na klik.
import { typo, datum } from "./typo.js";
import { DATA, NAZVY, nacti, stav, zapisStav } from "./data.js";
import { $, hlaska, dlazdice, segmenty, naZmenu, hlava } from "./spolecne.js";

const DRUH = document.body.dataset.druh; // "mapa" nebo "animace"
const q = stav();
const S = { povoden: q.get("povoden") || "2011-01", cil: q.get("cil") || "decin", bezi: false };
let POV;
const scena = $("#scena"), ramec = $("#ramec"), obrazek = $("#nahled");

const povoden = () => POV.povodne.find((p) => p.slug === S.povoden) || POV.povodne[0];
const cesta = () => `${DRUH}/${S.povoden}${DRUH === "mapa" ? "_" + S.cil : ""}.html`;

async function start() {
  try {
    POV = await nacti(DATA + "povodne.json");
  } catch (e) {
    scena.outerHTML = hlaska("Seznam povodní se nepodařilo načíst. Zkuste stránku obnovit.", "varovani");
    return;
  }
  if (!POV.povodne.some((p) => p.slug === S.povoden)) S.povoden = POV.povodne[0].slug;
  if (!POV.stanice[S.cil]) S.cil = "decin";
  $("#povodne").innerHTML = dlazdice("povoden", POV.povodne.map((p) => ({ hodnota: p.slug, nazev: p.klic })), S.povoden, "Povodeň");
  if ($("#mesta")) $("#mesta").innerHTML = segmenty("cil", Object.entries(POV.stanice).map(([k, v]) => ({ hodnota: k, nazev: v.nazev })), S.cil, "Město");
  const strana = $(".strana");
  naZmenu(strana, "povoden", (v) => { S.povoden = v; ukaz(); });
  naZmenu(strana, "cil", (v) => { S.cil = v; ukaz(); });
  $("#start").addEventListener("click", spust);
  ukaz();
}

const uzke = () => matchMedia("(max-width: 640px)").matches;

function ukaz() {
  zapisStav({ povoden: S.povoden, cil: DRUH === "mapa" ? S.cil : null });
  const p = povoden();
  const v = p.vrchol && p.vrchol[DRUH === "mapa" ? S.cil : "decin"];
  const vrchol = v ? `, vrchol ${DRUH === "mapa" ? NAZVY[S.cil] : "v Děčíně"} ${v.cm} cm ${datum(v.cas)}` : "";
  hlava(DRUH === "mapa" ? `Rozliv v mapě, ${NAZVY[S.cil]}` : "Jak voda teče k Děčínu",
    typo(DRUH === "mapa" ? `Předpověď 24 h předem vedle skutečnosti, hodinu po hodině. ${p.nazev}${vrchol}.`
      : `Kapky po řekách nesou průtok ze stanic proti proudu. ${p.nazev}${vrchol}.`));
  if (obrazek && DRUH === "mapa" && !obrazek.getAttribute("src").endsWith(`mapbox3_${S.cil}.webp`)) {
    obrazek.srcset = `img/mapbox3_${S.cil}_800.webp 800w, img/mapbox3_${S.cil}.webp 1600w`;
    obrazek.src = `img/mapbox3_${S.cil}.webp`;
  }
  if (S.bezi) ramec.src = cesta();
}

// Na telefonu je rám pro mapu s vlastním ovládáním malý, mapa se otevře jako celá stránka (zpět vrátí sem).
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
