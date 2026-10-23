"""Ridge, brány podle horizontu: na 12 h jen blízké stanice, na 24 h i střední, na 36 h všechny."""
from models import ridge

# průtoky kterých stanic model vidí; hladiny Děčína a Ústí vždy
BRANY = {
    12: ("decin", "usti", "louny", "melnik", "vranany", "kostelec"),
    24: ("decin", "usti", "louny", "melnik", "vranany", "kostelec", "praha", "nymburk", "jizera"),
    36: None,
}
PARAMETRY = ridge.PARAMETRY | dict(stanice="podle horizontu")


def fit(X, y, cil, horizont):
    stanice = BRANY[horizont]
    sloupce = None if stanice is None else [c for c in X.columns if "_H_" in c or c.split("_Q_")[0] in stanice]
    return ridge.fit(X, y, cil, horizont, sloupce=sloupce)
