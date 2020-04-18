# Primer webshop aplikacije: SPA, REST, Docker

## Potrebne stvari

* Python
* Django
* Docker

## Podešavanje za razvoj

Kreiranje virtuelnog okruženja:
```bash
python3 -m venv ~/path/to/new/venv
source ~/path/to/new/venv/bin/activate
```

Sve naredne operacije obavljaju se iz korenskog direktorijuma Django
projekta, dakle `webshop`.

Instaliranje potrebnih paketa
```bash
pip install -r requirements.txt
```

Migracija baze na poslednju verziju:
```bash
python manage.py migrate
```

Punjenje demo podataka:
```bash
python manage.py loaddata demodata.yaml
```

Pokretanje testova:
```bash
python manage.py test
```

Pokretanje razvojnog servera:
```bash
python manage.py runserver
```

Pokretanje Angular servera:
```bash
cd frontend
ng serve
```

Tokom razvoja frontend aplikacije je dostupan na adresi http://localhost:4200/. Zahtevi koji se upućuju
backendu će biti proksirani kroz Angular server.

## Kreiranje image-a za produkciju

Postaviti se u direktorijum gde stoji fajl `Dockerfile`.

Kreiranje Docker image-a:
```bash
docker build -t isa/webshop .
```

Pokretanje PostgreSQL baze:
```bash
docker run --name webshopdb -e POSTGRES_USER=webshop -e POSTGRES_PASSWORD=webshop -d postgres:12.2
```

Pokretanje aplikacije:
```bash
docker run --name webshop -e DJANGO_SETTINGS=prod -p 8000:8000 --link webshopdb -d isa/webshop
```


