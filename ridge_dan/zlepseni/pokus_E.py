"""Pokus E: Ridge 30 + zpoždění 48/60/72 h u nejvzdálenějších stanic, Děčín +36 h, LOFO-CV přes 22 povodní."""
import json
import sys
import time

sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni")
import lofo as L  # noqa: E402

H = 36
ZAKL = (0, 3, 6, 12, 18, 24, 36)
DLOUHE = ZAKL + (48, 60, 72)


def bez_numpy(d):
    return json.loads(json.dumps(d, default=float))


if __name__ == "__main__":
    L.cekej_na_ram(1500)
    t0 = time.time()
    varianty = {
        "ridge_12_36": dict(popis="týmový Ridge, Děčín +36 h", nove=()),
        "ridge_30_36": dict(popis="Ridge 30 stanic, Děčín +36 h", nove=L.NOVE),
        "E_dlouhe_36": dict(popis="Ridge 30 + zpoždění 48/60/72 h u vzdálených stanic (L.DALEKE), Děčín +36 h",
                            nove=L.NOVE, zpozdeni_nove={s: (DLOUHE if s in L.DALEKE else ZAKL) for s in L.NOVE}),
    }
    pred, vysl = {}, []
    for nazev, v in varianty.items():
        A, y = L.matice(H, nove=v["nove"], zpozdeni_nove=v.get("zpozdeni_nove", ZAKL))
        m = L.Motor(A.to_numpy(), y, H)
        pred[nazev], _ = m.lofo()
        val, _ = L.validace_ridge(A.to_numpy(), y, H)
        z = dict(nazev=nazev, popis=v["popis"], horizont=H, sloupcu=A.shape[1],
                 **L.skore(pred[nazev], H, zaklad_pred=pred.get("ridge_12_36")), val=val)
        if nazev == "E_dlouhe_36":
            r30 = L.skore(pred[nazev], H, zaklad_pred=pred["ridge_30_36"])
            z["proti_ridge_30"] = {k: r30[k] for k in ("rozdil", "zlepseno", "zhorseno", "nejhorsi_zhorseni",
                                                        "znamenkovy_p", "splnuje")}
        vysl.append(bez_numpy(z))
        print(nazev, A.shape[1], z["lofo"], z.get("rozdil"), z.get("zlepseno"), z.get("nejhorsi_zhorseni"),
              z.get("splnuje"), "val", val["mae_povodne"], round(time.time() - t0), "s", flush=True)
        del m, A
    (L.ZDE / "vysledky_E.json").write_text(json.dumps(vysl, ensure_ascii=False, indent=1), encoding="utf-8")
