# Danova část prezentace: co jsme zkoušeli navíc a co nevyšlo

Délka 60–90 s, tři slajdy, na každém jeden existující graf. V kostře na 7 minut (`docs/PREZENTACE_7MIN.md`) má Dan
slajd 5 (40 s) a 10. Místo slajdu 5 by bylo potřeba ušetřit dalších 20–50 s jinde, jinak jako záložní slajdy po poděkování.
Rozhodne Tobias s Ondrou.

## Slajd A · „Stromy neumí víc, než viděly“

- **Graf:** `docs/grafy/lgbm_c_povoden2011.png` (povodeň 1/2011, předpověď na 24 h: LightGBM při stoupání přestřelí
  asi o 70 cm, přímka jde hladce).
- **Na slajdu:** velká čísla „LightGBM 23,1 cm“ a „přímka 17,1 cm“, pod nimi „průměrná chyba během povodní“.
- **Proč:** LightGBM (stovky rozhodovacích stromů) na tabulkách obvykle vyhrává. Stromy ale špatně pokračují za hranici
  toho, co viděly, a velké povodně jsou v tréninku jen dvě (8/2010, 6/2013). V ranním průzkumu předpověděl LightGBM
  povodeň 2013 na 823 místo 1 072 cm.

## Slajd B · „Stanice dál proti proudu vidí vlnu dřív“

- **Graf:** `prezentace_dan/grafy/G3_zacatek_vzestupu_stanice.png`.
- **Na slajdu:** „+ 18 stanic ČHMÚ: začátek vzestupu o 5–8 cm přesnější u všech čtyř modelů“ (Děčín +24 h, validace;
  fyzikální model zapojí jen 8 nových stanic).
- **Proč:** stanice na horní Ohři, Berounce nebo Orlici ukážou vlnu dřív, než dorazí do Prahy a Mělníka. Celkově na
  validaci ale regrese s 30 stanicemi lepší není (Děčín +24 h 17,8 proti 15,5 cm, rozdíl dělá jarní povodeň 2006).
- **Srážky jednou větou:** zkoušeli jsme třikrát, i šestihodinové ze synoptických stanic, a nepomohly. Na 12–36 h je
  voda z deště už v řekách a my ji měříme. Kdyby se ptali, graf `docs/grafy/prezentace/Z3_proc_ne_srazky.png`.

## Slajd C · „Přísnější zkouška: 22 povodní místo 4“

- **Graf:** `prezentace_dan/grafy/G4_cerven_2013_g3_vs_tym.png` (červen 2013, předpověď z modelu, který tuhle povodeň
  neviděl: směs G3 41,8 cm, týmový model 47,8 cm).
- **Na slajdu:** „směs přímky a stromů s 30 stanicemi: lepší u 20 z 22 povodní, na původní validaci horší → finále
  zůstává jednoduchá přímka“.
- **Proč:** validace má jen 4 povodně, proto jsme každou z 22 povodní 2006–2020 jednou vynechali (LOFO). Směs G3 tam
  vyšla pro Děčín +24 h 13,9 proti 15,3 cm, ve vícenásobné validaci jen o 0,5 cm lépe (19,6 proti 20,1). Dva modely místo jednoho, bez
  nezávislého testu a na validaci horší, proto ji ukazujeme jako slibný směr, ne jako finální model.

## Mluvený text (asi 80 s)

> Já jsem zkoušel, jestli to jde líp než s jednoduchou přímkou.
>
> **[Slajd A]** Nejdřív LightGBM, stovky rozhodovacích stromů, které na tabulkách obvykle vyhrávají. Tady prohrály:
> na povodních se pletly o 23 centimetrů, přímka o 17. Stromy neumí dobře pokračovat za to, co už viděly, a velké
> povodně jsou v tréninku jen dvě. Při povodni 2011 proto při stoupání přestřelil asi o 70 centimetrů.
>
> **[Slajd B]** Pak jsem přidal 18 dalších stanic ČHMÚ dál proti proudu, třeba na horní Ohři nebo Orlici. Ty vidí
> vlnu dřív. Začátek vzestupu, tedy chvíle, kdy se voda teprve dává do pohybu, se zlepšil u všech čtyř modelů,
> u přímky z 35 na 28 centimetrů. Zkoušel jsem i srážky, i šestihodinové ze synoptických stanic. Spolehlivě
> nepomohly: na 12 až 36 hodin je voda z deště už v řekách a my ji měříme.
>
> **[Slajd C]** Nejdůležitější je ale poctivé hodnocení. Místo čtyř povodní jsem modely zkoušel na všech 22 povodních
> od roku 2006, každou jednou vynechanou. Směs přímky a stromů s 30 stanicemi tam pro Děčín na 24 hodin vyšla lépe u 20 z 22 povodní. Na naší
> původní validaci ale horší, hlavně kvůli jarní povodni 2006 z tání sněhu. Proto ji ukazujeme jako slibný směr
> a finální zůstává jednoduchá přímka.

## Co poctivě nevyšlo (kdyby byl čas nebo otázka)

- LightGBM: 23,1 cm proti 17,1, i jako oprava přímky ji zhoršil (18,7).
- Doba doběhu podle průtoku: 21,8 proti 22,2 cm, pod hranicí 1 cm. Zpomalení vlny při velké povodni nejde změřit,
  nad 1 500 m³/s je v tréninku jen červen 2013.
- Srážky (denní, šestihodinové, i dokonalá předpověď): u regrese nejvýš o 1 cm; LightGBM se šestihodinovými srážkami
  o 1,2 cm lépe na validaci, ale se 4 planými poplachy 3. stupně.
- Neuronová síť s 18 stanicemi nebo se srážkami: beze změny (CV −0,5 a +0,4 cm).
- Nové stanice zhorší jarní povodeň 2006 u regrese (16,0 → 24,7 cm) a u sítě (22,2 → 30,1 cm), přestřelení při rozlivu
  vody do nivy Polabí; u LightGBM a fyziky ne.

## Nejpravděpodobnější otázky na Dana

`OTAZKY_POROTY.md`: 16 (proč ne LightGBM), 22 (proč G3 není finální), 29–31 (srážky), 26 (zpomalení vlny),
a sekce „Nejtěžší otázky“.

Zdroje čísel: `PREHLED_POKUSU.md` (řádky 8, 13, 29–34), `docs/POKUSY.md` (pá 19:45–20:45),
`ridge_dan/STANICE_VSEM.md`, `ridge_dan/ZLEPSENI.md`, `ridge_dan/VALIDACE_ONDRA.md`, `srazky_dan/ZPRAVA_SRAZKY.md`.
