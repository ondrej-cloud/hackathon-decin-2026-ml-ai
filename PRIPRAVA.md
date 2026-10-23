# Příprava počítače na hackathon

Celý tenhle text vlož do Claude Code (stačí spustit `claude` v libovolné složce) a napiš: **„Proveď se mnou tenhle návod, jsem <jméno>.“** Claude udělá všechno sám a u každého kroku řekne, proč ho dělá.

Příkazy, u kterých se přihlašuješ v prohlížeči (`gh auth login`, `kaggle auth login`), spustíš sám: napiš je do Claude Code s vykřičníkem na začátku, třeba `! gh auth login`. Když se příkaz po dvou minutách přesune na pozadí, nevadí, přihlášení v prohlížeči normálně dokonči.

**Pokyny pro Claude:** postupuj krok po kroku a každý krok ověř, než půjdeš dál. Zjisti, jestli jde o Mac, nebo Windows, a použij odpovídající příkazy. Na Windows klidně volej rovnou `.venv\Scripts\python` místo aktivace prostředí. Nic nemaž a nečti přihlašovací údaje. Na konci vypiš, co prošlo a co ne.

## 1. Git a GitHub

**Proč:** kód sdílíme v soukromém repozitáři na GitHubu. Bez přihlášení ho nestáhneš ani do něj nic nenahraješ.

- Mac: `brew install git gh` (když chybí Homebrew, návod je na brew.sh)
- Windows: `winget install Git.Git GitHub.cli`
- Přihlášení: `! gh auth login` (GitHub.com → HTTPS → přihlásit v prohlížeči), pak `gh auth setup-git`, aby Git používal stejné přihlášení.
- Přijmout pozvánku do repozitáře: odkaz v e-mailu od GitHubu, nebo https://github.com/ondrej-cloud/hackathon-decin-2026-ml-ai/invitations
- Ověření: `gh repo view ondrej-cloud/hackathon-decin-2026-ml-ai` musí vypsat popis repozitáře.

## 2. Stáhnout repozitář a přepnout se na svou větev

**Proč:** každý pracuje na své větvi (`ondra`, `dan`, `honza`, `tobias`), takže si nepřepisujeme práci. Do `main` jde jen to, co funguje.

```
git clone https://github.com/ondrej-cloud/hackathon-decin-2026-ml-ai.git
cd hackathon-decin-2026-ml-ai
git switch <jméno>
```

## 3. Python a knihovny

**Proč:** potřebujeme Python 3.11 nebo novější, se starším nové knihovny nefungují. Knihovny se instalují do virtuálního prostředí `.venv` ve složce projektu, takže nic jiného v počítači nerozbijí.

- Mac: `brew install python@3.12 libomp` (`libomp` potřebuje LightGBM, bez něj na Macu nejde spustit)
- Windows: `winget install Python.Python.3.12`

Prostředí a knihovny:

```
# Mac
python3.12 -m venv .venv
source .venv/bin/activate

# Windows
py -3.12 -m venv .venv
.venv\Scripts\activate

pip install pandas numpy scikit-learn lightgbm xgboost optuna shap matplotlib plotly streamlit jupyter torch torchvision kaggle
```

| Knihovna | K čemu ji budeme mít |
|---|---|
| pandas, numpy | načítání a úprava dat, tabulky |
| scikit-learn | základní modely, rozdělení dat, metriky |
| lightgbm, xgboost | gradient boosting, obvykle nejsilnější modely na tabulková data |
| optuna | automatické ladění parametrů modelu |
| shap | vysvětlení, proč model rozhodl tak, jak rozhodl (do aplikace i pro porotu) |
| matplotlib, plotly | grafy |
| streamlit | aplikace, kterou ukážeme porotě |
| jupyter | zkoumání dat po kouscích |
| torch, torchvision | neuronové sítě a předtrénované modely na obrázky |
| kaggle | posílání tréninku na GPU zdarma |

Na starém nebo slabém notebooku stačí bez `torch torchvision`, ušetří to kolem 1 GB.

## 4. Ověřit, že všechno funguje

**Proč:** chyby v instalaci chceme najít doma, ne na místě.

```
python -c "import pandas, sklearn, lightgbm, xgboost, streamlit; print('OK')"
python kaggle/gpu-test/gpu_test.py
```

Druhý příkaz změří, jak rychle tvůj počítač počítá neuronové sítě, a vypíše to v TFLOPS (čím víc, tím rychleji). Pro srovnání: Ondrův MacBook M1 má 0,5 TFLOPS.

## 5. Claude Code v repozitáři

**Proč:** Claude si ve složce projektu sám načte `CLAUDE.md`, tedy kontext hackathonu, pravidla, harmonogram a celý plán týmu. Příkazem se svým jménem se dozví, kdo jsi, jaký máš počítač a na co se zaměřuješ.

```
claude
```

- Potvrď, že složce důvěřuješ. Bez toho neplatí povolení z `.claude/settings.json` a Claude se bude ptát na každý příkaz.
- Napiš svůj příkaz: `/ondra`, `/dan`, `/honza` nebo `/tobias`.
- S Claude Pro přepni model: `/model sonnet`, ať vydrží limit.

## 6. Zkušební commit

**Proč:** ověří, že můžeš nahrávat do repozitáře a že postup s větvemi funguje.

Vytvoř soubor `docs/test-<jméno>.txt` s libovolným textem a napiš `/sync`. Claude ho commitne, stáhne práci ostatních a pushne tvoji větev.

## 7. Kaggle (kdo chce trénovat neuronové sítě na GPU)

**Proč:** Kaggle dává zdarma GPU T4, kolem 30 hodin týdně na účet. Trénink tam běží i se zavřeným notebookem a je řádově rychlejší než na našich počítačích. Každý účet má vlastní kvótu, takže víc lidí = víc tréninků najednou.

1. Založ si účet na kaggle.com a v Settings **ověř telefon**. Bez toho Kaggle nedá GPU.
2. Přihlas se: `! kaggle auth login` (když prostředí není aktivované: `! .venv/bin/kaggle auth login` na Macu, `! .venv\Scripts\kaggle auth login` na Windows).
3. Test GPU: `python kaggle/push.py kaggle/gpu-test`. Za pár minut stáhni výsledek: `kaggle kernels output <tvůj účet>/hackathon-gpu-test -p kaggle/.out/gpu-test`.
4. Když výsledek ukáže `"device": "cpu"`, Kaggle GPU nepřidělil, nejčastěji kvůli neověřenému telefonu. Ověř ho a pošli test znovu.
5. Kolik hodin GPU zbývá, ukáže `kaggle quota`. Kvóta se obnovuje v sobotu v 0:00 UTC (u nás ve 2:00), takže během hackathonu přibude.

Podrobnosti jsou v `kaggle/README.md`.

## 8. Sbalit

Nabíječka, prodlužka, flashka, mobil na hotspot (záloha, když nepůjde Wi-Fi), spacák a karimatka.

## Hotovo, když

- [ ] `gh repo view` vypíše repozitář
- [ ] repozitář je stažený a jsi na své větvi
- [ ] import knihoven vypsal `OK` a test GPU vypsal čísla
- [ ] Claude Code ve složce zná tvoji roli (příkaz se jménem)
- [ ] zkušební `/sync` prošel
- [ ] (kdo chce Kaggle) test GPU na Kaggle doběhl
