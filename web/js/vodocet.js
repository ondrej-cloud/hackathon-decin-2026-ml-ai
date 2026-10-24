// Svislá měrná lať: stupně povodňové aktivity, hladina teď a předpověď za 12, 24 a 36 h s rozmezím nejistoty.
// Světlá kresba sladěná s grafy: bílá lať s šedým dělením, voda světle modrá s modrým okrajem, značky předpovědi
// modré, rozmezí světle modré pruhy, štítky stupňů v pilulkách. Prahy jsou tři stupně v cm, pred {h: cm},
// rozmezi {h: [dolní, horní] nebo null}, chmu {h: cm nebo null}.
// kompakt = užší kresba pro karty pod 400 px (telefon): kratší štítky, větší písmo.
import { BARVY, BARVY_SPA } from "./data.js";
import { cislo } from "./typo.js";

const NA_SPA = [BARVY.text, BARVY.text, "#ffffff"];

export function vodocet(prahy, ted, pred, rozmezi, chmu = {}, anim = false, kompakt = false) {
  chmu = Object.fromEntries(Object.entries(chmu).filter(([, v]) => v != null));
  const vse = [ted, ...Object.values(pred), ...Object.values(chmu), ...Object.values(rozmezi).flatMap((r) => r || [])]
    .filter((v) => v != null);
  const dole = Math.max(0, Math.floor(Math.min(Math.min(...vse) - 60, prahy[0] - 100) / 50) * 50);
  const nahore = Math.ceil(Math.max(Math.max(...vse) + 50, prahy[2] + 90) / 50) * 50;
  const K = kompakt;
  const W = K ? 360 : 480, VY = K ? 560 : 600, T = 14, B = 20;
  const dno = VY - B;
  const k = (dno - T) / (nahore - dole);
  const y = (c) => +(T + (nahore - c) * k).toFixed(1);
  // pilulky prahů těsně u pravého okraje, štítky předpovědi vlevo od nich; v kompaktu jsou pilulky užší
  const L0 = K ? 44 : 50, L1 = K ? 108 : 124, STITKY = W - (K ? 64 : 92), POPIS = K ? 168 : 214;
  const pruhy = K ? { 12: L1 + 10, 24: L1 + 24, 36: L1 + 38 } : { 12: L1 + 12, 24: L1 + 28, 36: L1 + 44 };
  const s = [];
  const hranice = [...prahy, nahore];
  for (let i = 0; i < 3; i++) {
    const a = Math.max(hranice[i], dole), b = Math.min(hranice[i + 1], nahore);
    if (a < b) {
      s.push(`<rect x="${L1}" y="${y(b)}" width="${W - L1}" height="${(y(a) - y(b)).toFixed(1)}" fill="${BARVY_SPA[i]}" fill-opacity="${[0.05, 0.06, 0.07][i]}"/>`);
      s.push(`<rect x="${L1}" y="${y(b)}" width="4" height="${(y(a) - y(b)).toFixed(1)}" fill="${BARVY_SPA[i]}"/>`);
    }
  }
  // lať: bílá s vlasovým obrysem a šedým dělením po 10 cm, střídavé pruhy po 20 cm jako na skutečné lati
  s.push(`<rect x="${L0}" y="${T}" width="${L1 - L0}" height="${dno - T}" fill="#ffffff" stroke="${BARVY.caraSilna}"/>`);
  for (let c = dole; c < nahore; c += 10) {
    if (Math.floor(c / 10) % 2 === 0) {
      const x = Math.floor(c / 100) % 2 === 0 ? L0 + 8 : L1 - 30;
      s.push(`<rect x="${x}" y="${y(c + 10)}" width="22" height="${(y(c) - y(c + 10)).toFixed(1)}" fill="${BARVY.text}" fill-opacity=".07"/>`);
    }
  }
  for (let c = dole; c <= nahore; c += 10) {
    const [x2, op] = c % 100 === 0 ? [L1, 0.6] : c % 50 === 0 ? [L0 + 30, 0.45] : [L0 + 8, 0.3];
    s.push(`<line x1="${L0}" x2="${x2}" y1="${y(c)}" y2="${y(c)}" stroke="${BARVY.text2}" stroke-opacity="${op}"/>`);
    // číslo stupnice vynecháme, kde by ho zakryla pilulka „teď“
    if (c % 100 === 0 && Math.abs(c - ted) >= 15) s.push(`<text x="${L0 - 8}" y="${y(c) + 5}" text-anchor="end" class="lat-cislo">${c}</text>`);
  }
  s.push(`<rect class="voda" x="${L0}" y="${y(ted)}" width="${L1 - L0}" height="${(dno - y(ted)).toFixed(1)}" fill="${BARVY.modraSvetla}" fill-opacity=".6"/>`);
  s.push(`<line x1="${L0}" x2="${W}" y1="${dno}" y2="${dno}" stroke="${BARVY.caraSilna}"/>`);

  prahy.forEach((prah, i) => {
    const yp = y(prah);
    s.push(`<line x1="${L0}" x2="${STITKY}" y1="${yp}" y2="${yp}" stroke="${BARVY_SPA[i]}" stroke-width="1.5" stroke-dasharray="3 4"/>`);
    s.push(`<rect x="${STITKY}" y="${yp - 11}" width="${W - STITKY}" height="22" rx="11" fill="${BARVY_SPA[i]}"/>`);
    s.push(`<text x="${(STITKY + W) / 2}" y="${yp + 4}" text-anchor="middle" class="lat-stupen" fill="${NA_SPA[i]}">${i + 1}. ${K ? "st." : "stupeň"} ${prah}</text>`);
  });

  s.push(`<g class="lat-pohyb">`);
  s.push(`<line x1="${L0}" x2="${STITKY}" y1="${y(ted)}" y2="${y(ted)}" stroke="${BARVY.modra}" stroke-width="2"/>`);
  s.push(`<rect x="0" y="${y(ted) - 13}" width="${L0 - 5}" height="26" rx="13" fill="${BARVY.modra}"/>`);
  s.push(`<text x="${(L0 - 5) / 2}" y="${y(ted) + 5}" text-anchor="middle" class="lat-ted">${Math.round(ted)}</text>`);

  // Štítky předpovědi: šířka boxu podle počtu číslic (26px číslice ≈ 15,4 px) a textu; v kompaktu jde ČHMÚ na druhý řádek.
  // Boxy se řadí pod sebe s rozestupem a uhýbají pilulkám prahů, když by s nimi sdílely výšku i sloupec.
  const sChmu = Object.keys(chmu).length > 0;
  const vysBox = K && sChmu ? 44 : 32, rozestup = vysBox + 4;
  const sirkaCisla = (v) => String(Math.round(v)).length * 15.4;
  const sirkaOsa = K ? 68 : 63; // „cm za 36 h“
  const sirkaBoxu = (h) => 4 + sirkaCisla(pred[h]) + 6 + sirkaOsa + (h in chmu && !K ? 74 : 0) + 6;
  const uhybat = Object.keys(pruhy).some((h) => POPIS - 2 + sirkaBoxu(h) > STITKY - 6);
  const prekazky = uhybat ? prahy.map(y).filter((yp) => yp > T && yp < dno).map((yp) => [yp - 15, yp + 15]) : [];
  const narazi = (p) => prekazky.find(([a, b]) => p + vysBox / 2 > a && p - vysBox / 2 < b);
  const popisky = Object.keys(pruhy).map((h) => [y(pred[h]), +h]).sort((a, b) => a[0] - b[0]);
  const polohy = [];
  for (const [yp] of popisky) {
    const minP = polohy.length ? polohy[polohy.length - 1] + rozestup : T + vysBox / 2;
    let p = Math.max(yp, minP);
    for (let i = 0; i < 4; i++) {
      const hit = narazi(p);
      if (!hit) break;
      const nad = hit[0] - vysBox / 2, pod = hit[1] + vysBox / 2;
      if (nad >= minP && !narazi(nad) && (yp - nad <= pod - yp || pod + vysBox / 2 > dno - 2)) { p = nad; break; }
      p = pod;
    }
    polohy.push(p);
  }
  const posun = Math.max(0, polohy[polohy.length - 1] + vysBox - 16 - (dno - 2));
  popisky.forEach(([yp, h], n) => {
    const ly = polohy[n] - posun, x = pruhy[h], p = pred[h];
    if (rozmezi[h]) {
      const [lo, hi] = rozmezi[h];
      s.push(`<rect x="${x}" y="${y(hi)}" width="10" height="${(y(lo) - y(hi)).toFixed(1)}" rx="3" fill="${BARVY.modraSvetla}" fill-opacity=".55"/>`);
    }
    s.push(`<rect x="${x - 3}" y="${yp - 2}" width="16" height="4" rx="2" fill="${BARVY.modra}"/>`);
    if (h in chmu) s.push(`<path d="M${x + 12} ${y(chmu[h])}l8 -5v10z" fill="${BARVY.text}"/>`);
    s.push(`<path d="M${x + 13} ${yp}H${L1 + (K ? 50 : 66)}L${POPIS - 8} ${ly}H${POPIS - 2}" fill="none" stroke="${BARVY.modra}" stroke-opacity=".5"/>`);
    const xCislo = POPIS + 2 + sirkaCisla(p);
    s.push(`<rect x="${POPIS - 2}" y="${ly - 16}" width="${sirkaBoxu(h).toFixed(1)}" height="${vysBox}" rx="10" fill="#ffffff" stroke="${BARVY.cara}"/>`);
    const dalsi = h in chmu && !K ? `<tspan class="lat-chmu"> · ČHMÚ ${Math.round(chmu[h])}</tspan>` : "";
    s.push(`<text x="${xCislo.toFixed(1)}" y="${ly + 9}" text-anchor="end" class="lat-hodnota">${Math.round(p)}</text><text x="${(xCislo + 6).toFixed(1)}" y="${ly + 5}" class="lat-osa">cm za ${h} h${dalsi}</text>`);
    if (h in chmu && K) s.push(`<text x="${(xCislo + 6).toFixed(1)}" y="${ly + 22}" class="lat-chmu">ČHMÚ ${Math.round(chmu[h])}</text>`);
  });
  s.push(`</g>`);
  const popis = `Vodočet: teď ${cislo(ted)} cm, ${Object.keys(pruhy).map((h) => `za ${h} h ${cislo(pred[h])} cm`).join(", ")}; stupně povodňové aktivity ${prahy[0]}, ${prahy[1]} a ${prahy[2]} cm.`;
  return `<div class="lat${anim ? " anim" : ""}${K ? " kompakt" : ""}"><svg viewBox="0 0 ${W} ${VY}" role="img" aria-label="${popis}" preserveAspectRatio="xMidYMid meet">${s.join("")}</svg></div>`;
}
