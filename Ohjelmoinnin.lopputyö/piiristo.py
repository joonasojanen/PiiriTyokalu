"""
piiristo - yksinkertainen RLC-piirilaajennus ikkunasto:lle

@author Mika Oja, Oulun yliopisto

Kirjasto on laajennus yksinkertaiselle ikkunasto-nimiselle käyttöliittymä-
kirjastolle. Sisältää uuden käyttöliittymäkomponentin (rajoitettujen) 
piirikaavioiden piirtämiseen. Piirikaavioelementin luomista ja siihen 
piirtämistä varten on omat funktionsa. Yksinkertaisen käyttöesimerkin löydät
tämän kirjaston pääohjelmasta. 

Kirjasto käyttää schemdraw-kirjastoa

https://cdelker.bitbucket.io/schemdraw/schemdraw.html

sekä SchemCanvas-laajennusta, joka lisää kirjastoon tuen 
käyttöliittymäelementtiin piirtämiseen (schemdraw.py). Laajennustiedosto tulee
laittaa samaan kansioon tämän kirjaston ja sitä käyttävän ohjelman kanssa. 
"""

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from tkinter import *
from tkinter.ttk import *

import SchemDraw as scm
import SchemDraw.elements as e
from SchemCanvas import CanvasDrawing, CanvasFigure

piirtoikkuna = {
    "kuvaaja": None,
    "piirtoalue": None,
    "akselit": None,
}

def _piirra_komponentti(piiri, komponentti, arvo, pituusyksikko):
    """
    Piirtää piirii yhden komponentin piirtokursorin nykyiseen sijaintiin ja 
    päivittää piirtokursorin sijainnin. Funktio on tarkoitettu tämän kirjaston
    sisäiseen käyttöön, ja tarvit sitä ainoastaan jos haluat 
    uudelleenkirjoittaa piirin asettelualgoritmin. 
    
    :param str komponentti: komponentin tyyppi (R, L tai C)
    :param str arvo: komponentin arvo, voi sisältää kerrannaisyksikön
    :param float pituusyksikko: piirin asettelussa käytettävä pituuskerroin
    """
    
    if komponentti[0].lower() == "r":
        piiri.add(e.RES, d="down", label="{}$\Omega$".format(arvo), l=3*pituusyksikko)
    elif komponentti[0].lower() == "c":
        piiri.add(e.CAP, d="down", label="{}F".format(arvo), l=3*pituusyksikko)
    elif komponentti[0].lower() == "l":
        piiri.add(e.INDUCTOR2, d="down", label="{}H".format(arvo), l=3*pituusyksikko)

def _piirra_pariton_rinnankytkenta(piiri, komponentit, pituusyksikko):
    """
    Piirtää rinnankytkennän, jossa on pariton määrä komponentteja. Kytkentä 
    piirretään piirtokursorin nykyiseen sijaintiin, ja piirron päätteeks 
    kursorin sijainti päivitetään. Funktio on tarkoitettu tämän kirjaston 
    sisäisen käyttöön, ja tarvit sitä ainoastaan jos haluat uudelleenkirjoittaa
    piirin asettelualgoritmin.
    
    Piirtää komponentit keskilinjasta ulospäin molempiin suuntiin. 
    
    :param object piiri: piiriobjekti, johon piiri piirretään
    :param list komponentit: lista rinnankytkennän komponenteista
    :param float pituusyksikko: piiri asettelussa käytettävä pituuskerroin    
    """
    
    # Jaetaan komponentit kahteen puoliskoon ja keskikomponenttiin
    keski = len(komponentit) // 2
    vasen = komponentit[:keski]
    oikea = komponentit[keski+1:]
    piiri.add(e.DOT)
    
    # tallennetaan keskilinjan sijainti
    piiri.push()
    
    # piirretään vasemman puolen komponentit
    for i, komp in enumerate(vasen[::-1]):
        piiri.add(e.LINE, d="left", l=1)
        
        # reunimmaiseen liittymään ei tule täppää
        if i != len(vasen) - 1:
            piiri.add(e.DOT)
            
        # talletetaan piirtokursorin sijainti ja piirretään komponentti
        # sekä kytketään se edelliseen / keskilinjaan
        piiri.push()
        _piirra_komponentti(piiri, komp[0], komp[1], pituusyksikko)
        if i != len(vasen) - 1:
            piiri.add(e.DOT)
        piiri.add(e.LINE, d="right", l=1)
        
        # palautetaan piirtokursori seuraavaa komponenttia varten
        piiri.pop()
    
    # palataan keskilinjaan ja tallennetaan se uudestaan
    piiri.pop()    
    piiri.push()
    
    # piirretään oikean puolen komponentit
    for i, komp in enumerate(oikea):
        piiri.add(e.LINE, d="right", l=1)
        
        # reunimmiaseen liittymään ei tule täppää
        if i != len(oikea) - 1:
            piiri.add(e.DOT)
                        
        # talletetaan piirtokursorin sijainti ja piirretään komponentti
        # sekä kytketään se edelliseen / keskilinjaan
        piiri.push()
        _piirra_komponentti(piiri, komp[0], komp[1], pituusyksikko)
        if i != len(oikea) - 1:
            piiri.add(e.DOT)
        piiri.add(e.LINE, d="left", l=1)
        piiri.pop()

    # palataan keskilinjaan ja piirretään keskikomponentti
    piiri.pop()
    _piirra_komponentti(piiri, komponentit[keski][0], komponentit[keski][1], pituusyksikko)
    piiri.add(e.DOT)
    

def _piirra_parillinen_rinnankytkenta(piiri, komponentit, pituusyksikko):
    """
    Piirtää rinnankytkennän, jossa on parillinen määrä komponentteja. Kytkentä 
    piirretään piirtokursorin nykyiseen sijaintiin, ja piirron päätteeks 
    kursorin sijainti päivitetään. Funktio on tarkoitettu tämän kirjaston 
    sisäisen käyttöön, ja tarvit sitä ainoastaan jos haluat uudelleenkirjoittaa
    piirin asettelualgoritmin.
    
    Piirtää komponentit keskilinjasta ulospäin molempiin suuntiin siten, että 
    keskelle ei tule komponenttia, ja komponenttien väli on aina saman 
    pituinen.
    
    :param object piiri: piiriobjekti, johon piiri piirretään
    :param list komponentit: lista rinnankytkennän komponenteista
    :param float pituusyksikko: piiri asettelussa käytettävä pituuskerroin    
    """
    
    # Jaetaan komponentit kahteen puoliskoon
    keski = len(komponentit) // 2
    vasen = komponentit[:keski]
    oikea = komponentit[keski:]
    piiri.add(e.DOT)
    
    # tallennetaan keskilinjan sijainti
    piiri.push()
    
    # piirretään vasemman puolen komponentit
    for i, komp in enumerate(vasen[::-1]):
        
        # ensimmäinen johdin on puolet lyhyempi
        if i == 0:            
            piiri.add(e.LINE, d="left", l=0.5)
        else:
            piiri.add(e.LINE, d="left", l=1)
            
        # reunimmaiseen liittymään ei tule täppää            
        if i != len(vasen) - 1:
            piiri.add(e.DOT)
        
        # talletetaan piirtokursorin sijainti ja piirretään komponentti
        # sekä kytketään se edelliseen / keskilinjaan
        piiri.push()
        _piirra_komponentti(piiri, komp[0], komp[1], pituusyksikko)
        if i != len(vasen) - 1:
            piiri.add(e.DOT)

        if i == 0:
            piiri.add(e.LINE, d="right", l=0.5)
        else:            
            piiri.add(e.LINE, d="right", l=1)
            
        # palautetaan piirtokursori seuraavaa komponenttia varten
        piiri.pop()
        
    # palataan keskilinjaan        
    piiri.pop()
    
    # piirretään oikean puolen komponentit
    for i, komp in enumerate(oikea):

        # ensimmäinen johdin on puolet lyhyempi
        if i == 0:
            piiri.add(e.LINE, d="right", l=0.5)
        else:
            piiri.add(e.LINE, d="right", l=1)

        # reunimmaiseen liittymään ei tule täppää            
        if i != len(oikea) - 1:
            piiri.add(e.DOT)

        # talletetaan piirtokursorin sijainti ja piirretään komponentti
        # sekä kytketään se edelliseen / keskilinjaan
        piiri.push()
        _piirra_komponentti(piiri, komp[0], komp[1], pituusyksikko)
        if i != len(oikea) - 1:
            piiri.add(e.DOT)
        if i == 0:
            piiri.add(e.LINE, d="left", l=0.5)
            
            # tallennetaan erikseen kohta, jossa oikea puoli liittyy 
            # keskilinjaan
            piiri._state.insert(-1, (piiri.here, piiri.theta))
        else:
            piiri.add(e.LINE, d="left", l=1)

        # palautetaan piirtokursori seuraavaa komponenttia varten
        piiri.pop()
    
    # palautetaan keskilinjan sijainti
    piiri.pop()
    piiri.add(e.DOT)



def luo_piiri(kehys, leveys=600, korkeus=400, fonttikoko=16):
    """
    Luo piirikaavion, sekä siihen liittyvän matplotlib-kuvaajan, akselit sekä
    piirtoalueen käyttöliittymän sisällä. Piirtoalueelle määritetään kiinteät
    leveys ja korkeus pikseleinä antamalla niitä vastaavat argumentit. Piiri 
    skaalautuu piirtoalueen koon mukaan, mutta tekstit eivät, joten fonttikoko
    on syytä sovittaa piirtoalueen kokoon. Palauttaa piiri-objektin, jota 
    tarvitaan myöhemmin haarojen ja komponenttien piirtämiseen.
    
    :param object kehys: kehys, johon piirtoalue sijoitetaan
    :param int leveys: piirtoalueen leveys pikseleinä
    :param int korkeus: piirtoalueen korkeus pikseleinä
    :param int fonttikoko: teksteissä käytettävä fonttikoko
    
    :return: piirikaavio-objekti.
    """
    
    piiri = CanvasDrawing(fontsize=fonttikoko)
    pohjakuvaaja = Figure(figsize=(leveys / 100, korkeus / 100), dpi=100)
    akselit = pohjakuvaaja.add_axes((0.0, 0.0, 1.0, 1.0))
    akselit.axis("equal")
    piirtoalue = FigureCanvasTkAgg(pohjakuvaaja, master=kehys)
    piirtoalue.get_tk_widget().pack(side=TOP)
    kuvaaja = CanvasFigure(pohjakuvaaja, akselit)
    piirtoikkuna["kuvaaja"] = kuvaaja
    piirtoikkuna["akselit"] = akselit
    piirtoikkuna["piirtoalue"] = piirtoalue
    return piiri

def tyhjaa_piiri(piiri):
    """
    Pyyhkii edellisen piirin pois piirtoikkunasta. Käytettävä aina ennen uuden 
    piirin aloittamista.
    
    :param object piiri: piiriobjekti, johon liittyvä piirtoalue tyhjätään
    """
    
    piiri.clear()
    piirtoikkuna["akselit"].clear()

def piirra_piiri(piiri):
    """
    Piirtää rakennetun piirin näkyviin piirtoalueelle. 
    
    :param object piiri: piiriobjekti, joka piirretään
    """
    
    piiri.draw(piirtoikkuna["piirtoalue"], piirtoikkuna["kuvaaja"], piirtoikkuna["akselit"])        

def piirra_jannitelahde(piiri, jannite, taajuus, v_asetteluvali=2):
    """
    Piirtää piirin jännitelähteen. Koska kirjasto on optimoitu juuri piiriloppu-
    työn tekemiseen, usean jännitelähteen lisääminen saattaa aiheuttaa outoja
    kaavioita. Asiaan voi vaikuttaa v_asetteluvali-parametrilla. Molemmat 
    numeroarvot annetaan merkkijonoina, joten niissä voi olla kerrannaisyksikkö 
    mukana. Yksiköt sen sijaan sisällytetään mukaan automaattisesti. 
    
    Normaalisti oletusarvo 2 v_asetteluvali-parametrille toimii hyvin, mutta
    jos piiri näyttää pystysuunnassa huonolta, voi tätä parametria koittaa 
    säätää.
    
    :param object piiri: piiriobjekti, jota ollaan muokkaamassa
    :param str jannite: lähteen jännite merkkijonona
    :param str taajuus: lähteen jännite merkkijonona
    :param float v_asetteluvali: komponenttien asetteluun liittyvä kerroin
    """
    
    piiri.clear()
    piirtoikkuna["akselit"].clear()
    piiri.add(e.LINE, d="right", l=0.5, move_cur=False)
    piiri.add(e.SOURCE_V, label="{}V\n{}Hz".format(jannite, taajuus), reverse=True, l=6*v_asetteluvali)    
    piiri.add(e.LINE, d="right", l=0.5)
    
def piirra_haara(piiri, komponentit, h_asetteluvali, v_asetteluvali=2, viimeinen=False):
    """
    Piirtää yhden haaran kaikki komponentit ja rinnankytkennät. Komponentit 
    tulee antaa listana, jossa jokainen komponentti on monikko, jonka 1. arvo 
    on komponentin tyyppi ("r", "c" tai "l") ja toinen on komponentin vieressä
    näytettävä arvo merkkijonona, eli kerrannaisyksikkö voi olla mukana. 
    Rinnankytkennät ovat listassa listoina, jotka sisältävät komponentteja em. 
    tavalla. Yksinkertainen esimerkki haarasta jossa on kolme vastusta, joista 
    kaksi rinnankytkennässä: 
    
    haara = [("r", "100"), [("r", "100"), ("r", "100")]]
    
    Parametreistä v_asetteluvali vaikuttaa komponenttien asetteluun 
    pystysuunnassa (oletusarvo on yleensä ok) ja h_asetteluvali määrittää 
    kuinka paljon tyhjää haaran molemmille puolille jää. Piiri piirtyy hyvin, 
    jos tämän parametrin arvoksi annetaan haaran leveimmän rinnankytkennän 
    komponenttien lukumäärä 
    
    Viimeinen parametri kertoo onko kyseessä piirin viimeinen haara, jolloin 
    ei piirretä liittymäkohtaa, eikä johtimia enää eteenpäin. 
    
    :param object piiri: piiriobjekti, jota ollaan muokkaamassa
    :param list komponentit: lista haaran komponenteista
    :param int h_asetteluvali: vaakasuunan asetteluun vaikuttava kerroin
    :param float v_asetteluvali: pystysuunnan asetteluun liittyvä kerroin
    :param bool viimeinen: onko haara piirin viimeinen
    """
    
    piiri.pop()
    piiri.add(e.LINE, d="right", l=h_asetteluvali/2)
    if not viimeinen:
        piiri.push()        
        piiri.add(e.DOT)
        piiri.add(e.LINE, d="right", l=h_asetteluvali/2)
        piiri._state.insert(-1, (piiri.here, piiri.theta))
        piiri.pop() 
        
    parallels = sum([1 for k in komponentit if isinstance(k, list)])
    if isinstance(komponentit[0], list) and isinstance(komponentit[-1], list):
        loppujohdin = True
        pituusyksikko = v_asetteluvali / (len(komponentit) + 2) * 2  
        piiri.add(e.LINE, d="down", l=3*pituusyksikko)
    elif isinstance(komponentit[0], list):
        loppujohdin = False
        pituusyksikko = v_asetteluvali / (len(komponentit) + 1) * 2  
        piiri.add(e.LINE, d="down", l=3*pituusyksikko)
    elif isinstance(komponentit[-1], list):
        loppujohdin = True
        pituusyksikko = v_asetteluvali / (len(komponentit) + 1) * 2  
    else:
        loppujohdin = False
        pituusyksikko = v_asetteluvali / len(komponentit) * 2  
    for komponentti in komponentit:
        if isinstance(komponentti, list):
            if len(komponentti) % 2 == 0:
                _piirra_parillinen_rinnankytkenta(piiri, komponentti, pituusyksikko)
            else:
                _piirra_pariton_rinnankytkenta(piiri, komponentti, pituusyksikko)
        else:
            _piirra_komponentti(piiri, komponentti[0], komponentti[1], pituusyksikko)
    
    if loppujohdin:
        piiri.add(e.LINE, d="down", l=3*pituusyksikko)
    
    if not viimeinen:
        piiri.add(e.DOT)
        piiri.add(e.LINE, d="right", l=h_asetteluvali/2, move_cur=False)
        
    piiri.add(e.LINE, d="left", l=h_asetteluvali/2)


if __name__ == "__main__":
    import ikkunasto as ui
    
    def piirra_testipiiri():
        haara = [[("r", 100), ("r", 100)], ("r", 200), [("r", 100), ("r", 100), ("r", 100), ("r", 100)]]
        piirra_jannitelahde(piiri, 10, "10k", 2)
        piirra_haara(piiri, haara, 3, 2, viimeinen=False)
        haara = [("c", "1.0n")]
        piirra_haara(piiri, haara, 1, 2, viimeinen=True)
        piirra_piiri(piiri)
        
        
    ikkuna = ui.luo_ikkuna("much circuit")
    kehys = ui.luo_kehys(ikkuna, TOP)
    ui.luo_nappi(kehys, "TESTAA", piirra_testipiiri)
    ui.luo_nappi(kehys, "LOPETA", ui.lopeta)
    piiri = luo_piiri(kehys, 600, 600, 10)
    ui.kaynnista()