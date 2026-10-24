// Společné kusy stránek: hlášky, přepínače, drobné pomocné funkce.
import { typo } from "./typo.js";

export const $ = (s, el = document) => el.querySelector(s);
export const $$ = (s, el = document) => [...el.querySelectorAll(s)];

export const hlaska = (text, druh = "") => `<div class="hlaska${druh ? " " + druh : ""}" role="status">${typo(text)}</div>`;

// Pilulky (radio) pro výběr: položky [{hodnota, nazev}], vybraná hodnota; popisek je název skupiny pro čtečku.
export function dlazdice(jmeno, polozky, vybrana, popisek = "") {
  return `<div class="dlazdice" role="radiogroup"${popisek ? ` aria-label="${popisek}"` : ""}>${polozky.map((p) =>
    `<label><input type="radio" name="${jmeno}" value="${p.hodnota}"${p.hodnota === vybrana ? " checked" : ""}>` +
    `<b>${typo(p.nazev)}</b></label>`).join("")}</div>`;
}

export function segmenty(jmeno, polozky, vybrana, popisek = "") {
  return `<div class="segmenty" role="radiogroup"${popisek ? ` aria-label="${popisek}"` : ""}>${polozky.map((p) =>
    `<label><input type="radio" name="${jmeno}" value="${p.hodnota}"${p.hodnota === vybrana ? " checked" : ""}>${typo(p.nazev)}</label>`).join("")}</div>`;
}

// Krátké oznámení pro čtečku obrazovky po překreslení hlavní části (místo aria-live na celé části).
export function oznam(text) {
  const el = $("#oznameni");
  if (el) el.textContent = typo(text);
}

export function naZmenu(kontejner, jmeno, fn) {
  kontejner.addEventListener("change", (e) => {
    if (e.target.name === jmeno) fn(e.target.value);
  });
}

// Nadpis a podtitul stránky.
export function hlava(nadpis, podtitul = "") {
  $("#nadpis").innerHTML = typo(nadpis);
  $("#podtitul").innerHTML = podtitul;
}
