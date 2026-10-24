// Načítání JSON dat, stupně povodňové aktivity a stav v adrese stránky.
import { typo } from "./typo.js";

export const DATA = "data/";
export const H = [12, 24, 36];
export const STUPNE = ["pod 1. stupněm", "1. stupeň (bdělost)", "2. stupeň (pohotovost)", "3. stupeň (ohrožení)"];
export const STUPNE_KRATCE = ["bez stupně", "1. stupeň", "2. stupeň", "3. stupeň"];
export const BARVY_SPA = ["#f2c437", "#ef6c00", "#c62828"];
export const KDE = { decin: "v Děčíně", usti: "v Ústí nad Labem" };
export const NAZVY = { decin: "Děčín", usti: "Ústí nad Labem" };
// Barvy jako v grafech z prezentace (změřené z docs/grafy/prezentace): modrá a světlá modrá sloupců, oranžová, šedá „bude jako teď“.
export const BARVY = { karta: "#ffffff", pozadi: "#f5f5f7", text: "#1d1d1f", text2: "#6e6e73", text3: "#86868b",
  jakoTed: "#666666", modra: "#167c9c", modraSvetla: "#9fcad8", oranzova: "#cb6c31", cara: "#e5e5ea", caraSilna: "#d2d2d7" };

export const stupen = (spa, cm) => spa.reduce((n, p) => n + (cm >= p ? 1 : 0), 0);
export function odznak(spa, cm, kratce = false) {
  const s = stupen(spa, cm);
  return `<span class="odznak spa-${s}"${kratce ? ` title="${STUPNE[s]}"` : ""}>${typo((kratce ? STUPNE_KRATCE : STUPNE)[s])}</span>`;
}

const pamet = new Map();
export function nacti(url) {
  if (!pamet.has(url)) {
    pamet.set(url, fetch(url).then((r) => {
      if (!r.ok) throw new Error(`${url}: ${r.status}`);
      return r.json();
    }).catch((e) => { pamet.delete(url); throw e; }));
  }
  return pamet.get(url);
}

export const stav = () => new URLSearchParams(location.search);
export function zapisStav(obj) {
  const p = new URLSearchParams(location.search);
  for (const [k, v] of Object.entries(obj)) {
    if (v == null || v === false || v === "") p.delete(k); else p.set(k, v);
  }
  const q = p.toString();
  history.replaceState(null, "", location.pathname + (q ? "?" + q : "") + location.hash);
}

export const trend = (ted, drive) => (drive == null ? "" : ted > drive * 1.05 ? "stoupá" : ted < drive * 0.95 ? "klesá" : "drží se");

// Index přesného nebo nejbližšího času v poli časů "YYYY-MM-DDTHH:MM" (pole je vzestupné).
export function nejblizsi(casy, iso) {
  const i = casy.indexOf(iso);
  if (i >= 0) return i;
  let lo = 0, hi = casy.length - 1;
  while (lo < hi) {
    const m = (lo + hi) >> 1;
    if (casy[m] < iso) lo = m + 1; else hi = m;
  }
  if (lo > 0 && casy[lo] > iso) {
    const t = Date.parse(iso + "Z");
    if (t - Date.parse(casy[lo - 1] + "Z") < Date.parse(casy[lo] + "Z") - t) return lo - 1;
  }
  return lo;
}

export function nazevPovodne(p) {
  return p.nazev || p.klic;
}
