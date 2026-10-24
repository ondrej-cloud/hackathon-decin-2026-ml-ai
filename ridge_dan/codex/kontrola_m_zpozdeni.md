- **Nízká — [zpozdeni_simulace.py:59](/C:/Users/danie/Documents/hackathon-2026-ridge/ridge_dan/provoz/zpozdeni_simulace.py:59):** `np.allclose` připouští malé rozdíly, takže assert nezaručuje požadovanou přesnou shodu při d = 0. Návrh: použít `DataFrame.equals` nebo `np.array_equal`. Na současných datech byla shoda všech čtyř variant ověřena jako přesná.

Další chyby v kontrolovaných bodech nenalezeny:

- Kladný `shift` probíhá před `reindex`; `ffill` používá pouze starší hodnoty. V běžných scénářích nic nedoplňuje, u `model_vi` doplní pouze 1/2/3/6 hodin za posunutou únorovou dírou 2006, mimo hodnocená okna.
- Běžné scénáře trénují na čerstvém `A0`; zpožděná matice slouží pouze pro predikce hodnocených oken. `model_vi` správně používá posun `z + d` při tréninku i hodnocení.
- Zachováno je 22 LOFO oken i stejný čerstvý model jako základ rozdílu. Čerstvé základy v CSV odpovídají ostatním uloženým LOFO výsledkům.
- `rsplit("_", 2)`, odmocnění průtoků a výběr 12/30 stanic jsou správně.

Kontrola proběhla pouze čtením, bez celé simulace a s výpočty omezenými na roky 2006–2020.

**Simulace zpoždění v kontrolovaných scénářích nemá únik z budoucnosti do vstupů.**