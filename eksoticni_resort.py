from bottle import *
import sqlite3
import hashlib


# KONFIGURACIJA
baza_datoteka = 'eksoticni_resort.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True)  # za izpise pri razvoju

# Mapa za statične vire (slike, css, ...)
static_dir = "./static"

# Funkcija za pomoč pri štetju dni

def daterange(start_date, end_date):
    date_format = "%Y-%m-%d"
    a = datetime.strptime(start_date, date_format)
    b = datetime.strptime(end_date, date_format)
    for n in range(int((b - a).days)):
        yield start_date + timedelta(n)



# SPLETNI NASLOVI

@route("/static/<filename:path>") #za slike in druge "monade"
def static(filename):
    return static_file(filename, root=static_dir)



@get('/')
def zacetna_stran():
    redirect('gost')


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
    zasedena = cur.execute("SELECT datum, gost_id, gost.ime, gost.priimek FROM nastanitve INNER JOIN gost ON gost_id = gost.emso WHERE soba_id = ?", (stevilka,)).fetchall()
    return template('pregled-zasedenosti.html', zasedena=zasedena, stevilka=stevilka, napaka=napaka) 



@get('/sobe/rezerviraj/<stevilka>')
def rezerviraj_sobo_get(stevilka):
    napaka = None
    zasedena = cur.execute("SELECT datum, gost_id, gost.ime, gost.priimek FROM nastanitve INNER JOIN gost ON gost_id = gost.emso WHERE soba_id = ?", (stevilka,)).fetchall()
    return template('rezerviraj-sobo.html', zasedena=zasedena, napaka=napaka, stevilka=stevilka)

@post('/sobe/rezerviraj/<stevilka>')
def rezerviraj_sobo_post(stevilka):
    gost_id = request.forms.gost_id
    soba_id = request.forms.soba_id
    datumprihoda = request.forms.datumprihoda
    datumodhoda = request.forms.datumodhoda

    cur = baza.cursor()

#    for single_date in daterange(datumprihoda, datumodhoda):    
    cur.execute("INSERT INTO nastanitve (gost_id, datum, soba_id) VALUES (?, ?, ?)", 
        (gost_id, datumprihoda, soba_id))
    redirect('/sobe/pregled/' + soba_id)


#@post('/zaposleni/uredi/<emso>')
#def uredi_zaposlenega_post(emso):
#    novi_emso = request.forms.emso
#    ime = request.forms.ime
#    priimek = request.forms.priimek
#    spol = request.forms.spol
#    placa = request.forms.placa
#    oddelek = request.forms.oddelek
#    cur = baza.cursor()
#    cur.execute("UPDATE zaposleni SET emso = ?, ime = ?, priimek = ?, spol = ?, placa = ?, oddelek = ? WHERE emso = ?", 
#        (novi_emso, ime, priimek, spol, placa, oddelek, emso))
#    redirect('/zaposleni')
#
#





baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.set_trace_callback(print) # izpis sql stavkov v terminal (za debugiranje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# reloader=True nam olajša razvoj (ozveževanje sproti - razvoj)
run(host='localhost', port=8080, reloader=True)