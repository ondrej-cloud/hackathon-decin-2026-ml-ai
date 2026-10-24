// Společné kusy stránek: tiráž, hlášky, drobné pomocné funkce.
import { typo } from "./typo.js";

export const $ = (s, el = document) => el.querySelector(s);
export const $$ = (s, el = document) => [...el.querySelectorAll(s)];

export function tiraz({ okamzik }) {
  const el = $("#t-okamzik");
  if (el) el.textContent = typo(okamzik);
}

export const hlaska = (text, druh = "") => `<div class="hlaska${druh ? " " + druh : ""}" role="status">${typo(text)}</div>`;

export const stitek = (text, vpravo = "") =>
  `<div class="stitek"><b>${typo(text)}</b>${vpravo ? `<i>${typo(vpravo)}</i>` : ""}</div>`;

// Dlaždice (radio) pro výběr: položky [{hodnota, nazev, popis}], vybraná hodnota, název skupiny; popisek je název skupiny pro čtečku.
export function dlazdice(jmeno, polozky, vybrana, trida = "", popisek = "") {
  return `<div class="dlazdice${trida ? " " + trida : ""}" role="radiogroup"${popisek ? ` aria-label="${popisek}"` : ""}>${polozky.map((p) =>
    `<label><input type="radio" name="${jmeno}" value="${p.hodnota}"${p.hodnota === vybrana ? " checked" : ""}${p.vypnuto ? " disabled" : ""}>` +
    `<b>${typo(p.nazev)}</b>${p.popis ? `<small>${typo(p.popis)}</small>` : ""}</label>`).join("")}</div>`;
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

// Tabulka širší než karta: pravý okraj se ztrácí do pozadí a pod tabulkou je poznámka, že se posouvá do strany.
export function posuvnaTabulka(obal) {
  if (!obal || obal.__posuv) return;
  obal.__posuv = true;
  const pozn = document.createElement("p");
  pozn.className = "posuv-pozn";
  pozn.textContent = typo("Tabulka pokračuje vpravo, posuňte ji do strany.");
  obal.after(pozn);
  const uprav = () => {
    const presah = obal.scrollWidth - obal.clientWidth > 2;
    obal.classList.toggle("posuv", presah);
    obal.classList.toggle("na-konci", presah && obal.scrollLeft + obal.clientWidth >= obal.scrollWidth - 2);
  };
  uprav();
  obal.addEventListener("scroll", uprav, { passive: true });
  new ResizeObserver(uprav).observe(obal);
}

export function naZmenu(kontejner, jmeno, fn) {
  kontejner.addEventListener("change", (e) => {
    if (e.target.name === jmeno) fn(e.target.value);
  });
}

export function chyba(el, text) {
  el.innerHTML = hlaska(text, "varovani");
}

// Panel Nastavení: na telefonu je sbalený na jeden řádek se shrnutím, tlačítko Změnit ho rozbalí.
export function panelSbaleni(panel) {
  const prepnout = $(".panel-prepnout", panel);
  if (!prepnout) return;
  prepnout.addEventListener("click", () => {
    const otevrit = !panel.classList.contains("otevreny");
    panel.classList.toggle("otevreny", otevrit);
    prepnout.setAttribute("aria-expanded", String(otevrit));
    prepnout.textContent = otevrit ? "Hotovo" : "Změnit";
  });
}
export function shrnutiPanelu(casti) {
  const el = $("#panel-shrnuti");
  if (el) el.textContent = typo(casti.filter(Boolean).join("\u00A0· "));
}
