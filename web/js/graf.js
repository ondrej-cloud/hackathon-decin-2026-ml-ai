// Čárový graf v SVG bez knihoven: hladina v čase, pás nejistoty, čáry stupňů povodňové aktivity, odečet pod kurzorem.
// cfg: {serie: [{nazev, x: [Date], y: [cm|null], barva, sirka, car, body, trojuhelnik, stitek}], pas: {x, lo, hi}|null,
//       spa: [prahy], svisla: Date|null, vyska, osaY}; stitek = název řady na konci čáry
import { BARVY, BARVY_SPA } from "./data.js";
import { NB, cislo, denMesic, hodina, isoZ, datumCas, typo } from "./typo.js";

const NA_SPA = [BARVY.text, BARVY.text, "#ffffff"];

export function graf(el, cfg) {
  el.__cfg = cfg;
  el.classList.add("graf");
  vykresli(el);
  if (!el.__ro) {
    let sirka = el.clientWidth;
    el.__ro = new ResizeObserver(() => {
      if (el.clientWidth !== sirka) { sirka = el.clientWidth; vykresli(el); }
    });
    el.__ro.observe(el);
  }
}

function krok(rozsah, n) {
  const hruby = rozsah / n, rad = 10 ** Math.floor(Math.log10(hruby));
  for (const m of [1, 2, 2.5, 5, 10]) if (m * rad >= hruby) return m * rad;
  return 10 * rad;
}

function osaX(xmin, xmax) {
  const hodin = (xmax - xmin) / 3600e3;
  const krokH = hodin <= 36 ? 3 : hodin <= 72 ? 6 : hodin <= 150 ? 12 : hodin <= 300 ? 24 : 48;
  const tiky = [];
  const start = new Date(xmin);
  start.setUTCMinutes(0, 0, 0);
  start.setUTCHours(Math.ceil(start.getUTCHours() / krokH) * krokH);
  if (krokH >= 24) start.setUTCHours(0);
  for (let t = start.getTime(); t <= xmax; t += krokH * 3600e3) {
    if (t < xmin) continue;
    const d = new Date(t);
    const pulnoc = d.getUTCHours() === 0;
    tiky.push({ t, text: pulnoc ? denMesic(isoZ(d)) : hodina(isoZ(d)), velky: pulnoc });
  }
  return tiky;
}

function vykresli(el) {
  const cfg = el.__cfg;
  const W = Math.max(280, el.clientWidth || 600), VY = cfg.vyska || 400;
  const uzke = W < 520;
  // štítky na konci čar: na šířku mají místo vpravo od čáry, na telefonu je nahrazuje krátká legenda pod grafem
  const stitkove = cfg.serie.filter((sr) => sr.stitek && sr.nazev);
  const m = { l: uzke ? 46 : 52, r: stitkove.length && !uzke ? Math.min(150, Math.max(...stitkove.map((sr) => sr.nazev.length)) * 7.5 + 20) : 14, t: 12, b: 40 };
  const vx = (d) => d.getTime();
  const vsechnyX = [], vsechnyY = [];
  for (const s of cfg.serie) { for (const d of s.x) vsechnyX.push(vx(d)); for (const v of s.y) if (v != null) vsechnyY.push(v); }
  if (cfg.pas) { for (const d of cfg.pas.x) vsechnyX.push(vx(d)); for (const v of [...cfg.pas.lo, ...cfg.pas.hi]) if (v != null) vsechnyY.push(v); }
  if (!vsechnyX.length || !vsechnyY.length) { el.innerHTML = ""; return; }
  const xmin = Math.min(...vsechnyX), xmax = Math.max(...vsechnyX);
  let ymax = Math.max(...vsechnyY), ymin = Math.min(...vsechnyY);
  let spaVidet = (cfg.spa || []).filter((p) => p <= ymax * 1.6 + 60);
  ymax = Math.max(ymax, ...spaVidet);
  const rozsah = Math.max(40, ymax - ymin);
  ymin = ymin - rozsah * 0.1; ymax = ymax + rozsah * 0.12;
  const kY = krok(ymax - ymin, 6);
  ymin = Math.floor(ymin / kY) * kY; ymax = Math.ceil(ymax / kY) * kY;
  spaVidet = spaVidet.filter((p) => p >= ymin);
  const X = (t) => m.l + ((t - xmin) / (xmax - xmin || 1)) * (W - m.l - m.r);
  const Y = (v) => m.t + ((ymax - v) / (ymax - ymin)) * (VY - m.t - m.b);
  const s = [];

  s.push(`<g class="mriz">`);
  for (let v = ymin; v <= ymax + 1e-9; v += kY) s.push(`<line x1="${m.l}" x2="${W - m.r}" y1="${Y(v).toFixed(1)}" y2="${Y(v).toFixed(1)}"/>`);
  s.push(`</g>`);

  if (cfg.pas && cfg.pas.x.length) {
    const body = cfg.pas.x.map((d, i) => [X(vx(d)), cfg.pas.lo[i], cfg.pas.hi[i]]).filter((b) => b[1] != null && b[2] != null);
    if (body.length > 1) {
      const horni = body.map(([x, , hi]) => `${x.toFixed(1)},${Y(hi).toFixed(1)}`);
      const dolni = body.map(([x, lo]) => `${x.toFixed(1)},${Y(lo).toFixed(1)}`).reverse();
      s.push(`<path d="M${horni.join("L")}L${dolni.join("L")}Z" fill="${BARVY.modraSvetla}" fill-opacity=".35"/>`);
    }
  }

  (cfg.spa || []).forEach((prah, i) => {
    if (!spaVidet.includes(prah)) return;
    const yp = Y(prah).toFixed(1);
    s.push(`<line x1="${m.l}" x2="${W - m.r}" y1="${yp}" y2="${yp}" stroke="${BARVY_SPA[i]}" stroke-width="1.5" stroke-dasharray="3 4"/>`);
  });

  if (cfg.svisla) {
    const x = X(vx(cfg.svisla)).toFixed(1);
    s.push(`<line x1="${x}" x2="${x}" y1="${m.t}" y2="${VY - m.b}" stroke="${BARVY.caraSilna}" stroke-width="1.5"/>`);
  }

  // body a úseky řad v pixelech: pilulky prahů se umísťují tam, kde neprotínají křivky
  const bodyRad = [], useky = [];
  for (const sr of cfg.serie) {
    let pred = null;
    sr.x.forEach((d, i) => {
      const v = sr.y[i];
      if (v == null) { pred = null; return; }
      const b = [X(vx(d)), Y(v)];
      bodyRad.push(b);
      if (pred && !sr.jenBody) useky.push([pred[0], pred[1], b[0], b[1]]);
      pred = b;
    });
  }
  const obsazeneObd = [];
  const protina = (r, okraj = 6) => {
    const x0 = r.x - okraj, x1 = r.x + r.w + okraj, y0 = r.y - okraj, y1 = r.y + r.h + okraj;
    const uvnitr = (x, y) => x >= x0 && x <= x1 && y >= y0 && y <= y1;
    if (bodyRad.some(([x, y]) => uvnitr(x, y))) return true;
    for (const [ax, ay, bx, by] of useky) {
      if (Math.max(ax, bx) < x0 || Math.min(ax, bx) > x1 || Math.max(ay, by) < y0 || Math.min(ay, by) > y1) continue;
      // úsek protíná obdélník, když kříží některou jeho hranu (krajní body uvnitř už odchytily body řad)
      if (ax !== bx) for (const xe of [x0, x1]) { const k = (xe - ax) / (bx - ax); if (k >= 0 && k <= 1 && uvnitr(xe, ay + k * (by - ay))) return true; }
      if (ay !== by) for (const ye of [y0, y1]) { const k = (ye - ay) / (by - ay); if (k >= 0 && k <= 1 && uvnitr(ax + k * (bx - ax), ye)) return true; }
    }
    return obsazeneObd.some((o) => !(o.x + o.w < r.x || o.x > r.x + r.w || o.y + o.h < r.y || o.y > r.y + r.h));
  };
  const odstup = (r) => Math.min(...bodyRad.map(([x, y]) => Math.hypot(Math.max(0, r.x - x, x - r.x - r.w), Math.max(0, r.y - y, y - r.y - r.h))));

  const stitky = [];
  for (const sr of cfg.serie) {
    const cesty = []; let kus = [];
    sr.x.forEach((d, i) => {
      const v = sr.y[i];
      if (v == null) { if (kus.length) cesty.push(kus); kus = []; return; }
      kus.push(`${X(vx(d)).toFixed(1)},${Y(v).toFixed(1)}`);
    });
    if (kus.length) cesty.push(kus);
    if (!sr.jenBody) {
      const d = cesty.filter((k) => k.length > 1).map((k) => "M" + k.join("L")).join("");
      if (d) s.push(`<path d="${d}" fill="none" stroke="${sr.barva}" stroke-width="${sr.sirka || 2}" stroke-linejoin="round" stroke-linecap="round"${sr.car ? ` stroke-dasharray="${sr.car}"` : ""}/>`);
    }
    if (sr.body || sr.trojuhelnik) {
      sr.x.forEach((d, i) => {
        const v = sr.y[i];
        if (v == null) return;
        const x = X(vx(d)).toFixed(1), y = Y(v).toFixed(1);
        if (sr.trojuhelnik) s.push(`<path d="M${x} ${y}l9 -6v12z" fill="${sr.barva}"/>`);
        else s.push(`<circle cx="${x}" cy="${y}" r="${i === 0 && sr.prvniMaly ? 4 : 6}" fill="${sr.barva}" stroke="#ffffff" stroke-width="2"/>`);
      });
    }
    // štítek přímo na konci čáry místo legendy (jen na šířku; na telefonu je legenda pod grafem)
    if (sr.stitek && sr.nazev && !uzke) {
      let k = sr.y.length - 1;
      while (k >= 0 && sr.y[k] == null) k--;
      if (k >= 0) stitky.push({ x: X(vx(sr.x[k])), y: Y(sr.y[k]) + 4, text: sr.nazev, barva: sr.barva });
    }
  }

  // pilulky prahů: zleva nad čarou, zleva pod čarou, zprava nad, zprava pod; první místo, kde nic neprotínají.
  // Když takové není, pilulka je poloprůhledná s textem s halo, aby čára pod ní zůstala vidět.
  (cfg.spa || []).forEach((prah, i) => {
    if (!spaVidet.includes(prah)) return;
    const yp = Y(prah), sir = uzke ? 92 : 112, vys = 20;
    const kand = [[m.l + 8, yp - vys - 2], [m.l + 8, yp + 2], [W - m.r - sir - 8, yp - vys - 2], [W - m.r - sir - 8, yp + 2]]
      .filter(([, y]) => y >= m.t && y + vys <= VY - m.b).map(([x, y]) => ({ x, y, w: sir, h: vys }));
    let r = kand.find((o) => !protina(o));
    const volne = !!r;
    if (!r) r = kand.slice().sort((a, b) => odstup(b) - odstup(a))[0] || { x: m.l + 8, y: yp - vys - 2, w: sir, h: vys };
    obsazeneObd.push(r);
    const halo = volne ? "" : ` stroke="${NA_SPA[i] === "#ffffff" ? BARVY_SPA[i] : "#ffffff"}"`;
    s.push(`<rect x="${r.x.toFixed(1)}" y="${r.y.toFixed(1)}" width="${sir}" height="${vys}" rx="10" fill="${BARVY_SPA[i]}"${volne ? "" : ' fill-opacity=".92"'}/>`);
    s.push(`<text x="${(r.x + sir / 2).toFixed(1)}" y="${(r.y + 14).toFixed(1)}" text-anchor="middle" class="spa-text${volne ? "" : " halo"}" fill="${NA_SPA[i]}"${halo}>${uzke ? `${i + 1}. st. · ${prah}` : `${i + 1}. stupeň · ${prah} cm`}</text>`);
  });

  stitky.sort((a, b) => a.y - b.y);
  for (let k = 1; k < stitky.length; k++) stitky[k].y = Math.max(stitky[k].y, stitky[k - 1].y + 16);
  const presah = stitky.length ? stitky[stitky.length - 1].y - (VY - m.b - 4) : 0;
  for (const st of stitky) {
    const y = Math.max(m.t + 10, st.y - Math.max(0, presah)).toFixed(1);
    s.push(`<text x="${(st.x + 10).toFixed(1)}" y="${y}" class="cara-stitek" fill="${st.barva}">${typo(st.text)}</text>`);
  }
  // legenda pod grafem jen na telefonu: všechny pojmenované řady, značka odpovídá kresbě čáry
  const legenda = uzke && stitkove.length ? `<div class="graf-legenda">${cfg.serie.filter((sr) => sr.nazev).map((sr) => {
    const znak = sr.jenBody && sr.trojuhelnik ? `<path d="M7 5l9 -6v12z" fill="${sr.barva}"/>`
      : `<line x1="0" x2="22" y1="5" y2="5" stroke="${sr.barva}" stroke-width="${sr.sirka || 2}"${sr.car ? ` stroke-dasharray="${sr.car}"` : ""}/>${sr.body ? `<circle cx="11" cy="5" r="4" fill="${sr.barva}" stroke="#ffffff" stroke-width="1.5"/>` : ""}`;
    return `<span><svg width="22" height="10" aria-hidden="true">${znak}</svg>${typo(sr.nazev)}</span>`;
  }).join("")}</div>` : "";

  s.push(`<g class="osa">`);
  s.push(`<line x1="${m.l}" x2="${m.l}" y1="${m.t}" y2="${VY - m.b}"/><line x1="${m.l}" x2="${W - m.r}" y1="${VY - m.b}" y2="${VY - m.b}"/>`);
  for (let v = ymin; v <= ymax + 1e-9; v += kY) {
    s.push(`<line x1="${m.l - 4}" x2="${m.l}" y1="${Y(v).toFixed(1)}" y2="${Y(v).toFixed(1)}"/><text x="${m.l - 8}" y="${(Y(v) + 4).toFixed(1)}" text-anchor="end">${cislo(v)}</text>`);
  }
  const tiky = osaX(xmin, xmax);
  const minMezera = uzke ? 44 : 56;
  const obsazene = [];
  const volno = (x) => obsazene.every((o) => Math.abs(o - x) >= minMezera);
  for (const t of [...tiky.filter((t) => t.velky), ...tiky.filter((t) => !t.velky)]) {
    const x = X(t.t);
    if (volno(x)) { obsazene.push(x); t.ukaz = true; }
  }
  for (const t of tiky) {
    const x = X(t.t);
    s.push(`<line x1="${x.toFixed(1)}" x2="${x.toFixed(1)}" y1="${VY - m.b}" y2="${VY - m.b + 4}"/>`);
    if (!t.ukaz) continue;
    const kotva = x > W - 30 ? "end" : x < m.l + 10 ? "start" : "middle";
    s.push(`<text x="${x.toFixed(1)}" y="${VY - m.b + 18}" text-anchor="${kotva}"${t.velky ? ' fill="#1d1d1f" font-weight="600"' : ""}>${t.text}</text>`);
  }
  if (cfg.osaY && !uzke) s.push(`<text class="osa-nazev" transform="translate(12 ${((VY - m.b + m.t) / 2).toFixed(1)}) rotate(-90)" text-anchor="middle">${cfg.osaY}</text>`);
  s.push(`</g>`);
  s.push(`<g class="kurzor" hidden><line y1="${m.t}" y2="${VY - m.b}"/></g>`);
  s.push(`<rect class="plocha" x="${m.l}" y="${m.t}" width="${W - m.l - m.r}" height="${VY - m.t - m.b}" fill="transparent"/>`);

  el.innerHTML = `<svg viewBox="0 0 ${W} ${VY}" width="${W}" height="${VY}" role="img" aria-label="${cfg.popis || "graf hladiny"}">${s.join("")}</svg>${legenda}<div class="graf-tip" hidden></div>`;

  // odečet pod kurzorem: nejbližší hodina, hodnoty všech řad v ní
  const svg = el.firstElementChild, tip = el.lastElementChild, kurzor = svg.querySelector(".kurzor");
  const casy = [...new Set(vsechnyX)].sort((a, b) => a - b);
  const hodnoty = new Map();
  cfg.serie.forEach((sr, k) => sr.x.forEach((d, i) => {
    if (sr.y[i] == null) return;
    const t = vx(d);
    if (!hodnoty.has(t)) hodnoty.set(t, []);
    hodnoty.get(t).push([k, sr.y[i]]);
  }));
  const plocha = svg.querySelector(".plocha");
  plocha.addEventListener("pointermove", (e) => {
    const r = svg.getBoundingClientRect();
    const t = xmin + ((e.clientX - r.left) / r.width * W - m.l) / (W - m.l - m.r) * (xmax - xmin);
    let lo = 0, hi = casy.length - 1;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (casy[mid] < t) lo = mid + 1; else hi = mid; }
    if (lo > 0 && Math.abs(casy[lo - 1] - t) < Math.abs(casy[lo] - t)) lo--;
    const tc = casy[lo], radky = hodnoty.get(tc) || [];
    if (!radky.length) { tip.hidden = true; kurzor.hidden = true; return; }
    const x = X(tc);
    kurzor.hidden = false;
    kurzor.firstElementChild.setAttribute("x1", x.toFixed(1));
    kurzor.firstElementChild.setAttribute("x2", x.toFixed(1));
    tip.innerHTML = `<b>${datumCas(isoZ(new Date(tc)))}</b>` + radky.map(([k, v]) =>
      `<div><i style="background:${cfg.serie[k].barva}"></i>${cfg.serie[k].nazev}${NB}<span>${cislo(v)}${NB}cm</span></div>`).join("");
    tip.hidden = false;
    const px = x / W * r.width;
    const vlevo = px + tip.offsetWidth + 14 > r.width;
    tip.style.left = vlevo ? "auto" : `${px + 14}px`;
    tip.style.right = vlevo ? `${r.width - px + 14}px` : "auto";
    tip.style.top = `${Math.max(0, (e.clientY - r.top) - 20)}px`;
  });
  plocha.addEventListener("pointerleave", () => { tip.hidden = true; kurzor.hidden = true; });
}
