DROP TABLE IF EXISTS gost;
DROP TABLE IF EXISTS sobe;
DROP TABLE IF EXISTS zaposleni;
DROP TABLE IF EXISTS nastanitve;
DROP TABLE IF EXISTS hrana;
DROP TABLE IF EXISTS ciscenje;


CREATE TABLE gost (
    emso           CHAR    PRIMARY KEY,
    ime            CHAR    NOT NULL,
    priimek        CHAR    NOT NULL,
    drzava         CHAR    NOT NULL,
    spol           CHAR    NOT NULL,
    starost        INTEGER NOT NULL
);


CREATE TABLE sobe (
    stevilka    INTEGER     PRIMARY KEY,
    cena        INTEGER     NOT NULL,
    postelje    INTEGER     NOT NULL
);


CREATE TABLE zaposleni (
    emso        CHAR    PRIMARY KEY,
    ime         CHAR    NOT NULL,
    priimek     CHAR    NOT NULL,
    spol        CHAR    NOT NULL,    
    placa       INTEGER NOT NULL,
    oddelek     CHAR    NOT NULL
);


CREATE TABLE nastanitve (
    id              INTEGER         UNIQUE                 PRIMARY KEY,            
    gost_id         CHAR            REFERENCES gost(emso)          NOT NULL,
    datum           DATE            NOT NULL,
    soba_id            INTEGER         REFERENCES sobe(stevilka)   NOT NULL
);


CREATE TABLE hrana (
    id          INTEGER         UNIQUE      PRIMARY KEY,
    gost_id     CHAR            REFERENCES gost(emso),
    datum       DATE            NOT NULL,
    tip_obroka  CHAR            NOT NULL,
    pripravljena    BIT         NOT NULL,
    pripravil_id    CHAR        REFERENCES zaposleni(emso)
);


CREATE TABLE ciscenje (
    id          INTEGER         UNIQUE          PRIMARY KEY,
    pocisceno   BIT             NOT NULL,
    cistilka_id CHAR            REFERENCES zaposleni(emso),
    datum       DATE,
    obvezno_do  DATE            NOT NULL,
    soba_id     INTEGER         REFERENCES sobe(stevilka)
);

