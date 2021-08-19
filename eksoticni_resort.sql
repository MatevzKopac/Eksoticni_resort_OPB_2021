DROP TABLE IF EXISTS gost;
DROP TABLE IF EXISTS soba;
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


CREATE TABLE soba (
    stevilka    INTEGER     PRIMARY KEY,
    cena        INTEGER         NOT NULL,
    postelje    INTEGER     NOT NULL
);


CREATE TABLE zaposleni (
    emso        CHAR    PRIMARY KEY,
    ime         CHAR    NOT NULL,
    priimek     CHAR    NOT NULL,    
    placa       INTEGER NOT NULL,
    oddelek     CHAR    NOT NULL
);


CREATE TABLE nastanitve (
    id              AUTO_INCREMENT   PRIMARY KEY,            
    gost            CHAR            REFERENCES gost(emso),
    datum_prihoda   DATE            NOT NULL,
    datum_odhoda    DATE            NOT NULL,
    soba            INTEGER         REFERENCES soba(stevilka)     NOT NULL
);


CREATE TABLE hrana (
    id      AUTO_INCREMENT   PRIMARY KEY,
    gost    CHAR            REFERENCES gost(emso),
    datum   DATE            NOT NULL,
    tip_obroka  CHAR        NOT NULL,
    pripravil   CHAR        REFERENCES zaposleni(emso)
);


CREATE TABLE ciscenje (
    id          AUTO_INCREMENT   PRIMARY KEY,
    cistilka    CHAR            REFERENCES zaposleni(emso),
    datum       DATE            NOT NULL,
    soba        INTEGER         REFERENCES soba(stevilka)
);

