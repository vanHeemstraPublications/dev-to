---
title: "Game on Djangular 🎮 Ep.5"
part: 5
published: false
description: "Episode 5: The Django backend exchanges XML files with an external Linux server — catalogue updates, vault exports, audit feeds. Plain HTTP by default, HTTPS on demand. The xml_bridge app: lxml serialisation, requests HTTP client, configurable transport, and Django management commands to trigger syncs."
tags: [django, python, xml, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/game_on_djangular_series/game-on-djangular-episode-05.png"
series: "Game on Djangular Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 5: Save Data Over the Wire

> *“Your save file is in the cloud. The cloud is a Linux server. The protocol is configurable.”*

-----

## Why XML? Why a Linux Server? 📡

GameLib is a web application, but it does not live in isolation. In real deployments, a game metadata server might supply catalogue updates. A compliance system might request vault exports for audit. A legacy partner integration might only speak XML over HTTP. The requirement is explicit: the Django backend must POST and GET XML files to and from an external Linux server, with plain HTTP as the default protocol and HTTPS as an optional upgrade.

This episode builds the `xml_bridge` Django application that handles this exchange. It does not rely on REST conventions — it sends and receives raw XML documents via HTTP POST and GET, authenticated via headers, with transport configurable at runtime from Django settings.

-----

## 🗂️ SIPOC — Save Data Over the Wire

|**Suppliers**          |**Inputs**                                      |**Process**                                             |**Outputs**                                      |**Customers**                                             |
|-----------------------|------------------------------------------------|--------------------------------------------------------|-------------------------------------------------|----------------------------------------------------------|
|GameLib database       |QuerySet of `Game` objects or `UserGame` entries|`lxml` serialises to XML document                       |A well-formed XML file in memory                 |`requests.post()` — sends it to the Linux server          |
|Linux server (external)|An HTTP/HTTPS endpoint accepting XML POST       |Receives XML, parses it, processes business logic       |HTTP 200 with optional XML response body         |Django `xml_bridge` client — parses the response          |
|Linux server (external)|A GET endpoint returning XML feed               |`requests.get()` — fetches the XML                      |XML document in memory                           |Django parser → model updates (catalogue sync)            |
|Django settings        |`XML_BRIDGE_USE_HTTPS`, `XML_BRIDGE_BASE_URL`   |`BridgeClient` reads config to build the URL and session|A `requests.Session` configured for HTTP or HTTPS|Every bridge call — transport is transparent to the caller|

-----

## The `xml_bridge` App Structure 📁

```
backend/xml_bridge/
├── __init__.py
├── apps.py
├── client.py          ← HTTP/HTTPS transport layer
├── serializers.py     ← Django → XML / XML → Django
├── views.py           ← DRF endpoints to trigger bridge operations
├── management/
│   └── commands/
│       ├── push_catalogue.py   ← management command: POST catalogue
│       └── pull_updates.py     ← management command: GET updates
└── tests.py
```

-----

## XML Serialisation with `lxml` 🗒️

```bash
pip install lxml
```

```python
# xml_bridge/serializers.py
from lxml import etree
from games.models import Game
from vault.models import UserGame


def games_to_xml(queryset) -> bytes:
    """Serialise a Game queryset to an XML document."""
    root = etree.Element("GameCatalogue", version="1.0")
    root.set("xmlns", "urn:gamelib:catalogue:v1")

    for game in queryset.prefetch_related("genres"):
        game_el = etree.SubElement(root, "Game")
        game_el.set("id", str(game.id))

        etree.SubElement(game_el, "Title").text = game.title
        etree.SubElement(game_el, "Developer").text = game.developer or ""
        etree.SubElement(game_el, "ReleaseYear").text = (
            str(game.release_year) if game.release_year else ""
        )
        etree.SubElement(game_el, "Description").text = game.description or ""

        genres_el = etree.SubElement(game_el, "Genres")
        for genre in game.genres.all():
            g = etree.SubElement(genres_el, "Genre")
            g.set("slug", genre.slug)
            g.text = genre.name

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def vault_to_xml(usergames) -> bytes:
    """Serialise a UserGame queryset to an XML export document."""
    root = etree.Element("VaultExport")
    root.set("xmlns", "urn:gamelib:vault:v1")

    for ug in usergames.select_related("game", "user"):
        entry = etree.SubElement(root, "Entry")
        entry.set("user",   ug.user.username)
        entry.set("gameId", str(ug.game.id))
        entry.set("status", ug.status)
        etree.SubElement(entry, "Title").text       = ug.game.title
        etree.SubElement(entry, "HoursPlayed").text = str(ug.hours_played)
        etree.SubElement(entry, "UpdatedAt").text   = ug.updated_at.isoformat()

    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")


def xml_to_games(xml_bytes: bytes) -> list[dict]:
    """
    Parse an inbound XML catalogue update from the Linux server.
    Returns a list of dicts suitable for upsert into the Game model.
    """
    root = etree.fromstring(xml_bytes)
    # Strip namespace for simplicity
    ns = {"ns": "urn:gamelib:catalogue:v1"}

    result = []
    for game_el in root.findall("ns:Game", ns):
        result.append({
            "external_id": game_el.get("id"),
            "title":       game_el.findtext("ns:Title",       namespaces=ns) or "",
            "developer":   game_el.findtext("ns:Developer",   namespaces=ns) or "",
            "description": game_el.findtext("ns:Description", namespaces=ns) or "",
        })
    return result
```

-----

## The Bridge Client: HTTP and HTTPS Transport 🌐

The `BridgeClient` reads Django settings to decide whether to use plain HTTP or HTTPS. The caller never touches the protocol — it just calls `.post_xml()` or `.get_xml()`.

```python
# xml_bridge/client.py
import logging
from typing import Optional
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class BridgeClient:
    """
    HTTP/HTTPS client for XML exchange with the external Linux server.

    Settings (in settings.py or environment):
        XML_BRIDGE_BASE_URL    — base URL of the Linux server endpoint
                                 e.g. "http://linux-srv.internal:8080"
                                 or   "https://linux-srv.internal:8443"
        XML_BRIDGE_USE_HTTPS   — bool; True enables HTTPS mode
        XML_BRIDGE_CA_CERT     — path to CA cert bundle for HTTPS verification
                                 (used in Episode 6+)
        XML_BRIDGE_CLIENT_CERT — (cert, key) tuple for mTLS (Episode 7)
        XML_BRIDGE_API_KEY     — shared secret sent as a request header
    """

    def __init__(self):
        self.base_url   = settings.XML_BRIDGE_BASE_URL
        self.use_https  = getattr(settings, "XML_BRIDGE_USE_HTTPS", False)
        self.ca_cert    = getattr(settings, "XML_BRIDGE_CA_CERT", None)
        self.client_cert = getattr(settings, "XML_BRIDGE_CLIENT_CERT", None)  # (crt, key)
        self.api_key    = getattr(settings, "XML_BRIDGE_API_KEY", "")
        self.timeout    = getattr(settings, "XML_BRIDGE_TIMEOUT_SECONDS", 30)
        self._session   = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()

        # Auth header
        if self.api_key:
            session.headers.update({"X-GameLib-API-Key": self.api_key})

        if self.use_https:
            # Episode 6: server certificate verification
            if self.ca_cert:
                session.verify = self.ca_cert          # trust our custom CA
            else:
                session.verify = True                  # use system trust store

            # Episode 7: mTLS — present our own client certificate
            if self.client_cert:
                session.cert = self.client_cert        # (cert_path, key_path)
        else:
            # HTTP mode — no verification
            session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return session

    # ---------------------------------------------------------------
    # POST: send XML to the Linux server
    # ---------------------------------------------------------------
    def post_xml(self, path: str, xml_bytes: bytes) -> Optional[bytes]:
        """
        POST an XML document to the Linux server endpoint.

        Args:
            path:      relative path, e.g. "/catalogue/update"
            xml_bytes: UTF-8 encoded XML document

        Returns:
            Response body as bytes (if any), or None on error.
        """
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        try:
            response = self._session.post(
                url,
                data=xml_bytes,
                headers={"Content-Type": "application/xml; charset=utf-8"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            logger.info("POST XML to %s — HTTP %s", url, response.status_code)
            return response.content if response.content else None

        except requests.exceptions.SSLError as exc:
            logger.error("SSL error POSTing XML to %s: %s", url, exc)
            raise
        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error POSTing XML to %s: %s", url, exc)
            raise
        except requests.exceptions.HTTPError as exc:
            logger.error(
                "HTTP %s from %s: %s",
                exc.response.status_code, url, exc.response.text[:500]
            )
            raise

    # ---------------------------------------------------------------
    # GET: retrieve XML from the Linux server
    # ---------------------------------------------------------------
    def get_xml(self, path: str, params: Optional[dict] = None) -> bytes:
        """
        GET an XML document from the Linux server endpoint.

        Args:
            path:   relative path, e.g. "/catalogue/feed"
            params: optional query parameters

        Returns:
            Response body as bytes (the XML document).
        """
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        try:
            response = self._session.get(
                url,
                params=params,
                headers={"Accept": "application/xml"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            logger.info("GET XML from %s — HTTP %s (%d bytes)",
                        url, response.status_code, len(response.content))
            return response.content

        except requests.exceptions.SSLError as exc:
            logger.error("SSL error GETting XML from %s: %s", url, exc)
            raise
        except requests.exceptions.HTTPError as exc:
            logger.error("HTTP %s from %s", exc.response.status_code, url)
            raise


# Module-level singleton — re-use the session across requests
bridge_client = BridgeClient()
```

-----

## Django Settings: The Protocol Toggle ⚙️

```python
# gamelib/settings.py (or .env)

# Default: plain HTTP
XML_BRIDGE_USE_HTTPS   = os.environ.get("XML_BRIDGE_USE_HTTPS", "false").lower() == "true"
XML_BRIDGE_BASE_URL    = os.environ.get("XML_BRIDGE_BASE_URL", "http://linux-srv.internal:8080")
XML_BRIDGE_API_KEY     = os.environ.get("XML_BRIDGE_API_KEY", "")
XML_BRIDGE_CA_CERT     = os.environ.get("XML_BRIDGE_CA_CERT", None)     # set in Episode 6
XML_BRIDGE_CLIENT_CERT = None                                             # set in Episode 7
XML_BRIDGE_TIMEOUT_SECONDS = 30
```

Switching from HTTP to HTTPS:

```bash
# .env
XML_BRIDGE_USE_HTTPS=true
XML_BRIDGE_BASE_URL=https://linux-srv.internal:8443
XML_BRIDGE_CA_CERT=/etc/gamelib/certs/ca.crt
```

No code change. The `BridgeClient` constructor re-reads settings. Restart Django.

-----

## Management Commands: Trigger Syncs 🛠️

```python
# xml_bridge/management/commands/push_catalogue.py
from django.core.management.base import BaseCommand
from games.models import Game
from xml_bridge.serializers import games_to_xml
from xml_bridge.client import bridge_client


class Command(BaseCommand):
    help = "POST the full game catalogue as XML to the external Linux server."

    def add_arguments(self, parser):
        parser.add_argument("--genre", type=str, help="Filter by genre slug")

    def handle(self, *args, **options):
        qs = Game.objects.all()
        if options["genre"]:
            qs = qs.filter(genres__slug=options["genre"])
            self.stdout.write(f"Filtering by genre: {options['genre']}")

        xml = games_to_xml(qs)
        self.stdout.write(f"Serialised {qs.count()} games ({len(xml)} bytes).")

        try:
            response = bridge_client.post_xml("/catalogue/update", xml)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Posted successfully. Server replied: {response[:200] if response else 'no body'}"
                )
            )
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Push failed: {exc}"))
```

```python
# xml_bridge/management/commands/pull_updates.py
from django.core.management.base import BaseCommand
from xml_bridge.client import bridge_client
from xml_bridge.serializers import xml_to_games
from games.models import Game, Genre


class Command(BaseCommand):
    help = "GET catalogue updates as XML from the external Linux server and upsert games."

    def handle(self, *args, **options):
        try:
            xml_bytes = bridge_client.get_xml("/catalogue/feed")
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Pull failed: {exc}"))
            return

        game_dicts = xml_to_games(xml_bytes)
        self.stdout.write(f"Received {len(game_dicts)} game entries.")

        created_count = updated_count = 0
        for gd in game_dicts:
            external_id = gd.pop("external_id", None)
            obj, created = Game.objects.update_or_create(
                title=gd["title"],
                defaults={k: v for k, v in gd.items() if v},
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done: {created_count} created, {updated_count} updated."
        ))
```

Run them:

```bash
python manage.py push_catalogue
python manage.py push_catalogue --genre=rpg
python manage.py pull_updates
```

-----

## DRF Endpoint to Trigger Bridge from API 🔌

For programmatic triggering (from Angular admin panel, or CI/CD pipeline):

```python
# xml_bridge/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status as http_status
from games.models import Game
from .serializers import games_to_xml
from .client import bridge_client


@api_view(["POST"])
@permission_classes([IsAdminUser])
def push_catalogue(request):
    xml = games_to_xml(Game.objects.all())
    try:
        bridge_client.post_xml("/catalogue/update", xml)
        return Response({"status": "ok", "games_pushed": Game.objects.count()})
    except Exception as exc:
        return Response({"error": str(exc)}, status=http_status.HTTP_502_BAD_GATEWAY)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def pull_updates(request):
    try:
        xml_bytes = bridge_client.get_xml("/catalogue/feed")
        game_dicts = xml_to_games(xml_bytes)
        return Response({"status": "ok", "games_received": len(game_dicts)})
    except Exception as exc:
        return Response({"error": str(exc)}, status=http_status.HTTP_502_BAD_GATEWAY)
```

-----

The wire is live. Plain HTTP works. The protocol toggle is wired. In **Episode 6**, we add the lock — TLS. The same client code, a self-signed certificate on the Linux server, and a custom CA cert trusted by Django.

-----

**🔗 Resources**

- **`requests` library**: [docs.python-requests.org](https://docs.python-requests.org)
- **lxml tutorial**: [lxml.de/tutorial.html](https://lxml.de/tutorial.html)
- **Django management commands**: [docs.djangoproject.com/en/5.x/howto/custom-management-commands](https://docs.djangoproject.com/en/5.x/howto/custom-management-commands/)

-----

*🎮 Game on Djangular Series is a series about building GameLib with Django REST Framework, Angular, XML exchange, TLS/mTLS, SailPoint IAM, and PKI management.*
