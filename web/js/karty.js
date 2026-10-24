// Karty společné pro Dnes a Povodně: hladina teď a za 12, 24 a 36 h, věta proč, graf s vodočtem vedle sebe.
import { typo, cislo, cm, jedn, znamenko } from "./typo.js";
import { H, stupen, odznak, trend } from "./data.js";

// Teď vlevo, 12, 24 a 36 h vpravo; pod každou předpovědí rozmezí a srovnání (ČHMÚ, nebo co opravdu přišlo).
export function prehled(spa, ted, pred, rozmezi, srovnani, veta) {
  const sloupce = H.map((h) => {
    const d = pred[h] - ted;
    const smer = d >= 5 ? " roste" : d <= -5 ? " klesa" : "";
    const pod = [rozmezi[h] ? `nejspíš ${cislo(rozmezi[h][0])}–${cm(rozmezi[h][1])}` : "", srovnani[h] || ""].filter(Boolean);
    return `<div><span class="popisek">Za ${h} h</span><span class="stredni">${cislo(pred[h])}<small>cm</small></span>` +
      `<span class="zmena${smer}">${znamenko(d)} cm</span>${stupen(spa, pred[h]) ? odznak(spa, pred[h], true) : ""}` +
      pod.map((r) => `<span class="drobne">${typo(r)}</span>`).join("") + "</div>";
  });
  return `<section class="karta prehled" aria-label="Hladina teď a předpověď">
    <div><span class="popisek">Teď</span><span class="velke">${cislo(ted)}<small>cm</small></span>${odznak(spa, ted)}</div>
    <div class="prehled-pred">${sloupce.join("")}</div>
    ${veta ? `<p class="prehled-veta">${typo(veta)}</p>` : ""}
  </section>`;
}

// Proč to tak vyšlo: co teče Prahou a Mělníkem a jestli to stoupá.
export function veta(praha, prahaDrive, melnik, melnikDrive) {
  const kus = (kde, q, drive) => q == null ? "" : `${kde} ${jedn(q, "m³/s")}${trend(q, drive) ? " a " + trend(q, drive) : ""}`;
  const casti = [kus("Vltava v Praze teče", praha, prahaDrive), kus("Labe v Mělníku", melnik, melnikDrive)].filter(Boolean);
  return casti.length ? `${casti.join(", ")}. Tahle voda doteče do Ústí a Děčína zhruba za půl dne až den.` : "";
}

export const grafSVodoctem = (nazevGrafu) => `<div class="mrizka">
    <section class="karta"><h3>${typo(nazevGrafu)}</h3><div class="graf-misto"></div></section>
    <section class="karta"><h3>Vodočet</h3><div class="lat-misto"></div></section>
  </div>`;
