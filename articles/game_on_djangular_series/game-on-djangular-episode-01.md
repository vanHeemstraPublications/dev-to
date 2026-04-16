---
title: "Game on Djangular 🎮 Ep.1"
part: 1
published: false
description: "Episode 1: GameLib is your digital game vault — track your backlog, log completions, write reviews. Powered by Django REST Framework and Angular, secured by JWT, connected by PostgreSQL. The Djangular stack, explained through the games you play."
tags: [django, angular, python, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/djangular_gamelib_series/djangular-gamelib-episode-01.png"
series: "Game on Djangular Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 1: Welcome to the Vault

> *“Every gamer has a backlog. The good ones have a system.”*

-----

## The Backlog Problem 🎯

Every gamer knows the feeling. Forty-three games in your library. You can only name eight of them from memory. Three are half-finished from two years ago. You started one last week but cannot remember whether the save file is on the laptop or the desktop. Someone on Reddit just posted that a game you bought on sale is “not worth it past hour 12” and you are on hour 11.

You need a Vault.

**GameLib** is that vault: a full-stack web application where gamers manage their personal libraries, track progress, discover new titles, and share reviews. Built for a Web Development course at KBTU, it is a working example of the **Djangular** stack — Django REST Framework on the backend, Angular on the frontend, PostgreSQL as the game database, and JWT tokens as the keys to your personal collection.

This series builds GameLib from the ground up and extends it into enterprise territory: XML file exchange with external Linux servers, TLS and mutual TLS certificate management, SailPoint IAM for identity verification, and a full PKI infrastructure managed by `django-ca`.

-----

## 🗂️ SIPOC — The Vault

|**Suppliers**                       |**Inputs**                                                  |**Process**                                      |**Outputs**                                               |**Customers**                                                           |
|------------------------------------|------------------------------------------------------------|-------------------------------------------------|----------------------------------------------------------|------------------------------------------------------------------------|
|Gamers (registered users)           |Game titles, play status, ratings, reviews                  |Angular frontend → DRF API → PostgreSQL          |A personal vault: tracked games, statuses, scores, reviews|The gamer — with a searchable, filterable record of their entire library|
|The global game catalogue           |Game metadata: title, genre, description, cover image       |Django admin / seed scripts → Game model         |A browsable catalogue of all games the system knows about |All users — browsing before adding to their vault                       |
|External Linux server (Episodes 5–8)|XML files containing game catalogue updates or vault exports|Django backend ↔ Linux server via HTTP/HTTPS/mTLS|Synchronised data; audit trail; identity-verified exchange|Enterprise operators, partner systems, compliance teams                 |

-----

## The Gamer Metaphor: Your Stack as Your Library 🗂️

The metaphor is exact, not decorative.

|Game library world                          |Djangular stack                           |
|--------------------------------------------|------------------------------------------|
|Your game Vault (personal collection)       |PostgreSQL + Django `UserGame` model      |
|The global catalogue you browse             |DRF read-only `Game` and `Genre` endpoints|
|Adding a game to your Vault                 |Authenticated POST to `UserGame` API      |
|Your status badge (Playing/Finished/Planned)|`status` field — string enum on `UserGame`|
|Your review and score out of ten            |`Review` model — one per user per game    |
|Genre filter on the shelf                   |`django-filter` + DRF `FilterBackend`     |
|Your login / session token                  |JWT via `djangorestframework-simplejwt`   |
|Angular loading your shelf on login         |`HttpClient` → DRF API → component binding|
|Exporting saves to a remote server          |Django `requests.post()` with XML payload |
|Encrypting the connection to the server     |TLS — self-signed cert, `verify=ca.crt`   |
|Both sides proving who they are             |mTLS — mutual certificate handshake       |
|The key factory that issues all certs       |PKI — Root CA + Intermediate CA           |
|The guild’s member identity check           |SailPoint IAM — verifying server requester|
|A banned player’s membership card           |Revoked certificate — CRL or OCSP         |

-----

## The Project Structure 🗂️

Based on the GameLib repository at [github.com/software-journey/djangular](https://github.com/software-journey/djangular):

```
djangular/
├── backend/                    ← Django project
│   ├── manage.py
│   ├── gamelib/                ← Django settings/urls/wsgi
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── games/                  ← Django app: catalogue
│   │   ├── models.py           ← Game, Genre
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── vault/                  ← Django app: personal library
│   │   ├── models.py           ← UserGame, Review
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── users/                  ← Django app: auth
│   │   ├── models.py           ← Custom User
│   │   ├── serializers.py
│   │   └── views.py
│   ├── xml_bridge/             ← Django app: XML exchange (Ep.5–7)
│   │   ├── client.py           ← HTTP/HTTPS/mTLS requests
│   │   ├── serializers.py      ← lxml XML serialisation
│   │   └── views.py
│   └── requirements.txt
│
└── frontend/gamelib/           ← Angular project
    ├── src/
    │   ├── app/
    │   │   ├── core/           ← AuthService, JwtInterceptor, Guards
    │   │   ├── features/
    │   │   │   ├── catalogue/  ← Browse games, genre filter
    │   │   │   ├── vault/      ← Your library, status, reviews
    │   │   │   └── auth/       ← Login, register
    │   │   └── shared/         ← Components, pipes, models
    │   └── environments/
    └── angular.json
```

-----

## The Series Map: Nine Episodes 🗺️

|#|Episode                          |Gamer concept                   |Technical concept                               |
|-|---------------------------------|--------------------------------|------------------------------------------------|
|1|*This one* — Welcome to the Vault|The backlog problem             |Architecture overview                           |
|2|Building the Game Catalogue      |Designing the Vault             |Django models, DRF serializers, viewsets        |
|3|Your Login Token                 |The guild membership card       |JWT auth, simplejwt, Angular interceptor        |
|4|Loading Your Shelf               |The front of the Vault          |Angular components, services, routing           |
|5|Save Data Over the Wire          |Syncing to a remote server      |XML POST/GET to Linux server, HTTP toggle       |
|6|Encrypting the Channel           |Locking the save file           |TLS, self-signed certs, `requests` verify       |
|7|Both Sides of the Lock           |Proving who you are             |mTLS, client cert generation, full handshake    |
|8|The Guild Registry               |The guildmaster’s identity check|SailPoint IAM, SCIM 2.0, access verification    |
|9|The Key Factory                  |Where all locks are made        |PKI management, `django-ca`, CRL, OCSP, rotation|

-----

## Technology Stack Cheat Sheet 📋

**Backend:**

- Python 3.12+
- Django 5.x + Django REST Framework 3.15+
- `djangorestframework-simplejwt` — JWT auth
- `django-filter` — queryset filtering
- `django-cors-headers` — CORS for Angular dev server
- `psycopg2-binary` — PostgreSQL adapter
- `requests` — HTTP client for XML exchange
- `lxml` — XML serialisation / deserialisation
- `cryptography` / OpenSSL — TLS / mTLS cert handling
- `django-ca` — PKI certificate authority management

**Frontend:**

- Angular 17+ with standalone components
- TypeScript 5+
- Angular `HttpClient` + `HttpInterceptor`
- Angular Router with route guards
- RxJS for reactive state
- Angular Material (optional) or TailwindCSS

**Database:** PostgreSQL 16+

**External Linux server:** Nginx (TLS termination) + custom XML endpoint

**IAM:** SailPoint IdentityIQ or IdentityNow (SCIM 2.0 API)

-----

## Quick-Start: Running GameLib Locally 🚀

```bash
# Clone the repo
git clone https://github.com/Elsa-Yanke/web-dev-project-2026.git
cd web-dev-project-2026

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create PostgreSQL database
createdb gamelib_db               # or use pgAdmin

# Configure environment
cp .env.example .env              # fill in DB credentials, SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend setup (new terminal)
cd ../frontend/gamelib
npm install
ng serve                          # http://localhost:4200
```

In **Episode 2**, we open the database and build the models: Game, Genre, UserGame, Review. The Vault takes shape.

-----

**🔗 Resources**

- **GameLib repository**: [github.com/software-journey/djangular](https://github.com/software-journey/djangular)
- **Django REST Framework**: [django-rest-framework.org](https://www.django-rest-framework.org)
- **Angular**: [angular.dev](https://angular.dev)
- **djangorestframework-simplejwt**: [django-rest-framework-simplejwt.readthedocs.io](https://django-rest-framework-simplejwt.readthedocs.io)

-----

*🎮 Game on Djangular Series is a series about building GameLib — a full-stack game library tracker — with Django REST Framework and Angular, extended with XML exchange, TLS/mTLS, SailPoint IAM, and PKI management.*
