<!-- Text převedený z ufp-ubihajici-elektrony.pdf (obrázky jsou jen v PDF) -->

Určení parametrů ubíhajících elektronů
z obrázků rychlé infračervené kamery
Úvodní text k hackathonu

Vítejte na hackathonu! Během něj se podíváte do světa termojaderné fúze –
technologie, která by jednou mohla vyrábět téměř nevyčerpatelnou a čistou
energii. Vaším úkolem bude naprogramovat a natrénovat neuronovou síť,
která z obrázku pořízeného rychlou infračervenou kamerou určí vlastnosti
takzvaných ubíhajících elektronů – například jakou mají energii. Jde o
skutečný problém, na kterém dnes pracují vědci po celém světě.

Než se pustíte do práce, projděte si tento úvod. Dozvíte se z něj, odkud se
ubíhající elektrony berou, proč jsou nebezpečné, jak je můžeme „vidět“
kamerou a jak vypadají data, se kterými budete pracovat. Nebojte se –
žádné předchozí znalosti fyziky plazmatu nepotřebujete.

Konkrétní zadání vašeho úkolu a popis dat, která budete k řešení používat,
najdete na konci dokumentu.


Fúze a tokamaky
Slunce i ostatní hvězdy září díky jaderné fúzi – slučování lehkých atomových
jader (hlavně vodíku) na těžší. Při tom se uvolňuje obrovské množství energie.
Aby se jádra mohla sloučit, musí do sebe narazit velkou rychlostí, a proto je
potřeba palivo zahřát na teploty v řádu desítek milionů stupňů Celsia. Při
takových teplotách už atomy nedrží pohromadě – elektrony se oddělí od
jader a vznikne plazma, tedy horký plyn z elektricky nabitých částic.

Přímý dotek takto horkého plazmatu by nevydržela žádná nádoba. Protože
jsou ale částice plazmatu nabité, lze je udržet magnetickým polem.
Nejrozšířenějším zařízením tohoto typu je tokamak – vakuová komora ve tvaru
prstence (podobného donutu), obklopená silnými cívkami. Nabité částice se
v magnetickém poli pohybují po šroubovicích kolem magnetických siločar, a
tak obíhají dokola uvnitř prstence, aniž by se dotkly stěn. Mezi známé
tokamaky patří evropský JET ve Velké Británii (v provozu 1983–2023), český
tokamak COMPASS-U, který se staví v Praze, nebo mezinárodní ITER,
budovaný ve Francii.

Plazmatem v tokamaku navíc teče silný elektrický proud – u velkých zařízení
až miliony ampér. Proud vybuzuje centrální cívka (solenoid) uprostřed
tokamaku: změnou proudu v ní vzniká v plazmatu kruhové elektrické pole,
které míří dokola podél prstence a pohání nabité částice (Obrázek 1).
Tokamak tak funguje podobně jako transformátor, v němž centrální solenoid
tvoří primární vinutí a plazma vinutí sekundární. Právě toto kruhové elektrické
pole ale může za určitých podmínek urychlit část elektronů na obrovské
rychlosti – a vytvořit tak ubíhající elektrony.




Obrázek 1: Schéma tokamaku. Plazma (růžově) drží magnetické pole složené z toroidálního
  pole (toroidal magnetic field) vytvářeného cívkami toroidálního pole (toroidal field coils,
 modře) a poloidálního pole (poloidal magnetic field, zelené šipky) vytvářeného proudem v
 plazmatu (plasma electrical current, horizontální zelená šipka). Výsledné siločáry mají tvar
 šroubovice (helical magnetic field). Centrální solenoid (central solenoid, zeleně) indukuje v
                plazmatu kruhové elektrické pole, které proud pohání. Zdroj:
                 [https://www.energy.gov/science/doe-explainstokamaks].



Ubíhající elektrony
Kruhové elektrické pole v tokamaku neustále urychluje elektrony dokola podél
prstence. Za normálních podmínek ale elektrony nezrychlují donekonečna:
při pohybu se srážejí s ostatními částicemi plazmatu a tyto srážky působí jako
tření, které je brzdí. Urychlování a brzdění se vyrovnají a elektrony mají v
průměru stálou rychlost – podobně jako cyklista, který šlape stále stejně silně
proti větru.

Toto tření má ale zvláštní vlastnost: u dostatečně rychlých elektronů slábne s
rostoucí rychlostí. Rychlý elektron totiž proletí kolem ostatních částic tak
rychle, že ho stihnou ovlivnit jen málo. Pokud tedy elektron překročí určitou
kritickou rychlost, elektrické pole ho urychluje víc, než ho srážky dokážou
brzdit. Elektron pak zrychluje dál a dál, až se jeho rychlost přiblíží rychlosti
světla, a získá energii desítek milionů elektronvoltů (MeV) – zhruba tisíckrát víc
než běžné elektrony v plazmatu. Takovým elektronům říkáme ubíhající
(anglicky runaway electrons), protože brzdicímu účinku srážek „utečou“.

Nejčastěji ubíhající elektrony vznikají při disrupci – náhlé ztrátě kontroly nad
plazmatem. Plazma se během ní ve zlomku sekundy ochladí, prudce vzroste
jeho elektrický odpor a rychlý pokles proudu indukuje silné elektrické pole.
Navíc může nastat lavinový efekt: ubíhající elektron při srážce „nakopne“
pomalý elektron, ten se také stane ubíhajícím a jejich počet roste
exponenciálně – podobně jako sněhová lavina.

Svazek ubíhajících elektronů nese obrovskou energii soustředěnou do malého
prostoru. Když narazí do stěny reaktoru, může ji roztavit, nebo dokonce
odpařit (Obrázek 2). V budoucích velkých zařízeních, jako je ITER, by takový
zásah mohl způsobit vážné poškození komponent tokamaku a vést k dlouhé
odstávce kvůli opravám, nebo dokonce trvale vyřadit reaktor z provozu.
Proto vědci intenzivně zkoumají, jak ubíhající elektrony vznikají, jak se chovají,
jak je bezpečně zabrzdit, nebo jak jim předejít. Abychom je ale mohli
zkoumat, musíme je nejdříve umět změřit.
Obrázek 2: Poškození berylliových dlaždic na vnitřní stěně tokamaku JET po zásahu svazkem
   ubíhajících elektronů (výboj č. 86801). Svazek s energií pouhých 0,3 MJ – zhruba tolik
pohybové energie má auto jedoucí rychlostí 80 km/h – roztavil kov v pruhu vysokém asi 10
            cm. Zdroj: Matthews et al. (2015); Tomeš (2023, 2024); Mlynář (2019).



Synchrotronové záření
Ubíhající elektrony mají tak vysokou energii, že by je většina běžných měřicích
přístrojů nezměřila – nebo by je elektrony rovnou zničily. Naštěstí o sobě dávají
vědět samy: vyzařují světlo.

Každá      nabitá   částice,    která    mění    směr     svého    pohybu,      vyzařuje
elektromagnetické záření. Elektrony v tokamaku se nepohybují rovně:
magnetické pole je nutí kroužit kolem magnetických siločar, takže letí po
šroubovici (Obrázek 3). Úhel mezi směrem pohybu elektronu a magnetickým
polem nazýváme úhel sklonu (anglicky pitch angle). Je-li malý, letí elektron
téměř rovně podél siločáry; je-li velký, opisuje široké kroužky. Navíc elektron
obíhá celý prstenec tokamaku, takže jeho dráha je zakřivená i ve velkém
měřítku.
Obrázek 3: Elektron (modře) se v magnetickém poli (červeně) pohybuje po šroubovici kolem
  magnetické siločáry. Úhel sklonu určuje, jak široká je šroubovice ve srovnání s pohybem
                                        podél pole.


Záření elektronů pohybujících se rychlostí blízkou rychlosti světla se nazývá
synchrotronové – podle urychlovačů částic (synchrotronů), kde bylo poprvé
pozorováno. Díky jevům speciální teorie relativity má dvě důležité vlastnosti:

   ●​ Míří prěvážně dopředu. Elektron nesvítí do všech stran jako žárovka, ale
      vyzařuje do úzkého kužele ve směru svého pohybu – podobně jako
      baterka. Čím vyšší je energie elektronu, tím je kužel užší. Kamera proto
      uvidí jen ty elektrony, jejichž záření je v daném okamžiku namířeno
      směrem k ní.
   ●​ Velká část záření připadá na infračervenou oblast.                 U ubíhajících
      elektronů v tokamaku může maximum vyzařování ležet na vlnových
      délkách několika mikrometrů, tedy na infračervenou oblast, kterou
      lidské oko nevidí, ale speciální kamery ano. Množství záření i jeho
      spektrum („barva“) silně závisí na energii elektronu a také na jeho úhlu
      sklonu.

Infračervená kamera se proto umisťuje tak, aby se do komory dívala tečně,
„proti proudu“ letících elektronů (Obrázek 4). V části své dráhy elektrony letí
směrem ke kameře a ta zachytí záření z jejich světelných kuželů. Protože se
vše odehrává velmi rychle – disrupce trvá jen desítky milisekund –, používá se
rychlá kamera, která pořídí až tisíce snímků za sekundu.
    Obrázek 4: Pohled na tokamak shora. Kamera se dívá do komory tečně, takže ubíhající
     elektrony (rychlost vre) letí směrem k ní a kamera zachytí jejich synchrotronové záření
                 (oranžová ploška). Šipka B ukazuje směr magnetického pole.


Výsledný snímek vypadá jako na Obrázku 5. Kromě samotného záření
ubíhajících elektronů jsou na něm vidět i odrazy na lesklých částech komory
a    obrys     vnitřního    sloupku     tokamaku.       Tvar,    velikost   a    jas   skvrny
synchrotronového záření přitom nejsou náhodné – závisí na tom, kolik
ubíhajících elektronů v plazmatu je, kde se nacházejí, jakou mají hybnost a
jaké mají úhly sklonu. Ze snímku tedy můžeme zpětně odhadnout vlastnosti
elektronů. A přesně o to se budete na hackathonu pokoušet.




  Obrázek 5: Snímek z rychlé infračervené kamery na tokamaku JET. Jasná skvrna uprostřed
 (tvaru měsíce) je synchrotronové záření ubíhajících elektronů, oblouky vlevo jsou odrazy na
lesklých žebrech vnější stěny komory, vpravo je vnitřní sloupek tokamaku. Osy udávají polohu
                    v pixelech. Zdroj: [Reux et al PRL 2021, Tomeš 2024].



Rozdělovací funkce ubíhajících elektronů
V plazmatu není jen jeden ubíhající elektron, ale obrovské množství – ve
velkých tokamacích až stovky biliard – a každý má trochu jinou polohu,
energii i směr pohybu. Popisovat každý elektron zvlášť je nemožné. Fyzici
proto používají rozdělovací funkci, která říká, kolik elektronů se nachází na
daném místě plazmatu a jakou mají hybnost a úhel sklonu. Můžete si ji
představit jako histogram: na vodorovné ose je sledovaná veličina a výška
sloupce udává, kolik elektronů do daného intervalu spadá.

Abychom nemuseli pracovat s celou funkcí, popíšeme její tvar jen několika
čísly – parametry. Podobně lze rozložení výšek žáků ve třídě popsat
průměrnou výškou a tím, jak moc se výšky od průměru liší. V našich datech
popisuje rozdělovací funkci sedm parametrů ve třech skupinách:

   ●​ Hybnost      elektronů.     Hybnost      je   součin     hmotnosti      a   rychlosti
       (nerelativisticky, jinak u relativistických elektronů může růst i tehdy, když
       se jejich rychlost už téměř nemění). U elektronů letících téměř rychlostí
       světla už rychlost skoro neroste, hybnost a energie však rostou dál, a
       proto se jejich energie a pohyb popisuje právě hybností. Parametr
       momentum_mean udává střední hybnost, tedy polohu vrcholu rozdělení,
       a momentum_std jeho šířku – jak moc se hybnosti jednotlivých elektronů
       liší (Obrázek 6). V datech je hybnost udávána jako relativistická
       hybnost elektronu v bezrozměrných jednotkách (vydělená součinem
       hmotnosti elektronu a rychlosti světla, mₑc). Pro představu: energie
       elektronu v MeV je přibližně polovina této hodnoty, takže hodnota
       momentum_mean = 5 odpovídá elektronům s energií zhruba 2,5 MeV.
       Takové elektrony letí rychlostí zhruba 98% rychlosti světla.
   ●​ Úhel sklonu. Většina ubíhajících elektronů letí téměř rovnoběžně s
       magnetickým polem, tedy s malým úhlem sklonu; elektronů s velkým
       úhlem sklonu je méně. Parametr pitch_decay popisuje pokles hustoty
       ubíhajících elektronů s rostoucím úhlem sklonu, tedy jak rychle
       elektronů s větším úhlem sklonu ubývá. Jeho hodnoty jsou záporné
       (například −18 na Obrázku 8) – čím větší je jeho absolutní hodnota, tím
      rychleji hustota klesá a tím víc elektronů letí téměř podél magnetického
      pole. Protože synchrotronové záření míří ve směru pohybu elektronu,
      má úhel sklonu velký vliv na tvar skvrny na snímku.
   ●​ Prostorový    profil hustoty. Ubíhající elektrony nejsou v plazmatu
      rozmístěné rovnoměrně – nejčastěji jich bývá nejvíc ve středu a k okraji
      jejich množství ubývá (Obrázek 7). Parametr ne_magaxis udává
      hustotu elektronů ve středu plazmatu (na tzv. magnetické ose) a
      ne_lcfs hustotu na jeho okraji (na tzv. poslední uzavřené magnetické
      ploše). Parametry concavity a convexity popisují tvar křivky mezi nimi
      – jak dlouho zůstává hustota u středu vysoká a jak plynule klesá k okraji.




                                               Obrázek 7: Prostorový profil hustoty
                                             ubíhajících elektronů od středu k okraji
  Obrázek 6: Gaussovo rozdělení elektronů   plazmatu a parametry, které popisují jeho
 podle hybnosti. Parametr momentum_mean                       tvar.
    posouvá vrchol doleva či doprava,
      momentum_std určuje jeho šířku.




Od obrázku k parametrům: inverzní úloha
Spočítat, jak bude snímek vypadat, když rozdělovací funkci známe, je
poměrně přímočaré – stačí nasimulovat záření všech elektronů a sledovat,
která jeho část dopadne do kamery. Takovému postupu říkáme dopředná
úloha. Řeší se pomocí simulačních programů, které sledují dráhy jednotlivých
paprsků světla (tzv. ray tracing) – stejnou technikou se vytváří realistická
grafika v počítačových hrách a filmech.

Ve skutečném experimentu ale potřebujeme opak: máme snímek a chceme
zjistit, jaká rozdělovací funkce ho vytvořila. To je inverzní úloha a ta bývá
mnohem těžší. Různé kombinace parametrů mohou vést k podobně
vypadajícím snímkům, skutečné snímky obsahují šum a odrazy a jednoduchý
vzorec, který by snímek převedl na parametry, neexistuje. Tady přicházejí na
řadu neuronové sítě, které se dokážou naučit i velmi složité závislosti mezi
vzhledem snímku a parametry rozdělovací funkce.

Neuronová síť se ale potřebuje učit na příkladech, u nichž známe správnou
odpověď. Ze skutečných měření takových snímků dostatek není – u
naměřeného snímku správné parametry předem nikdo nezná, a chybí tedy
„učitel“, podle kterého by se síť mohla učit. Proto pro vás byla pomocí 3D
ray-tracingové platformy SERECH připravena sada několika tisíc umělých, ale
velmi věrohodných (syntetických) snímků, u nichž parametry přesně známe.

Vaším úkolem bude ověřit, zda a jak dobře dokáže neuronová síť z takových
snímků parametry rozdělovací funkce určit. Pokud se to podaří, mohli by fyzici
v budoucnu vyhodnocovat snímky z kamery téměř okamžitě – a třeba i
během výboje včas zasáhnout, než ubíhající elektrony napáchají škody.


Popis datasetů
Pro hackathon bylo připraveno několik datasetů, které budete používat k
trénování neuronových sítí i k ověřování přesnosti jejich výsledků. Každý
dataset obsahuje:

   ●​ složku pictures se syntetickými snímky z kamery,
   ●​ soubor parameters.csv s parametry rozdělovací funkce, se kterými byl
      každý     snímek      vytvořen.     Sloupec      run_name       udává       název
      odpovídajícího obrázku ve složce pictures.




  Obrázek 8: Ukázka syntetického snímku a parametrů rozdělovací funkce, se kterými byl
                                       vytvořen.
 Datasety se liší tím, zda obsahují odrazy světla od první stěny reaktoru
 (vnitřního povrchu komory obráceného k plazmatu), a tím, jak byly zvoleny
 hodnoty parametrů. Jsou seřazené od nejjednoduššího po nejtěžší:

       Dataset        Odrazy od stěny    momentum_mean a     Ostatní parametry
                                         pitch_decay

          A           ne                 pravidelná mřížka   pevně dané

          B           ano                pravidelná mřížka   pevně dané

          C           ano                pravidelná mřížka   náhodné

          D           ano                náhodné             náhodné




 Dataset A – bez odrazů. V simulacích byly vypnuté odrazy od první stěny,
 takže na snímcích je jen světlo vyzářené směrem ke kameře. Proto se tento
 dataset interpretuje nejsnáze. Parametry momentum_mean a pitch_decay
 jsou rozmístěny rovnoměrně na pravidelné mřížce mezi zvolenou dolní a horní
 mezí, ostatní parametry jsou pevně dané (stejné pro všechny snímky).

 Dataset B – s odrazy. Stejný jako dataset A, ale se zapnutými odrazy: světlo na
 snímcích mohlo do kamery dopadnout přímo, nebo se odrazit od vnitřní stěny
 tokamaku. Snímky tak víc připomínají skutečná měření (srovnejte s Obrázkem
 5).

 Dataset C – s odrazy, náhodné ostatní parametry. Parametry momentum_mean
 a pitch_decay leží na stejné mřížce jako v datasetech A a B, ostatní
 parametry jsou ale zvoleny náhodně.

 Dataset D – s odrazy, všechny parametry náhodné. Na rozdíl od datasetu C
 jsou náhodně zvoleny všechny parametry, žádný z nich tedy neleží na
 pravidelné mřížce.



Příklad načtení a vizualizace dat pomocí knihoven pandas a Pillow naleznete
na                                                                         adrese
https://repo.tok.ipp.cas.cz/seidl/cvut-ml-hackaton-2026-compass/-/blob/master
/notebooks/uloha-2-ubihajici_elektrony-nacteni-dat.ipynb
Pro vytvoření vhodného python prostředí můžete použít např. správce prostředí
pixi - viz
https://repo.tok.ipp.cas.cz/seidl/cvut-ml-hackaton-2026-compass/-/blob/master
/README.md


Dataset byl poskytnut Ústavem fyziky plazmatu AV ČR (ÚFP) pouze pro účely tohoto
hackatonu a data tedy není povoleno bez předchozího svolení ÚFP jakýmkoliv způsobem
zveřejnit či zpřístupnit komukoliv mimo účastníků hackatonu.


 Úlohy
 Náročnost úloh postupně roste, proto doporučujeme začít datasetem A a
 postupovat až k datasetu D.


 Úloha 1
 Rozdělte dataset A na trénovací a testovací část. Na trénovací části
 natrénujte neuronovou síť, která ze snímku určí parametry momentum_mean a
 pitch_decay. Na testovací části, kterou síť během trénování neviděla, pak
 zjistěte, jak přesně tyto parametry určuje.


 Úloha 2
 Zopakujte úlohu 1 pro datasety B, C a D. U datasetů C a D natrénujte sítě tak,
 aby určovaly všechny parametry rozdělovací funkce: ne_magaxis, ne_lcfs,
 concavity, convexity, momentum_mean, momentum_std a pitch_decay.


 Úloha 3
 Zjistěte, jak si síť poradí se snímky, které se liší od těch, na kterých se učila:

     ●​ Vliv odrazů: síť natrénovanou na datasetu A použijte na snímky z
         datasetu B.
     ●​ Vliv neznámých ostatních parametrů: síť natrénovanou na datasetu B
         použijte na snímky z datasetů C a D.
     ●​ Vliv náhodného rozložení parametrů: síť natrénovanou na datasetu C
         použijte na snímky z datasetu D.
Úloha 4
Zjistěte, kolik snímků je potřeba k natrénování spolehlivé sítě. Z datasetu D
náhodně vyřaďte část snímků, natrénujte síť na zbytku a porovnejte přesnost s
případem, kdy jste použili všechny snímky. Postupně vyřazujte stále víc snímků,
dokud přesnost určených parametrů významně neklesne.


Slovníček pojmů
   ●​ Plazma – horký plyn, ve kterém jsou elektrony oddělené od atomových
      jader, takže je tvořen nabitými částicemi.
   ●​ Tokamak – zařízení ve tvaru prstence, které drží horké plazma pomocí
      silného magnetického pole.
   ●​ Disrupce – náhlá ztráta kontroly nad plazmatem, při níž se plazma
      rychle ochladí a zanikne.
   ●​ Ubíhající elektrony – elektrony urychlené elektrickým polem na rychlost
      blízkou rychlosti světla, u nichž elektrické pole překonává brzdný účinek
      srážek.
   ●​ Hybnost – součin hmotnosti a rychlosti; u velmi rychlých elektronů lépe
      než rychlost vyjadřuje, jak „silný“ je jejich pohyb.
   ●​ Úhel sklonu (pitch angle) – úhel mezi směrem pohybu elektronu a
      směrem magnetického pole.
   ●​ Synchrotronové záření – záření, které vysílají velmi rychlé nabité částice
      při pohybu po zakřivené dráze.
   ●​ Rozdělovací funkce – popis toho, kolik elektronů je na daném místě a
      jakou mají hybnost a úhel sklonu.
   ●​ První stěna – vnitřní povrch komory tokamaku, který je přímo obrácený
      k plazmatu.
   ●​ Ray tracing – simulace, která sleduje dráhy jednotlivých paprsků světla
      včetně jejich odrazů.
   ●​ Syntetický snímek – snímek vytvořený počítačovou simulací, u něhož
      přesně známe parametry, se kterými vznikl.
   ●​ Dopředná úloha – výpočet výsledku (snímku) ze známých příčin
      (parametrů rozdělovací funkce).
   ●​ Inverzní úloha – určení příčin (parametrů rozdělovací funkce) ze
      změřeného výsledku (snímku z kamery).
