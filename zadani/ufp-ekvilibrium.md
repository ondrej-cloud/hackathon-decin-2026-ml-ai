<!-- Text převedený z ufp-ekvilibrium.pdf (obrázky jsou jen v PDF) -->

Určení tvaru a pozice plazmatu z magnetických
měření a ze snímků z ultrarychlé kamery

Cílem úlohy je vytvořit model, který z měření magnetických cívek, případně ze snímků
tokamakového plazmatu pořízených ultrarychlou kamerou určí tvar a polohu plazmatu.



Stručný popis
K dispozici máte dva typy dat z tokamaku COMPASS: (1) měření magnetického pole
cívkami rozmístěnými kolem komory tokamaku a (2) několik tisíc snímků plazmatu z
barevné ultrarychlé kamery Photron FASTCAM. Ke každému okamžiku každého výboje
navíc znáte „správné odpovědi“ – hodnoty popisující tvar a polohu plazmatu. Vytvořte
model, který dostane na vstup okamžitá magnetická měření, snímek plazmatu, nebo
obojí, a co nejpřesněji z nich určí tvar a polohu plazmatu.




Nahoře: Tvar plazmatu a pozice magnetických měření.
Dole: Kamera Photron FASTCAM mini UX100 (4-800 kfps) a typický snímek plazmatu ve viditelném spektru.




                                       ​                                    ​
Detailnější popis (fyzikální souvislosti)
Pro stabilní provoz tokamaku je zásadní nejen dosáhnout vysoké teploty plazmatu, ale
také přesně znát a řídit jeho polohu a tvar. Geometrie plazmatu výrazně ovlivňuje
stabilitu výboje, transport energie i interakci plazmatu se stěnou tokamaku. Tyto
parametry je proto potřeba během výboje průběžně určovat a využívat jako vstup do
systému zpětnovazebního řízení výboje. Špatné určení polohy či tvaru plazmatu může
vést ke zvýšenému tepelnému zatížení stěn tokamaku, ztrátě stability a v krajním
případě k předčasnému ukončení výboje či dokonce poškození zařízení.

Standardní rekonstrukce tvaru a polohy plazmatu vychází především z měření
magnetického pole v okolí plazmatu. Na tokamaku COMPASS jsou k dispozici časové
průběhy z magnetických cívek (IPR) a magnetických smyček (flux loopů), ze kterých lze
pomocí numerické rekonstrukce magnetické rovnováhy určit požadované geometrické
parametry plazmatu. Přesná fyzikální rekonstrukce však může být výpočetně náročná a
je pro použití v reálném čase nevhodná. Pro řízení tokamaku je nutné získat výsledek
prakticky okamžitě, ideálně s latencí v řádu jednotek milisekund.

V rámci této úlohy proto zkusíme vytvořit rychlou aproximaci této rekonstrukce pomocí
metod strojového učení. Pro řadu časových okamžiků a výbojů tokamaku COMPASS
budete mít jako vstupní data (X) k dispozici měření magnetického pole z IPR a
magnetických smyček a jako cílové hodnoty (Y) parametry popisující okamžitý tvar a
polohu plazmatu – například elongaci, horní a dolní triangularitu, radiální a vertikální
polohu středu plazmatu a polohy X-pointu a strike pointů. Úkolem vašeho algoritmu
bude z naměřených signálů co nejpřesněji určit tyto parametry a současně
navrhnout model dostatečně rychlý pro potenciální použití v real-time systému,
tedy s dobou vyhodnocení v řádu milisekund.

Úlohu je možné dále rozšířit o obrazová data z ultrarychlé kamery Photron, která
během výboje zachycuje viditelné záření plazmatu. Z těchto snímků lze některé
geometrické charakteristiky plazmatu rovněž odhadnout. Je proto možné porovnat
rekonstrukci založenou pouze na magnetických měřeních s modelem využívajícím
pouze obrazová data, případně vytvořit multimodální model kombinující oba typy
diagnostiky.

Slovníček pojmů
  Pojem                     Význam

  Tokamak                   Zařízení tvaru prstence (toroidu), v němž silné magnetické
                            pole drží horké plazma mimo stěny komory. Obrázky výše
                            ukazují svislý řez prstencem (tzv. poloidální průřez).

  Okraj plazmatu            Poslední uzavřený magnetický povrch; uvnitř něj je plazma
  (separatrix)              dobře udržené.
  Střed plazmatu             Radiální poloha R (vzdálenost od svislé osy tokamaku) a
                             vertikální poloha Z, obojí v metrech.

  Elongace κ                 Jak moc je plazma protažené svisle: κ = b/a, kde b je
                             polovina výšky a a polovina šířky (malý poloměr) plazmatu.
                             Kruhový průřez má κ = 1.

  Triangularita δ (horní a   Jak moc se průřez podobá písmenu D. Udává, o kolik je
  dolní)                     nejvyšší (resp. nejnižší) bod plazmatu posunutý směrem k ose
                             tokamaku oproti geometrickému středu, vztaženo k malému
                             poloměru a.

  X-bod (X-point)            Místo na okraji plazmatu, kde se magnetické siločáry kříží do
                             tvaru písmene X.

  Strike pointy              Místa, kde siločáry vycházející z okolí X-bodu dopadají na
                             stěnu; stěna je zde nejvíce tepelně namáhaná.

  Limiter                    Místo, kde se plazma přímo dotýká stěny (sloupce R_limiter,
                             Z_limiter).

  Proud plazmatem Ip         Elektrický proud, který teče plazmatem dokola kolem
                             prstence tokamaku. Vytváří magnetické pole, které spolu s
                             polem vnějších cívek drží plazma pohromadě, a zároveň
                             plazma ohřívá. Na tokamaku COMPASS dosahuje až stovek
                             kiloampérů (sloupec plasma_current, v ampérech).

  IPR cívky a magnetické     Magnetické diagnostiky kolem komory. IPR cívky měří složku
  smyčky (flux loopy)        magnetického pole v daném směru (fialové šipky na
                             obrázku), magnetické smyčky měří magnetický tok.

  L-mód, H-mód a ELM         Režimy plazmatu (sloupec mode). V H-módu (high
                             confinement) plazma lépe udržuje energii než v L-módu (low
                             confinement). ELM (edge localized mode) jsou krátké
                             opakované výrony energie a částic z okraje plazmatu v
                             H-módu.




Dataset
Hlavní dataset je tvořen souborem equil_data.csv obsahujícím magnetická měření
a jim odpovídající tvar plazmatu. Ve sloupci discharge je uloženo anonymizované
číslo experimentálního výboje, sloupec time pak obsahuje relativní čas v tomto výboji.
Tyto sloupce pro trénování přímo nepoužívejte, pouze indexují jednotlivá měření.
Sloupce začínající IPR a FL obsahují měřená data, která můžete použít jako vstup
svého modelu. Ostatní sloupce jsou parametry plazmatu, které má váš model určit:
●​     parametry tvaru a polohy plazmatu z obrázku výše
●​     sloupec plasma_current – proud v ampérech, který plazmatem v protéká
●​    sloupce R_limiter a Z_limiter – místo, kde se plazma přímo dotýká stěny
(pokud se dotýká)

Pokud strike pointy existují, jsou vždy dva - jeden s menší, jeden s větší souřadnicí R.
Pozor, pořadí strike pointů ve sloupcích 1 a 2 se v jednotlivých řádcích datasetu může
měnit.

Dataset s kamerovými daty je tvořen složkou img obsahující snímky plazmatu ve
formátu jpg a csv souborem camera_data.csv, který jednotlivým snímkům přiřazuje
číslo výboje a čas v něm. Pomocí nich lze v equil_data.csv vyhledat (interpolovat)
odpovídající tvar plazmatu. Pokud to vašemu modelu pomůže, můžete jako vstup
použít i sloupec mode, který udává aktuální režim plazmatu (L-mód, H-mód nebo ELM).

Příklad načtení a vizualizace dat pomocí knihoven pandas a Pillow a také detailnější
popis     jednotlivých     sloupců     v    csv    tabulce  naleznete    na     adrese
https://repo.tok.ipp.cas.cz/seidl/cvut-ml-hackaton-2026-compass/-/blob/master/noteboo
ks/uloha-1-ekvilibrium-nacteni-dat.ipynb
Pro vytvoření vhodného python prostředí můžete použít např. správce prostředí pixi -
viz
https://repo.tok.ipp.cas.cz/seidl/cvut-ml-hackaton-2026-compass/-/blob/master/READM
E.md

Dataset byl poskytnut Ústavem fyziky plazmatu AV ČR (ÚFP) pouze pro účely tohoto
hackatonu a data tedy není povoleno bez předchozího svolení ÚFP jakýmkoliv způsobem
zveřejnit či zpřístupnit komukoliv mimo účastníků hackatonu.



Cíle
1.​   Vytvořte model pro určení tvaru plazmatu z magnetických měření (lehčí úloha) ​
nebo snímků plazmatu (obtížnější).​

2.​   Zhodnoťte, zda by bylo možné použít vytvořený model v reálném čase při řízení
experimentu (nutná reakce v řádu jednotek až desítek milisekund). Předpokládejte, že
model je možné provozovat na GPU.​

3.​   Vyhodnoťte přesnost modelu pro jednotlivé parametry tvaru plazmatu a stabilitu
výstupů modelu v průběhu časového vývoje plazmatu.​

4.​    Zjistěte, jak se změní úspěšnost modelu, pokud bude mít na vstupu méně
informací (méně magnetických měření či menší část obrazu). Jsou některé vstupy či
části obrazu důležitější než jiné?
Bonusové úkoly pro inspiraci (nepovinné)
●​    Vytvořte model i pro druhý zdroj dat, případně multimodální model, a porovnejte
úspěšnost.​

●​     Jak úspěšnost modelu závisí na počtu trénovacích dat?​

●​      Mnoho tokamaků má pouze černobílé kamery. Mělo by použití černobílé kamery
vliv na úspěšnost obrazového modelu?​

●​    Lze výstup modelu zpřesnit zahrnutím časového vývoje (informace z více časů
za sebou)?​

●​    Kamera se může při výboji klepat či mezi výboji pohnout. Jak citlivý je váš model
na přesné umístění a natočení kamery?​

●​    Magnetická měření mohou být zatížena výrazným šumem, či dokonce driftem,
kdy se v průběhu výboje k měřenému signálu přičítá nefyzikální složka lineárně závislá
na čase (v každém výboji jinak velká):​
​
měřený_signál(t, výboj) = správný_signál(t) + šum(t) + náhodný_koeficient(výboj) * t
​
Jak odolný je váš model vůči takovým chybám měření? Lze ho nějak učinit odolnějším?
Příklad takto zašuměných dat najdete v souboru equil_data_noisy.csv, pro hlubší
analýzu si ale můžete podobný dataset vygenerovat z původního sami pomocí výše
uvedeného vzorce.​

●​    Dokážete říct, na základě kterých částí obrazu či kterých magnetických měření
model tvar plazmatu určuje?

●​    Většina tvarů plazmatu na COMPASSu si byla vzájemně velmi podobná a
parametry plazmatu navzájem korelované. Jak by váš model reagoval, pokud bychom
se rozhodli vytvořit plazma s novým, unikátním tvarem, která tuto korelaci porušuje?



Poznámky

●​     Používejte běžnou metodologii: rozdělte data na trénovací a testovací. Můžete,
ale nemusíte použít křížovou validaci (cross-validation). Data z jednoho výboje si bývají
velmi podobná, proto je rozdělujte po celých výbojích (sloupec discharge), ne po
jednotlivých řádcích – jinak bude odhad přesnosti příliš optimistický.​
●​      Vezměte v potaz, že hodnoty parametrů plazmatu jsou v datech zastoupeny
nerovnoměrně (některé tvary a polohy jsou mnohem častější než jiné). Promyslete, jak
to ovlivní trénování i vyhodnocení modelu.​

●​      Nemusíte vytvářet žádnou aplikaci s grafickým uživatelským rozhraním.
Součástí práce ale musí být např. Jupyter notebooky (lze i Google Colab) s modely a
grafy, které budou obsahovat všechny vaše detailní závěry.​

●​    Výstupem je prezentace, ve které shrnete své výsledky.
