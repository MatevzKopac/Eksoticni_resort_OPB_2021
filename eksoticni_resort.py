from re import A
from tempfile import SpooledTemporaryFile
from bottle import *
import hashlib

from bottleext import *

#podatki za povezavo na bazo
import auth_public as auth

#psycopg2 za priklop na bazo
import psycopg2, psycopg2.extensions, psycopg2.extras 
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)


# Baza
baza_datoteka = 'eksoticni_resort.db'
debug(True)  # za izpise pri razvoju
static_dir = "./static"


#Privzete nastavitve za Bottle
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/') 
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


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


# Pomožne funkcije

def nastaviSporocilo(sporocilo = None):
    staro = request.get_cookie("sporocilo", secret=skrivnost)
    if sporocilo is None:
        response.delete_cookie('sporocilo', path="/")
    else:
        response.set_cookie('sporocilo', sporocilo, secret=skrivnost, path="/")
    return staro 
    
def preveriUporabnika(): 
    username = request.get_cookie("username", secret=skrivnost)
    if username:
        cur = baza.cursor()
        uporabnik = None
        try: 
            cur.execute('SELECT * FROM gost WHERE username = %s', (username, ))
            uporabnik = cur.fetchone()
        except:
            uporabnik = None
        if uporabnik: 
            return uporabnik
    redirect(url('/prijava'))

def preveriZaposlenega(): 
    username = request.get_cookie("username", secret=skrivnost)
    if username:
        cur = baza.cursor()    
        uporabnik = None
        try: 
            cur.execute('SELECT * FROM zaposleni WHERE username = %s', (username, ))
            uporabnik = cur.fetchone()
        except:
            uporabnik = None
        if uporabnik: 
            return uporabnik
    redirect(url('/prijava'))


# Tukaj se potem začnejo spletni naslovi

@route("/static/<filename:path>") #za slike in druge "monade"
def static(filename):
    return static_file(filename, root=static_dir)

@get('/')
def zacetna_stran():
    redirect(url('prijava'))

def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()

    

#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   ~~~~~~~~~~~~~~~~~~~ PRVI DEL KODE: DOSTOP ZAPOSLENIH ~~~~~~~~~~~~~~~~~~
#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ G O S T J E ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/gost')
def gost():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()

    cur = baza.cursor()
    cur.execute("SELECT emso, ime, priimek, drzava, spol, starost FROM gost")
    gosti = cur

    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    return template('gost.html', gosti=gosti, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@get('/gost/dodaj')
def dodaj_gosta_get():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

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
    cur.execute('SELECT * FROM gost WHERE emso = %s', (emso, ))
    uniqueemso = cur.fetchone()

    if uniqueemso != None:
        nastaviSporocilo("Gost s tem emšom je že v sistemu")
        redirect(url('/gost/dodaj'))

    else:
        cur = baza.cursor()
        cur.execute("INSERT INTO gost (emso, ime, priimek, drzava, spol, starost) VALUES (%s, %s, %s, %s, %s, %s)", 
             (emso, ime, priimek, drzava, spol, starost))
        baza.commit()
        redirect(url('gost'))


@get('/gost/uredi/<emso>')
def uredi_gosta_get(emso):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    cur.execute('SELECT emso, ime, priimek, drzava, spol, starost FROM gost WHERE emso = %s', (emso,))
    gost = cur.fetchone()

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

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
    cur.execute("UPDATE gost SET ime = %s, priimek = %s, drzava = %s, spol = %s, starost = %s WHERE emso = %s", 
        (ime, priimek, drzava, spol, starost, emso))
    baza.commit()
    redirect(url('gost'))


@post('/gost/brisi/<emso>')
def brisi_gosta(emso):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    
    cur = baza.cursor()
    cur.execute('SELECT * FROM nastanitve WHERE gost_id = %s', (emso, ))
    aliimanastanitev = cur.fetchone()


    if aliimanastanitev == None:
        cur.execute("DELETE FROM gost WHERE emso = %s", (emso, ))
        baza.commit()
        redirect(url('gost'))
    else:
        nastaviSporocilo("Gost ima aktivno rezervacijo. Brisanje neuspešno!")
        redirect(url('/gost'))


@get('/gost/rezervacije/<id>')
def rezervacije_gosta(id):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return    
    napaka = nastaviSporocilo()
    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    cur = baza.cursor()
    cur.execute('SELECT emso, ime, priimek FROM gost WHERE emso = %s', (id,))
    ime_gosta = cur.fetchone()

    cur = baza.cursor()
    cur.execute('SELECT id, datum, soba_id FROM nastanitve WHERE gost_id = %s ORDER BY datum ASC', (id,))
    rezervacije = cur.fetchall()

    return template('rezervacije_gosta.html', rezervacije=rezervacije, napaka=napaka, ime_gosta=ime_gosta, tip_zaposlenega=tip_zaposlenega) 


@post('/gost/rezervacije/brisi/<id>/<brisanje>')
def brisi_rezervacijo(id, brisanje):
    cur = baza.cursor()
    cur.execute('SELECT datum FROM nastanitve WHERE id = %s', (brisanje, ))
    datum = cur.fetchone()[0]

    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    cur.execute("DELETE FROM nastanitve WHERE id = %s", (brisanje, ))
    cur.execute("DELETE FROM hrana WHERE gost_id = %s AND datum = %s", (id, datum))
    baza.commit()
    redirect(url('rezervacije_gosta',id=id))


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Z A P O S L E N I ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/zaposleni')
def zaposleni():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()

    cur.execute('SELECT emso, ime, priimek, spol, placa, oddelek FROM zaposleni WHERE (stanje IS NULL)')
    zaposleni = cur

    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    return template('zaposleni.html', zaposleni=zaposleni, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@post('/zaposleni/brisi/<emso>')
def brisi_zaposlenega(emso):

    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    if (tip_zaposlenega == 'admin'):
        uporabnik = preveriZaposlenega()
        if uporabnik is None: 
            return
        napaka = nastaviSporocilo()
        cur = baza.cursor()
        cur.execute("UPDATE zaposleni SET stanje = %s WHERE emso = %s", ("odpuscen",emso))
        baza.commit()
        redirect(url('/zaposleni'))
    else:
        nastaviSporocilo("Nimate pravic za brisanje zaposlenih. Obrnite se na administratorja")
        redirect(url('/zaposleni'))

@get('/zaposleni/dodaj')
def dodaj_zaposlenega_get():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

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

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    cur = baza.cursor()
    cur.execute('SELECT * FROM zaposleni WHERE emso = %s', (emso, ))
    uniqueemso = cur.fetchone()

    if tip_zaposlenega == 'admin':
        if uniqueemso != None:
            nastaviSporocilo("Zaposleni s tem emšom je že v sistemu")
            redirect(url('/zaposleni/dodaj'))
        else:
            cur.execute("INSERT INTO zaposleni (emso, ime, priimek, spol, placa, oddelek, username, geslo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                 (emso, ime, priimek, spol, placa, oddelek, emso, emso))
            baza.commit()
            redirect(url('/zaposleni'))
    else:
        nastaviSporocilo("Nimate pravic za dodajanje zaposlenih. Obrnite se na administratorja")
        redirect(url('/zaposleni'))

@get('/zaposleni/uredi/<emso>')
def uredi_zaposlenega_get(emso):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()

    cur = baza.cursor()
    cur.execute("SELECT emso, ime, priimek, spol, placa, oddelek FROM zaposleni WHERE emso = %s", (emso,))
    zaposleni = cur.fetchone()
    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

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

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    if tip_zaposlenega == 'admin':
        cur = baza.cursor()
        cur.execute("UPDATE zaposleni SET ime = %s, priimek = %s, spol = %s, placa = %s, oddelek = %s WHERE emso = %s", 
            (ime, priimek, spol, placa, oddelek, emso))
        baza.commit()
        redirect(url('/zaposleni'))
    else:
        nastaviSporocilo("Nimate pravic za urejanje zaposlenih. Obrnite se na administratorja")
        redirect(url('/zaposleni'))

#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ S O B E ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/sobe')
def sobe():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    cur.execute('SELECT stevilka, cena, postelje FROM sobe')
    sobe = cur

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    return template('sobe.html', sobe=sobe, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@get('/sobe/pregled/<stevilka>')
def pregled_rezervacij(stevilka):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    cur.execute("SELECT id, datum, gost_id, gost.ime, gost.priimek FROM nastanitve INNER JOIN gost ON gost_id = gost.emso WHERE soba_id = %s ORDER BY datum ASC", (stevilka,))
    zasedena = cur.fetchall()
    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    return template('pregled-zasedenosti.html', zasedena=zasedena, stevilka=stevilka, napaka=napaka, tip_zaposlenega=tip_zaposlenega) 


@get('/sobe/rezerviraj/<stevilka>')
def rezerviraj_sobo_get(stevilka):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    
    napaka = nastaviSporocilo()
    cur = baza.cursor()

    cur.execute("SELECT id, datum, gost_id, gost.ime, gost.priimek FROM nastanitve INNER JOIN gost ON gost_id = gost.emso WHERE soba_id = %s", (stevilka,))
    zasedena = cur.fetchall()

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    return template('rezerviraj-sobo.html', zasedena=zasedena, napaka=napaka, stevilka=stevilka, tip_zaposlenega=tip_zaposlenega)


@post('/sobe/rezerviraj/<stevilka>')
def rezerviraj_sobo_post(stevilka):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    gost_id = request.forms.gost_id

    cur = baza.cursor()

    cur.execute("SELECT * FROM gost WHERE emso = %s", (gost_id, ))
    alisplohjenas = cur.fetchone()

    if alisplohjenas == None:
        nastaviSporocilo("Vpiši veljaven emšo gosta ali pa ga dodaj v sistem")
        redirect(url('rezerviraj_sobo_get',stevilka=stevilka))

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
            redirect(url('rezerviraj_sobo_get', stevilka=stevilka))   
        if datumprihoda < datetime.today().strftime('%Y-%m-%d'):
            nastaviSporocilo("Prosimo, da ne rezervirate sobe v preteklosti.")
            redirect(url('rezerviraj_sobo_get', stevilka=stevilka))

        import datetime
        datumodhodaminusena = datetime.datetime.strptime(datumodhoda, "%Y-%m-%d")
        datumodhodaminusena = datumodhodaminusena - datetime.timedelta(days=1)
        
        seznam = daterange(datumprihoda, datumodhoda)

        cur = baza.cursor()
        cur.execute('SELECT id FROM nastanitve WHERE datum BETWEEN %s and %s AND soba_id = %s', (datumprihoda, datumodhodaminusena, soba_id, ))
        mozne_rezervacije = cur.fetchone()

        if mozne_rezervacije != None:
                nastaviSporocilo("Žal je soba v tem obdobju že rezervirana.")
                redirect(url('rezerviraj_sobo_get', stevilka=stevilka))
    
        cur = baza.cursor()
        for datum in seznam:
            cur.execute("INSERT INTO nastanitve (gost_id, datum, soba_id) VALUES (%s, %s, %s)", 
                (gost_id, datum, soba_id))
            if zajtrk:
                cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (%s, %s, %s, 0, NULL)", 
                    (gost_id, datum, 'zajtrk'))
            if kosilo:
                cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (%s, %s, %s, 0, NULL)", 
                    (gost_id, datum, 'kosilo'))
            if vecerja:
                cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (%s, %s, %s, 0, NULL)", 
                    (gost_id, datum, 'vecerja'))
        cur.execute("INSERT INTO ciscenje (pocisceno, cistilka_id, datum, obvezno_do, soba_id) VALUES (0, NULL, NULL, %s, %s)", (datumprihoda, soba_id))
        baza.commit()
        redirect(url('pregled_rezervacij', stevilka=stevilka))


@post('/sobe/brisi/<id>/<stevilka>')
def brisi_sobo(id, stevilka):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    
    cur = baza.cursor()
    cur.execute("DELETE FROM nastanitve WHERE id = %s", (id, ))
    baza.commit()
    redirect(url('pregled_rezervacij',stevilka=stevilka))


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ H R A N A ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/hrana')
def narocila():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()

    cur = baza.cursor()
    cur.execute("""
        SELECT DISTINCT hrana.id, hrana.gost_id, gost.ime, gost.priimek, nastanitve.soba_id, hrana.datum, tip_obroka FROM hrana 
        INNER JOIN gost ON hrana.gost_id = gost.emso 
        INNER JOIN nastanitve ON (hrana.gost_id = nastanitve.gost_id AND hrana.datum = nastanitve.datum)
        WHERE (pripravljena = 0)
        ORDER BY hrana.datum ASC
    """)
    hrana = cur

    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    return template('hrana.html', hrana=hrana, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@post('/hrana/postrezi/<id>')
def postrezi(id):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return

    cur = baza.cursor()
    username = request.get_cookie("username", secret=skrivnost)
    cur.execute('SELECT emso FROM zaposleni WHERE username = %s', (username, ))
    id_zaposlenega = cur.fetchone()[0]

    from datetime import datetime

    cur = baza.cursor()
    cur.execute('SELECT datum FROM hrana WHERE id = %s',(id, ))
    datum_hrane = cur.fetchone()[0]
    danes = datetime.today().strftime('%Y-%m-%d')

    # Tukaj ne dela več
    if str(danes) == str(datum_hrane):
        cur = baza.cursor()
        cur.execute("UPDATE hrana SET pripravljena = 1, pripravil_id = %s WHERE id = %s",(id_zaposlenega, id, ))
        baza.commit()
        redirect(url('/hrana'))
    else:
        nastaviSporocilo("Priprava hrane je možna samo na dan naročila")
        redirect(url('/hrana'))


@get('/hrana/dodaj')
def dodaj_hrano_get():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    return template('hrana-dodaj.html', napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@post('/hrana/dodaj')
def dodaj_hrano_post():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    emso = request.forms.emso
    datum = request.forms.datum
    obrok = request.forms.obrok
    cur = baza.cursor()
    cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (%s, %s, %s, 0, NULL)", 
        (emso, datum, obrok))
    baza.commit()
    redirect(url('/hrana'))


@get('/hrana/zgodovina')
def zgodovina_hrane():
    cur = baza.cursor()
    napaka = nastaviSporocilo()
    cur.execute("""
        SELECT DISTINCT hrana.id, hrana.gost_id, gost.ime, gost.priimek, nastanitve.soba_id, hrana.datum, tip_obroka, zaposleni.emso, zaposleni.ime, zaposleni.priimek FROM hrana 
        INNER JOIN gost ON hrana.gost_id = gost.emso 
        INNER JOIN nastanitve ON (hrana.gost_id = nastanitve.gost_id AND hrana.datum = nastanitve.datum)
        INNER JOIN zaposleni ON (hrana.pripravil_id = zaposleni.emso)
        WHERE (pripravljena = 1)
    """)
    hrana = cur
    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    return template('hrana-zgodovina.html', hrana=hrana, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@post('/hrana/izbrisi/<id>')
def izbrisi_obrok(id):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return

    cur = baza.cursor()
    cur.execute("DELETE FROM hrana WHERE id = %s", (id, ))
    baza.commit()
    redirect(url('/hrana'))


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ C I S C E N J E ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/ciscenje')
def ciscenje():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    cur.execute("""
        SELECT id, obvezno_do, soba_id FROM ciscenje 
        WHERE (pocisceno = 0)
        ORDER BY obvezno_do ASC;
    """)
    ciscenje = cur
    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    return template('ciscenje.html', ciscenje=ciscenje, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@get('/ciscenje/zgodovina')
def ciscenje_zgodovina():
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    cur.execute("""
        SELECT id, soba_id, datum, cistilka_id, zaposleni.ime, zaposleni.priimek FROM ciscenje
        INNER JOIN zaposleni ON (zaposleni.emso = cistilka_id)
        WHERE (pocisceno = 1)
        ORDER BY datum DESC;
    """)
    ciscenje = cur

    username = request.get_cookie("username", secret=skrivnost)  

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]

    return template('ciscenje-zgodovina.html', ciscenje=ciscenje, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


@post('/ciscenje/pocisti/<id>')
def pocisti(id):
    uporabnik = preveriZaposlenega()
    if uporabnik is None: 
        return
    from datetime import date

    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()
    cur.execute('SELECT emso FROM zaposleni WHERE username = %s', (username, ))
    id_cistilke = cur.fetchone()[0]

    cur = baza.cursor()
    cur.execute("UPDATE ciscenje SET pocisceno = 1, datum = %s, cistilka_id = %s WHERE id = %s", 
        (date.today().strftime("%Y-%m-%d"), id_cistilke, id))
    baza.commit()
    redirect(url('/ciscenje'))


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
        redirect(url('/registracija'))
        return
    if len(password) < 4:
        nastaviSporocilo('Geslo mora vsebovati vsaj štiri znake') 
        redirect(url('/registracija'))
        return
    if emso is None or username is None or password is None or password2 is None or ime is None or priimek is None or spol is None or drzava is None or starost is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect(url('/registracija'))
        return
    cur = baza.cursor()
    uporabnik = None   
    try:
        cur.execute('SELECT * FROM gost WHERE emso = %s', (emso, ))
        uporabnik = cur.fetchone()  
    except:
        uporabnik = None    
    if uporabnik is not None:
        nastaviSporocilo('Uporabnik s tem emšom že obstaja!') 
        redirect(url('/registracija'))
        return
    uporabnik = None   
    try:
        cur = baza.cursor()
        cur.execute('SELECT * FROM gost WHERE username = %s', (username, ))
        uporabnik = cur.fetchone()  
    except:
        uporabnik = None    
    if uporabnik is not None:
        nastaviSporocilo('Username že obstaja!') 
        redirect(url('/registracija'))
        return
    zgostitev = hashGesla(password)    
    cur.execute('INSERT INTO gost (emso, ime, priimek, drzava, spol, starost, username, geslo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',(emso, ime, priimek, drzava,spol, starost, username, zgostitev))
    baza.commit()
    response.set_cookie('username', username, secret=skrivnost)
    return redirect(url('/prijava'))

@post('/prijava')
def prijava_post():
    username = request.forms.username
    password = request.forms.password

    # Tega v bistvu sploh ne rabimo
    if username is None or password is None:
        nastaviSporocilo('Mankajoče uporabniško ime ali geslo!') 
        redirect(url('/prijava'))
    
    cur = baza.cursor()
    hgeslo = None
    geslo = None
    try:
        cur.execute("SELECT geslo FROM gost WHERE username=%s", (username, ))
        hgeslo = cur.fetchone()
        hgeslo = hgeslo[0]
    except:
        hgeslo = None

    cur = baza.cursor()
    try:
        cur.execute("SELECT geslo FROM zaposleni WHERE username=%s", (username, ))
        geslo = cur.fetchone()
        geslo = geslo[0]
    except:
        geslo = None    
    
    cur = baza.cursor()
    try:
        cur.execute("SELECT emso FROM zaposleni WHERE username=%s", (username, ))
        emgeslo = cur.fetchone()
        emgeslo = emgeslo[0]
    except:
        emgeslo = None    

    if hgeslo is None and geslo is None and emgeslo is None:
        nastaviSporocilo('Uporabniško ime ali geslo nista ustrezni!') 
        redirect(url('/prijava'))
        return
    if hashGesla(password) != hgeslo and password != emgeslo and hashGesla(password) != geslo:
        nastaviSporocilo('Napačno geslo!') 
        redirect(url('/prijava'))
        return
    response.set_cookie('username', username, secret=skrivnost)

    # Tukaj je za zaposlene
    if hgeslo is None:
        redirect(url('/uporabnik'))

    # Tukaj je za goste
    if geslo is None:
        redirect(url('/uporabnik_gost'))


@get('/odjava')
def odjava_get():
    response.delete_cookie('username')
    redirect(url('/prijava'))


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ DOSTOP GOSTOV ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/dostop_gosta')
def gost_gost():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    cur.execute("""
        SELECT emso, ime, priimek, drzava, spol, starost FROM gost
    """)
    gosti = cur
    return template('dostop_gosta.html', gosti=gosti, napaka=napaka)



#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   ~~~~~~~~~~~~~~~~~~~~~ DRUGI DEL KODE: DOSTOP GOSTOV ~~~~~~~~~~~~~~~~~~~~
#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SOBE ZA GOSTE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/sobe_gost')
def sobe_gost():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    cur.execute("""
        SELECT stevilka, cena, postelje FROM sobe
    """)
    sobe = cur
    return template('sobe_gost.html', sobe=sobe, napaka=napaka)


@get('/sobe_gost/pregled/<stevilka>')
def pregled_rezervacij_gost(stevilka):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    cur.execute("SELECT id, datum, gost_id, gost.ime, gost.priimek, gost.username FROM nastanitve INNER JOIN gost ON gost_id = gost.emso WHERE soba_id = %s ORDER BY datum ASC", (stevilka,))
    zasedena = cur.fetchall()
    return template('pregled-zasedenosti_gost.html', zasedena=zasedena, stevilka=stevilka, napaka=napaka) 


@get('/sobe_gost/moje_rezervacije')
def moje_rezervacije_gost():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return    

    napaka = nastaviSporocilo()
    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  

    cur.execute('SELECT emso FROM gost WHERE username = %s', (username, ))
    emso_gosta = cur.fetchone()[0]

    cur = baza.cursor()
    cur.execute("SELECT datum, soba_id FROM nastanitve WHERE gost_id = %s ORDER BY datum ASC", (emso_gosta,))
    rezervacije = cur.fetchall()
    return template('sobe_gost-mojerezervacije.html', rezervacije=rezervacije, napaka=napaka) 


@get('/sobe_gost/rezerviraj')
def rezerviraj_sobo_get_gost():
    uporabnik = preveriUporabnika()
    napaka = nastaviSporocilo()

    if uporabnik is None: 
        return
    return template('rezerviraj-sobo_gost.html', napaka=napaka)


@get('/sobe_gost/rezerviraj/<stevilka>')
def rezerviraj_sobo_stevilka_gost(stevilka):
    uporabnik = preveriUporabnika()
    napaka = nastaviSporocilo()

    if uporabnik is None: 
        return
    return template('rezerviraj-sobo_gost.html', napaka=napaka, stevilka=stevilka)


@post('/sobe_gost/rezerviraj/<stevilka>')
def rezerviraj_sobo_post_gost(stevilka):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    
    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  
    cur.execute('SELECT emso FROM gost WHERE username = %s', (username, ))
    emso_gosta = cur.fetchone()[0]
    cur = baza.cursor()

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
        redirect(url('rezerviraj_sobo_stevilka_gost',stevilka=soba_id))
    if datumprihoda < datetime.today().strftime('%Y-%m-%d'):
        nastaviSporocilo("Prosimo, da ne rezervirate sobe v preteklosti.")
        redirect(url('rezerviraj_sobo_stevilka_gost',stevilka=soba_id))

    import datetime
    datumodhodaminusena = datetime.datetime.strptime(datumodhoda, "%Y-%m-%d")
    datumodhodaminusena = datumodhodaminusena - datetime.timedelta(days=1)

    seznam = daterange(datumprihoda, datumodhoda)

    cur = baza.cursor()
    cur.execute('SELECT id FROM nastanitve WHERE datum BETWEEN %s and %s AND soba_id = %s', (datumprihoda, datumodhodaminusena, soba_id, ))
    mozne_rezervacije = cur.fetchone()
    
    if mozne_rezervacije != None:
            nastaviSporocilo("Žal je soba v tem obdobju že rezervirana.")
            redirect(url('rezerviraj_sobo_stevilka_gost',stevilka=soba_id))
 
    cur = baza.cursor()
    for datum in seznam:
        cur.execute("INSERT INTO nastanitve (gost_id, datum, soba_id) VALUES (%s, %s, %s)", 
            (gost_id, datum, soba_id))
        if zajtrk:
            cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (%s, %s, %s, 0, NULL)", 
                (gost_id, datum, 'zajtrk'))
        if kosilo:
            cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (%s, %s, %s, 0, NULL)", 
                (gost_id, datum, 'kosilo'))
        if vecerja:
            cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (%s, %s, %s, 0, NULL)", 
                (gost_id, datum, 'vecerja'))
    baza.commit()
    cur.execute("INSERT INTO ciscenje (pocisceno, cistilka_id, datum, obvezno_do, soba_id) VALUES (0, NULL, NULL, %s, %s)", (datumprihoda, soba_id))
    redirect(url('pregled_rezervacij_gost', stevilka=soba_id))


@post('/sobe_gost/brisi/<datum>/<soba>')
def brisi_sobo_gost(datum, soba):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  

    cur.execute('SELECT emso FROM gost WHERE username = %s', (username, ))
    emso_gosta = cur.fetchone()[0]

    cur = baza.cursor()
    cur.execute("DELETE FROM nastanitve WHERE datum = %s AND soba_id = %s AND gost_id = %s", (datum, soba, emso_gosta))

    cur = baza.cursor()
    cur.execute("DELETE FROM hrana WHERE datum = %s AND gost_id = %s", (datum, emso_gosta))
    cur.execute("DELETE FROM ciscenje WHERE soba_id = %s AND obvezno_do = %s", (soba, datum))
    baza.commit()
    redirect(url('/sobe_gost/moje_rezervacije'))


#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HRANA ZA GOSTE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/hrana_gost')
def narocila_gost():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()

    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT emso FROM gost WHERE username = %s', (username, ))
    emso_gosta = cur.fetchone()[0]

    cur = baza.cursor()
    cur.execute("""
        SELECT DISTINCT hrana.id, nastanitve.soba_id, hrana.datum, tip_obroka FROM hrana 
        INNER JOIN nastanitve ON (hrana.gost_id = nastanitve.gost_id AND hrana.datum = nastanitve.datum)        
        WHERE (hrana.gost_id = %s AND hrana.pripravljena != 1)
        ORDER BY hrana.datum ASC
    """, (emso_gosta, ))
    hrana = cur
    return template('hrana_gost.html', hrana=hrana, napaka=napaka)


@get('/hrana_gost/dodaj')
def dodaj_hrano_get_gost():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    
    napaka = nastaviSporocilo()
    return template('hrana-dodaj_gost.html', napaka=napaka)


@post('/hrana_gost/dodaj')
def dodaj_hrano_post_gost():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return

    username = request.get_cookie("username", secret=skrivnost)
    cur = baza.cursor()  

    cur.execute('SELECT emso FROM gost WHERE username = %s', (username, ))
    emso_gosta = cur.fetchone()[0]

    emso = emso_gosta
    datum = request.forms.datum
    obrok = request.forms.obrok

    cur = baza.cursor()
    cur.execute('SELECT * FROM nastanitve WHERE gost_id = %s AND datum = %s', (emso, datum, ))
    alisplohbivaprinas = cur.fetchone()

    if alisplohbivaprinas == None:
        nastaviSporocilo('V izbranem datumu ne bivate v hotelu')  
        redirect(url('/hrana_gost'))

    cur = baza.cursor()
    cur.execute("INSERT INTO hrana (gost_id, datum, tip_obroka, pripravljena, pripravil_id) VALUES (%s, %s, %s, 0, NULL)", 
         (emso, datum, obrok))
    baza.commit()
    redirect(url('/hrana_gost'))


@post('/hrana_gost/izbrisi/<id>')
def izbrisi_obrok_gost(id):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = None
    cur = baza.cursor()
    cur.execute("DELETE FROM hrana WHERE id = %s", (id, ))
    baza.commit()
    redirect(url('/hrana_gost'))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~PROFIL GOSTA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~1

@get('/uporabnik_gost')
def uporabnik_gost():
    uporabnik = preveriUporabnika()
    if gost is None: 
        return
    napaka = nastaviSporocilo()
    username = request.get_cookie("username", secret=skrivnost)
    cur.execute("SELECT * FROM gost WHERE username = %s", (username, ))
    uporabnik = cur
    return template('profil_uporabnika.html', uporabnik=uporabnik, napaka=napaka,)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~PROFIL ZAPOSLENEGA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/uporabnik')
def uporabnik_zaposleni():
    uporabnik = preveriZaposlenega()
    if gost is None: 
        return
    napaka = nastaviSporocilo()
    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()

    cur.execute("SELECT emso, ime, priimek, spol, placa, oddelek, username, geslo FROM zaposleni WHERE username = %s", (username, ))
    uporabnik = cur.fetchall()

    username = request.get_cookie("username", secret=skrivnost)

    cur = baza.cursor()  
    cur.execute('SELECT oddelek FROM zaposleni WHERE username = %s', (username, ))
    tip_zaposlenega = cur.fetchone()[0]
 
    return template('profil_zaposlenega.html', uporabnik=uporabnik, napaka=napaka, tip_zaposlenega=tip_zaposlenega)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~SPREMEMBA GESLA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@get('/spremeni_geslo')
def spremeni_geslo():
    napaka = nastaviSporocilo()

    username = request.get_cookie("username", secret=skrivnost)

    return template('spremeni_geslo.html', napaka=napaka)

@post('/spremeni_geslo')
def spremeni_geslo_post():
    username = request.get_cookie("username", secret=skrivnost)
    password = request.forms.password
    password2 = request.forms.password2
    if password != password2:
        nastaviSporocilo('Gesli se ne ujemata') 
        redirect(url('/spremeni_geslo'))
        return
    if len(password) < 4:
        nastaviSporocilo('Geslo mora vsebovati vsaj štiri znake') 
        redirect(url('/spremeni_geslo'))
        return 
    cur = baza.cursor()
    if username:    
        uporabnik1 = None
        uporabnik2 = None
        try: 
            cur = baza.cursor()
            cur.execute("SELECT * FROM zaposleni WHERE username = %s", (username, ))
            uporabnik1 = cur.fetchone()
        except:
            uporabnik1 = None
        try: 
            cur = baza.cursor()
            cur.execute("SELECT * FROM gost WHERE username = %s", (username, ))
            uporabnik2 = cur.fetchone()            
        except:
            uporabnik2 = None    
        if uporabnik1: 
            zgostitev1 = hashGesla(password)
            cur.execute("UPDATE zaposleni SET  geslo = %s WHERE username = %s", (zgostitev1 ,username))
            baza.commit()
            return redirect(url('/prijava'))
        if uporabnik2:
            zgostitev2 = hashGesla(password)
            cur.execute("UPDATE gost SET  geslo = %s WHERE username = %s", (zgostitev2 ,username))
            baza.commit()
            return redirect(url('/prijava'))
    nastaviSporocilo('Obvezna registracija') 
    redirect(url('/registracija'))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

baza = psycopg2.connect(database=auth.dbname, host=auth.host, user=auth.user, password=auth.password, port = DB_PORT)
cur = baza.cursor(cursor_factory=psycopg2.extras.DictCursor) 

run(host='localhost', port=SERVER_PORT, reloader=True)










