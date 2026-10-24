# Pásmo nejistoty: text do prezentace

Pro toho, kdo pásmo na slajdu nebo v aplikaci vysvětluje porotě. Čísla: Děčín za 24 h, lineární regrese (finální
model), podrobnosti v `ZPRAVA_NEJISTOTA.md`.

## Na slajd (jedna věta + obrázek)

**„Nejspíš 708 až 794 cm“: zpětně na 22 povodních padla skutečnost do takového pásma asi v 8 z 10 hodin; při rychlém
vzestupu jen asi ve 2 ze 3.**
Obrázek: `grafy/aplikace_povoden_2011.png` (aplikace, leden 2011) nebo `grafy/pasmo_2011-01-16.png` (světlý graf),
k tomu `grafy/pokryti.png` (dnešní pásmo proti novému).

## Co říct (asi 30 s)

- Předpověď jedním číslem nestačí, komise potřebuje vědět, jak moc jí věřit. Proto ke každé předpovědi ukazujeme
  rozmezí, kam zpětně na minulých povodních padla skutečnost asi v 8 z 10 hodin.
- Rozmezí jsme nevzali z chyb na datech, na kterých se model učil, protože ty jsou menší, než bude v ostrém provozu.
  Vzali jsme chyby na 22 povodních 2006–2020, které model při učení neviděl.
- A ověřili jsme ho poctivě: pro každou povodeň jsme model i rozmezí spočítali bez ní (a bez povodní těsně vedle ní).
  Skutečnost padla do
  rozmezí v 78–80 % hodin, jak slibujeme. Dnešní 90% rozmezí v aplikaci (z učicích dat) jen v 72–83 %.

## Proč je pásmo při rychlém vzestupu širší

- Rozmezí se počítá zvlášť podle toho, jakou změnu model čeká. Když čeká klid, byl v minulosti skoro vždy blízko:
  pásmo je asi **−9 až +24 cm** (33 cm). Když čeká velký vzestup (aspoň o 40 cm za den), mýlil se víc: pásmo je
  **−30 až +56 cm** (86 cm).
- Důvod: model z vodoměrů proti proudu ví, že vlna jde, ale neví přesně, jak bude vysoká a kdy dorazí. U každé povodně
  se to trochu liší (jak rychle se rozleje do nivy, kolik ještě naprší).
- Pásmo není souměrné, nahoru má víc místa. Při vzestupu se skutečnost častěji ukáže vyšší, než model čeká, protože
  lineární model vzestupy spíš tlumí.
- Proto je široké pásmo při vzestupu poctivé: říká „pozor, teď si jsme jistí méně“. To je pro komisi stejně důležitá
  informace jako samotné číslo.

## Co přiznat, když se porota zeptá

- **Při rychlém vzestupu** padne skutečnost do 80% pásma jen asi ve 2 ze 3 případů. Začátek vzestupu, kdy u nás voda
  ještě nestoupá, jsme z vodoměrů lépe poznat nedokázali (zkoušeli jsme trend, výšku hladiny,
  Mělník i poslední chybu). Pomohla by nejspíš srážková předpověď.
- **Největší povodeň 2013** (1 072 cm) je mimo všechno ostatní v souboru: pásmo zachytilo jen 4 z 10 hodin. Když je
  hladina nad historickým rozsahem, pásmu nevěřit.
- **Dnešek:** model pro dnešek je učený na všech datech do 2025, na něm se pásmo ověřit nedalo (nemá neviděná data).
  Kontrola metody na modelu učeném do 2018 a neviděných povodních 2006–2011 (ani kalibrace je neviděla) vyšla spíš
  opatrně (85–90 % místo 80 %).

## Otázka poroty a odpověď

„Proč je rozmezí někdy úzké a někdy skoro metr?“ Protože se nemýlíme pořád stejně. Když řeka stojí, bývají chyby malé. Když od Prahy jde vlna, víme, že přijde, ale ne přesně jak vysoká, a z 22 minulých povodní víme, o kolik
jsme se v takové chvíli mýlili. To rozmezí je vlastně paměť našich minulých chyb v podobné situaci.
