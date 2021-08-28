DROP TABLE IF EXISTS nastanitve;
DROP TABLE IF EXISTS hrana;
DROP TABLE IF EXISTS ciscenje;
DROP TABLE IF EXISTS zaposleni;
DROP TABLE IF EXISTS sobe;
DROP TABLE IF EXISTS gost;


CREATE TABLE gost (
    emso           TEXT    PRIMARY KEY,
    ime            TEXT    NOT NULL,
    priimek        TEXT    NOT NULL,
    drzava         TEXT    NOT NULL,
    spol           TEXT    NOT NULL,
    starost        INTEGER NOT NULL,
    username       TEXT    UNIQUE,
    geslo          TEXT    
);


CREATE TABLE sobe (
    stevilka    INTEGER     PRIMARY KEY,
    cena        INTEGER     NOT NULL,
    postelje    INTEGER     NOT NULL
);


CREATE TABLE zaposleni (
    emso        TEXT    PRIMARY KEY,
    ime         TEXT    NOT NULL,
    priimek     TEXT    NOT NULL,
    spol        TEXT    NOT NULL,    
    placa       INTEGER NOT NULL,
    oddelek     TEXT    NOT NULL,
    username       TEXT    UNIQUE,
    geslo          TEXT,
    stanje      TEXT    
);


CREATE TABLE nastanitve (
    id              SERIAL          UNIQUE                 PRIMARY KEY,            
    gost_id         TEXT            REFERENCES gost(emso)          NOT NULL,
    datum           DATE            NOT NULL,
    soba_id            INTEGER         REFERENCES sobe(stevilka)   NOT NULL
);


CREATE TABLE hrana (
    id          SERIAL          UNIQUE      PRIMARY KEY,
    gost_id     TEXT            REFERENCES gost(emso),
    datum       DATE            NOT NULL,
    tip_obroka  TEXT            NOT NULL,
    pripravljena    INTEGER         NOT NULL,
    pripravil_id    TEXT        REFERENCES zaposleni(emso)
);


CREATE TABLE ciscenje (
    id          SERIAL          UNIQUE          PRIMARY KEY,
    pocisceno   INTEGER             NOT NULL,
    cistilka_id TEXT            REFERENCES zaposleni(emso),
    datum       DATE,
    obvezno_do  DATE            NOT NULL,
    soba_id     INTEGER         REFERENCES sobe(stevilka)
);


GRANT ALL ON DATABASE sem2021_majg TO majg;
GRANT ALL ON SCHEMA public TO majg;
GRANT ALL ON ALL TABLES IN SCHEMA public TO majg;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO majg;

GRANT ALL ON DATABASE sem2021_majg TO matevzk;
GRANT ALL ON SCHEMA public TO matevzk;
GRANT ALL ON ALL TABLES IN SCHEMA public TO matevzk;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO matevzk;

GRANT ALL ON DATABASE sem2021_majg TO zanm;
GRANT ALL ON SCHEMA public TO zanm;
GRANT ALL ON ALL TABLES IN SCHEMA public TO zanm;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO zanm;


GRANT ALL ON DATABASE sem2021_majg TO javnost;
GRANT ALL ON SCHEMA public TO javnost;
GRANT ALL ON ALL TABLES IN SCHEMA public TO javnost;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO javnost;

GRANT USAGE ON SCHEMA public TO PUBLIC;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO javnost;
GRANT CONNECT ON DATABASE sem2021_majg TO javnost;
