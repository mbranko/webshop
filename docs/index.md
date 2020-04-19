# Primer webshop aplikacije

Ovaj dokument opisuje arhitekturu, konfiguraciju i detalje
funkcionisanja webshop aplikacije.

## Osnovni elementi arhitekture

Aplikacija se sastoji od zadnjeg dela (implementiranog u Pajtonu
pomoću (Django)[https://www.djangoproject.com/] radnog okvira) i
prednjeg dela ((TypeScript)[https://www.typescriptlang.org/] i
(Angular)[https://angular.io/] radni okvir). Relaciona baza podataka
se koristi za trajno skladištenje.

Frontend komunicira sa backendom putem REST API-ja. Za neke URL
putanje nije potrebna autentifikacija, dok za većinu jeste.
Autentifikacija se oslanja na JSON Web Token (JWT, RFC 7519,
https://jwt.io/) standard.

Neki delovi sistema, pre svega dokumentacija za API i podsistem za
administratorski pristup podacima u bazi su automatski generisani i
direktno ih opslužuje backend -- nije bilo potrebe za bilo kakvom
implementacijom na frontendu. Ovi delovi sistema koriste
autentifikaciju zasnovanu na HTTP sesijama koja je standardna za
Django.

Potrošačka korpa u koju korisnik smešta željene proizvode čuva se na
strani browsera, u localStorage objektu. Prilikom potvrđivanja
kupovine i plaćanja, sadržaj korpe se šalje na server i tamo obavlja
provera:

* da li su traženi proizvodi dostupni u traženoj količini i
* da li je u međuvremenu (tokom izvršavanja ove transakcije) neko 
  drugi zauzeo tražene proizvode - optimističko zaključavanje.

Komunikacija između frontenda i backenda se odvija putem HTTP 
protokola i poruka koje su u JSON formatu.

### URL putanje

Aplikacija definiše sledeće tipove URL putanja. Prvo slede putanje
koje se obrađuju na frontendu:

* `/`: početna stranica webshopa sa listom najpopularnijih proizvoda
* `/login`: stranica za prijavljivanje korisnika
* `/register`: stranica za registraciju korisnika
* `/category/:id`: prikaz podataka o kategoriji proizvoda
* `/product/:id`: prikaz podataka o proizvodu
* `/cart`: prikaz trenutnog stanja u korpi
* `/payment`: unos podataka za plaćanje

Sledeće putanje se obrađuju na backendu:

* `/api/register/`: registracija novog korisnika, iza koje sledi 
  slanje emaila za aktivaciju naloga
* `/api/token-auth/`: prijavljivanje na sistem i dobijanje JWT tokena
* `/activate/([a-zA-Z0-9]{16})/`: link za aktivaciju
* `/api/categories/`: REST API za upravljanje podacima o kategorijama
* `/api/products/`: REST API za upravljanje podacima o proizvodima
* `/api/suppliers/`: REST API za upravljanje podacima o dobavljačima
* `/api/most-popular-products/`: lista 6 najprodavanijih proizvoda
* `/admin/`: *Django admin* korisnički interfejs za uređivanje 
  podataka u bazi
* `/swagger/`: dokumentacija za API u (Swagger)[https://swagger.io/] 
  formatu
* `/redoc/`: dokumentacija za API u (ReDoc)[https://redoc.ly/] 
  formatu

### Konfiguracija za razvoj

Razvojna konfiguracija sistema se sastoji iz sledećeg:

* SQLite baze podataka, koja koristi fajl `/backend/db.sqlite3`
* backend servera implementiranog pomoću Django i 
  (DRF)[https://www.django-rest-framework.org/] (Django REST
  Framework) okvira
* frontend servera implementiranog pomoću (Angular 
  CLI)[https://cli.angular.io/]

Ukoliko fajl koji koristi baza podataka ne postoji, biće automatski
kreiran. Za pokretanje backenda potrebno je prvo kreirati Pajton
virtuelno okruženje i u njega instalirati sve potrebne biblioteke:

```bash
python3 -m venv /path/to/venv
source /path/to/venv/bin/activate
pip install --upgrade pip
cd backend
pip install -r requirements.txt
```

Pokretanje backend servera se potom, uz prethodnu aktivaciju
virtuelnog okruženja, obavlja na sledeći način:

```bash
source /path/to/venv/bin/activate
cd backend
python manage.py runserver
```

Pokrenuti backend server će zauzeti TCP port 8000. Backend funkcijama
može se pristupiti putem URL-a: http://localhost:8000/.

Pokretanje testova tokom razvoja se obavlja na sledeći način
(podrazumeva se podešeno virtuelno okruženje):

```bash
python manage.py test
```

Za pokretanje frontend servera potrebno je prethodno instalirati 
(Node.js)[https://nodejs.org/] i sve neophodne biblioteke:

```bash
cd frontend
npm install
```

Pokretanje servera obavlja se komandom:
```bash
ng serve
```

Pokretanje testova obavlja se komandama (prvo za unit a drugo za 
end-to-end testove uz pomoć Protractor biblioteke):
```bash
ng test
ng e2e
```

Pokrenuti frontend server će zauzimati TCP port 4200. Funkcijama
koje će opsluživati frontend server može se pristupiti putem URL-a
http://localhost:4200/.

Putanje kojima se frontend aplikacija obraća backendu će, u razvojnoj
konfiguraciji, biti prosleđivane od strane frontend servera backend
serveru. Na taj način frontend program ne mora voditi računa o 
različitim URL-ovima na kojima se nalaze frontend i backend. U 
razvojnoj konfiguraciji browser će sve zahteve slati na frontend 
server, dakle, na port 4200.

Prosleđivanje zahteva namenjenih backendu konfiguriše se u okviru
`frontend/angular.json` fajla. U property 
`projects.frontend.architect.serve.options` treba dodati još jedan
property `proxyConfig` tako da fragment izgleda ovako:

```json
"options": {
    "browserTarget": "frontend:build",
    "proxyConfig": "src/proxy.conf.json"
}
```

U fajlu `frontend/src/proxy.conf.json` navode se prefiksi putanja 
koje Angular CLI server treba da prosleđuje na backend server.

```json
{
  "/admin": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/static": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/api": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/swagger": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/redoc": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/activate": {
    "target": "http://localhost:8000",
    "secure": false
  }
}
```

Putanje koje počinju sa `/static` su putanje koje koriste Django
aplikacije za serviranje svojih statičkih sadržaja (slike, JavaScript
fajlovi, itd).

### Konfiguracija za produkciju

TODO: docker build uputstvo i objašnjenje šta će se naći u image-u (multi-stage build...)

## Backend

### Konfiguracija

Django sistem za konfigurisanje aplikacije polazi od fajla 
`backend/webshop/settings.py` u kome očekuje da nađe sve parametre
aplikacije. U ovom slučaju napravićemo nešto složeniji model za
konfigurisanje, koji će razdvojiti vrednosti parametara za razvoj i 
produkciju, uz definisanje parametara koji imaju iste vrednosti na
jednom mestu. U folderu `backend/webshop/app_settings` nalaze se
sledeći fajlovi:

* `base.py`: parametri zajednički za razvoj i produkciju
* `dev.py`: parametri specifični za razvoj
* `prod.py`: parametri specifični za produkciju
* `utils.py`: pomoćne funkcije za učitavanje parametara

Moduli `dev` i `prod` će zajedničke parametre prvo povući iz modula
`base` pa će potom definisati svoje specifične vrednosti.

Modul `settings` će proveriti vrednost promenljive okruženja 
`DJANGO_SETTINGS` i, zavisno od toga da li je njena vrednost `dev`
ili `prod`, učitati parametre iz odgovarajućeg modula. U slučaju da
promenljiva `DJANGO_SETTINGS` nije definisana, podrazumeva se `dev`
konfiguracija. Zahvaljujući tome, prilikom razvoja, pokretanje
razvojnog servera ne traži eksplicitno definisanu ovu promenljivu,
mada se i to može uraditi na sledeći način (primer je za bash shell):

```bash
export DJANGO_SETTINGS=dev
python manage.py runserver
```

TODO: SECRET_KEY, učitavanje iz fajla ili okruženja u produkciji

### Model podataka

Model podataka kojim rukuje backend definisan je u 
`backend/mainshop/models.py` fajlu. Klase definisane u tom fajlu
nasleđuju Djangovu `Model` klasu i definišu atribute klase (slično
kao statički atributi u Javi) koji opisuju pojedina polja u bazi
podataka.

Klasa `Category` opisuje kategoriju u kojoj se nalaze proizvodi. Za
nju je specifična unarna veza koja opisuje hijerarhijski odnos između
kategorija. Ova unarna veza je opisana atributom `parent`. Njegov
parametar `on_delete` označava da se prilikom brisanja "roditeljske"
kategorije vrednost ove veze menja na `None`, što znači da posmatrana
kategorija više nema roditelja (postaje tzv. "korenska" kategorija).

Klasa `Supplier` predstavlja dobavljača proizvoda i sadrži samo
proste atribute. 

Klasa `Product` predstavlja proizvod u bazi podataka. Pored 
uobičajenih atributa (naziv proizvoda, naziv proizvođača, cena, itd)
tu se nalaze i sledeći atributi:
* `available_quantity`: količina proizvoda koja je trenutno dostupna
* `version`: atribut potreban za optimističko zaključavanje

Pored toga, veza između `Product` i `Supplier` je takva da se 
brisanjem dobavljača automatski brišu i vezani proizvodi 
(`on_delete=CASCADE`) dok se prilikom brisanja kategorije, ukoliko u
njoj postoje vezani proizvodi, brisanje brani (`on_delete=PROTECT`).
Ove vrednosti parametra `on_delete` su izabrane pre svega radi
ilustracije mogućnosti i ne moraju uvek biti najbolji izbor za našu
aplikaciju.

Klasa `Customer` predstavlja registrovanog korisnika aplikacije. Osim
uobičajenih atributa (adresa, poštanski broj, mesto) tu je atribut
`activation_link` koji sadrži heširan kod namenjen za aktivaciju
naloga nakon registracije. Aktivacija se obavlja klikom na link u
dobijenom mailu. U pitanju je URL putanja `/activate/<hash>/` koja se
obrađuje direktno na backendu i nakon čega se korisnik prosleđuje
(HTTP odgovor 302) na početnu stranicu sajta.

Pored toga, rukovanje korisnicima u ovoj aplikaciji oslanja se na
Djangov ugrađeni model za korisnike, 
`django.contrib.auth.models.User`, koji obezbeđuje autentifikaciju i
vezu sa sistemom za autorizaciju zasnovanu na grupama korisnika i
pravima pristupa pojedinačnim elementima modela podataka. Ova veza
je predstavljena atributom `user` koji predstavlja 1-prema-1 vezu
sa ugrađenom klasom `User`.

Klasa `ShoppingCart` opisuje jednu realizovanu narudžbinu, dok klasa
`ShoppingCartItem` predstavlja stavku realizovane narudžbine.
Narudžbine koje nisu realizovane, tj. čija priprema je u toku, ne
čuvaju se u bazi podataka već u `localStorage`-u veb čitača.

### Admin UI

Django radni okvir nudi mogućnost da aplikacija dobije tzv. admin
korisnički interfejs za održavanje podataka u bazi, zapravo CRUDS 
forme za sve elemente modela podataka, uz minimalan trud. Prilikom
kreiranja novog Django projekta ova funkcionalnost je uključena i
vidi se kao `django.contrib.admin` aplikacija u listi instaliranih
aplikacija datoj u konfiguraciono parametru `INSTALLED_APPS` (fajl
`backend/webshop/app_settings/base.py`).

Dodatna podešavanja Admin interfejsa prave se u fajlu
`backend/mainshop/admin.py`. U ovom primeru prikaz podataka za
`User` klasu dopunjen je podacima iz `Customer` klase. Ostale klase
modela su samo registrovane, tj. prijavljene admin sistemu da budu
uključene u prikaz.

Admin intefejs je dostupan na URL-u `/admin/`, zahteva 
autentifikaciju, oslanja se na HTTP cookie za identifikaciju 
korisnika, a svoje statičke sadržaje isporučuje na URL-ovima koji
počinju sa `/static/`.

### Serijalizacija za REST API

Django REST Framework (DRF) je Django aplikacija koja omogućava
pravljenje REST API-ja na osnovu modela podataka na vrlo
efikasan i jezgrovit način. Serijalizacija modela u JSON se
kontroliše pomoću tzv. *serializer* klasa, koje su definisane u
`backend/mainshop/serializers.py`. Sve klase iz ovog modula praktično
definišu kako se pojedini objekti iz modela podataka serijalizuju u
JSON, odnosno koji atributi su obuhvaćeni serijalizacijom. U ovom
slučaju smo odlučili da serijalizacija obuhvata sve atribute. Pored
toga, zahtev za registracijom novog korisnika, koji podrazumeva JSON
objekat koji nema odgovarajući model, koristiće za JSON konverziju
klasu `NewUserSerializer` kod koje su svojstva JSON objekta 
eksplicitno popisana, kao i pravila za validaciju.

### REST API

Nakon definisane serijalizacije može se implementirati REST API na
jednostavan način. Za svaki element modela podataka definisane su
po dve klase u fajlu `/backend/mainshop/views_api.py`. Na primer, za
model `Product` definisane su klase:
* `ProductList` koja obrađuje zahteve poslate na URL za kolekciju,
  `/api/products` i
* `ProductDetail` koja obrađuje zahteve poslate na URL za elemente
  kolekcije, `/api/products/<id>`.

Klasa `ProductList` nasleđuje `ListAPIView` što znači da se 
implementira samo čitanje liste proizvoda, tj. obrada GET zahteva. U
slučaju da treba implementirati i kreiranje novih elemenata kolekcije
(POST zahtev) nasleđuje se klasa `ListCreateAPIView`, a u slučaju da
treba implementirati samo kreiranje, nasleđuje se klasa 
`CreateAPIView`. Atribut `queryset` definiše koji objekti ulaze u
sastav rezultata. Ovde su u pitanju svi objekti iz baze, dok je u
drugim slučajevima moguće i filtriranje. Prava pristupa su određena
atributom `permission_classes` i u ovom slučaju pravo pristupa imaju
svi korisnici, i prijavljeni i neprijavljeni (`AllowAny`). 
Sredstvo za serijalizaciju određeno je atributom `serializer_class`.
Dinamičko filtriranje podataka prilikom obrade zahteva implementirano
je pomoću klase čiji naziv se navodi u atributu `filter_backends`. U
pitanju je klasa koja je sastavni deo paketa `django-filter`. 
Polja po kojima je moguće filtriranje su navedeni u atributu
`filter_fields`. U ovom slučaju to znači da sledeći upiti mogu biti
automatski obrađeni:
* `/api/products/` -- vraća sve proizvode,
* `/api/products/?name=Thinkpad` -- vraća sve proizvode sa datim 
  imenom,
* `/api/products/?supplier__name=Žika` -- vraća sve proizvode koje 
  isporučuje dobavljač sa datim imenom (ovde se mora raditi spoj dve
  tabele prilikom izvršavanja SQL upita),
* `/api/products/?category_id=4` -- vraća sve proizvode koji se
  nalaze u kategoriji sa ID=4.

Klasa `ProductDetail` namenjena je obradi zahteva upućenih na URL
`/api/products/<id>`. Pri tome, zavisno od klase koju nasleđuje,
može služiti obradi sledećih HTTP zahteva:
* `RetrieveAPIView`: GET
* `DestroyAPIView`: DELETE
* `UpdateAPIView`: PUT
* `RetrieveUpdateAPIView`: GET, PUT
* `RetrieveDestroyAPIView`: GET, DELETE
* `RetrieveUpdateDestroyAPIView`: GET, PUT, DELETE

Atributi klase `ProductDetail` imaju isto značenje kao i kod klase
`ProductList`. Pošto se ovde radi o URL-u namenjenom pojedinačnim
proizvodima, filtriranje nema smisla.

Na sličan način definisane su i po dve klase za ostale elemente 
modela podataka: `SupplierList` i `SupplierDetail`, itd. Donekle je
izuzetak klasa `CategoryList` za koju je napisan poseban filter, u
klasi `CategoryFilter`. Njime je definisano značenje pojedinih
dodatnih parametara za filtriranje:
* `/api/categories/?noparent=True`: lista kategorija koje nemaju
  roditelja
* `/api/categories/?child=4`: lista kategorija kojima je dete
  kategorija sa ID=4
* `/api/categories/?product=5`: lista kategorija koje sadrže proizvod
  sa ID=5

Pored toga, definisane su i funkcije za obradu zahteva koji se ne 
mapiraju direktno na elemente modela. To su sledeće funkcije:
* `register`: obrada POST zahteva poslatih na `/api/register/` za
  registraciju novih korisnika
* `purchase`: obrada POST zahteva poslatih na `/api/purchase/` za
  smeštanje nove porudžbine
* `most_popular_products`: obrada GET zahteva poslatih na
  `/api/most-popular-products/` za dobijanje liste najprodavanijih
  proizvoda

Ove tri funkcije su dodatno označene `swagger_auto_schema` 
dekoratorom kako bi njihov opis ušao u automatski generisanu 
dokumentaciju. 

### Autentifikacija

Django u startu nudi `django.contrib.auth.models.User` klasu za
reprezentovanje korisnika sistema, uz implementirane metode za
autentifikaciju, izbor nove lozinke i slično. Lozinke se u bazi
podataka čuvaju heširane, pri čemu format heša zavisi od 
konfiguracionog parametra `PASSWORD_HASHERS` (definisan u
`backend/webshop/app_settings/base.py`). Kako mi želimo da se u našem
sistemu korisnik prijavljuje pomoću emaila i lozinke, umesto posebnog
korisničkog imena i lozinke, što je podrazumevano za klasu `User`,
napisan je poseban modul za autentifikaciju pomoću emaila i lozinke u
fajlu `backend/webshop/auth.py` i klasa `EmailBackend` je navedena u
konfiguracionom parametru  `AUTHENTICATION_BACKENDS`. Ograničenja na
sadržaj lozinke data su konfiguracionim parametrom
`AUTH_PASSWORD_VALIDATORS`.

Pristup Admin, Swagger i ReDoc interfejsu podrazumeva autentifikaciju
u skladu sa prethodno navedenim parametrima i identifikovanje 
korisnika pomoću HTTP cookie-ja. 

Pristup URL-ovima koji se koriste za REST API definisan je
konfiguracionim parametrom `REST_FRAMEWORK`:
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}
```

U našem slučaju, svaki REST API poziv podrazumevano zahteva da
korisnik bude autentifovan (`DEFAULT_PERMISSION_CLASSES`), da se
autentifikacija obavlja pomoću JWT tokena ili HTTP sesije 
(`DEFAULT_AUTHENTICATION_CLASSES`), i da se na sve REST API pozive
(gde to ima smisla) primenjuje filtriranje koje implementira paket
`django-filters` (`DEFAULT_FILTER_BACKENDS`).

Ova podrazumevana podešavanja dovoljno je izmeniti samo u situacijama
gde se od njih odstupa. Na primer, obrada POST zahteva na 
`/api/register/` mora biti dostupna i neautentifikovanim korisnicima
pa je funkcija za obradu ovih zahteva `register` dodatno označena 
dekoratorom: `@permission_classes([permissions.AllowAny])`

Pored toga, želimo da ograničimo broj poslatih zahteva na ovaj URL za
jednog korisnika, na 10 zahteva dnevno (u produkciji), odnosno na 100
zahteva dnevno (u razvoju). U fajlu `views_api.py` nalazi se i klasa
`DailyThrottle` koja definiše ovaj limit. Ona se oslanja na
konfiguracioni parametar `API_THROTTLE_RATE` koji je posebno 
definisan za razvoj (u fajlu `dev.py`) i produkciju (u fajlu 
`prod.py`). Zato je funkcija `register` još dodatno označena i 
sledećim dekoratorom: `@throttle_classes([DailyThrottle])`

### Dokumentacija

Dokumentacija za API koji je implementiran u okviru backenda dobija
se automatski kao sastavni deo implementacije REST API-ja pomoću DRF
i dodatnog paketa `drf-yasg`. Funkcije koje su pisane dodatno 
anotirane su `@swagger_auto_schema` dekoratorom radi dokumentovanja.

Dokumentacija je dostupna na `/swagger/` odnosno `/redoc/` URL-ovima
uz prethodnu autentifikaciju pomoću HTTP cookie-ja.

### Transakcije

TODO: Django default je auto commit mode, to se isključuje u konfig
parametru. Onda se usvoji da je jedna transakcija = jedna obrada 
zahteva.

TODO: Snimanje nove porudžbine podrazumeva smanjenje broja dostupnih
proizvoda, što može dovesti do kolizije sa drugim korisnicima u
konkurentnom pristupu istim proizvodima. Opisati optimističko
zaključavanje sprovedeno u ovom slučaju. Obratiti pažnju na to da je
optimističko prvo čitanje sprovedeno preko REST API-ja, a druga faza
je u momentu poziva register.

### Testiranje

TODO: opis implementacije testova

## Frontend

TODO: Opis arhitekture frontenda: servisi, komponente, rutiranje.

## Kontejneri

TODO: Layout fajlova u image-u.

## Oblak

TODO