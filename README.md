# Eksotični resort

V projektu smo izdelali database za eksotični resort, ki ga lahko uporabljajo tako zaposleni kot tudi gostje. Ideja je najprej 
bila, da bomo urejali finančni vidik eksotičnega resorta, a smo se potem malo preusmerili. Spletna stran sedaj služi kot orodje
za nemoteno upravljanje resorta.


## Uporaba strani za goste

Najprej se mora v stran vsak nov gost registrirati, pri čemer mora paziti, da vnese svoje prave podatke, saj jih kasneje ne 
bo mogel sam več spreminjati (zaradi varnostnih razlogov). Ko se enkrat registrira, ga stran doda v database tabelo gost. 
Gost se sedaj prijavi z izbranim uporabniških imenom in geslom. Stran ga preusmeri na stran `Moji podatki`. Tukaj lahko uporabnik spreminja tudi 
svoje geslo.

Gostu sta na voljo še zavihka `Rezervacije` in `Kuhinja`.

V zavihku `Rezervacije` lahko gost dostopa do podatkov zasedenosti vsake 
sobe (ki zaradi osebnih podatkov razkriva samo uporabniško ime tistega, ki 
ima rezervacijo). Poleg tega lahko vsako sobo tudi rezervira, če ta v željenem obdobju še ni zasedena. Ko enkrat opravi rezervacijo sobe, jo lahko 
tudi prekliče, s klikom na gumb `Moje rezervacije`.

Ko ima enkrat rezervirano, lahko za obdobje, ko biva v hotelu naročuje tudi hrano. Če gost prekliče rezervacijo za nek datum, se izbrišejo tudi vsa naročila hrane za dani datum.

## Uporaba strani za zaposlene

Zaposleni se ne morejo sami registrirati, temveč jih mora v sistem vnesti administrator (uporabniško ime: admin, geslo: admin). Ko se zaposleni prijavijo, jih stran preusmeri na njihove podatke, kjer si po želji 
spremenijo geslo (njihovo uporabniško ime je kar enako njihovemu emšu, 
isto zaradi varnosti, default geslo pa tudi).

Potem se vsakemu zaposlenemu navbar prilagodi njihovi vlogi na strani. Na primer, če je zaposleni v sistem vnešen kot čistilka, potem ima v navbaru 
samo zavihek `Čiščenje`. Vsak zaposleni sicer lahko dostopa do celotne strani
preko URL-ja. Navbar skrbi samo, da pri zaposlenemu ne pride do zmede.

## Vloge zaposlenih:
- **Čistilka**: Skrbi za čiščenje sob, na njeni strani ima prioritetno listo sob, ki jih je potrebno počistiti (ob rezervaciji se avtomatsko v seznam čiščenj doda soba, ki jo je potrebno do prihoda gosta počistiti). Ko sobo počisti, to tudi označi v sistemu in vrže čiščenje iz prioritetne liste v `Zgodovino čiščenj`. Za vsako čiščenje se tudi označi, katera čistilka je počistila, če pride do pritožb.

- **Receptor**: Receptor upravlja z rezervacijami, jih briše ali dodaja. Poleg tega ima tudi možnost dodajanja gostov v sistem ali brisanja (za tiste goste, ki niso računalniško vešči). 

- **Kuhar**: Kuhar upravlja s podobno prioritetno listo kot čistilka. Ko gost odda naročilo, se to pojavi na tej listi. Kuhar lahko naročilo prekliče.
Ko kuhar naročilo potreže, to vpiše v sistem. Naročilo je potem avtomatsko vrženo v `Zgodovino` in hkrati se tudi označi, kateri zaposleni ga je pripravil (pritožbe). Kuhar lahko naročilo postreže samo na datum naročila.

- **Administrator**: Ima poln dostop do vseh zavihkov in lahko tudi ureja, dodaja in briše zaposlene. Pri urejanju zaposlenih se dodatno preveri, da 
morda ne spreminja kateri zaposleni.

## ER diagram
Er diagram je dostopen [tukaj](https://github.com/MatevzKopac/Eksoticni_resort_OPB_2021/blob/main/ER-diagram.pdf).