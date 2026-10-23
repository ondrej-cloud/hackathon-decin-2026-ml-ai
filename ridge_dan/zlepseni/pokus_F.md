# Pokus F: Ridge s Huberovou ztrátou (IRLS)

- Co: místo součtu čtverců Huberova ztráta přes IRLS. StandardScaler bez vah (μ, sd z tréninku foldu jako týmová
  pipeline), pak vážený Ridge(alpha 1) jako sklearn `Ridge(sample_weight=w)`. Váhy w = min(1, δ/|r|),
  δ = 1,345 · 1,4826 · MAD reziduí (asi 9,8 cm, přepočítané v každé iteraci), start z obyčejného Ridge, 10 iterací.
  Nic se neladí (δ je standardní volba), takže není co vnořovat.
- Proč: menší vliv extrémů (velké chyby na povodních táhnou čtvercovou ztrátu).
- Kontrola (fold 0, 12 stanic): start IRLS = obyčejný Ridge z motoru (rozdíl 2e-9 cm), vážený Ridge = sklearn se
  stejnými vahami (4e-9 cm). Ztráta „srazí“ váhu asi 22 % tréninkových hodin.

| Varianta | LOFO 22 | rozdíl proti týmu | zlepšeno z 22 | nejhorší zhoršení | splňuje | val Děčín +24 | začátek vzestupu (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|
| týmový Ridge (základ) | 15,29 | | | | | 15,5 | 41,9 | 16,7 | 4 |
| F12 Huber, 12 stanic | 15,91 | +0,62 | 3 (19 horší) | 5,2 | ne | 17,4 | 44,5 | 22,0 | 4 |
| F30 Huber, 30 stanic | nedoběhlo do 00:05 | | | | | | | | |

- F12 na validaci: začátek vzestupu 37,6 (tým 35,4), 2006 21,8 (tým 16,0), přestřelení na stoupání 2006 43 cm
  (tým 57), plané 2./3. SPA 0/0.
- Závěr: Huber týmovému Ridge škodí (horší 19 z 22 povodní, znaménkový test p = 0,0009). Povodně jsou přesně ty
  „extrémy“, které Huber potlačuje, takže se model učí hlavně klid a na povodních podhodnocuje. Méně přestřelí
  v roce 2006, ale za cenu horší chyby. F30 nedoběhl: počítač byl v souběhu s dalšími 6 agenty a session se sítí
  bez volné RAM (pod 0,5 GB volno), pokračující běh `pokus_F.py` skončil kolem 00:09 bez výsledku F30 (proces ukončený zvenku,
  v logu žádná chyba), F30 tedy CHYBÍ. Vzhledem k F12 se neočekává, že by F30 pravidlo splnil.
- Soubory: `pokus_F.py`, `vysledky_F.json` (F12), `pokus_F_beh1_float64.log` (první úplný běh F12 s kontrolou).
