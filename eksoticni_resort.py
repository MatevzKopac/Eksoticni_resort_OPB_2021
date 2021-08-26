from re import A
from tempfile import SpooledTemporaryFile
from bottle import *
import sqlite3
import hashlib


# KONFIGURACIJA1
baza_datoteka = 'eksoticni_resort.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True)  # za izpise pri razvoju

# Mapa za statične vire (slike, css, ...)
static_dir = "./static"

# Funkcija za pomoč pri štetju dni
import datetime


###PREBERI: podatek username dobiš avtoamtsko s funkcijo username = request.get_cookie("username", secret=skrivnost)#### Hvala lepa Žan
def daterange(start_date, end_date):
    list = []
    date_1 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    date_2 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    datum = date_1

    while datum != date_2:
        list.append(datum.strftime("%Y-%m-%d"))
        datum = datum + datetime.timedelta(days=1)

    return list

skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"


def nastaviSporocilo(sporocilo = None):
    # global napakaSporocilo
    staro = request.get_cookie("sporocilo", secret=skrivnost)
    if sporocilo is None:
        response.delete_cookie('sporocilo')
    else:
        response.set_cookie('sporocilo', sporocilo, path="/", secret=skrivnost)
    return staro 
    

def preveriUporabnika(): 
    username = request.get_cookie("username", secret=skrivnost)
    if username:
        cur = baza.cursor()    
        uporabnik = None
        try: 
            uporabnik = cur.execute("SELECT * FROM gost WHERE username = ?", (username, )).fetchone()
        except:
            uporabnik = None
        if uporabnik: 
            return uporabnik
    redirect('/prijava')


def preveriZaposlenega(): 
    username = request.get_cookie("username", secret=skrivnost)
    if username:
        cur = baza.cursor()    
        uporabnik = None
        try: 
            uporabnik = cur.execute("SELECT * FROM zaposleni WHERE username = ?", (username, )).fetchone()
        except:
            uporabnik = None
        if uporabnik: 
            return uporabnik
    redirect('/prijava')


# SPLETNI NASLOVI

@route("/static/<filename:path>") #za slike in druge "monade"
def static(filename):
    return static_file(filename, root=static_dir)



@get('/')
def zacetna_stran():
    redirect('prijava')

def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()
#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ G O S T J E ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/gost')
def gost():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    gosti = cur.execute("""
        SELECT emso, ime, priimek, drzava, spol, starost FROM gost
    """)

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('gost.html', gosti=gosti, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@get('/gost/dodaj')
def dodaj_gosta_get():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('gost-dodaj.html', napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@post('/gost/dodaj')
def dodaj_gosta_post():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    emso = request.forms.emso
    ime = request.forms.ime
    priimek = request.forms.priimek
    drzava = request.forms.drzava
    spol = request.forms.spol
    starost = request.forms.starost
    cur = baza.cursor()
    cur.execute("INSERT INTO gost (emso, ime, priimek, drzava, spol, starost) VALUES (?, ?, ?, ?, ?, ?)", 
         (emso, ime, priimek, drzava, spol, starost))
    redirect('/gost')


@get('/gost/uredi/<emso>')
def uredi_gosta_get(emso):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()  
    gost = cur.execute("SELECT emso, ime, priimek, drzava, spol, starost FROM gost WHERE emso = ?", (emso,)).fetchone()

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('gost-uredi.html', napaka=napaka, gost=gost, tip_zaposlenega = tip_zaposlenega)


@post('/gost/uredi/<emso>')
def uredi_gosta_post(emso):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    ime = request.forms.ime
    priimek = request.forms.priimek
    drzava = request.forms.drzava
    spol = request.forms.spol
    starost = request.forms.starost
    cur = baza.cursor()
    cur.execute("UPDATE gost SET ime = ?, priimek = ?, drzava = ?, spol = ?, starost = ? WHERE emso = ?", 
        (ime, priimek, drzava, spol, starost, emso))
    redirect('/gost')


@post('/gost/brisi/<emso>')
def brisi_gosta(emso):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    try:
        cur.execute("DELETE FROM gost WHERE emso = ?", (emso, ))
        nastaviSporocilo()
        redirect('/gost')
    except:
        nastaviSporocilo("Gost ima aktivno rezervacijo. Brisanje neuspešno!")
        redirect('/gost')        

@get('/gost/rezervacije/<id>')
def rezervacije_gosta(id):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return    

    napaka = None
    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    ime_gosta = cur.execute("SELECT emso, ime, priimek FROM gost WHERE emso = ?", (id,)).fetchone()
    rezervacije = cur.execute("SELECT id, datum, soba_id FROM nastanitve WHERE gost_id = ? ORDER BY datum ASC", (id,)).fetchall()
    return template('rezervacije_gosta.html', rezervacije=rezervacije, napaka=napaka, ime_gosta=ime_gosta, tip_zaposlenega=tip_zaposlenega) 

@post('/gost/rezervacije/brisi/<id>/<brisanje>')
def brisi_rezervacijo(id, brisanje):
    cur = baza.cursor()
    datum = cur.execute("SELECT datum FROM nastanitve WHERE id = ?", (brisanje, )).fetchone()[0]
    cur = baza.cursor()
    soba = cur.execute("SELECT soba_id FROM nastanitve WHERE id = ?", (brisanje, )).fetchone()[0]
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    cur.execute("DELETE FROM nastanitve WHERE id = ?", (brisanje, ))
    cur.execute("DELETE FROM hrana WHERE gost_id = ? AND datum = ?", (id, datum))
    redirect('/gost/rezervacije/' + id)

#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Z A P O S L E N I ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/zaposleni')
def zaposleni():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    zaposleni = cur.execute("""
        SELECT emso, ime, priimek, spol, placa, oddelek FROM zaposleni WHERE (stanje IS NULL)
    """)

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('zaposleni.html', zaposleni=zaposleni, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@post('/zaposleni/brisi/<emso>')
def brisi_zaposlenega(emso):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    cur.execute("UPDATE zaposleni SET stanje = ? WHERE emso = ?", ("odpuscen",emso))
    redirect('/zaposleni')


@get('/zaposleni/dodaj')
def dodaj_zaposlenega_get():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]


    return template('zaposleni-dodaj.html', napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@post('/zaposleni/dodaj')
def dodaj_zaposlenega_post():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    emso = request.forms.emso
    ime = request.forms.ime
    priimek = request.forms.priimek
    spol = request.forms.spol
    placa = request.forms.placa
    oddelek = request.forms.oddelek
    cur = baza.cursor()
    cur.execute("INSERT INTO zaposleni (emso, ime, priimek, spol, placa, oddelek) VALUES (?, ?, ?, ?, ?, ?)", 
         (emso, ime, priimek, spol, placa, oddelek))
    redirect('/zaposleni')


@get('/zaposleni/uredi/<emso>')
def uredi_zaposlenega_get(emso):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None

    cur = baza.cursor()
    zaposleni = cur.execute("SELECT emso, ime, priimek, spol, placa, oddelek FROM zaposleni WHERE emso = ?", (emso,)).fetchone()

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('zaposleni-uredi.html', zaposleni=zaposleni, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@post('/zaposleni/uredi/<emso>')
def uredi_zaposlenega_post(emso):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    ime = request.forms.ime
    priimek = request.forms.priimek
    spol = request.forms.spol
    placa = request.forms.placa
    oddelek = request.forms.oddelek
    cur = baza.cursor()
    cur.execute("UPDATE zaposleni SET ime = ?, priimek = ?, spol = ?, placa = ?, oddelek = ? WHERE emso = ?", 
        (ime, priimek, spol, placa, oddelek, emso))
    redirect('/zaposleni')


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ S O B E ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/sobe')
def sobe():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    sobe = cur.execute("""
        SELECT stevilka, cena, postelje FROM sobe
    """)

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('sobe.html', sobe=sobe, napaka=napaka, tip_zaposlenega=tip_zaposlenega)

@get('/sobe/pregled/<stevilka>')
def pregled_rezervacij(stevilka):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    zasedena = cur.execute("SELECT id, datum, gost_id, gost.ime, gost.priimek FROM nastanitve INNER JOIN gost ON gost_id = gost.emso WHERE soba_id = ?", (stevilka,)).fetchall()

    username = request.get_cookie("username", secret=skrivnost)
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('pregled-zasedenosti.html', zasedena=zasedena, stevilka=stevilka, napaka=napaka, tip_zaposlenega=tip_zaposlenega) 



@get('/sobe/rezerviraj/<stevilka>')
def rezerviraj_sobo_get(stevilka):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    zasedena = cur.execute("SELECT id, datum, gost_id, gost.ime, gost.priimek FROM nastanitve INNER JOIN gost ON gost_id = gost.emso WHERE soba_id = ?", (stevilka,)).fetchall()

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('rezerviraj-sobo.html', zasedena=zasedena, napaka=napaka, stevilka=stevilka, tip_zaposlenega=tip_zaposlenega)

@post('/sobe/rezerviraj/<stevilka>')
def rezerviraj_sobo_post(stevilka):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    gost_id = request.forms.gost_id

    cur = baza.cursor()
    alisplohjenas = cur.execute("SELECT * FROM gost WHERE emso = ?", (gost_id, )).fetchone()

    if alisplohjenas == None:
        nastaviSporocilo("Vpiši veljaven emšo gosta ali pa ga dodaj v sistem")
        redirect('/sobe/rezerviraj/' + stevilka)

    else:
        soba_id = request.forms.soba_id
        datumprihoda = request.forms.datumprihoda
        datumodhoda = request.forms.datumodhoda


        zajtrk = request.forms.zajtrk
        kosilo = request.forms.kosilo
        vecerja = request.forms.vecerja
        from datetime import datetime

        if datumprihoda > datumodhoda: 
            nastaviSporocilo("Datum prihoda ne sme biti kasneje kot datum odhoda")
            redirect('/sobe/rezerviraj/' + soba_id)      
        if datumprihoda < datetime.today().strftime('%Y-%m-%d'):
            nastaviSporocilo("Prosimo, da ne rezervirate sobe v preteklosti.")
            redirect('/sobe/rezerviraj/' + soba_id)

        seznam = daterange(datumprihoda, datumodhoda)

        cur = baza.cursor()
        mozne_rezervacije = cur.execute('SELECT id FROM nastanitve WHERE datum BETWEEN ? and ? AND soba_id = ?', (datumprihoda, datumodhoda, soba_id, )).fetchone()
        if mozne_rezervacije != None:
                nastaviSporocilo("Žal je soba v tem obdobju že rezervirana.")
                redirect('/sobe/rezerviraj/' + soba_id)
    
        cur = baza.cursor()
        for datum in seznam:
            cur.execute("INSERT INTO nastanitve (gost_id, datum, soba_id) VALUES (?, ?, ?)", 
                (gost_id, datum, soba_id))
            if zajtrk:
                cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (?, ?, ?, 0, NULL)", 
                    (gost_id, datum, 'zajtrk'))
            if kosilo:
                cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (?, ?, ?, 0, NULL)", 
                    (gost_id, datum, 'kosilo'))
            if vecerja:
                cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (?, ?, ?, 0, NULL)", 
                    (gost_id, datum, 'vecerja'))
        cur.execute("INSERT INTO ciscenje (pocisceno, cistilka_id, datum, obvezno_do, soba_id) VALUES (0, NULL, NULL, ?, ?)", (datumprihoda, soba_id))
        redirect('/sobe/pregled/' + soba_id)


@post('/sobe/brisi/<id>/<stevilka>')
def rezerviraj_sobo_post(id, stevilka):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    cur.execute("DELETE FROM nastanitve WHERE id = ?", (id, ))
    redirect('/sobe/pregled/' + stevilka)


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ H R A N A ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/hrana')
def narocila():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()

    cur = baza.cursor()
    hrana = cur.execute("""
        SELECT DISTINCT hrana.id, hrana.gost_id, gost.ime, gost.priimek, nastanitve.soba_id, hrana.datum, tip_obroka FROM hrana 
        INNER JOIN gost ON hrana.gost_id = gost.emso 
        INNER JOIN nastanitve ON (hrana.gost_id = nastanitve.gost_id AND hrana.datum = nastanitve.datum)
        WHERE (pripravljena == 0)
        ORDER BY hrana.datum ASC
    """)

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('hrana.html', hrana=hrana, napaka=napaka, tip_zaposlenega=tip_zaposlenega)

@post('/hrana/postrezi/<id>')
def postrezi(id):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return

    cur = baza.cursor()

    username = request.get_cookie("username", secret=skrivnost)
    id_zaposlenega = cur.execute('SELECT emso FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    from datetime import datetime
    datum_hrane = cur.execute("SELECT datum FROM hrana WHERE id = ?",(id, )).fetchone()[0]
    danes = datetime.today().strftime('%Y-%m-%d')

    if danes == datum_hrane:
        cur = baza.cursor()
        cur.execute("UPDATE hrana SET pripravljena = 1, pripravil_id = ? WHERE id = ?",(id_zaposlenega, id, ))
        redirect('/hrana')
    else:
        nastaviSporocilo("Priprava hrane je možna samo na dan naročila")
        redirect('/hrana')

@get('/hrana/dodaj')
def dodaj_hrano_get():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None 
    cur = baza.cursor()

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('hrana-dodaj.html', napaka=napaka, tip_zaposlenega=tip_zaposlenega)

@post('/dodaj')
def dodaj_hrano_post():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    emso = request.forms.emso
    datum = request.forms.datum
    obrok = request.forms.obrok
    cur = baza.cursor()
    cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (?, ?, ?, 0, NULL)", 
         (emso, datum, obrok))
    redirect('/hrana')


@get('/hrana/zgodovina')
def zgodovina_hrane():
    cur = baza.cursor()
    napaka = None
    hrana = cur.execute("""
        SELECT DISTINCT hrana.id, hrana.gost_id, gost.ime, gost.priimek, nastanitve.soba_id, hrana.datum, tip_obroka, zaposleni.emso, zaposleni.ime, zaposleni.priimek FROM hrana 
        INNER JOIN gost ON hrana.gost_id = gost.emso 
        INNER JOIN nastanitve ON (hrana.gost_id = nastanitve.gost_id AND hrana.datum = nastanitve.datum)
        INNER JOIN zaposleni ON (hrana.pripravil_id = zaposleni.emso)
        WHERE (pripravljena == 1)
    """)

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('hrana-zgodovina.html', hrana=hrana, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ C I S C E N J E ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/ciscenje')
def ciscenje():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    ciscenje = cur.execute("""
        SELECT id, obvezno_do, soba_id FROM ciscenje 
        WHERE (pocisceno == 0)
        ORDER BY obvezno_do ASC;
    """)

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('ciscenje.html', ciscenje=ciscenje, napaka=napaka, tip_zaposlenega=tip_zaposlenega)

@get('/ciscenje/zgodovina')
def ciscenje_zgodovina():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    ciscenje = cur.execute("""
        SELECT id, soba_id, datum, cistilka_id, zaposleni.ime, zaposleni.priimek FROM ciscenje
        INNER JOIN zaposleni ON (zaposleni.emso = cistilka_id)
        WHERE (pocisceno == 1)
        ORDER BY datum DESC;
    """)

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('ciscenje-zgodovina.html', ciscenje=ciscenje, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@post('/ciscenje/pocisti/<id>')
def pocisti(id):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    from datetime import date

    username = request.get_cookie("username", secret=skrivnost)
    id_cistilke = cur.execute('SELECT emso FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    cur.execute("UPDATE ciscenje SET pocisceno = 1, datum = ?, cistilka_id = ? WHERE id = ?", 
        (date.today().strftime("%Y-%m-%d"), id_cistilke, id))
    redirect('/ciscenje')


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ R E G I S T R A C I J A, P R I J A V A ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/registracija')
def registracija():
    napaka = nastaviSporocilo()
    return template('registracija.html', napaka=napaka)

@get('/prijava')
def prijava():
    napaka = nastaviSporocilo()
    return template('prijava.html', napaka=napaka)


@post('/registracija')
def registracija_post():
    emso = request.forms.emso
    username = request.forms.username
    password = request.forms.password
    password2 = request.forms.password2
    ime = request.forms.ime
    priimek = request.forms.priimek
    spol = request.forms.spol
    drzava = request.forms.drzava
    starost = request.forms.starost  
    if password != password2:
        nastaviSporocilo('Gesli se ne ujemata') 
        redirect('/registracija')
        return
    if len(password) < 4:
        nastaviSporocilo('Geslo mora vsebovati vsaj štiri znake') 
        redirect('/registracija')
        return
    if emso is None or username is None or password is None or password2 is None or ime is None or priimek is None or spol is None or drzava is None or starost is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect('/registracija')
        return
    cur = baza.cursor()
    uporabnik = None   
    try:
        uporabnik = cur.execute('SELECT * FROM gost WHERE emso = ?', (emso, )).fetchone()  
    except:
        uporabnik = None    
    if uporabnik is not None:
        nastaviSporocilo('Uporabnik s tem emšom že obstaja!') 
        redirect('/registracija')
        return
    uporabnik = None   
    try:
        uporabnik = cur.execute('SELECT * FROM gost WHERE username = ?', (username, )).fetchone()  
    except:
        uporabnik = None    
    if uporabnik is not None:
        nastaviSporocilo('Username že obstaja!') 
        redirect('/registracija')
        return
    zgostitev = hashGesla(password)    
    cur.execute('INSERT INTO gost (emso, ime, priimek, drzava, spol, starost, username, geslo) VALUES (?,?,?,?,?,?,?,?)',(emso, ime, priimek, drzava,spol, starost, username, zgostitev))
    response.set_cookie('username', username, secret=skrivnost)
    return redirect('/prijava')

@post('/prijava')
def prijava_post():
    username = request.forms.username
    password = request.forms.password

    # Tega v bistvu sploh ne rabimo
    if username is None or password is None:
        nastaviSporocilo('Mankajoče uporabniško ime ali geslo!') 
        redirect('/prijava')
    
    cur = baza.cursor()
    hgeslo = None
    geslo = None
    try:
        hgeslo = cur.execute('SELECT geslo FROM gost WHERE username = ?', (username, )).fetchone()
        hgeslo = hgeslo[0]
    except:
        hgeslo = None
          
    try:
        geslo = cur.execute('SELECT geslo FROM zaposleni WHERE username = ?', (username, )).fetchone()
        geslo = geslo[0]
    except:
        geslo = None    
    if hgeslo is None and geslo is None:
        nastaviSporocilo('Uporabniško ime ali geslo nista ustrezni!') 
        redirect('/prijava')
        return
    if hashGesla(password) != hgeslo and password != geslo:
        nastaviSporocilo('Napačno geslo!') 
        redirect('/prijava')
        return
    response.set_cookie('username', username, secret=skrivnost)

    # Tukaj je za zaposlene
    if hgeslo is None:
        redirect('/uporabnik')

    # Tukaj je za goste
    if geslo is None:
        redirect('/uporabnik_gost')


@get('/odjava')
def odjava_get():
    response.delete_cookie('username')
    redirect('/prijava')


#težave:
#       rezervacije se prekrivajo, možno rezervirati v preteklost, gostje drug drugemu brišejo rezervacije(brišejo samo zaposleni)
#       username in password   zaposlenih (potrebno dodati)
#       dostop zaposlenih/gostov ---> morajo imeti razlčne vpoglede
#       izdelati moj profil stran (mogoče tukaj notri možne rezervacije nočitev in prehrane)

#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ DOSTOP GOSTOV ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@get('/dostop_gosta')
def gost():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    gosti = cur.execute("""
        SELECT emso, ime, priimek, drzava, spol, starost FROM gost
    """)
    return template('dostop_gosta.html', gosti=gosti, napaka=napaka)



#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ STRANI ZA GOSTE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SOBE ZA GOSTE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/sobe_gost')
def sobe():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    sobe = cur.execute("""
        SELECT stevilka, cena, postelje FROM sobe
    """)
    return template('sobe_gost.html', sobe=sobe, napaka=napaka)



@get('/sobe_gost/pregled/<stevilka>')
def pregled_rezervacij(stevilka):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    zasedena = cur.execute("SELECT id, datum, gost_id, gost.ime, gost.priimek, gost.username FROM nastanitve INNER JOIN gost ON gost_id = gost.emso WHERE soba_id = ?", (stevilka,)).fetchall()
    return template('pregled-zasedenosti_gost.html', zasedena=zasedena, stevilka=stevilka, napaka=napaka) 

@get('/sobe_gost/moje_rezervacije')
def moje_rezervacije():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return    

    napaka = None
    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    emso_gosta = cur.execute('SELECT emso FROM gost WHERE username = ?', (username, )).fetchone()[0]

    cur = baza.cursor()
    rezervacije = cur.execute("SELECT datum, soba_id FROM nastanitve WHERE gost_id = ? ORDER BY datum ASC", (emso_gosta,)).fetchall()

    return template('sobe_gost-mojerezervacije.html', rezervacije=rezervacije, napaka=napaka) 


@get('/sobe_gost/rezerviraj')
def rezerviraj_sobo_get():
    uporabnik = preveriUporabnika()
    napaka = nastaviSporocilo()

    if uporabnik is None: 
        return
    return template('rezerviraj-sobo_gost.html', napaka=napaka)


@get('/sobe_gost/rezerviraj/<stevilka>')
def rezerviraj_sobo_get(stevilka):
    uporabnik = preveriUporabnika()
    napaka = nastaviSporocilo()

    if uporabnik is None: 
        return
    return template('rezerviraj-sobo_gost.html', napaka=napaka, stevilka=stevilka)


@post('/sobe_gost/rezerviraj/<stevilka>')
def rezerviraj_sobo_post(stevilka):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    
    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    emso_gosta = cur.execute('SELECT emso FROM gost WHERE username = ?', (username, )).fetchone()[0]

    gost_id = emso_gosta
    soba_id = request.forms.soba_id
    datumprihoda = request.forms.datumprihoda
    datumodhoda = request.forms.datumodhoda

    zajtrk = request.forms.zajtrk
    kosilo = request.forms.kosilo
    vecerja = request.forms.vecerja



    from datetime import datetime

    if datumprihoda > datumodhoda: 
        nastaviSporocilo("Datum prihoda ne sme biti kasneje kot datum odhoda")
        redirect('/sobe_gost/rezerviraj/' + soba_id)      
    if datumprihoda < datetime.today().strftime('%Y-%m-%d'):
        nastaviSporocilo("Prosimo, da ne rezervirate sobe v preteklosti.")
        redirect('/sobe_gost/rezerviraj/' + soba_id)

    seznam = daterange(datumprihoda, datumodhoda)

    cur = baza.cursor()
    mozne_rezervacije = cur.execute('SELECT id FROM nastanitve WHERE datum BETWEEN ? and ? AND soba_id = ?', (datumprihoda, datumodhoda, soba_id, )).fetchone()
    if mozne_rezervacije != None:
            nastaviSporocilo("Žal je soba v tem obdobju že rezervirana.")
            redirect('/sobe_gost/rezerviraj/' + soba_id)
 
    cur = baza.cursor()
    for datum in seznam:
        cur.execute("INSERT INTO nastanitve (gost_id, datum, soba_id) VALUES (?, ?, ?)", 
            (gost_id, datum, soba_id))

        if zajtrk:
            cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (?, ?, ?, 0, NULL)", 
                (gost_id, datum, 'zajtrk'))
        if kosilo:
            cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (?, ?, ?, 0, NULL)", 
                (gost_id, datum, 'kosilo'))
        if vecerja:
            cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (?, ?, ?, 0, NULL)", 
                (gost_id, datum, 'vecerja'))
    
    cur.execute("INSERT INTO ciscenje (pocisceno, cistilka_id, datum, obvezno_do, soba_id) VALUES (0, NULL, NULL, ?, ?)", (datumprihoda, soba_id))

    redirect('/sobe_gost/pregled/' + soba_id)


@post('/sobe_gost/brisi/<datum>/<soba>')
def brisi_sobo(datum, soba):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = None

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    emso_gosta = cur.execute('SELECT emso FROM gost WHERE username = ?', (username, )).fetchone()[0]

    cur = baza.cursor()
    cur.execute("DELETE FROM nastanitve WHERE datum = ? AND soba_id = ? AND gost_id = ?", (datum, soba, emso_gosta))

    cur = baza.cursor()
    cur.execute("DELETE FROM hrana WHERE datum = ? AND gost_id = ?", (datum, emso_gosta))
    cur.execute("DELETE FROM ciscenje WHERE soba_id = ? AND obvezno_do = ?", (soba, datum))

    redirect('/sobe_gost/moje_rezervacije')

#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HRANA ZA GOSTE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/hrana_gost')
def narocila():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    emso_gosta = cur.execute('SELECT emso FROM gost WHERE username = ?', (username, )).fetchone()[0]

    cur = baza.cursor()
    hrana = cur.execute("""
        SELECT DISTINCT nastanitve.soba_id, hrana.datum, tip_obroka FROM hrana 
        INNER JOIN nastanitve ON (hrana.gost_id = nastanitve.gost_id AND hrana.datum = nastanitve.datum)        
        WHERE (hrana.gost_id == ?)
        ORDER BY hrana.datum ASC
    """, (emso_gosta, ))
    return template('hrana_gost.html', hrana=hrana, napaka=napaka)


@get('/hrana_gost/dodaj')
def dodaj_hrano_get():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    
    napaka = None
    cur = baza.cursor()

    return template('hrana-dodaj_gost.html', napaka=napaka)

@post('/hrana_gost/dodaj')
def dodaj_hrano_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    emso_gosta = cur.execute('SELECT emso FROM gost WHERE username = ?', (username, )).fetchone()[0]

    emso = emso_gosta
    datum = request.forms.datum
    obrok = request.forms.obrok

    alisplohbivaprinas = cur.execute('SELECT * FROM nastanitve WHERE gost_id = ? AND datum = ?', (emso, datum, )).fetchone()

    if alisplohbivaprinas == None:
        nastaviSporocilo('V izbranem datumu ne bivate v hotelu')  
        redirect('/hrana_gost')

    cur = baza.cursor()
    cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (?, ?, ?, 0, NULL)", 
         (emso, datum, obrok))
    redirect('/hrana_gost')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~PROFIL GOSTA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~1


@get('/uporabnik_gost')
def uporabnik():
    uporabnik = preveriUporabnika()
    if gost is None: 
        return
    napaka = nastaviSporocilo()
    username = request.get_cookie("username", secret=skrivnost)
    uporabnik = cur.execute("SELECT * FROM gost WHERE username = ?", (username, ))
    return template('profil_uporabnika.html', uporabnik=uporabnik, napaka=napaka,)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~PROFIL ZAPOSLENEGA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@get('/uporabnik')
def uporabnik():
    uporabnik = preveriZaposlenega()
    if gost is None: 
        return
    napaka = nastaviSporocilo()
    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    uporabnik = cur.execute("SELECT emso, ime, priimek, spol, placa, oddelek, username, geslo FROM zaposleni WHERE username = ?", (username, ))
    
    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]
    
    return template('profil_zaposlenega.html', uporabnik=uporabnik, napaka=napaka, tip_zaposlenega=tip_zaposlenega)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~SPREMEMBA GESLA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/spremeni_geslo')
def spremeni_geslo():
    napaka = nastaviSporocilo()

    username = request.get_cookie("username", secret=skrivnost)
    tip_zaposlenega = cur.execute('SELECT oddelek FROM zaposleni WHERE username = ?', (username, )).fetchone()[0]

    return template('spremeni_geslo.html', napaka=napaka, tip_zaposlenega=tip_zaposlenega)

@post('/spremeni_geslo')
def spremeni_geslo():
    username = request.get_cookie("username", secret=skrivnost)
    password = request.forms.password
    password2 = request.forms.password2
    if password != password2:
        nastaviSporocilo('Gesli se ne ujemata') 
        redirect('/spremeni_geslo')
        return
    if len(password) < 4:
        nastaviSporocilo('Geslo mora vsebovati vsaj štiri znake') 
        redirect('/spremeni_geslo')
        return 
    cur = baza.cursor()
    if username:    
        uporabnik1 = None
        uporabnik2 = None
        try: 
            uporabnik1 = cur.execute("SELECT * FROM zaposleni WHERE username = ?", (username, )).fetchone()
        except:
            uporabnik1 = None
        try: 
            uporabnik2 = cur.execute("SELECT * FROM gost WHERE username = ?", (username, )).fetchone()
        except:
            uporabnik2 = None    
        if uporabnik1: 
            cur.execute("UPDATE zaposleni SET  geslo = ? WHERE username = ?", (password ,username))
            return redirect('/prijava')  
        if uporabnik2:
            zgostitev = hashGesla(password)
            cur.execute("UPDATE gost SET  geslo = ? WHERE username = ?", (zgostitev ,username))     
            return redirect('/prijava')
    nastaviSporocilo('Obvezna registracija') 
    redirect('/registracija')    



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~1
baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.set_trace_callback(print) # izpis sql stavkov v terminal (za debugiranje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# reloader=True nam olajša razvoj (ozveževanje sproti - razvoj)
run(host='localhost', port=8080, reloader=True)










