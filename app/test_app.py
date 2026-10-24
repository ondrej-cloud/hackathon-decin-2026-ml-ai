r"""Kontrola aplikace bez prohlížeče (Streamlit AppTest). Spouští se z kořene repozitáře:

    Windows:  $env:PYTHONUTF8=1; .venv\Scripts\python app\test_app.py
    Mac:      .venv/bin/python app/test_app.py

Výchozí pohled aplikace je Dnešek, ostatní kroky ho vypnou. Přepínač --dnesek navíc ověří živá data ČHMÚ (potřebuje internet).
Kód ukončení je 0, když všechno prošlo, jinak 1.
"""
import logging
import re
import sys
import time
from pathlib import Path

APP = Path(__file__).resolve().parent
sys.path.insert(0, str(APP))
sys.stdout.reconfigure(encoding="utf-8")

from streamlit.testing.v1 import AppTest  # noqa: E402

logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").addFilter(
    lambda zaznam: "ScriptRunContext" not in zaznam.getMessage())  # bez serveru Streamlit hlásí zbytečné varování

ZALOZKY = ["Teď", "Jak dobře to funguje", "Mapa povodí", "Animace povodně"]
METRIKY = ["Hladina teď", "Za 12 h", "Za 24 h", "Za 36 h"]
VALIDACNI = ["4/2006", "3/2009", "9/2010", "1/2011"]
BORIS = "9/2024 Boris (test)"


def nova(dnesek=False):
    """Aplikace po startu; výchozí je Dnešek, pro přehrávání historie se vypne."""
    at = AppTest.from_file(str(APP / "app.py"), default_timeout=300).run()
    if not dnesek:
        prvek(at.sidebar.toggle, "Dnešek: živá data ČHMÚ").set_value(False).run()
    return at


def bez_vyjimky(at):
    assert not at.exception, f"výjimka v aplikaci: {at.exception[0].value}"


def prvek(seznam, label, key=None):
    """Prvek podle popisku a klíče (selectbox, radio a toggle v AppTestu nemají jednodušší přístup)."""
    nalezene = [w for w in seznam if w.label == label and w.key == key]
    assert nalezene, f"chybí ovládací prvek „{label}“"
    return nalezene[0]


def metriky(at):
    assert [m.label for m in at.metric] == METRIKY, f"metriky: {[m.label for m in at.metric]}"
    return {m.label: int(re.search(r"-?\d+", m.value).group()) for m in at.metric}


def krok_nabehne():
    # výchozí Dnešek; bez internetu aplikace ukáže varování a přehrává historii
    at = nova(dnesek=True)
    bez_vyjimky(at)
    assert not at.error, f"chybová hláška: {at.error[0].value}"


def krok_zalozky():
    at = nova()
    assert [t.label for t in at.tabs] == ZALOZKY, f"záložky: {[t.label for t in at.tabs]}"


def krok_ted():
    at = nova()
    m = metriky(at)
    assert m["Hladina teď"] == 646, f"hladina teď {m['Hladina teď']} cm, čekáno 646"
    assert abs(m["Za 24 h"] - 738) <= 3, f"za 24 h {m['Za 24 h']} cm, čekáno asi 738"
    odznaky = [x.value for x in at.markdown if "<span" in x.value]
    assert len(odznaky) == 4 and "3. stupeň" in odznaky[2], "odznak za 24 h není 3. stupeň"
    assert "3. stupeň" in at.info[0].value, f"věta pro laika: {at.info[0].value[:80]}"
    assert len(at.get("plotly_chart")) == 2, "chybí graf"
    return f"hladina {m['Hladina teď']} cm, za 24 h {m['Za 24 h']} cm, 3. stupeň"


def krok_usti():
    # radio s format_func se nastavuje popiskem z menu, ne klíčem decin / usti
    at = nova()
    decin = metriky(at)["Hladina teď"]
    prvek(at.sidebar.radio, "Stanice").set_value("Ústí nad Labem").run()
    bez_vyjimky(at)
    assert at.main.subheader[0].value.startswith("Ústí nad Labem"), at.main.subheader[0].value
    usti = metriky(at)["Hladina teď"]
    assert usti != decin, "hladina se po přepnutí nezměnila"
    return f"Ústí {usti} cm, Děčín {decin} cm"


def krok_mapa():
    at = nova()
    for pohled in ("Děčín", "Ústí nad Labem", "celé povodí"):
        prvek(at.radio, "Pohled", "mapa_pohled").set_value(pohled).run()
        bez_vyjimky(at)
        # mapa je buď Mapbox (iframe, s tokenem), nebo pydeck (deck_gl_json_chart); druhý iframe je animace
        assert len(at.get("deck_gl_json_chart")) + len(at.get("iframe")) == 2, f"pohled {pohled}: chybí mapa"
        assert any("Co předpověď znamená" in x.value for x in at.markdown), f"pohled {pohled}: chybí věta o rozlivu"
    return "tři pohledy s rozlivem"


def krok_kvalita():
    at = nova()
    for povoden in VALIDACNI:
        prvek(at.radio, "Povodeň").set_value(povoden).run()
        bez_vyjimky(at)
        assert not at.warning, f"{povoden}: {at.warning[0].value}"
        assert len(at.table) == 1, f"{povoden}: chybí tabulka metrik"
    return ", ".join(VALIDACNI)


def krok_boris():
    at = nova()
    for h in ("12", "24", "36"):
        prvek(at.radio, "Povodeň").set_value(BORIS).run()
        prvek(at.radio, "Předpověď vydaná ... hodin předem").set_value(h).run()
        bez_vyjimky(at)
        assert not at.warning, f"Boris, {h} h: {at.warning[0].value}"
        assert len(at.table) == 1, f"Boris, {h} h: chybí tabulka metrik"
    assert any("Boris 9/2024" in i.value for i in at.info), "chybí poznámka, že jde o testovací část"
    return "záložka Jak dobře to funguje, horizonty 12, 24 a 36 h"


def krok_animace():
    at = nova()
    for povoden in (BORIS, "1/2011"):
        prvek(at.radio, "Povodeň", "animace_povoden").set_value(povoden).run()
        bez_vyjimky(at)
        assert len(at.get("iframe")) >= 1, f"{povoden}: chybí animace"
    return f"{BORIS} a 1/2011"


def krok_ridge_vse():
    at = nova()
    prvek(at.sidebar.selectbox, "Model").set_value("ridge_vse").run()
    bez_vyjimky(at)
    m = metriky(at)
    assert abs(m["Za 24 h"] - 738) <= 50, f"za 24 h {m['Za 24 h']} cm je daleko od ridge"
    # výsledky v results/ má jen ridge, ridge_vse dostane v záložce kvality upozornění, ne výjimku
    return f"za 24 h {m['Za 24 h']} cm" + ("; v záložce kvality upozornění na chybějící předpovědi" if at.warning else "")


def krok_dnesek():
    at = nova(dnesek=True)
    bez_vyjimky(at)
    assert not at.sidebar.warning, f"živá data se nenačetla: {at.sidebar.warning[0].value}"
    podnadpis = at.main.subheader[0].value
    assert " dnes" in podnadpis, f"podnadpis: {podnadpis}"
    metriky(at)
    prvek(at.sidebar.radio, "Stanice").set_value("Ústí nad Labem").run()
    bez_vyjimky(at)
    assert " dnes" in at.main.subheader[0].value, f"podnadpis Ústí: {at.main.subheader[0].value}"
    return podnadpis


def main():
    kroky = [("aplikace naběhne bez výjimky", krok_nabehne),
             ("jsou 4 záložky", krok_zalozky),
             ("Teď: výchozí okamžik Děčín 15. 1. 2011 9:00", krok_ted),
             ("přepnutí stanice na Ústí", krok_usti),
             ("Mapa povodí: pohledy a rozliv", krok_mapa),
             ("Jak dobře to funguje: povodně z validace", krok_kvalita),
             ("Jak dobře to funguje: Boris 9/2024 (test)", krok_boris),
             ("Animace povodně: výběr povodně", krok_animace),
             ("model ridge_vse", krok_ridge_vse)]
    dnesek = "--dnesek" in sys.argv
    if dnesek:
        kroky.append(("Dnešek: živá data ČHMÚ", krok_dnesek))
    chyby = 0
    for popis, krok in kroky:
        start = time.time()
        try:
            detail = krok()
            print(f"OK     {popis}" + (f": {detail}" if detail else "") + f" ({time.time() - start:.1f} s)", flush=True)
        except Exception as e:
            chyby += 1
            zprava = str(e) if isinstance(e, AssertionError) else f"{type(e).__name__}: {e}"
            print(f"CHYBA  {popis}: {zprava}", flush=True)
    print(f"\nProšlo {len(kroky) - chyby} z {len(kroky)} kroků." + ("" if dnesek else " Dnešek se nekontroloval (spusť s --dnesek)."))
    sys.exit(1 if chyby else 0)


if __name__ == "__main__":
    main()
