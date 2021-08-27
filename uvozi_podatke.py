import psycopg2, psycopg2.extensions, psycopg2.extras 
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

import csv

from psycopg2 import sql


from auth_public import *

baza_datoteka = 'eksoticni_resort.db'

def uvoziSQL(cur, datoteka):
    with open(datoteka) as f:
        script = f.read()
        cur.execute(script)


def uvoziCSV(cur, tabela):
    with open('podatki/{0}.csv'.format(tabela)) as csvfile:
        podatki = csv.reader(csvfile)   
        vsiPodatki = [vrstica for vrstica in podatki]
        glava = vsiPodatki[0]
        vrstice = vsiPodatki[1:]
        cur.executemany("INSERT INTO {0} ({1}) VALUES ({2})".format(
            tabela, ",".join(glava), ",".join(['?']*len(glava))), vrstice)

with psycopg2.connect(database=dbname, host=host, user=user, password=password) as con:
    cur = con.cursor()
    uvoziSQL(cur, 'eksoticni_resort.sql')
    uvoziSQL(cur, 'podatki\gost.sql')
    uvoziSQL(cur, 'podatki\zaposleni.sql')
    uvoziSQL(cur, 'podatki\sobe.sql')
    uvoziSQL(cur, 'podatki\\nastanitve.sql')
    uvoziSQL(cur, 'podatki\hrana.sql')
    uvoziSQL(cur, 'podatki\ciscenje.sql')
    con.commit()



#with sqlite3.connect(baza_datoteka) as baza:
#    cur = baza.cursor()
#    uvoziSQL(cur, 'eksoticni_resort.sql')
#    uvoziSQL(cur, 'podatki\zaposleni.sql')
#    uvoziSQL(cur, 'podatki\sobe.sql')
#    uvoziSQL(cur, 'podatki\\nastanitve.sql')
#    uvoziSQL(cur, 'podatki\hrana.sql')
#    uvoziSQL(cur, 'podatki\ciscenje.sql')
#    uvoziSQL(cur, 'podatki\gost.sql')
#