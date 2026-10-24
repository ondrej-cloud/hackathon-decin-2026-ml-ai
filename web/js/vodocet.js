// Svislá měrná lať: stupně povodňové aktivity, hladina teď a předpověď za 12, 24 a 36 h s rozmezím nejistoty.
// Stejná kresba jako v aplikaci (app/styl.py); prahy jsou tři stupně v cm, pred {h: cm},
// rozmezi {h: [dolní, horní] nebo null}, chmu {h: cm nebo null}.
// kompakt = užší kresba pro karty pod 400 px (telefon): kratší štítky, větší písmo, legenda ve dvou řádcích.
import { BARVY, BARVY_SPA } from "./data.js";
import { cislo } from "./typo.js";

const NA_SPA = [BARVY.studna, BARVY.studna, BARVY.text];

export function vodocet(prahy, ted, pred, rozmezi, chmu = {}, anim = false, kompakt = false) {
  chmu = Object.fromEntries(Object.entries(chmu).filter(([, v]) => v != null));
  const vse = [ted, ...Object.values(pred), ...Object.values(chmu), ...Object.values(rozmezi).flatMap((r) => r || [])]
    .filter((v) => v != null);
  const dole = Math.max(0, Math.floor(Math.min(Math.min(...vse) - 60, prahy[0] - 100) / 50) * 50);
  const nahore = Math.ceil(Math.max(Math.max(...vse) + 50, prahy[2] + 90) / 50) * 50;
  const K = kompakt;
  const W = K ? 360 : 480, VY = K ? 560 : 600, T = 14, B = K ? 62 : 40;
  const dno = VY - B;
  const k = (dno - T) / (nahore - dole);
  const y = (c) => +(T + (nahore - c) * k).toFixed(1);
  const L0 = K ? 44 : 50, L1 = K ? 108 : 124, STITKY = W - (K ? 70 : 86), POPIS = K ? 170 : 214;
  const pruhy = K ? { 12: L1 + 10, 24: L1 + 24, 36: L1 + 38 } : { 12: L1 + 12, 24: L1 + 28, 36: L1 + 44 };
  const s = [];
  const hranice = [...prahy, nahore];
  for (let i = 0; i < 3; i++) {
    const a = Math.max(hranice[i], dole), b = Math.min(hranice[i + 1], nahore);
    if (a < b) {
      s.push(`<rect x="${L1}" y="${y(b)}" width="${W - L1}" height="${(y(a) - y(b)).toFixed(1)}" fill="${BARVY_SPA[i]}" fill-opacity="${[0.035, 0.045, 0.06][i]}"/>`);
      s.push(`<rect x="${L1}" y="${y(b)}" width="5" height="${(y(a) - y(b)).toFixed(1)}" fill="${BARVY_SPA[i]}"/>`);
    }
  }
  s.push(`<rect x="${L0}" y="${T}" width="${L1 - L0}" height="${dno - T}" fill="${BARVY.ovladac}"/>`);
  for (let c = dole; c < nahore; c += 10) {
    if (Math.floor(c / 10) % 2 === 0) {
      const x = Math.floor(c / 100) % 2 === 0 ? L0 + 8 : L1 - 30;
      s.push(`<rect x="${x}" y="${y(c + 10)}" width="22" height="${(y(c) - y(c + 10)).toFixed(1)}" fill="${BARVY.text2}" fill-opacity=".13"/>`);
    }
  }
  for (let c = dole; c <= nahore; c += 10) {
    const [x2, op] = c % 100 === 0 ? [L1, 0.75] : c % 50 === 0 ? [L0 + 30, 0.5] : [L0 + 8, 0.3];
    s.push(`<line x1="${L0}" x2="${x2}" y1="${y(c)}" y2="${y(c)}" stroke="${BARVY.text2}" stroke-opacity="${op}"/>`);
    if (c % 100 === 0) s.push(`<text x="${L0 - 8}" y="${y(c) + 5}" text-anchor="end" class="lat-cislo">${c}</text>`);
  }
  s.push(`<rect class="voda" x="${L0}" y="${y(ted)}" width="${L1 + 5 - L0}" height="${(dno - y(ted)).toFixed(1)}" fill="${BARVY.voda}" fill-opacity=".5"/>`);
  s.push(`<line x1="${L0}" x2="${W}" y1="${dno}" y2="${dno}" stroke="${BARVY.text2}" stroke-opacity=".25"/>`);

  prahy.forEach((prah, i) => {
    const yp = y(prah);
    s.push(`<line x1="${L0}" x2="${STITKY}" y1="${yp}" y2="${yp}" stroke="${BARVY_SPA[i]}" stroke-width="1.2" stroke-opacity=".9"/>`);
    s.push(`<rect x="${STITKY}" y="${yp - 11}" width="${W - STITKY}" height="22" rx="4" fill="${BARVY_SPA[i]}"/>`);
    s.push(`<text x="${(STITKY + W) / 2}" y="${yp + 5}" text-anchor="middle" class="lat-stupen" fill="${NA_SPA[i]}">${i + 1}. ${K ? "st." : "stupeň"} ${prah}</text>`);
  });

  s.push(`<g class="lat-pohyb">`);
  s.push(`<line x1="0" x2="${STITKY}" y1="${y(ted)}" y2="${y(ted)}" stroke="${BARVY.vodaSvetla}" stroke-width="2"/>`);
  s.push(`<rect x="0" y="${y(ted) - 12}" width="${L0 - 5}" height="24" rx="4" fill="${BARVY.vodaSvetla}"/>`);
  s.push(`<text x="${(L0 - 5) / 2}" y="${y(ted) + 6}" text-anchor="middle" class="lat-ted">${Math.round(ted)}</text>`);

  const popisky = Object.keys(pruhy).map((h) => [y(pred[h]), +h]).sort((a, b) => a[0] - b[0]);
  const polohy = [];
  for (const [yp] of popisky) polohy.push(polohy.length ? Math.max(yp, polohy[polohy.length - 1] + 34) : yp);
  const posun = Math.max(0, polohy[polohy.length - 1] - (dno - 16));
  popisky.forEach(([yp, h], n) => {
    const ly = polohy[n] - posun, x = pruhy[h], p = pred[h];
    if (rozmezi[h]) {
      const [lo, hi] = rozmezi[h];
      s.push(`<rect x="${x}" y="${y(hi)}" width="10" height="${(y(lo) - y(hi)).toFixed(1)}" rx="2" fill="${BARVY.vodaSvetla}" fill-opacity=".32"/>`);
    }
    s.push(`<rect x="${x - 3}" y="${yp - 2}" width="16" height="4" rx="1" fill="${BARVY.vodaSvetla}"/>`);
    if (h in chmu) s.push(`<path d="M${x + 12} ${y(chmu[h])}l8 -5v10z" fill="${BARVY.text}"/>`);
    s.push(`<path d="M${x + 13} ${yp}H${L1 + (K ? 50 : 66)}L${POPIS - 8} ${ly}H${POPIS - 2}" fill="none" stroke="${BARVY.vodaSvetla}" stroke-opacity=".6"/>`);
    s.push(`<rect x="${POPIS - 2}" y="${ly - 15}" width="${h in chmu ? (K ? 170 : 176) : 124}" height="30" fill="${BARVY.studna}" fill-opacity=".85" rx="3"/>`);
    const dalsi = h in chmu ? `<tspan class="lat-chmu"> · ČHMÚ ${Math.round(chmu[h])}</tspan>` : "";
    s.push(`<text x="${POPIS + 46}" y="${ly + 9}" text-anchor="end" class="lat-hodnota">${Math.round(p)}</text><text x="${POPIS + 52}" y="${ly + 7}" class="lat-osa">cm za ${h} h${dalsi}</text>`);
  });
  s.push(`</g>`);
  // legenda: na šířku v jednom řádku, kompaktně ve dvou
  const ly1 = dno + 16, ly2 = K ? dno + 38 : dno + 16, x2 = K ? L0 : L0 + 196;
  s.push(`<rect x="${L0}" y="${ly1}" width="14" height="10" rx="2" fill="${BARVY.vodaSvetla}" fill-opacity=".32"/><text x="${L0 + 20}" y="${ly1 + 9}" class="lat-legenda">rozmezí nejistoty (90 % chyb)</text>`);
  s.push(`<rect x="${x2}" y="${ly2}" width="14" height="10" fill="${BARVY.voda}" fill-opacity=".5"/><text x="${x2 + 20}" y="${ly2 + 9}" class="lat-legenda">voda teď</text>`);
  if (Object.keys(chmu).length) {
    s.push(`<path d="M${x2 + 94} ${ly2 + 5}l8 -5v10z" fill="${BARVY.text}"/><text x="${x2 + 108}" y="${ly2 + 9}" class="lat-legenda">ČHMÚ</text>`);
  }
  const popis = `Vodočet: teď ${cislo(ted)} cm, ${Object.keys(pruhy).map((h) => `za ${h} h ${cislo(pred[h])} cm`).join(", ")}; stupně povodňové aktivity ${prahy[0]}, ${prahy[1]} a ${prahy[2]} cm.`;
  return `<div class="lat${anim ? " anim" : ""}${K ? " kompakt" : ""}"><svg viewBox="0 0 ${W} ${VY}" role="img" aria-label="${popis}" preserveAspectRatio="xMidYMid meet">${s.join("")}</svg></div>`;
}
