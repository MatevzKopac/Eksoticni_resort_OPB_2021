from bottle import *
import sqlite3
import hashlib


# KONFIGURACIJA
baza_datoteka = 'eksoticni_resort.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True)  # za izpise pri razvoju

# Mapa za statične vire (slike, css, ...)
static_dir = "./static"


# SPLETNI NASLOVI

@route("/static/<filename:path>") #za slike in druge "monade"
def static(filename):
    return static_file(filename, root=static_dir)



@get('/')
def zacetna_stran():
    redirect('gost')


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



baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.set_trace_callback(print) # izpis sql stavkov v terminal (za debugiranje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# reloader=True nam olajša razvoj (ozveževanje sproti - razvoj)
run(host='localhost', port=8080, reloader=True)