r"""Aplikace pro porotu: zadáš spotřebu, klikneš na Vyhodnotit a uvidíš předpověď.

Spuštění z kořene repozitáře:
    Windows:  .\.venv\Scripts\python.exe -m streamlit run app\app.py
    Mac:      .venv/bin/python -m streamlit run app/app.py
"""

import streamlit as st

from predikce import predikuj

st.set_page_config(page_title="Vyhodnocení spotřeby", page_icon="⚡")

st.title("Vyhodnocení spotřeby energie")
# Až budeme znát zadání, sem patří jedna věta, komu aplikace pomáhá.
st.write("Zadejte roční spotřebu a aplikace odhadne, o jakého odběratele jde.")

# 1. Vstup
spotreba = st.number_input(
    "Roční spotřeba (kWh)", min_value=0.0, value=3000.0, step=100.0, format="%.0f"
)

# 2. Předpověď
if st.button("Vyhodnotit", type="primary"):
    vysledek = predikuj(spotreba)

    # 3. Výsledek
    if vysledek["ukazka"]:
        st.warning(
            "**Ukázková předpověď.** Nejde o skutečný model, jen o zkušební "
            "pravidla, než bude model hotový.",
            icon="⚠️",
        )
    st.metric("Předpověď", vysledek["kategorie"])
    st.write(vysledek["vysvetleni"])
