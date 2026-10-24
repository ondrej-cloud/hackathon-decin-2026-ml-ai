/* Ovládání prezentace: slajdy a kroky, škálování plochy, vodopád součtu, mapa stanic, linie řeky jako ukazatel průběhu,
   poznámky řečníka, hodiny, tisk. Bez knihoven. */
(function () {
  'use strict';
  const SVG = 'http://www.w3.org/2000/svg';
  const REDUKCE = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const plocha = document.querySelector('.plocha');
  const slajdy = Array.from(document.querySelectorAll('.slajd'));
  const N = slajdy.length;
  const HLAVNICH = 10;
  const video = document.getElementById('video');
  const hudCislo = document.getElementById('hud-cislo');
  const hudCas = document.getElementById('hud-cas');
  const poznamky = document.getElementById('poznamky');
  const cerna = document.getElementById('cerna');
  let i = -1, krok = 0, start = null, casovace = [];

  /* poznámky řečníka: čas, kdo, co říká; [mezerník] označuje krok */
  const POZNAMKY = [
    ['0:00–0:25 · Tobias', 'Video bez mluvení. Na konci videa (nebo mezerník) naskočí věta: Tohle je Děčín v září 2024. Náš model to hlásil 27 hodin předem.'],
    ['0:25–0:55 · Tobias', 'Hladina v Děčíně a Ústí za 12, 24 a 36 h, varování před 2. a 3. stupněm a rozliv v mapě. Pro povodňovou komisi, hasiče a lidi u řeky. Den navíc znamená odvézt auta, postavit pytle, vyklidit sklepy.', 'Fotka: Děčín 17. 9. 2024, hladina 621 cm, rozliv z výškového modelu terénu po hodinách.'],
    ['0:55–1:40 · Ondra', 'Hodinový archiv ČHMÚ, 12 stanic na Vltavě, horním Labi a Ohři, 2006–2025. Stejný zdroj jako balíček, jen 20 let a 12 stanic místo 2 let a 3 stanic. Z Prahy do Děčína teče voda 17 až 26 hodin, podle velikosti povodně.', '[mezerník] Odkryje třetí sloupec grafu.', 'S daty jen z balíčku (2 roky, stanice v kraji) by model byl stejně špatný jako „bude jako teď“ a propásl by polovinu povodní.'],
    ['1:40–2:15 · Honza', '98 čísel, jen to, co je v tu chvíli změřené: hladina a průtok teď a za posledních 36 h. Lineární regrese je vážený součet: kolik centimetrů přidá každá řeka. Boris, testovací část, Děčín 24 h dopředu, model učený do roku 2020.', '[mezerník × 6] Přidává řeky jednu po druhé, číslo vpravo roste.', 'Na Borisovi: z průměrné hladiny 198 cm model přičetl Děčín a Ústí +80, Vltavu +89, horní Labe +116, Mělník +96, Ohři −2, vyšlo 577 cm, nad 3. stupněm, a varoval.'],
    ['2:15–2:55 · Dan', '3 další modely: neuronová síť, LightGBM, fyzikální model. 8 úprav přímky: srážky, sníh a teplota, voda ve sněhu, víc stanic, polynom, součiny, větší váha povodní, doba putování podle průtoku, všechno dohromady. Nic nebylo lepší. Validace na 4 povodních 2006–2011, průměr Děčína a Ústí na 12, 24 a 36 h.', '[mezerník] Proč přímka.', 'Voda v Děčíně je součet Vltavy, Labe a Ohře posunutých o dobu putování, a velké povodně jsou v datech jen dvě, na složitý model málo.'],
    ['2:55–3:30 · Ondra', 'Ověřujeme třikrát, pokaždé na povodních, které model neviděl. Dělení v čase, nikdy náhodně. Model jsme vybrali na 4 vynechaných povodních, pak každou z 8 povodní 2006–2020 jednou vynechali (vícenásobná validace) a test 2021–2025 pustili jednou na konci, na finální model.', '[mezerník] Dvě pasti.', 'Data jsme zkontrolovali a našli dvě pasti, které braly informaci z budoucnosti (doplňování děr, denní srážky).'],
    ['3:30–4:10 · Ondra', 'Graf se kreslí v čase 3 s, pak samo naskočí 27 h (nebo mezerník).', 'Předpověď vydaná den předem jde se skutečností, „bude jako teď“ je vždycky o den pozadu. Vrchol 649 cm předpověděl na 611 cm. Model tuhle povodeň nikdy neviděl (testovací část 2021–2025, model učený do roku 2020). Stupně: 1. 400, 2. 490, 3. 560 cm.'],
    ['4:10–4:40 · Ondra', 'O 55 % menší chyba na testu i na všech 8 povodních. Test 2021–2025: 22,4 cm místo 50,2. Vícenásobná validace: 20,1 místo 45,2, na každé povodni o 34 až 66 % méně. Dvakrát stejné číslo, není to náhoda. Průměrná chyba hladiny během povodní, Děčín a Ústí, 12, 24 a 36 h dopředu.', 'Když se nestíhá: jen jednou větou na slajdu 7.'],
    ['4:40–5:50 · Honza', 'Boris v aplikaci: vodočet 14. 9. 2024 11:00, den před 3. stupněm. Dnešek: živá data ČHMÚ a naše předpověď vedle oficiální. Mapa Borise: Děčín, předpověď × skutečnost, rozliv po hodinách. Nacvičené kliknutí po kliknutí, nejvýš 70 s.', 'Když se zasekne: video ze slajdu 1 a jet dál.', 'Pozor: po kliknutí do mapy patří klávesy mapě. Zpět tlačítkem Zavřít mapu vpravo nahoře.'],
    ['5:50–7:00 · Dan, závěr Tobias', 'Na 36 h je chyba dvakrát větší, voda, která přijde, ještě neteče žádnou stanicí. Srážky na 12–36 h nepomáhají, voda už je v řekách. Vrcholy vyšší než kdy v tréninku podhodnotí, s oficiální předpovědí ČHMÚ se srovnat neumíme. Dál: předpověď srážek pro 2–3 dny, dvoustupňové varování.', '[mezerník] Závěrečná věta.', 'Z otevřených dat zdarma: o povodni v Děčíně den předem, s modelem, který se vejde na jeden obrázek. Děkujeme.'],
    ['Záloha · proč lineární regrese', 'Na povodních, které model neviděl, vyšla nejlíp (17,1 cm; síť 17,8, LightGBM 23,1, fyzikální 24,8). Nemá se na čem přeučit: Děčín 24 h má chybu na tréninku 19,7 cm a na validaci 15,5 cm (17,1 je průměr obou stanic a tří horizontů). Každou váhu vysvětlíme fyzikálně.'],
    ['Záloha · bude jako teď', 'Předpověď, že hladina za 24 h bude stejná jako teď. Při povodni vždycky o den pozadu, proto 44 až 50 cm chyby.'],
    ['Záloha · proč ne srážky', 'Horní mez: model dostal skutečný déšť na 3 dny dopředu, jako by předpověď počasí byla dokonalá. Chyba klesla jen o 1 cm, varování nepřišlo dřív. Déšť, který spadne teď, doteče do Děčína až za víc než 36 h. První nárůst vidíme v průtocích proti proudu 12–40 h předem.'],
    ['Záloha · jak moc se pleteme', 'Rozmezí od–do z chyb na vynechaných povodních (90 % chyb). Skutečnost se do něj vejde v 8 až 9 z 10 hodin.'],
    ['Záloha · povodeň 2011', 'Validační povodeň leden 2011, 3. stupeň hlášen 15 h předem. Vrchol 730 cm.'],
    ['Záloha · váhy modelu', 'Každé políčko je váha jednoho vstupu: o kolik cm se změní předpověď, když je hodnota o obvyklý rozkmit vyšší. Děčín teď +88, Praha teď +49. Oranžová vedle modré: model odečítá starší hodnotu od nové, počítá, jestli voda stoupá. 98 vah: hladina v Děčíně a Ústí × 7 zpoždění 0 až 24 h, průtok 12 stanic × 7 zpoždění 0 až 36 h.'],
    ['Záloha · rozliv', 'Není to hydraulický model. Výška terénu (ČÚZK DMR 5G, po 10 cm) proti výšce hladiny, ověřená proti úřední mapě: při pětileté vodě 167 ha náš, 183 ha úřední, 165 ha průnik, shoda 0,89.'],
  ];

  /* vodopád součtu na slajdu 4 (příspěvky z modelu pro předpověď vydanou 14. 9. 2024 11:00) */
  const SOUCET = {
    zaklad: 197.78, predpoved: 577.08,
    kroky: [['Děčín', 'a Ústí', 80.15], ['Vltava', '', 89.42], ['horní', 'Labe', 115.84], ['Mělník', '', 95.46], ['Ohře', '', -1.57]],
  };
  const SOUCTY = [];
  (function () {
    let s = SOUCET.zaklad;
    SOUCTY.push(s);
    for (const k of SOUCET.kroky) { s += k[2]; SOUCTY.push(s); }
    SOUCTY.push(SOUCET.predpoved);
  })();
  /* popisky příspěvků zaokrouhlené metodou největšího zbytku, aby jejich součet seděl se zaokrouhlenou předpovědí (Mělník 95,46 → +96) */
  const POPISKY_SOUCTU = (function () {
    const hodnoty = [SOUCET.zaklad, ...SOUCET.kroky.map(k => k[2])];
    const dolu = hodnoty.map(Math.floor);
    const chybi = Math.round(SOUCET.predpoved) - dolu.reduce((a, b) => a + b, 0);
    const poradi = hodnoty.map((v, j) => [v - dolu[j], j]).sort((a, b) => b[0] - a[0]);
    for (let j = 0; j < chybi; j++) dolu[poradi[j][1]] += 1;
    return dolu;
  })();

  function el(tag, attrs, text) {
    const e = document.createElementNS(SVG, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    return e;
  }
  const cislo = (x, des) => x.toFixed(des || 0).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

  /* škálování plochy 1920 × 1080 na okno */
  function meritko() {
    const s = Math.min(innerWidth / 1920, innerHeight / 1080);
    plocha.style.transform = `translate(${(innerWidth - 1920 * s) / 2}px, ${(innerHeight - 1080 * s) / 2}px) scale(${s})`;
  }
  addEventListener('resize', meritko);
  meritko();

  /* vodopád */
  function postavSoucet() {
    const svg = document.getElementById('soucet');
    const L = 130, R = 1072, T = 26, B = 500, MAX = 700;
    const y = cm => T + (MAX - cm) / MAX * (B - T);
    const slot = (R - L) / 7, sirka = 86;
    const x = n => L + slot * n + (slot - sirka) / 2;
    for (let cm = 0; cm <= MAX; cm += 100) {
      svg.appendChild(el('line', { x1: L, x2: R, y1: y(cm), y2: y(cm), class: cm ? 'mriz' : 'osa' }));
      svg.appendChild(el('text', { x: L - 16, y: y(cm) + 10, 'text-anchor': 'end' }, String(cm)));
    }
    svg.appendChild(el('text', { x: 40, y: (T + B) / 2, 'text-anchor': 'middle', transform: `rotate(-90 40 ${(T + B) / 2})` }, 'hladina v Děčíně za 24 h (cm)'));
    [[400, 'spa1', '1. stupeň'], [490, 'spa2', '2. stupeň'], [560, 'spa3', '3. stupeň']].forEach(([cm, trida, nazev]) => {
      svg.appendChild(el('line', { x1: L, x2: R, y1: y(cm), y2: y(cm), class: 'spa ' + trida }));
      const g = el('g', { class: 'spa-stitek ' + trida });
      g.appendChild(el('rect', { x: R + 14, y: y(cm) - 21, width: 156, height: 42, rx: 21 }));
      g.appendChild(el('text', { x: R + 14 + 78, y: y(cm) + 10, 'text-anchor': 'middle' }, nazev));
      svg.appendChild(g);
    });
    const sloupec = (n, od, do_, barva, trida, krok) => {
      const top = Math.min(y(od), y(do_)), h = Math.max(Math.abs(y(od) - y(do_)), 3);
      const r = el('rect', { x: x(n), y: top, width: sirka, height: h, fill: barva, class: 'sloupec ' + trida });
      if (krok) r.dataset.krok = krok;
      svg.appendChild(r);
      return top;
    };
    const popisek = (n, top, text, krok) => {
      const t = el('text', { x: x(n) + sirka / 2, y: top - 14, 'text-anchor': 'middle', class: 'hodnota' }, text);
      if (krok) t.dataset.krok = krok;
      svg.appendChild(t);
    };
    const kategorie = (n, radky, silna) => radky.forEach((r, j) => {
      if (r) svg.appendChild(el('text', { x: x(n) + sirka / 2, y: B + 40 + j * 32, 'text-anchor': 'middle', class: 'kategorie' + (silna ? ' silna' : '') }, r));
    });
    let dosud = SOUCET.zaklad;
    popisek(0, sloupec(0, 0, dosud, 'var(--seda)', 'zaklad'), cislo(POPISKY_SOUCTU[0]));
    kategorie(0, ['průměrná', 'hladina']);
    SOUCET.kroky.forEach(([a, b, v], j) => {
      const n = j + 1, zaporne = v < 0;
      const top = sloupec(n, dosud, dosud + v, zaporne ? 'var(--oranz)' : 'var(--modra-svetla)', zaporne ? 'shora' : '', n);
      popisek(n, top, (zaporne ? '−' : '+') + cislo(Math.abs(POPISKY_SOUCTU[n])), n);
      kategorie(n, [a, b]);
      dosud += v;
    });
    popisek(6, sloupec(6, 0, SOUCET.predpoved, 'var(--modra)', '', 6), cislo(SOUCET.predpoved), 6);
    kategorie(6, ['předpověď', 'na 15. 9.'], true);
  }

  /* mapa stanic na slajdu 3; popisek: posun od stanice, zarovnání, text (\n zalomí řádek, Kostelec se jinam mezi řeky nevejde) */
  const POPISKY = {
    decin: [26, 2, 'start', 'Děčín'], usti: [28, 40, 'start', 'Ústí nad Labem'], louny: [0, 56, 'middle', 'Louny'],
    melnik: [28, 10, 'start', 'Mělník'], vranany: [-30, -8, 'end', 'Vraňany'], kostelec: [-38, 102, 'start', 'Kostelec\nnad Labem'],
    praha: [30, 16, 'start', 'Praha-Chuchle'], nymburk: [26, -14, 'start', 'Nymburk'], jizera: [20, -32, 'middle', 'Předměřice'],
    beroun: [-24, 4, 'end', 'Beroun'], sazava: [28, 12, 'start', 'Nespeky'], prelouc: [-10, -28, 'end', 'Přelouč'],
  };
  const NAZVY_REK = [['Vltava · 4,5 h', 215, 700], ['Labe · 12 h', 455, 330], ['4 h', 335, 160], ['Ohře · 12 h', 60, 330], ['Berounka', 290, 975], ['Sázava', 495, 962], ['horní Labe', 1040, 870]];
  function postavMapu() {
    const svg = document.getElementById('mapa'), R = window.REKA;
    if (!R) return;
    for (const k in R.pritoky) svg.appendChild(el('path', { d: R.pritoky[k], class: 'tok pritok' }));
    svg.appendChild(el('path', { d: R.hlavni, class: 'tok hlavni' }));
    NAZVY_REK.forEach(([t, x, y]) => svg.appendChild(el('text', { x, y, class: 'reka-nazev', 'text-anchor': 'middle' }, t)));
    const poradi = ['praha', 'beroun', 'sazava', 'vranany', 'melnik', 'kostelec', 'jizera', 'nymburk', 'prelouc', 'louny', 'usti', 'decin'];
    poradi.forEach((k, n) => {
      const s = R.stanice[k], p = POPISKY[k], cil = k === 'decin' || k === 'usti';
      const g = el('g', { class: 'stanice' + (cil ? ' cil' : '') });
      g.style.transitionDelay = (1900 + n * 90) + 'ms';
      g.appendChild(el('circle', { cx: s.x, cy: s.y, r: cil ? 16 : 11 }));
      const t = el('text', { x: s.x + p[0], y: s.y + p[1] + 12, 'text-anchor': p[2] });
      p[3].split('\n').forEach((r, j) => t.appendChild(el('tspan', { x: s.x + p[0], dy: j ? '1em' : '0' }, r)));
      g.appendChild(t);
      svg.appendChild(g);
    });
    svg.querySelectorAll('.reka-nazev').forEach(t => { t.style.transitionDelay = '2600ms'; });
    svg.querySelectorAll('.tok').forEach(p => {
      const L = p.getTotalLength();
      p.style.strokeDasharray = L;
      p.style.strokeDashoffset = L;
    });
  }
  function mapaKresli(hned) {
    const svg = document.getElementById('mapa');
    svg.classList.toggle('hned', !!hned);
    svg.querySelectorAll('.tok').forEach(p => { p.style.strokeDashoffset = 0; });
    svg.classList.add('hotovo');
  }
  function mapaReset() {
    const svg = document.getElementById('mapa');
    svg.classList.add('hned');
    svg.classList.remove('hotovo');
    svg.querySelectorAll('.tok').forEach(p => { p.style.strokeDashoffset = p.style.strokeDasharray; });
  }

  /* linie řeky jako ukazatel průběhu v každém slajdu kromě videa */
  const mini = [];
  function postavMini() {
    const R = window.REKA;
    if (!R) return;
    const vzor = el('path', { d: R.hlavni });
    slajdy.forEach((s, n) => {
      if (n === 0) { mini.push(null); return; }
      const svg = el('svg', { viewBox: '150 -30 370 950', class: 'reka-mini', 'aria-hidden': 'true' });
      const p = el('path', { d: R.hlavni });
      svg.appendChild(p);
      svg.appendChild(el('text', { x: 300, y: 22, 'text-anchor': 'middle' }, 'Děčín'));
      svg.appendChild(el('text', { x: 500, y: 905, 'text-anchor': 'end' }, 'Praha'));
      const g = el('g', { class: 'tecka' });
      g.appendChild(el('circle', { cx: 0, cy: 0, r: 30 }));
      svg.appendChild(g);
      s.appendChild(svg);
      mini.push({ svg, g, p });
    });
  }
  function miniBod(n) {
    const m = mini[n] || mini[1];
    const t = Math.min(1, Math.max(0, (n - 1) / (HLAVNICH - 1)));
    const b = m.p.getPointAtLength(m.p.getTotalLength() * t);
    return `translate(${b.x.toFixed(1)}px, ${b.y.toFixed(1)}px)`;
  }
  function miniNastav(n, predchozi) {
    const m = mini[n];
    if (!m) return;
    if (predchozi >= 1 && !REDUKCE) {
      m.svg.classList.add('hned');
      m.g.style.transform = miniBod(predchozi);
      m.g.getBoundingClientRect();
      m.svg.classList.remove('hned');
    }
    m.g.style.transform = miniBod(n);
  }

  /* počítadla čísel */
  function pocitej(span, hned) {
    const cil = parseFloat(span.dataset.pocitej), od = parseFloat(span.dataset.od || '0'), des = +(span.dataset.des || 0);
    const vypis = v => { span.textContent = cislo(v, des); };
    if (hned || REDUKCE) { vypis(cil); return; }
    const t0 = performance.now(), trvani = 1100;
    const tik = t => {
      const u = Math.min(1, (t - t0) / trvani), e = 1 - Math.pow(1 - u, 3);
      vypis(od + (cil - od) * e);
      if (u < 1) requestAnimationFrame(tik);
    };
    requestAnimationFrame(tik);
  }
  let soucetAnim = null, soucetHodnota = SOUCTY[0];
  function soucetUkaz(k, hned) {
    const span = document.getElementById('soucet-cislo'), blok = document.getElementById('soucet-cislo-blok');
    const cil = SOUCTY[Math.min(k, SOUCTY.length - 1)];
    blok.classList.toggle('varuje', k >= 6);
    if (soucetAnim) cancelAnimationFrame(soucetAnim);
    if (hned || REDUKCE) { soucetHodnota = cil; span.textContent = cislo(cil); return; }
    const od = soucetHodnota, t0 = performance.now(), trvani = 650;
    const tik = t => {
      const u = Math.min(1, (t - t0) / trvani), e = 1 - Math.pow(1 - u, 3);
      soucetHodnota = od + (cil - od) * e;
      span.textContent = cislo(soucetHodnota);
      if (u < 1) soucetAnim = requestAnimationFrame(tik);
    };
    soucetAnim = requestAnimationFrame(tik);
  }

  /* kroky uvnitř slajdu */
  function nastavKrok(k, hned) {
    const s = slajdy[i];
    krok = k;
    document.body.dataset.krokSlajdu = k;
    s.classList.toggle('hned', !!hned);
    s.querySelectorAll('[data-krok], [data-odkryj]').forEach(e => {
      const v = +(e.dataset.krok || e.dataset.odkryj);
      const bylo = e.classList.contains('je'), bude = k >= v;
      e.classList.toggle('je', bude);
      if (bude && !bylo) e.querySelectorAll('[data-pocitej]').forEach(sp => pocitej(sp, hned));
      if (bude && !bylo && e.matches('[data-pocitej]')) pocitej(e, hned);
    });
    if (s.id === 's-soucet') soucetUkaz(k, hned);
    if (hned) { s.getBoundingClientRect(); s.classList.remove('hned'); }
    ukazPoznamky();
  }
  const kroku = s => +(s.dataset.kroky || 0);

  function zrusCasovace() { casovace.forEach(clearTimeout); casovace = []; }
  function pozdeji(f, ms) { casovace.push(setTimeout(f, REDUKCE ? 0 : ms)); }

  /* vstup do slajdu: dopředu s animací, zpět v konečném stavu */
  function vstup(s, dopredu) {
    const hned = !dopredu || REDUKCE;
    s.querySelectorAll('.graf.vlna').forEach(g => {
      g.classList.toggle('hned', hned);
      g.classList.remove('kresli');
      g.getBoundingClientRect();
      g.classList.add('kresli');
      if (!hned) pozdeji(() => g.classList.remove('hned'), 50);
    });
    s.querySelectorAll(':scope > .hlava-s-cislem [data-pocitej], :scope .trojcisli [data-pocitej]').forEach(sp => pocitej(sp, hned));
    if (s.id === 's-reka') { if (hned) mapaKresli(true); else pozdeji(() => mapaKresli(false), 120); }
    if (s.id === 's-boris' && dopredu && krok === 0) pozdeji(() => { if (slajdy[i] === s && krok === 0) nastavKrok(1); }, 3500);
    if (s.classList.contains('video') && video) {
      try { video.currentTime = 0; } catch (e) { /* bez videa */ }
      const p = video.play();
      if (p && p.catch) p.catch(() => {});
    }
  }
  function odchod(s) {
    zrusCasovace();
    s.querySelectorAll('.graf.vlna').forEach(g => { g.classList.add('hned'); g.classList.remove('kresli'); });
    if (s.id === 's-reka') mapaReset();
    if (s.classList.contains('video') && video) video.pause();
    if (s.id === 's-demo') zavriMapu();
  }

  function prejdi(n, dozadu) {
    n = Math.max(0, Math.min(N - 1, n));
    if (n === i) return;
    const predchozi = i;
    if (i >= 0) { odchod(slajdy[i]); slajdy[i].classList.remove('aktivni'); }
    i = n;
    const s = slajdy[i];
    document.body.dataset.ton = s.classList.contains('tmavy') ? 'tmavy' : 'svetly';
    document.body.classList.toggle('na-videu', s.classList.contains('video'));
    s.classList.add('aktivni');
    miniNastav(i, predchozi);
    nastavKrok(dozadu ? kroku(s) : 0, true);
    vstup(s, !dozadu);
    hudCislo.textContent = `${i + 1} / ${N}`;
    history.replaceState(null, '', '#' + (i + 1));
  }
  function dalsi() {
    spustHodiny();
    if (krok < kroku(slajdy[i])) nastavKrok(krok + 1); else prejdi(i + 1);
  }
  function predchozi() {
    spustHodiny();
    if (krok > 0) nastavKrok(krok - 1); else prejdi(i - 1, true);
  }

  /* hodiny od prvního posunu */
  function spustHodiny() {
    if (start) return;
    start = Date.now();
    setInterval(() => {
      const s = Math.floor((Date.now() - start) / 1000);
      hudCas.textContent = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
      hudCas.className = s >= 420 ? 'pres' : s >= 390 ? 'pozor' : '';
    }, 500);
  }

  /* poznámky */
  function ukazPoznamky() {
    if (poznamky.hidden) return;
    const p = POZNAMKY[i] || ['', ''];
    document.getElementById('poznamky-hlava').textContent = `${i + 1} · ${slajdy[i].dataset.nazev} · ${p[0]}` + (kroku(slajdy[i]) ? ` · krok ${krok}/${kroku(slajdy[i])}` : '');
    const t = document.getElementById('poznamky-text');
    t.innerHTML = '';
    p.slice(1).forEach(odst => {
      const e = document.createElement('p');
      if (odst.startsWith('[')) e.className = 'krok';
      e.textContent = odst;
      t.appendChild(e);
    });
  }

  /* mapa v demu */
  const ramec = document.getElementById('ramec');
  function nactiMapu() {
    const s = document.getElementById('s-demo');
    if (!ramec.querySelector('iframe')) {
      const f = document.createElement('iframe');
      f.src = '../mapa/2024-09_decin.html';
      f.loading = 'lazy';
      f.title = 'Mapa Děčína, Boris 2024: předpověď × skutečnost';
      f.allow = 'fullscreen';
      ramec.appendChild(f);
    }
    document.getElementById('nacist-mapu').hidden = true;
    document.getElementById('zavrit-mapu').hidden = false;
    s.classList.add('mapa-cela');
  }
  function zavriMapu() {
    const s = document.getElementById('s-demo');
    if (!s.classList.contains('mapa-cela')) return;
    s.classList.remove('mapa-cela');
    document.getElementById('zavrit-mapu').hidden = true;
    document.getElementById('nacist-mapu').hidden = false;
    document.body.focus();
  }
  document.getElementById('nacist-mapu').addEventListener('click', nactiMapu);
  document.getElementById('zavrit-mapu').addEventListener('click', zavriMapu);

  if (video) video.addEventListener('ended', () => { if (slajdy[i].classList.contains('video') && krok === 0) nastavKrok(1); });

  /* tisk: všechno odkryté */
  function tisk() {
    slajdy.forEach((s, n) => {
      s.querySelectorAll('[data-krok], [data-odkryj]').forEach(e => e.classList.add('je'));
      s.querySelectorAll('[data-pocitej]').forEach(sp => pocitej(sp, true));
      if (mini[n]) mini[n].g.style.transform = miniBod(n);
    });
    document.getElementById('soucet-cislo').textContent = cislo(SOUCET.predpoved);
    document.getElementById('soucet-cislo-blok').classList.add('varuje');
    mapaKresli(true);
  }
  addEventListener('beforeprint', tisk);

  /* klávesy */
  addEventListener('keydown', e => {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
    if (!cerna.hidden && e.key !== 'b' && e.key !== 'B') { cerna.hidden = true; }
    switch (e.key) {
      case 'ArrowRight': case 'ArrowDown': case ' ': case 'PageDown': case 'Enter': e.preventDefault(); dalsi(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp': case 'Backspace': e.preventDefault(); predchozi(); break;
      case 'Home': e.preventDefault(); prejdi(0); break;
      case 'End': e.preventDefault(); prejdi(N - 1); break;
      case 'f': case 'F':
        if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen().catch(() => {});
        break;
      case 'n': case 'N': poznamky.hidden = !poznamky.hidden; ukazPoznamky(); break;
      case 'b': case 'B': cerna.hidden = !cerna.hidden; break;
      case 'Escape': zavriMapu(); if (!poznamky.hidden) poznamky.hidden = true; break;
    }
  });
  addEventListener('hashchange', () => {
    const n = parseInt(location.hash.slice(1), 10);
    if (n >= 1 && n <= N && n - 1 !== i) prejdi(n - 1);
  });

  postavSoucet();
  postavMapu();
  postavMini();
  const zHashe = parseInt(location.hash.slice(1), 10);
  prejdi(zHashe >= 1 && zHashe <= N ? zHashe - 1 : 0);

  window.deck = { prejdi, dalsi, predchozi, nastavKrok, tisk, get slajd() { return i; }, get krok() { return krok; } };
})();
