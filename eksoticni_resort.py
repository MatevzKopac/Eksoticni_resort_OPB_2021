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
    

# SPLETNI NASLOVI

@route("/static/<filename:path>") #za slike in druge "monade"
def static(filename):
    return static_file(filename, root=static_dir)



@get('/')
def zacetna_stran():
    redirect('prijava')


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ G O S T J E ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/gost')
def gost():
    napaka = None
    cur = baza.cursor()
    gosti = cur.execute("""
        SELECT emso, ime, priimek, drzava, spol, starost FROM gost
    """)
    return template('gost.html', gosti=gosti, napaka=napaka)


@get('/gost/dodaj')
def dodaj_gosta_get():
    napaka = None
    return template('gost-dodaj.html', napaka=napaka)


@post('/gost/dodaj')
def dodaj_gosta_post():
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
    napaka = None
    gost = cur.execute("SELECT emso, ime, priimek, drzava, spol, starost FROM gost WHERE emso = ?", (emso,)).fetchone()
    return template('gost-uredi.html', napaka=napaka, gost=gost)


@post('/gost/uredi/<emso>')
def uredi_gosta_post(emso):
    novi_emso = request.forms.emso
    ime = request.forms.ime
    priimek = request.forms.priimek
    drzava = request.forms.drzava
    spol = request.forms.spol
    starost = request.forms.starost
    cur = baza.cursor()
    cur.execute("UPDATE gost SET emso = ?, ime = ?, priimek = ?, drzava = ?, spol = ?, starost = ? WHERE emso = ?", 
        (novi_emso, ime, priimek, drzava, spol, starost, emso))
    redirect('/gost')


@post('/gost/brisi/<emso>')
def brisi_gosta(emso):
    napaka = None
    cur = baza.cursor()
    cur.execute("DELETE FROM gost WHERE emso = ?", (emso, ))
    redirect('/gost')


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Z A P O S L E N I ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/zaposleni')
def zaposleni():
    napaka = None
    cur = baza.cursor()
    zaposleni = cur.execute("""
        SELECT emso, ime, priimek, spol, placa, oddelek FROM zaposleni
    """)
    return template('zaposleni.html', zaposleni=zaposleni, napaka=napaka)


@post('/zaposleni/brisi/<emso>')
def brisi_zaposlenega(emso):
    napaka = None
    cur = baza.cursor()
    cur.execute("DELETE FROM zaposleni WHERE emso = ?", (emso, ))
    redirect('/zaposleni')


@get('/zaposleni/dodaj')
def dodaj_zaposlenega_get():
    napaka = None
    return template('zaposleni-dodaj.html', napaka=napaka)


@post('/zaposleni/dodaj')
def dodaj_zaposlenega_post():
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
    napaka = None
    zaposleni = cur.execute("SELECT emso, ime, priimek, spol, placa, oddelek FROM zaposleni WHERE emso = ?", (emso,)).fetchone()
    return template('zaposleni-uredi.html', zaposleni=zaposleni, napaka=napaka)


@post('/zaposleni/uredi/<emso>')
def uredi_zaposlenega_post(emso):
    novi_emso = request.forms.emso
    ime = request.forms.ime
    priimek = request.forms.priimek
    spol = request.forms.spol
    placa = request.forms.placa
    oddelek = request.forms.oddelek
    cur = baza.cursor()
    cur.execute("UPDATE zaposleni SET emso = ?, ime = ?, priimek = ?, spol = ?, placa = ?, oddelek = ? WHERE emso = ?", 
        (novi_emso, ime, priimek, spol, placa, oddelek, emso))
    redirect('/zaposleni')


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ S O B E ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/sobe')
def sobe():
    napaka = None
    cur = baza.cursor()
    sobe = cur.execute("""
        SELECT stevilka, cena, postelje FROM sobe
    """)
    return template('sobe.html', sobe=sobe, napaka=napaka)


@get('/sobe/pregled/<stevilka>')
def pregled_rezervacij(stevilka):
    napaka = None
    zasedena = cur.execute("SELECT id, datum, gost_id, gost.ime, gost.priimek FROM nastanitve INNER JOIN gost ON gost_id = gost.emso WHERE soba_id = ?", (stevilka,)).fetchall()
    return template('pregled-zasedenosti.html', zasedena=zasedena, stevilka=stevilka, napaka=napaka) 



@get('/sobe/rezerviraj/<stevilka>')
def rezerviraj_sobo_get(stevilka):
    napaka = None
    zasedena = cur.execute("SELECT id, datum, gost_id, gost.ime, gost.priimek FROM nastanitve INNER JOIN gost ON gost_id = gost.emso WHERE soba_id = ?", (stevilka,)).fetchall()
    return template('rezerviraj-sobo.html', zasedena=zasedena, napaka=napaka, stevilka=stevilka)

@post('/sobe/rezerviraj/<stevilka>')
def rezerviraj_sobo_post(stevilka):
    gost_id = request.forms.gost_id
    soba_id = request.forms.soba_id
    datumprihoda = request.forms.datumprihoda
    datumodhoda = request.forms.datumodhoda

    seznam = daterange(datumprihoda, datumodhoda)

    cur = baza.cursor()

    for datum in seznam:    
        cur.execute("INSERT INTO nastanitve (gost_id, datum, soba_id) VALUES (?, ?, ?)", 
            (gost_id, datum, soba_id))
    redirect('/sobe/pregled/' + soba_id)

@post('/sobe/brisi/<id>/<stevilka>')
def rezerviraj_sobo_post(id, stevilka):
    napaka = None
    cur = baza.cursor()
    cur.execute("DELETE FROM nastanitve WHERE id = ?", (id, ))
    redirect('/sobe/pregled/' + stevilka)


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ H R A N A ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/hrana')
def narocila():
    napaka = None
    cur = baza.cursor()
    hrana = cur.execute("""
        SELECT DISTINCT hrana.id, hrana.gost_id, gost.ime, gost.priimek, nastanitve.soba_id, hrana.datum, tip_obroka FROM hrana 
        INNER JOIN gost ON hrana.gost_id = gost.emso 
        INNER JOIN nastanitve ON (hrana.gost_id = nastanitve.gost_id AND hrana.datum = nastanitve.datum)
        WHERE (pripravljena == 0)
    """)
    return template('hrana.html', hrana=hrana, napaka=napaka)

# To je treba popraviti, da avtomatsko doda id zaposlenega, ki postreže (ko bojo ustimani usernameji)
@post('/hrana/postrezi/<id>')
def postrezi(id):
    napaka = None
    cur = baza.cursor()
    cur.execute("UPDATE hrana SET pripravljena = 1, pripravil_id = NULL WHERE id = ?",(id))
    redirect('/hrana')

@get('/hrana/dodaj')
def dodaj_hrano_get():
    napaka = None 
    cur = baza.cursor()
    return template('hrana-dodaj.html', napaka=napaka)

@post('/hrana/dodaj')
def dodaj_hrano_post():
    emso = request.forms.emso
    datum = request.forms.datum
    obrok = request.forms.obrok
    cur = baza.cursor()
    cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (?, ?, ?, 0, NULL)", 
         (emso, datum, obrok))
    redirect('/hrana')


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ C I S C E N J E ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/ciscenje')
def ciscenje():
    napaka = None
    cur = baza.cursor()
    ciscenje = cur.execute("""
        SELECT id, obvezno_do, soba_id FROM ciscenje 
        WHERE (pocisceno == 0)
        ORDER BY obvezno_do ASC;
    """)
    return template('ciscenje.html', ciscenje=ciscenje, napaka=napaka)

@get('/ciscenje/zgodovina')
def ciscenje_zgodovina():
    napaka = None
    cur = baza.cursor()
    ciscenje = cur.execute("""
        SELECT id, soba_id, datum, cistilka_id, zaposleni.ime, zaposleni.priimek FROM ciscenje
        INNER JOIN zaposleni ON (zaposleni.emso = cistilka_id)
        WHERE (pocisceno == 1)
        ORDER BY datum DESC;
    """)
    return template('ciscenje-zgodovina.html', ciscenje=ciscenje, napaka=napaka)

# Tukaj je treba dodati še, da se avtomatsko napiše emšo uporabnika-čistilke, ki je prijavljena v sistem
@post('/ciscenje/pocisti/<id>')
def pocisti(id):
    from datetime import date
    cur.execute("UPDATE ciscenje SET pocisceno = 1, datum = ?, cistilka_id = '4276ad76-7ff9-476a-85e0-b5b6c0842c1c' WHERE id = ?", 
        (date.today().strftime("%Y-%m-%d"), id))
    redirect('/ciscenje')


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ R E G I S T R A C I J A, P R I J A V A ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/registracija')
def registracija():
    napaka = None
    return template('registracija.html', napaka=napaka)

@get('/prijava')
def prijava():
    napaka = None
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
<<<<<<< HEAD
    cur.execute('INSERT INTO gost (emso, ime, priimek, drzava, spol, starost, username, geslo) VALUES (?,?,?,?,?,?,?,?)',(emso, ime, priimek, drzava,spol, starost, username, password))
    return redirect('/gost')
=======
    cur.execute('INSERT INTO gost()')

>>>>>>> 1df715d90929979c669b6538d251909ecc327e11

@post('/prijava')
def prijava_post():
    username = request.forms.username
    password = request.forms.password



baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.set_trace_callback(print) # izpis sql stavkov v terminal (za debugiranje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")


# reloader=True nam olajša razvoj (ozveževanje sproti - razvoj)
run(host='localhost', port=8080, reloader=True)