/* Ovládání prezentace: slajdy a kroky, škálování plochy, vodopád součtu, mapa hlavních stanic, mřížka 98 vstupů,
   linie řeky jako ukazatel průběhu, vstup prvků po 70 ms, video na mezerník, poznámky řečníka se stopkami, tisk. Bez knihoven. */
(function () {
  'use strict';
  const SVG = 'http://www.w3.org/2000/svg';
  const REDUKCE = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const plocha = document.querySelector('.plocha');
  const slajdy = Array.from(document.querySelectorAll('.slajd'));
  const N = slajdy.length;
  const HLAVNICH = 9;
  const video = document.getElementById('video');
  const hudCas = document.getElementById('hud-cas');
  const poznamky = document.getElementById('poznamky');
  const cerna = document.getElementById('cerna');
  let i = -1, krok = 0, start = null, casovace = [];

  /* poznámky řečníka: čas, kdo, co říká (prezentace/SLAJDY.md doslova); [mezerník] označuje krok decku; „Zdroje:“ byly dřív v patičce slajdu */
  const POZNAMKY = [
    ['0:00–0:40 · Honza', '[mezerník] (nebo klepnutí) spustí video, 24 s bez zvuku: povodeň červen 2013 v Děčíně, vlevo rozliv z předpovědi vydané den předem modelem učeným bez této povodně, vpravo skutečnost (vrchol 1 072 cm, předpověď 952 cm).', 'Honza při spuštění videa, než se rozjede voda:', 'Dobrý den. Červen 2013, největší povodeň za posledních dvacet let. Vlevo je, co náš model předpověděl den předem. Vpravo skutečnost.', 'Pak asi 12 s ticho, voda se rozlévá mezi domy. [mezerník] nebo konec videa: nadpis a 18 h.', 'Model tuhle povodeň nikdy neviděl, a přesto ohlásil třetí stupeň 18 hodin předem. Předpovídáme hladinu v Děčíně a Ústí na 12, 24 a 36 hodin a varujeme před druhým a třetím stupněm. Pro komisi, hasiče a lidi u řeky.', '59 slov (20 při startu videa, 39 po něm), asi 27 s mluvení a 12 s ticha. Čísla: předpověď na 24 h vydaná 1. 6. ve 22:00 už byla nad 560 cm, 3. stupeň voda překročila 2. 6. v 16:00; vrchol 6. 6. ve 2:00 1 072 cm, předpověď 952 cm; na 2. stupeň model varoval jen 2 až 4 h předem (nástup byl rychlý), kdyby se porota zeptala, říct to rovnou. Číslo 27 h patří Borisovi a je na slajdu 7.', 'Zdroje: video z aplikace, mapa Mapbox a OpenStreetMap, terén ČÚZK, záplavová území DIBAVOD, data ČHMÚ.'],
    ['0:40–1:20 · Dan', 'Balíček od pořadatelů má dva roky dat a stanice jen v kraji. Nejvýš proti proudu je Ústí, jen čtyři hodiny před Děčínem. Model jen z něj se plete o 44,6 centimetru, stejně jako „bude jako teď“, a polovinu povodní propásne.', '[mezerník] Odkryje třetí sloupec grafu.', 'Proto jsme vzali hodinový archiv ČHMÚ: dvacet let a dvanáct stanic na Vltavě, horním Labi a Ohři, až 25 hodin proti proudu. Je to stejný zdroj jako balíček, jen delší a s víc stanicemi. Chyba klesla na 17 centimetrů.', '79 slov (strop 86).', 'Na mapě je 7 hlavních stanic z 12 s dobou doběhu vody do Děčína (Ústí 4 h, Nymburk 10 h, Mělník 13 h, Louny 16 h, Praha 17 h, Beroun 23 h); zbylých pět: Vraňany, Kostelec nad Labem, Předměřice, Nespeky, Přelouč.', 'Zdroje: hodinový archiv ČHMÚ 2006–2025, řeky OpenStreetMap, doby doběhu z korelace změn průtoku (docs/DATA.md).'],
    ['1:20–2:10 · Dan', 'Model bere jen to, co je v tu chvíli změřené na řece: hladinu v Děčíně a v Ústí a průtok na dvanácti stanicích, teď a až 36 hodin zpátky. Dohromady 98 čísel.', '[mezerník] Graf: co se stane s chybou, když přidáme další vstup.', 'Srážky, sníh, teplotu, vlhkost, tlak i vítr jsme zkusili. Nic nepomohlo ani o centimetr. Co do Děčína přiteče do 36 hodin, už teče řekou a vidíme to v průtoku. I kdybychom déšť na tři dny dopředu znali přesně, chyba klesne jen o centimetr.', '[mezerník] Rámeček: dvě pasti z budoucnosti.', 'A při přípravě dat jsme našli dvě pasti, které braly informaci z budoucnosti: doplňování děr v datech a čas denních srážek. Obě jsme opravili.', '99 slov (strop 108).', 'Mřížka: hladina v Děčíně a Ústí teď a před 1, 2, 3, 6, 12 a 24 h (2 × 7), průtok 12 stanic teď a před 3, 6, 12, 18, 24 a 36 h (12 × 7), dohromady 98 (src/features.py).', 'Zdroje: validace na 4 povodních 2006–2011, pravidlo: zlepšení aspoň o 1 cm.'],
    ['2:10–3:15 · Ondra', 'Začali jsme laťkou: předpovědí, že bude jako teď. Při povodních se plete o 44 centimetrů.', '[mezerník] Odkryje čtyři modely.', 'Pak čtyři modely, každý dělal jeden z nás, se stejnými pravidly: stejná data, stejné ověření a změna musí zlepšit aspoň o centimetr. Fyzikální model, 25 centimetrů: počítá s pevnou dobou putování vody, jenže ta se mezi povodněmi mění. LightGBM, rozhodovací stromy, 23: neumí předpovědět víc, než kdy viděly, u povodně 2013 daly vrchol o dva a půl metru níž. Neuronová síť, 18: skoro stejně dobrá, ale má přes dvacet tisíc vah na dvě velké povodně a snadno se přeučí. Lineární regrese, 17: nejlepší a nejjednodušší. Vybrali jsme ji před testem.', '[mezerník] Odkryje úpravy přímky.', 'Pak jsme zkoušeli vylepšit i ji: polynom, větší váhu povodní, všechna malá zlepšení dohromady. Nic nebylo lepší o víc než centimetr.', '126 slov (strop 140).', 'Zdroje: validace na 4 povodních 2006–2011, průměrná chyba během povodní, vybráno před testem.'],
    ['3:15–3:55 · Ondra', 'Proč vyhrála přímka? Voda v Děčíně je součet toho, co přiteče po Vltavě, horním Labi a Ohři, a lineární regrese je přesně vážený součet. Tady je předpověď z Borise, vydaná den předem. Průměr 198 centimetrů,', '[mezerník] Děčín a Ústí plus 80, [mezerník] Vltava 89, [mezerník] horní Labe 116, [mezerník] Mělník 96, [mezerník] Ohře minus 2.', '[mezerník] Vyjde 577, nad třetím stupněm, a model varoval. Každé číslo umíme vysvětlit. A zadání samo říká: cílem není co nejsložitější model.', '71 slov (strop 86).', 'Zdroje: Boris 9/2024 z testu, model učený do 2020.'],
    ['3:55–4:30 · Honza', 'Jak víme, že to funguje? Data dělíme v čase, nikdy náhodně, a ověřujeme vždycky na povodních, které model při učení neviděl. Model jsme vybrali na čtyřech vynechaných povodních. Pak jsme každou z osmi povodní 2006 až 2020 jednou vynechali a model naučili na zbytku, to je vícenásobná validace. A test na letech 2021 až 2025 jsme pustili jen jednou, úplně na konci.', '62 slov (strop 75).', 'Zdroje: data ČHMÚ 2006–2025.'],
    ['4:30–5:25 · Honza', 'Graf se kreslí 3 s, pak samo naskočí 27 h (nebo mezerník).', 'Funguje to doopravdy? Tohle je Boris, září 2024, z testu, takže ho model nikdy neviděl. Černá je skutečnost, modrá naše předpověď vydaná den předem. Šedá je „bude jako teď“, ta je vždycky o den pozadu. Třetí stupeň model hlásil 27 hodin předem.', '[mezerník] −55 % a graf vícenásobné validace.', 'A není to jedna šťastná povodeň. Ve vícenásobné validaci jsme každou z osmi povodní jednou vynechali a chyba byla menší na všech osmi, o 34 až 66 procent. Na testu 2021 až 2025 je 22,4 centimetru proti 50,2, o 55 procent menší.', '[mezerník] Řádek o povodni 2013.', 'Povodeň 2013, největší v datech, model ji neviděl: 3. stupeň 18 h předem, vrchol 952 cm proti 1 072. Chyba 47,7 cm proti 97,4 u „bude jako teď“ (o 51 % méně). Je v tréninku, proto ji přehráváme modelem učeným bez ní (ridge_bez2013, Děčín, 24 h předem).', '84 slov (strop 119). Když se nestíhá: z druhého odstavce říct jen „na testu i ve vícenásobné validaci je chyba o 55 procent menší“.', 'Zdroje: test 2021–2025, model učený do 2020, průměrná chyba během povodní, Děčín a Ústí.'],
    ['5:25–5:55 · Tobias', 'Co z toho má město? Z předpovězené hladiny aplikace nakreslí, kam až voda dosáhne: porovná výšku terénu s výškou hladiny. Proti úřední mapě záplavových území to sedí z 82 až 90 procent. Vlevo rozliv z předpovědi vydané den předem, vpravo ze skutečnosti. Běží to živě na webu, každou hodinu nová předpověď.', '51 slov (strop 65).', 'Snímek: povodeň červen 2013 v Děčíně, vrchol 6. 6. 2013 2:00, vlevo rozliv z předpovědi vydané 24 h předem (952 cm), vpravo ze skutečné hladiny (1 072 cm). Kdyby se porota zeptala, jestli je to hydraulický model: záložní Z7.', 'Zdroje: mapa Mapbox a OpenStreetMap, terén ČÚZK DMR 5G, záplavová území DIBAVOD, data ČHMÚ.'],
    ['5:55–6:45 · Tobias', 'Kde to selže? Na 36 hodin je chyba skoro dvakrát větší než na 24, voda, která přijde, ještě neteče žádnou stanicí. Vrchol vyšší, než jaký model kdy viděl, podhodnotí. A přívalové povodně na malých přítocích, jako je Ploučnice nebo Kamenice, nevidí vůbec. Na dva až tři dny dopředu by pomohla předpověď počasí: s přesnou předpovědí by u dešťové povodně 2010 chyba na 72 hodin klesla o 40 procent. Jenže archiv starých předpovědí, na kterém by se model učil, neexistuje.', '[mezerník] Závěrečná věta, Děkujeme a QR na repozitář.', 'Z otevřených dat zdarma: o povodni v Děčíně víte den předem, s modelem, který se vejde na jeden obrázek. Děkujeme.', '99 slov (strop 108).', 'Na slajdu je jediná řádka se zdroji v celém decku (licence map).'],
    ['Záloha Z1 · Dan nebo Ondra', 'Proč jen lineární regrese? Na čtyřech povodních, které model neviděl, vyšla nejlíp: 17,1 cm, síť 17,8, LightGBM 23,1, fyzikální 24,8; velkých povodní je v tréninku málo, síť s přes 20 tisíci vahami se z nich naučí i náhodu, regrese má 98 vah a každou umíme vysvětlit.', 'Zdroje: validace, 4 povodně 2006–2011.'],
    ['Záloha Z2 · Ondra', 'Co znamená „bude jako teď“? Předpověď, že za 24 h bude stejně jako teď: na klidné řece přesná, při povodni vždycky o den pozadu, proto 44 až 50 cm chyby, a každý model ji musí porazit.'],
    ['Záloha Z3 · Dan', 'Proč ne srážky? Model dostal skutečný déšť na 3 dny dopředu, jako by předpověď byla dokonalá, a chyba klesla jen o 1 cm; voda, která přijde za 12 až 36 h, už teče v řekách, srážky by pomohly na 2 až 3 dny, jenže archiv starých předpovědí na trénink nemáme.'],
    ['Záloha Z4 · Honza', 'Jak moc se dá předpovědi věřit? Rozmezí od–do je spočítané z 90 % chyb na tréninku podle výšky vody a ověřené na validaci: na klidné vodě se do něj skutečnost vejde v 9 z 10 hodin, na povodních asi v 8 z 10.'],
    ['Záloha Z5 · Ondra', 'Funguje to i na jiné povodni než Boris? Leden 2011 z validace: 3. stupeň hlášen 15 hodin předem, vrchol 730 cm, a ve vícenásobné validaci byl model lepší než „bude jako teď“ na každé z 8 povodní.', 'Zdroje: validace.'],
    ['Záloha Z6 · Honza', 'Podle čeho model rozhoduje (proč jsou některé váhy záporné)? Každé políčko je váha jednoho vstupu, Děčín teď +88 cm, Praha teď +49 cm; oranžová vedle modré znamená, že model odečítá starší hodnotu od nové, tedy počítá trend.', 'Zdroje: 98 vah, zpoždění 0 až 36 h.'],
    ['Záloha Z7 · Honza', 'Je rozliv hydraulický model? Není: výška terénu z ČÚZK proti výšce hladiny, ověřená proti úřední mapě záplavových území, při pětileté vodě 167 ha náš, 183 ha úřední, 165 ha průnik, shoda 0,89; zdi a hráze pod rozlišením terénu nevidí.', 'Zdroje: mapa Mapbox a OpenStreetMap, terén ČÚZK, záplavová území DIBAVOD.'],
    ['Záloha Z8 · Ondra', 'Jak dopadl test (a proč ne síť, když na testu vyšla lépe)? Test 2021 až 2025 jsme pustili jednou na model vybraný předem: 22,4 cm proti 50,2, o 55 % méně, před 3. stupněm varoval pokaždé; síť byla o 1,1 cm lepší, ale výběr podle testu neměníme, jinak by přestal být nezávislý.', 'Zdroje: test 2021–2025, model učený do 2020.'],
    ['Záloha Z9 · Dan', 'Proč jen 36 hodin dopředu? Z nejvzdálenějších stanic, Berounu a Nespek, doteče voda do Děčína za 23 až 25 h; co přijde později, ještě neprotekla žádnou naší stanicí, proto je chyba na 36 h skoro dvakrát větší než na 24 h.', 'Zdroje: korelace změn průtoku, trénovací část.'],
    ['Záloha Z10 · Honza', 'Proč neukazujete živé demo (jak vypadá aplikace dnes)? Sedm minut je málo a demo závisí na Wi-Fi a na tom, jestli ČHMÚ zrovna zveřejnil data; web field-zero.netlify.app je otevřený v druhé kartě a rádi ho ukážeme. Na snímku z 24. 10. v 6:00: Děčín 84 cm, za 24 h 94 cm, ČHMÚ 90 cm; data se stahují živě z ČHMÚ se zpožděním 1 až 3 h.', 'Zdroje: snímek z 24. 10. 6:00.'],
    ['Záloha Z11 · Ondra', 'Proč je předpověď v grafu křivka, když je to lineární regrese? Přímka je vztah mezi tím, co teče proti proudu, a hladinou v Děčíně, ne tvar v čase. Zjednodušeně s jedním vstupem: vlevo je každá hodina 2006–2018 jeden bod (průtok v Mělníku a hladina v Děčíně o 24 h později) a přímka se jimi proloží jednou, hladina za 24 h = 111 + 0,41 × průtok v Mělníku. Vpravo se do té samé přímky každou hodinu dosadí nový průtok a body v čase dají křivku. Skutečný model má 98 vstupů, takže je to vážený součet (slajd 5).', 'Zdroje: src/graf_primka.py, trénink 2006–2018.'],
    ['Záloha Z12 · Ondra', 'Jak je to s přímkou, když je vstupů 98? Když na osu x dáme celý vážený součet, tedy předpověď modelu, a na osu y skutečnou hladinu o 24 h později, je model zase přímka a přesná předpověď leží na úhlopříčce. Na validaci (Děčín +24 h): s jediným vstupem (průtok v Mělníku) jsou body rozházené, chyba 26,5 cm, nad 1. stupněm se přímka ohýbá vedle; s 98 vstupy leží těsně u úhlopříčky, 7,5 cm (přes všechny hodiny; při povodních je u Děčína na 24 h 15,5 cm, hlavní číslo 17,1 cm je průměr přes Děčín, Ústí a 12, 24, 36 h).', 'Zdroje: src/graf_primka.py, validace.'],
  ];

  /* vodopád součtu na slajdu 5 (příspěvky z modelu pro předpověď vydanou 14. 9. 2024 11:00) */
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

  /* 98 vstupů na slajdu 3 (src/features.py): hladina cílů teď a před 1, 2, 3, 6, 12, 24 h; průtok 12 stanic teď a před 3, 6, 12, 18, 24, 36 h */
  const VSTUPY = [
    { rail: 'hladina', hl: true, casy: ['teď', '1', '2', '3', '6', '12', '24'], stanice: ['Děčín', 'Ústí nad Labem'] },
    { rail: 'průtok', casy: ['teď', '3', '6', '12', '18', '24', '36'], stanice: [] },
    { rail: 'dolní Labe', stanice: ['Mělník', 'Ústí nad Labem', 'Děčín'] },
    { rail: 'Vltava', stanice: ['Vraňany', 'Praha-Chuchle', 'Beroun', 'Nespeky'] },
    { rail: 'horní Labe', stanice: ['Kostelec nad Labem', 'Předměřice', 'Nymburk', 'Přelouč'] },
    { rail: 'Ohře', stanice: ['Louny'] },
  ];

  function el(tag, attrs, text) {
    const e = document.createElementNS(SVG, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function h(tag, trida, text) {
    const e = document.createElement(tag);
    if (trida) e.className = trida;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  const cislo = (x, des) => x.toFixed(des || 0).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

  /* škálování plochy 1920 × 1080 na okno (na šířku i výšku, okolí má barvu stránky) */
  function meritko() {
    const s = Math.min(innerWidth / 1920, innerHeight / 1080);
    plocha.style.transform = `translate(${(innerWidth - 1920 * s) / 2}px, ${(innerHeight - 1080 * s) / 2}px) scale(${s})`;
  }
  addEventListener('resize', meritko);
  meritko();

  /* mřížka vstupů */
  function postavVstupy() {
    const karta = document.getElementById('vstupy');
    if (!karta) return;
    let n = 0;
    VSTUPY.forEach(sk => {
      const g = h('div', 'skupina');
      g.appendChild(h('p', 'rail' + (sk.hl ? ' hladina' : ''), sk.rail));
      if (sk.casy) {
        g.appendChild(h('p', 'cas-popis', 'hodin zpátky'));
        sk.casy.forEach(c => g.appendChild(h('p', 'cas', c)));
      }
      sk.stanice.forEach(st => {
        g.appendChild(h('p', 'nazev', st));
        for (let j = 0; j < 7; j++) {
          const b = h('i', 'bunka' + (sk.hl ? ' hl' : ''));
          b.style.setProperty('--i', n++);
          g.appendChild(b);
        }
      });
      karta.appendChild(g);
    });
  }

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
      const top = Math.min(y(od), y(do_)), vyska = Math.max(Math.abs(y(od) - y(do_)), 3);
      const r = el('rect', { x: x(n), y: top, width: sirka, height: vyska, fill: barva, class: 'sloupec ' + trida });
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

  /* mapa na slajdu 2: jen 7 hlavních stanic s dobou doběhu do Děčína (docs/DATA.md, korelace změn průtoku);
     popisek: posun od stanice, zarovnání, název, hodiny */
  const POPISKY = {
    decin: [26, 2, 'start', 'Děčín', ''], usti: [28, 42, 'start', 'Ústí nad Labem', '4 h'], louny: [-20, 62, 'start', 'Louny', '16 h'],
    melnik: [28, 8, 'start', 'Mělník', '13 h'], praha: [30, 16, 'start', 'Praha-Chuchle', '17 h'], nymburk: [26, -16, 'start', 'Nymburk', '10 h'],
    beroun: [-26, 6, 'end', 'Beroun', '23 h'],
  };
  const NAZVY_REK = [['Vltava', 215, 700], ['Labe', 455, 330], ['Ohře', 90, 330], ['Berounka', 290, 975], ['Sázava', 495, 962], ['horní Labe', 1040, 870]];
  function postavMapu() {
    const svg = document.getElementById('mapa'), R = window.REKA;
    if (!R) return;
    for (const k in R.pritoky) svg.appendChild(el('path', { d: R.pritoky[k], class: 'tok pritok' }));
    svg.appendChild(el('path', { d: R.hlavni, class: 'tok hlavni' }));
    NAZVY_REK.forEach(([t, x, y]) => svg.appendChild(el('text', { x, y, class: 'reka-nazev', 'text-anchor': 'middle' }, t)));
    const poradi = ['praha', 'beroun', 'melnik', 'nymburk', 'louny', 'usti', 'decin'];
    poradi.forEach((k, n) => {
      const s = R.stanice[k], p = POPISKY[k], cil = k === 'decin' || k === 'usti';
      const g = el('g', { class: 'stanice' + (cil ? ' cil' : '') });
      g.style.transitionDelay = (1900 + n * 110) + 'ms';
      g.appendChild(el('circle', { cx: s.x, cy: s.y, r: cil ? 16 : 12 }));
      const t = el('text', { x: s.x + p[0], y: s.y + p[1] + 12, 'text-anchor': p[2] }, p[3]);
      if (p[4]) t.appendChild(el('tspan', { class: 'cas' }, ' · ' + p[4]));
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

  /* linie řeky jako ukazatel průběhu na každém slajdu (na videu až s nadpisem); tečka Praha (slajd 1) → Děčín (slajd 9) */
  const mini = [];
  function postavMini() {
    const R = window.REKA;
    if (!R) return;
    slajdy.forEach(s => {
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
    const m = mini[n] || mini[0];
    const t = Math.min(1, Math.max(0, n / (HLAVNICH - 1)));
    const b = m.p.getPointAtLength(m.p.getTotalLength() * t);
    return `translate(${b.x.toFixed(1)}px, ${b.y.toFixed(1)}px)`;
  }
  function miniNastav(n, predchozi) {
    const m = mini[n];
    if (!m) return;
    if (predchozi >= 0 && !REDUKCE) {
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

  /* video na slajdu 1: krok 0 poster, krok 1 přehrávání (mezerník nebo klepnutí), krok 2 nadpis a 27 h (po dohrání nebo mezerníkem) */
  function videoNaKonec() {
    const f = () => { try { video.currentTime = Math.max(0, video.duration - 0.05); } catch (e) { /* bez metadat */ } };
    if (video.readyState >= 1) f(); else video.addEventListener('loadedmetadata', f, { once: true });
  }
  function videoKrok(k, hned) {
    if (!video) return;
    if (k === 0) {
      video.pause();
      try { video.currentTime = 0; } catch (e) { /* bez videa */ }
    } else if (k === 1) {
      if (hned) return;
      if (video.ended || (video.duration && video.currentTime >= video.duration - 0.1)) { try { video.currentTime = 0; } catch (e) { /* bez videa */ } }
      const p = video.play();
      if (p && p.catch) p.catch(() => {});
    } else if (k === 2 && hned) {
      video.pause();
      videoNaKonec();
    }
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
    if (s.classList.contains('video')) videoKrok(k, hned);
    if (hned) { s.getBoundingClientRect(); s.classList.remove('hned'); }
    ukazPoznamky();
  }
  const kroku = s => +(s.dataset.kroky || 0);

  function zrusCasovace() { casovace.forEach(clearTimeout); casovace = []; }
  function pozdeji(f, ms) { casovace.push(setTimeout(f, REDUKCE ? 0 : ms)); }

  /* prvky slajdu, které při vstupu dopředu nastupují po 70 ms: nadpis, pak bloky; řádky a sloupce se rozbalí na děti, kroky nechávají kroky */
  function jednotky(s) {
    const ven = [];
    const pridej = e => {
      if (e.matches('.reka-mini, .pata, .stin-video, .stin-veta, .veta, video, .jen-tisk, [data-krok], [data-odkryj], script')) return;
      if (e.matches('.radek, .sloupec, .ctyri, .trojcisli, .dve-cisla, .web-radek')) { Array.from(e.children).forEach(pridej); return; }
      ven.push(e);
    };
    if (!s.classList.contains('video')) Array.from(s.children).forEach(pridej);
    return ven;
  }

  /* vstup do slajdu: dopředu s animací, zpět v konečném stavu */
  function vstup(s, dopredu) {
    const hned = !dopredu || REDUKCE;
    s.classList.toggle('kresli', !hned);
    if (!hned) {
      const j = jednotky(s);
      j.forEach((e, n) => { e.style.setProperty('--zpozdeni', (n * 70) + 'ms'); e.classList.add('vstup'); });
      pozdeji(() => j.forEach(e => e.classList.remove('vstup')), j.length * 70 + 700);
    }
    s.querySelectorAll('.graf.vlna').forEach(g => {
      g.classList.toggle('hned', hned);
      g.classList.remove('kresli');
      g.getBoundingClientRect();
      g.classList.add('kresli');
      if (!hned) pozdeji(() => g.classList.remove('hned'), 50);
    });
    s.querySelectorAll('[data-pocitej]').forEach(sp => { if (!sp.closest('[data-krok]')) pocitej(sp, hned); });
    if (s.id === 's-reka') { if (hned) mapaKresli(true); else pozdeji(() => mapaKresli(false), 120); }
    if (s.id === 's-boris' && dopredu && krok === 0) pozdeji(() => { if (slajdy[i] === s && krok === 0) nastavKrok(1); }, 3500);
  }
  function odchod(s) {
    zrusCasovace();
    s.classList.remove('kresli');
    s.querySelectorAll('.vstup').forEach(e => e.classList.remove('vstup'));
    s.querySelectorAll('.graf.vlna').forEach(g => { g.classList.add('hned'); g.classList.remove('kresli'); });
    if (s.id === 's-reka') mapaReset();
    if (s.classList.contains('video') && video) video.pause();
  }

  function prejdi(n, dozadu) {
    n = Math.max(0, Math.min(N - 1, n));
    if (n === i) return;
    const predchozi = i;
    if (i >= 0) {
      const byl = slajdy[i];
      odchod(byl);
      byl.classList.remove('aktivni');
      byl.classList.add('odchazi');
      setTimeout(() => byl.classList.remove('odchazi'), 500);
    }
    i = n;
    const s = slajdy[i];
    s.classList.add('aktivni');
    miniNastav(i, predchozi);
    nastavKrok(dozadu ? kroku(s) : 0, true);
    vstup(s, !dozadu);
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

  /* stopky od prvního posunu, jen v panelu poznámek */
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
    document.getElementById('poznamky-hlava-text').textContent = `${i + 1} · ${slajdy[i].dataset.nazev} · ${p[0]}` + (kroku(slajdy[i]) ? ` · krok ${krok}/${kroku(slajdy[i])}` : '');
    const t = document.getElementById('poznamky-text');
    t.innerHTML = '';
    p.slice(1).forEach(odst => {
      const e = document.createElement('p');
      if (odst.startsWith('[')) e.className = 'krok';
      else if (odst.startsWith('Zdroje:')) e.className = 'zdroj';
      e.textContent = odst;
      t.appendChild(e);
    });
  }

  if (video) {
    video.addEventListener('ended', () => { if (slajdy[i].classList.contains('video') && krok === 1) nastavKrok(2); });
    document.getElementById('s-video').addEventListener('click', () => { if (i === 0 && krok < 2) dalsi(); });
  }

  /* tisk: všechno odkryté */
  function tisk() {
    slajdy.forEach((s, n) => {
      s.classList.remove('kresli');
      s.querySelectorAll('.vstup').forEach(e => e.classList.remove('vstup'));
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
      case 'Escape': if (!poznamky.hidden) poznamky.hidden = true; break;
    }
  });
  addEventListener('hashchange', () => {
    const n = parseInt(location.hash.slice(1), 10);
    if (n >= 1 && n <= N && n - 1 !== i) prejdi(n - 1);
  });

  postavVstupy();
  postavSoucet();
  postavMapu();
  postavMini();
  const zHashe = parseInt(location.hash.slice(1), 10);
  prejdi(zHashe >= 1 && zHashe <= N ? zHashe - 1 : 0);

  window.deck = { prejdi, dalsi, predchozi, nastavKrok, tisk, get slajd() { return i; }, get krok() { return krok; } };
})();
