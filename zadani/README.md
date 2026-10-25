# Zadání

Na Hackathonu ML/AI 2026 bylo pět úloh: tři od KSI s otevřenými daty z Ústeckého kraje (obce, ovzduší, Labe) a dvě od Ústavu fyziky plazmatu AV ČR s daty z tokamaků. Vybrali jsme Labe. V repu je jen její zadání: celý text v `ksi-3-labe.md` (převedený z PDF), originál s obrázky v `ksi-3-labe.pdf`.

## KSI 3: Dokážete předpovědět Labe?

- **Data:** historická a aktuální data z měřicích profilů na Labi (čas, vodní stav, průtok, teplota vody, stanice). Podle dostupnosti meteorologická data. Informace o stanicích a jejich poloze.
- **Co řešit:** předpověď vodního stavu nebo průtoku, rychlé změny, jak se změna výš po toku projeví níž, vztah k počasí, teplota vody, včasné varování.
- **Výstup:** predikční model, detekce anomálií, klasifikace situací, dashboard, aplikace.
- **Pozor:** časové pořadí. Pro předpověď nepoužívat nic, co v okamžiku předpovědi ještě nebylo známé.
- **V prezentaci musí být:** problém, data, příprava dat, vstupní proměnné, model, ověření kvality, limity.
