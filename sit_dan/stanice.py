"""Které stanice ČHMÚ bereme. Vybrané podle doby doběhu do Děčína a podle toho, jestli mají řady celé 2006–2025.

Děčín (240000, číslo hydrologického pořadí 1-14-04-0010, plocha povodí 50 974 km²) leží POD soutokem
s Ploučnicí (1-14-03) i s Bílinou (1-14-01), obě se vlévají mezi Ústím a Děčínem. Kamenice (Hřensko) je pod
Děčínem, ta nás nezajímá. Dolní Ohře pod Louny (Terezín) a Labe v Litoměřicích mají data až od 2013 a 2017,
validační povodně 2006–2011 by bez nich nešly, proto chybí.
"""
# DBC: (klíč, název)
HYDRO = {
    # stejné jako týmová tabulka (src/data.py)
    "240000": ("decin", "Děčín (Labe)"),
    "221000": ("usti", "Ústí nad Labem (Labe)"),
    "219000": ("louny", "Louny (Ohře)"),
    "204000": ("melnik", "Mělník (Labe)"),
    "203000": ("vranany", "Vraňany (Vltava)"),
    "104400": ("kostelec", "Kostelec nad Labem (Labe)"),
    "200100": ("praha", "Praha-Chuchle (Vltava)"),
    "080000": ("nymburk", "Nymburk (Labe)"),
    "101800": ("jizera", "Tuřice-Předměřice (Jizera)"),
    "198000": ("beroun", "Beroun (Berounka)"),
    "167200": ("sazava", "Nespeky (Sázava)"),
    "061000": ("prelouc", "Přelouč (Labe)"),
    # přítoky mezi Ústím a Děčínem, kde dnes vlna „vzniká z ničeho“
    "239000": ("benesov_pl", "Benešov nad Ploučnicí (Ploučnice)"),
    "238000": ("struznice", "Stružnice (Ploučnice)"),
    "235000": ("ceska_lipa", "Česká Lípa (Ploučnice)"),
    "226000": ("trmice", "Trmice (Bílina)"),
    # dál proti proudu, delší náskok
    "216000": ("zatec", "Žatec (Ohře)"),
    "214000": ("karlovy_vary", "Karlovy Vary (Ohře)"),
    "194500": ("zbecno", "Zbečno (Berounka)"),
    "191000": ("liblin", "Liblín (Berounka)"),
    "186000": ("plzen", "Plzeň-Bílá Hora (Berounka)"),
    "190000": ("plasy", "Plasy (Střela)"),
    "197300": ("litavka", "Beroun (Litavka)"),
    "169000": ("zbraslav", "Praha-Zbraslav (Vltava)"),
    "165000": ("kacov", "Kácov (Sázava)"),
    "161000": ("zruc", "Zruč nad Sázavou (Sázava)"),
    # Němčice (042000) staženy, ale vyřazené: díra 170 h v 10/2020 (val) by vyhodila řádky, Přelouč je hned pod nimi
    "059000": ("nemosice", "Nemošice (Chrudimka)"),
    "037000": ("tyniste", "Týniště nad Orlicí (Orlice)"),
    "075000": ("sany", "Sány (Cidlina)"),
    "098000": ("bakov", "Bakov nad Jizerou (Jizera)"),
}
TYM = ["decin", "usti", "louny", "melnik", "vranany", "kostelec", "praha", "nymburk", "jizera", "beroun", "sazava",
       "prelouc"]
CILE = ["decin", "usti"]
ROKY = range(2006, 2026)
