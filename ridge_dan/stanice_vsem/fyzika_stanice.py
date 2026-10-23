"""Fyzikální model (src/models/fyzika.py) beze změny a s novými stanicemi zapojenými do stromu řeky.

fit() je týž postup jako fyzika.fit (doba putování, měrná křivka, přírůstky z bran a stanic nad nimi, 3 vrstvy),
jen strom stanic je parametr. S týmovým stromem dává přesně stejné předpovědi (ověřeno v kontrola()).
Nové stanice jdou do stromu jen tam, kam fyzikálně patří a kam dosáhnou 3 vrstvy:
- Ohře: Louny ← Žatec ← Karlovy Vary; Cidlina Sány nad Nymburkem; Jizera Předměřice ← Bakov;
- pro Děčín přímé brány pod Ústím: Ploučnice Benešov ← Stružnice ← Česká Lípa, Bílina Trmice.
Nejdou (10 z 18): Zbraslav (Vltava i se Sázavou, která už v týmovém stromu visí přímo pod Prahou, přidání by vodu
Sázavy počítalo dvakrát nebo by se musel přestavět týmový strom), horní Berounka (Zbečno, Liblín, Plzeň, Střela,
Litavka), horní Sázava (Kácov, Zruč), Orlice Týniště a Chrudimka Nemošice: všechny by byly ve 4. vrstvě,
model jich bere 3; zvýšit počet vrstev by změnilo model, ne jen stanice.
"""
from models import fyzika
from models.fyzika import BRANY, NAD, PARAMETRY, doba_putovani, merna_krivka, prirustek

NAD_NOVE = NAD | {"louny": ["zatec"], "zatec": ["karlovy_vary"], "nymburk": NAD["nymburk"] + ["sany"],
                  "jizera": ["bakov"], "benesov_pl": ["struznice"], "struznice": ["ceska_lipa"]}
BRANY_DECIN_NOVE = ["benesov_pl", "trmice"]  # vlévají se pod Ústím, do Děčína přímo


def postav(brany, nad, brany_decin):
    def fit(X, y, cil, horizont, p=PARAMETRY):
        do_usti = 0 if cil == "usti" else doba_putovani(X, "usti", "decin", p)
        tau = {}
        b_cil = brany_decin if cil == "decin" else []

        def projdi(stanice, kam, zaklad, vrstva):
            for s in stanice:
                tau[s] = doba_putovani(X, s, kam, p) + zaklad
                if vrstva < p["vrstev"]:
                    projdi(nad.get(s, []), s, tau[s], vrstva + 1)

        projdi(brany, "usti", do_usti, 1)
        projdi(b_cil, cil, 0, 1)
        krivka = merna_krivka(X[f"{cil}_Q_0"], X[f"{cil}_H_0"], p)
        fit.tau = tau

        def pritece(X, s, zbyva, do_s):
            Q = prirustek(X, s, do_s, zbyva)
            for n in nad.get(s, []):
                if n in tau and zbyva > do_s:
                    Q = Q + pritece(X, n, zbyva - do_s, tau[n] - tau[s])
            return Q

        def predict(X):
            Q_ted = X[f"{cil}_Q_0"]
            Q = Q_ted + sum(pritece(X, b, horizont, tau[b]) for b in brany + b_cil)
            return X[f"{cil}_H_0"] + krivka(Q.clip(lower=1)) - krivka(Q_ted)

        return predict
    return fit


fit_tym = postav(BRANY, NAD, [])
fit_stanice = postav(BRANY, NAD_NOVE, BRANY_DECIN_NOVE)


def kontrola(X, y, c):
    """Týmový strom přes postav() = fyzika.fit na týchž datech (maximální rozdíl předpovědí v cm)."""
    tr, ev = c == "train", c == "val"
    a = fyzika.fit(X[tr], y[tr], "decin", 24)(X[ev])
    b = fit_tym(X[tr], y[tr], "decin", 24)(X[ev])
    return float((a - b).abs().max())
