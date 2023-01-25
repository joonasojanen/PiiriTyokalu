# Joni Kuusela - 2687858
# Joonas Ojanen - 2586289

import ikkunasto
import piiristo
import math
import cmath


kerrannaisyksikot = {
    "Y": 1e24,
    "Z": 1e21,
    "E": 1e18,
    "P": 1e15,
    "T": 1e12,
    "G": 1e9,
    "M": 1e6,
    "k": 1e3,
    "h": 1e2,
    "d": 1e-1,
    "c": 1e-2,
    "m": 1e-3,
    "u": 1e-6,
    "n": 1e-9,
    "p": 1e-12,
    "f": 1e-15,
    "a": 1e-18,
    "z": 1e-21,
    "y": 1e-24
}

piiri_suljettu = False

tila = {
    "jannite": None,
    "taajuus": None,
    "vastus": None,
    "kondensaattori": None,
    "kela": None,
    "vastus_rinnan": None,
    "kondensaattori_rinnan": None,
    "kela_rinnan": None,
    "laatikko": None,
    "piiri": None,
    "komponentit": [],
    "komponentit_piirto": [],
    "komponentit_rinnan": [],
    "haarat": [],
    "haarat_laskuihin": [],
    "haara": [],
    "rinnan": [],
    "U": None,
    "f": None,
}


def muuta_kerrannaisyksikko(luku: str, kohde):
    """
    Funktio palauttaa syötetyn luvun kerrannaisyksiköllä kerrottuna.
    Toisistaan eroavat virheilmoitukset kohde parametrin mukaisesti.
    """
    if kohde == tila["jannite"]:
        virhesyotto = "Jännitteen"

    elif kohde == tila["taajuus"]:
        virhesyotto = "Taajuuden"

    elif kohde == tila["vastus"]:
        virhesyotto = "Vastuksen"

    elif kohde == tila["kondensaattori"]:
        virhesyotto = "Kondensaattorin"

    elif kohde == tila["kela"]:
        virhesyotto = "Kelan"

    else:
        return None

    if not luku:
        ikkunasto.avaa_viesti_ikkuna("Huomio", "{} syöte oli virheellinen.".format(virhesyotto), virhe=False)
        return None

    alphas = ""
    digits = ""
    luku = luku.strip()
    for k in luku:
        if k not in kerrannaisyksikot.keys() and k.isnumeric() is False:
            ikkunasto.avaa_viesti_ikkuna("Huomio", "{} syöte oli virheellinen.".format(virhesyotto), virhe=False)
            return None
        if k.isnumeric():
            digits += k
        elif k.isalpha() and k in kerrannaisyksikot.keys():
            alphas += k
    if len(alphas) > 1 or digits == "":
        ikkunasto.avaa_viesti_ikkuna("Huomio", "{} syöte oli virheellinen.".format(virhesyotto), virhe=False)
        ikkunasto.tyhjaa_kentan_sisalto(kohde)
    elif alphas == "":
        return float(digits)
    else:
        lopullinen_arvo = float(digits) * kerrannaisyksikot[alphas]
        return lopullinen_arvo


def laske_arvot():
    komponentti_lista = []
    haara_lista = []
    lohko_lista = []
    vastus_rinnan_yht = 0
    kela_rinnan_yht = 0
    for haara in tila["haarat_laskuihin"]:
        for komponentit in haara:
            vastus_rinnan = 0
            kondensaattori_rinnan = 0
            kela_rinnan = 0
            if isinstance(komponentit, tuple):
                komponentti_lista.append(komponentit)
            elif isinstance(komponentit, list):
                for komponentti in komponentit:
                    if komponentti[0] == "r":
                        vastus_rinnan += 1 / komponentti[1]
                        vastus_rinnan_yht = 1 / vastus_rinnan
                    elif komponentti[0] == "c":
                        kondensaattori_rinnan += komponentti[1]
                    elif komponentti[0] == "l":
                        kela_rinnan += 1 / komponentti[1]
                        kela_rinnan_yht = 1 / kela_rinnan
                if vastus_rinnan > 0:
                    lohko_lista.append(("r", vastus_rinnan_yht))
                if kondensaattori_rinnan > 0:
                    lohko_lista.append(("c", kondensaattori_rinnan))
                if kela_rinnan > 0:
                    lohko_lista.append(("l", kela_rinnan_yht))
                komponentti_lista.append(lohko_lista[:])
                lohko_lista.clear()
        haara_lista.append(komponentti_lista[:])
        komponentti_lista.clear()
    return haara_lista[:]


def laske():
    """
    Laskee syötettyjen komponenttien jännitteet ja virrat. Tulokset esitetään tekstilaatikossa osoitinmuodossa.
    """
    if piiri_suljettu:
        laske_impedanssi(laske_arvot())
        virrat_ja_jannitteet(laske_impedanssi(laske_arvot()))
    elif not piiri_suljettu:
        ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Luo ensin piiri.", tyhjaa=False)
    else:
        ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Piiri täytyy ensin sulkea, jotta laskut voidaan "
                                                              "suorittaa.", tyhjaa=False)


def laske_impedanssi(haara_lista):
    haara_impedanssit = []
    haara_komponentti = []
    for haara in haara_lista:
        for komponentit in haara:
            if isinstance(komponentit, tuple):
                if komponentit[0] == "r":
                    vastus_sarja_impedanssi = komponentit[1]
                    haara_komponentti.append(vastus_sarja_impedanssi)
                elif komponentit[0] == "c":
                    kondensaattori_sarja_impedanssi = 1 / (2 * math.pi * tila["f"] * komponentit[1] * 1j)
                    haara_komponentti.append(kondensaattori_sarja_impedanssi)
                elif komponentit[0] == "l":
                    kela_sarja_impedanssi = (2 * math.pi * tila["f"] * komponentit[1] * 1j)
                    haara_komponentti.append(kela_sarja_impedanssi)
            elif isinstance(komponentit, list):
                vastus_rinnan_impedanssi = 0
                kondensaattori_rinnan_impedanssi = 0
                kela_rinnan_impedanssi = 0
                for komponentti in komponentit:
                    if komponentti[0] == "r":
                        vastus_rinnan_impedanssi = komponentti[1]
                    elif komponentti[0] == "c":
                        kondensaattori_rinnan_impedanssi = 1 / (2 * math.pi * tila["f"] * komponentti[1] * 1j)
                    elif komponentti[0] == "l":
                        kela_rinnan_impedanssi = (2 * math.pi * tila["f"] * komponentti[1] * 1j)

                try:
                    vastus = (1 / vastus_rinnan_impedanssi)
                except ZeroDivisionError:
                    vastus = 0
                try:
                    kondensaattori = (1 / kondensaattori_rinnan_impedanssi)
                except ZeroDivisionError:
                    kondensaattori = 0
                try:
                    kela = (1 / kela_rinnan_impedanssi)
                except ZeroDivisionError:
                    kela = 0
                if vastus or kondensaattori or kela:
                    impedanssi = 1 / (vastus + kondensaattori + kela)
                    haara_komponentti.append(impedanssi)

        haara_impedanssit.append(haara_komponentti[:])
        haara_komponentti.clear()
    return haara_impedanssit[:]


def virrat_ja_jannitteet(haara_impedanssit):
    haara_kokonais_impedanssi = []
    for impedanssit in haara_impedanssit:
        kokonais_impedanssi = 0
        for impedanssi in impedanssit:
            kokonais_impedanssi += impedanssi
        haara_kokonais_impedanssi.append(kokonais_impedanssi)

    for r, s in zip(haara_impedanssit, haara_kokonais_impedanssi):
        ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Haaran lasketut arvot: ", tyhjaa=False)
        for impedanssi in r:
            komponentit_jannite = (impedanssi / s) * tila["U"]
            jannite_arvo, jannite_kulma = cmath.polar(komponentit_jannite)
            virta_arvo, virta_kulma = cmath.polar(komponentit_jannite / impedanssi)
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"],
                                                "{:.4f} V < {:.4f}° ja {:.4f} A < {:.4f}°".format(jannite_arvo,
                                                                                                  jannite_kulma,
                                                                                                  virta_arvo,
                                                                                                  virta_kulma),
                                                tyhjaa=False)


def alusta():
    """
    Alustaa ohjelman eli asettaa kaiken alkutilanteeseen.
    """
    if not tila["U"] and not tila["f"]:
        ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Luo ensin piiri.", tyhjaa=True)
    else:
        global piiri_suljettu
        alusta_piirtoalue()
        tila["jannite"] = None
        tila["taajuus"] = None
        tila["vastus"] = None
        tila["kondensaattori"] = None
        tila["kela"] = None
        tila["vastus_rinnan"] = None
        tila["kondensaattori_rinnan"] = None
        tila["kela_rinnan"] = None
        tila["U"] = None
        tila["f"] = None
        tila["komponentit"].clear()
        tila["komponentit_piirto"].clear()
        tila["komponentit_rinnan"].clear()
        tila["haarat"].clear()
        tila["haarat_laskuihin"].clear()
        tila["haara"].clear()
        tila["rinnan"].clear()
        piiri_suljettu = False
        ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Alustaminen onnistui.", tyhjaa=True)


def alusta_piirtoalue():
    """
    Alustaa piirtoalueen eli asettaa sen alkutilanteeseen.
    """
    piiristo.tyhjaa_piiri(tila["piiri"])
    piiristo.piirra_piiri(tila["piiri"])


def lisaa_jannitelahde():
    """
    Lisää jännitelähteen piiriin.
    """

    def tallenna_arvot():
        if not tila["U"] and not tila["f"]:
            try:
                u = muuta_kerrannaisyksikko(ikkunasto.lue_kentan_sisalto(tila["jannite"]), tila["jannite"])
                if u is not None:
                    tila["U"] = u
                    ikkunasto.tyhjaa_kentan_sisalto(tila["jannite"])
            except ValueError:
                return
            try:
                f = muuta_kerrannaisyksikko(ikkunasto.lue_kentan_sisalto(tila["taajuus"]), tila["taajuus"])
                if f is not None:
                    tila["f"] = f
                    ikkunasto.tyhjaa_kentan_sisalto(tila["taajuus"])
            except ValueError:
                return
            if tila["U"] and tila["f"]:
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Jännitelähde lisätty.", tyhjaa=False)
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Jännite {} V".format(u), tyhjaa=False)
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Taajuus {} Hz".format(f), tyhjaa=False)
                ikkunasto.piilota_ali_ikkuna(syottoikkuna)
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piiristo.piirra_piiri(tila["piiri"])
            else:
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Jännitelähteen lisääminen epäonnistui.",
                                                    tyhjaa=False)
        else:
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Jännitelähde on jo määritelty.", tyhjaa=False)
            ikkunasto.piilota_ali_ikkuna(syottoikkuna)

    # Ikkunasto
    syottoikkuna = ikkunasto.luo_ali_ikkuna("Syötä jännite ja taajuus")
    syottoikkuna_kehys = ikkunasto.luo_kehys(syottoikkuna, ikkunasto.YLA)
    ikkunasto.luo_vaakaerotin(syottoikkuna_kehys, 2)
    ikkunasto.luo_tekstirivi(syottoikkuna_kehys, "Syötä tehonlähteen jännite ja taajuus")
    ikkunasto.luo_vaakaerotin(syottoikkuna_kehys, 8)
    syottoikkuna_kehys_vasen = ikkunasto.luo_kehys(syottoikkuna, ikkunasto.VASEN)
    ikkunasto.luo_tekstirivi(syottoikkuna_kehys_vasen, "Jännite: ")
    tila["jannite"] = ikkunasto.luo_tekstikentta(syottoikkuna_kehys_vasen)
    syottoikkuna_kehys_oikea = ikkunasto.luo_kehys(syottoikkuna, ikkunasto.OIKEA)
    ikkunasto.luo_tekstirivi(syottoikkuna_kehys_oikea, "Taajuus: ")
    tila["taajuus"] = ikkunasto.luo_tekstikentta(syottoikkuna_kehys_oikea)
    tallenna_kehys = ikkunasto.luo_kehys(syottoikkuna, ikkunasto.ALA)
    tallenna_nappikehys = ikkunasto.luo_kehys(tallenna_kehys, ikkunasto.ALA)
    ikkunasto.luo_nappi(tallenna_nappikehys, "Tallenna arvot", tallenna_arvot)
    ikkunasto.nayta_ali_ikkuna(syottoikkuna, otsikko=None)


def lisaa_komponentti(komponentin_tyyppi):
    """
    Lisää syötetyn komponentin sarjaan viimeisimmän komponentin kanssa.
    """
    tila["rinnan"] = []
    if not tila["U"] and not tila["f"]:
        ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Lisää ensin jännitelähde.", tyhjaa=False)
    else:
        if not piiri_suljettu:
            if komponentin_tyyppi == "R":
                komponentti = "vastus"
                tyyppi = "r"
            elif komponentin_tyyppi == "C":
                komponentti = "kondensaattori"
                tyyppi = "c"
            elif komponentin_tyyppi == "L":
                komponentti = "kela"
                tyyppi = "l"
            else:
                return
            arvo = muuta_kerrannaisyksikko(ikkunasto.lue_kentan_sisalto(tila[komponentti]), tila[komponentti])
            if arvo is not None:
                ikkunasto.tyhjaa_kentan_sisalto(tila[komponentti])
                tila["komponentit"].append((tyyppi, arvo))
                tila["komponentit_piirto"].append((tyyppi, arvo))
                tila["komponentit_rinnan"].append((tyyppi, arvo))
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piirra_haara()
                piiristo.piirra_haara(tila["piiri"], tila["komponentit"], 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "{} lisätty.".format(komponentti.capitalize()),
                                                    tyhjaa=False)
            else:
                pass
        else:
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Suljettuun piiriin ei voida lisätä komponentteja.",
                                                tyhjaa=False)


def lisaa_rinnankytkenta(komponentin_tyyppi):
    """
    Lisää viimeksi lisättyyn komponenttiin rinnankytkennän.
    """
    if not tila["U"] and not tila["f"]:
        ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Lisää ensin jännitelähde.", tyhjaa=False)
    else:
        if not piiri_suljettu:
            if komponentin_tyyppi == "R":
                komponentti_rinnan = "vastus_rinnan"
                komponentti = "vastus"
                tyyppi = "r"
            elif komponentin_tyyppi == "C":
                komponentti_rinnan = "kondensaattori_rinnan"
                komponentti = "kondensaattori"
                tyyppi = "c"
            elif komponentin_tyyppi == "L":
                komponentti_rinnan = "kela_rinnan"
                komponentti = "kela"
                tyyppi = "l"
            else:
                return
            arvo = muuta_kerrannaisyksikko(ikkunasto.lue_kentan_sisalto(tila[komponentti_rinnan]), tila[komponentti])
            if arvo is not None:
                ikkunasto.tyhjaa_kentan_sisalto(tila[komponentti_rinnan])
                if not tila["komponentit"]:
                    tila["komponentit"].append((tyyppi, arvo))
                    tila["komponentit_piirto"].append((tyyppi, arvo))
                    tila["komponentit_rinnan"].append((tyyppi, arvo))
                    piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                    piirra_haara()
                    piiristo.piirra_haara(tila["piiri"], tila["komponentit"], 2, 2, viimeinen=False)
                    piiristo.piirra_piiri(tila["piiri"])

                elif tila["komponentit_rinnan"]:
                    tila["rinnan"].append(tila["komponentit_rinnan"][-1])
                    tila["rinnan"].append((tyyppi, arvo))
                    tila["komponentit"][-1] = tila["rinnan"]
                    tila["komponentit_rinnan"] = []
                    tila["komponentit_piirto"].pop(-1)
                else:
                    tila["rinnan"].append((tyyppi, arvo))
                    tila["komponentit"][-1] = tila["rinnan"]
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piirra_haara()
                piiristo.piirra_haara(tila["piiri"], tila["komponentit"], 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"],
                                                    "{} lisätty rinnan viimeksi lisättyyn komponenttiin.".format(
                                                        komponentti.capitalize()), tyhjaa=False)
        else:
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Suljettuun piiriin ei voida lisätä komponentteja.",
                                                tyhjaa=False)


def poista_viimeisin_komponentti():
    """
    Funktio poistaa viimeisimmän lisätyn komponentin tai tyhjän haaran. Funktiota voidaan hyödyntää jos käyttäjä lisää
    vahingossa esimerkiksi väärän arvon omaavan komponentin piiriin.
    """
    global piiri_suljettu
    if piiri_suljettu:
        ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Suljetusta piiristä ei voi poistaa komponenteja.",
                                            tyhjaa=False)
    else:
        if not tila["haarat"] and tila["komponentit"] and isinstance(tila["komponentit"][-1], tuple):
            tila["komponentit"].pop(-1)
            if tila["komponentit"]:
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piirra_haara()
                piiristo.piirra_haara(tila["piiri"], tila["komponentit"], 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Komponentti poistettiin.", tyhjaa=False)
            else:
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piiristo.piirra_piiri(tila["piiri"])
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Komponentti poistettiin.", tyhjaa=False)
        elif not tila["komponentit"] and not tila["haarat"] and tila["U"] and tila["f"]:
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Haarassa ei ole komponenttia.", tyhjaa=False)
        elif not tila["komponentit"] and not tila["haarat"] and not tila["U"] and not tila["f"]:
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Lisää ensin jännitelähde.", tyhjaa=False)
        elif not tila["komponentit"] and tila["haarat"]:
            if len(tila["haarat"]) == 1:
                haara = tila["haarat"][-1]
                for komponentti in haara:
                    tila["komponentit"].append(komponentti)
                tila["haarat"].pop(-1)
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piirra_haara()
                piiristo.piirra_haara(tila["piiri"], tila["komponentit"], 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Haara poistettiin.", tyhjaa=False)
            elif len(tila["haarat"]) > 1:
                haara = tila["haarat"][-1]
                for komponentti in haara:
                    tila["komponentit"].append(komponentti)
                tila["haarat"].pop(-1)
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piirra_haara()
                piiristo.piirra_haara(tila["piiri"], tila["komponentit"], 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Haara poistettiin.", tyhjaa=False)
        elif isinstance(tila["komponentit"][-1], tuple) and tila["haarat"]:
            if len(tila["komponentit"]) > 1:
                tila["komponentit"].pop(-1)
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piirra_haara()
                piiristo.piirra_haara(tila["piiri"], tila["komponentit"], 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Komponentti poistettiin.", tyhjaa=False)
            elif len(tila["komponentit"]) == 1:
                tila["komponentit"].clear()
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piirra_haara()
                piiristo.piirra_piiri(tila["piiri"])
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Komponentti poistettiin.", tyhjaa=False)
        elif isinstance(tila["komponentit"][-1], list):
            tila["rinnan"] = tila["komponentit"][-1]
            if len(tila["rinnan"]) > 1:
                tila["rinnan"].pop(-1)
                tila["komponentit"][-1] = tila["rinnan"]
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piirra_haara()
                piiristo.piirra_haara(tila["piiri"], tila["komponentit"], 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Rinnan kytketty komponentti poistettiin.",
                                                    tyhjaa=False)
            elif len(tila["rinnan"]) == 1:
                tila["komponentit"][-1] = (tila["rinnan"][-1])
                tila["komponentit_rinnan"].append(tila["rinnan"][-1])
                tila["rinnan"] = []
                piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
                piirra_haara()
                piiristo.piirra_haara(tila["piiri"], tila["komponentit"], 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])
                ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Rinnan kytkentä purettiin.", tyhjaa=False)


def lisaa_komponentti_ui():
    """
    Funktio suorittaa lisaa_komponentti() funktiota, joka lisää halutun komponentin sarjaan. Funktio avaa
    myös ali-ikkunan, jossa on käyttöliittymä komponenttien lisäämiseen.
    """

    def lisaa_r():
        lisaa_komponentti("R")

    def lisaa_c():
        lisaa_komponentti("C")

    def lisaa_l():
        lisaa_komponentti("L")

    # Ikkunasto
    syottoikkuna = ikkunasto.luo_ali_ikkuna("Lisää komponentit")
    nappikehys = ikkunasto.luo_kehys(syottoikkuna, ikkunasto.VASEN)
    ikkunasto.luo_tekstirivi(nappikehys, "Syötä vastus: ")
    tila["vastus"] = ikkunasto.luo_tekstikentta(nappikehys)
    ikkunasto.luo_nappi(nappikehys, "Lisää", lisaa_r)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_tekstirivi(nappikehys, "Syötä kondensaattori: ")
    tila["kondensaattori"] = ikkunasto.luo_tekstikentta(nappikehys)
    ikkunasto.luo_nappi(nappikehys, "Lisää", lisaa_c)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_tekstirivi(nappikehys, "Syötä kela: ")
    tila["kela"] = ikkunasto.luo_tekstikentta(nappikehys)
    ikkunasto.luo_nappi(nappikehys, "Lisää", lisaa_l)


def lisaa_komponentti_rinnan_ui():
    """
    Funktio suorittaa lisaa_rinnankytkentä() funktiota, joka lisää halutun komponentin rinnankytkentään. Funktio avaa
    myös ali-ikkunan, jossa on käyttöliittymä komponenttien lisäämiseen.
    """

    def lisaa_r():
        lisaa_rinnankytkenta("R")

    def lisaa_c():
        lisaa_rinnankytkenta("C")

    def lisaa_l():
        lisaa_rinnankytkenta("L")

    syottoikkuna = ikkunasto.luo_ali_ikkuna("Lisää komponentit")
    nappikehys = ikkunasto.luo_kehys(syottoikkuna, ikkunasto.VASEN)
    ikkunasto.luo_tekstirivi(nappikehys, "Syötä vastus: ")
    tila["vastus_rinnan"] = ikkunasto.luo_tekstikentta(nappikehys)
    ikkunasto.luo_nappi(nappikehys, "Lisää", lisaa_r)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_tekstirivi(nappikehys, "Syötä kondensaattori: ")
    tila["kondensaattori_rinnan"] = ikkunasto.luo_tekstikentta(nappikehys)
    ikkunasto.luo_nappi(nappikehys, "Lisää", lisaa_c)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_tekstirivi(nappikehys, "Syötä kela: ")
    tila["kela_rinnan"] = ikkunasto.luo_tekstikentta(nappikehys)
    ikkunasto.luo_nappi(nappikehys, "Lisää", lisaa_l)


def piirra_haara():
    """
    Piirtää piiriin uuden haaran.
    """
    piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
    if not tila["haarat"]:
        return
    else:
        for haara in tila["haarat"]:
            if not tila["haarat"]:
                return
            else:
                piiristo.piirra_haara(tila["piiri"], haara, 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])


def uusi_haara():
    """
    Lisää piiriin uuden haaran.
    """
    tila["rinnan"] = []
    if not tila["komponentit"]:
        if not tila["U"] and not tila["f"]:
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Lisää ensin jännitelähde.", tyhjaa=False)
        elif piiri_suljettu:
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Piiri on suljettu.", tyhjaa=False)
        else:
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Lisää ensin komponentti.", tyhjaa=False)
        return
    else:
        tila["haarat"].append(tila["komponentit"][:])
        tila["komponentit"].clear()

    piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
    if not tila["haarat"]:
        return
    else:
        for haara in tila["haarat"]:
            if not tila["haarat"]:
                return
            else:
                piiristo.piirra_haara(tila["piiri"], haara, 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])
    ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"],
                                        "Piiriin lisätty uusi haara. Lisää uuteen haaraan komponentit.", tyhjaa=False)


def sulje_piiri():
    """
    Funktio sulkee piirin.
    """
    global piiri_suljettu

    if not piiri_suljettu:
        if not tila["komponentit"]:
            pass
        else:
            tila["haarat"].append(tila["komponentit"][:])
            tila["komponentit"].clear()
        tila["haarat_laskuihin"] = tila["haarat"].copy()
        piiristo.piirra_jannitelahde(tila["piiri"], tila["U"], tila["f"], v_asetteluvali=2)
        if not tila["U"] and not tila["f"]:
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Luo ensin piiri.", tyhjaa=False)
            return
        elif tila["U"] and tila["f"] and not tila["haarat"]:
            ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Lisää ensin komponentti.", tyhjaa=False)
            return
        elif len(tila["haarat"]) == 1:
            piiristo.piirra_haara(tila["piiri"], tila["haarat"][-1], 2, 2, viimeinen=True)
            piiristo.piirra_piiri(tila["piiri"])
        else:
            viimeinen_haara = tila["haarat"][-1]
            tila["haarat"].pop(-1)
            for haara in tila["haarat"]:
                piiristo.piirra_haara(tila["piiri"], haara, 2, 2, viimeinen=False)
                piiristo.piirra_piiri(tila["piiri"])
            piiristo.piirra_haara(tila["piiri"], viimeinen_haara, 2, 2, viimeinen=True)
            piiristo.piirra_piiri(tila["piiri"])
        ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Piiri suljettu.", tyhjaa=False)
        piiri_suljettu = True
    else:
        ikkunasto.kirjoita_tekstilaatikkoon(tila["laatikko"], "Piiri on jo suljettu.", tyhjaa=False)
        return


def main():
    """
    Luo käyttöliittymäikkunan, jossa on vasemmalla yhdeksän nappia ja niiden alapuolella tekstilaatikko.
    Tekstilaatikkossa ilmenee suoritetut toiminnot. Käyttöliittymäikkunan oikealla puolella on piirtoalue,
    johon komponentit piirtyvät kun niitä lisätään.
    """
    paaikkuna = ikkunasto.luo_ikkuna("Piiri pieni pyörii")
    nappikehys = ikkunasto.luo_kehys(paaikkuna, ikkunasto.VASEN)
    ikkunasto.luo_vaakaerotin(nappikehys, 21)
    ikkunasto.luo_kehys(paaikkuna, ikkunasto.VASEN)
    piirto_tekstikehys = ikkunasto.luo_kehys(paaikkuna, ikkunasto.YLA)
    ikkunasto.luo_kehys(paaikkuna, ikkunasto.OIKEA)
    ikkunasto.luo_tekstirivi(piirto_tekstikehys, "Piirtoalue")
    piirtokentta = ikkunasto.luo_kehys(paaikkuna, ikkunasto.OIKEA)
    nimikehys = ikkunasto.luo_kehys(piirtokentta, ikkunasto.ALA)
    nimikehys_oikea = ikkunasto.luo_kehys(nimikehys, ikkunasto.OIKEA)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_tekstirivi(nimikehys_oikea, "Joonas Ojanen   &   Joni Kuusela")
    tila["piiri"] = piiristo.luo_piiri(piirtokentta, 1200, 800, 8)
    ikkunasto.luo_nappi(nappikehys, "Lisää jännitelähde", lisaa_jannitelahde)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_nappi(nappikehys, "Lisää komponentit", lisaa_komponentti_ui)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_nappi(nappikehys, "Lisää uusi haara", uusi_haara)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_nappi(nappikehys, "Lisää rinnankytkentä", lisaa_komponentti_rinnan_ui)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_nappi(nappikehys, "Poista viimeisin komponentti", poista_viimeisin_komponentti)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_nappi(nappikehys, "Alusta", alusta)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_nappi(nappikehys, "Laske", laske)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_nappi(nappikehys, "Sulje piiri", sulje_piiri)
    ikkunasto.luo_vaakaerotin(nappikehys, 5)
    ikkunasto.luo_nappi(nappikehys, "Poistu", ikkunasto.lopeta)
    tila["laatikko"] = ikkunasto.luo_tekstilaatikko(nappikehys, leveys=50, korkeus=26.5)
    ikkunasto.kaynnista()


if __name__ == "__main__":
    main()

# Joni Kuusela - 2687858
# Joonas Ojanen - 2586289
