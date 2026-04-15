---
title: "Game on Djangular 🎮 Ep.2"
part: 2
published: false
description: "Episode 2: Every vault needs a catalogue. Game, Genre, UserGame, Review — Django models that mirror your library. DRF serializers that turn them into JSON. ViewSets that expose them as a REST API. The database layer of GameLib, built step by step."
tags: [django, python, postgresql, drf]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/game_on_djangular_series/game-on-djangular-episode-02.png"
series: "Game on Djangular Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 2: Building the Game Catalogue

> *“Before you can track a game, the game has to exist. Before it can exist, you need a schema.”*

-----

## The Inventory Before the Adventure 🗂️

Every RPG starts with character creation before the quest. Django starts with models before the endpoints. The model is your schema — the blueprint for every game, every genre, every player vault, and every review that will ever live in the database.

In Episode 1, we mapped the GameLib features to the stack. Now we build the foundation: four models, their serializers, their viewsets, and the URL wiring that turns them into a navigable REST API.

-----

## 🗂️ SIPOC — The Catalogue Layer

|**Suppliers**  |**Inputs**                                       |**Process**                                        |**Outputs**                                                                    |**Customers**                                                 |
|---------------|-------------------------------------------------|---------------------------------------------------|-------------------------------------------------------------------------------|--------------------------------------------------------------|
|Django ORM     |Python class definitions in `models.py`          |`python manage.py makemigrations` + `migrate`      |PostgreSQL tables with correct types, constraints, indices                     |DRF serializers reading and writing rows                      |
|DRF Serializers|Model instances or raw JSON dicts                |`.to_representation()` / `.to_internal_value()`    |Validated Python dicts ready to write; or JSON-serialisable dicts ready to send|ViewSets composing responses; Angular receiving them          |
|DRF ViewSets   |HTTP request (method + URL + body + auth)        |Router → ViewSet → queryset → serializer → response|A JSON HTTP response: 200, 201, 400, 403, 404                                  |Angular `HttpClient` calls from the frontend                  |
|`django-filter`|URL query parameters: `?genre=RPG&status=Playing`|`FilterBackend` applies queryset filters           |A filtered queryset subset                                                     |Angular shelf component rendering only what the user asked for|

-----

## The Four Models 🎮

### `Genre` — The Shelf Labels

```python
# games/models.py
from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
```

### `Game` — The Catalogue Entry

```python
class Game(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image = models.URLField(blank=True)
    release_year = models.PositiveSmallIntegerField(null=True, blank=True)
    developer = models.CharField(max_length=255, blank=True)
    genres = models.ManyToManyField(Genre, related_name="games", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return self.title
```

### `UserGame` — The Vault Entry

```python
# vault/models.py
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

STATUS_CHOICES = [
    ("playing",   "Playing"),
    ("finished",  "Finished"),
    ("planned",   "Planned"),
    ("dropped",   "Dropped"),
]


class UserGame(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vault",
    )
    game = models.ForeignKey(
        "games.Game",
        on_delete=models.CASCADE,
        related_name="user_entries",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned",
    )
    hours_played = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "game")]    # one entry per game per user
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} — {self.game.title} ({self.status})"
```

### `Review` — The Rating and Write-Up

```python
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    game = models.ForeignKey(
        "games.Game", on_delete=models.CASCADE, related_name="reviews"
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "game")]    # one review per game per user

    def __str__(self):
        return f"{self.user.username} on {self.game.title}: {self.score}/10"
```

-----

## DRF Serializers 🔄

Serializers are the translators — they convert Django model instances to Python dicts (for JSON responses) and validate incoming JSON back to model instances (for writes).

### Genre and Game Serializers

```python
# games/serializers.py
from rest_framework import serializers
from .models import Game, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug", "description"]


class GameListSerializer(serializers.ModelSerializer):
    """Compact serializer for catalogue browsing — excludes full description."""
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ["id", "title", "cover_image", "release_year", "developer", "genres"]


class GameDetailSerializer(serializers.ModelSerializer):
    """Full serializer for individual game view."""
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Genre.objects.all(),
        source="genres",
    )
    review_count = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            "id", "title", "description", "cover_image",
            "release_year", "developer", "genres", "genre_ids",
            "review_count", "average_score", "created_at",
        ]

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_average_score(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return round(sum(r.score for r in reviews) / len(reviews), 1)
```

### UserGame and Review Serializers

```python
# vault/serializers.py
from rest_framework import serializers
from .models import UserGame, Review
from games.serializers import GameListSerializer


class UserGameSerializer(serializers.ModelSerializer):
    game = GameListSerializer(read_only=True)
    game_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=__import__("games.models", fromlist=["Game"]).Game.objects.all(),
        source="game",
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserGame
        fields = [
            "id", "user", "game", "game_id",
            "status", "hours_played", "added_at", "updated_at",
        ]
        read_only_fields = ["added_at", "updated_at"]


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "user", "username", "game",
            "score", "body", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
```

-----

## DRF ViewSets and Filtering 🎯

ViewSets combine CRUD logic. One class handles `GET /games/`, `GET /games/{id}/`, `POST /games/`, `PATCH /games/{id}/`, `DELETE /games/{id}/`.

```python
# games/views.py
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Game, Genre
from .serializers import GameDetailSerializer, GameListSerializer, GenreSerializer


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.prefetch_related("genres").all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["genres__slug", "release_year"]
    search_fields = ["title", "developer", "description"]
    ordering_fields = ["title", "release_year", "created_at"]
    ordering = ["title"]

    def get_serializer_class(self):
        if self.action == "list":
            return GameListSerializer
        return GameDetailSerializer

    def get_permissions(self):
        # Anyone can read; only admins can write catalogue entries
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
```

```python
# vault/views.py
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import UserGame, Review
from .serializers import UserGameSerializer, ReviewSerializer


class UserGameViewSet(viewsets.ModelViewSet):
    serializer_class = UserGameSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "game__genres__slug"]
    ordering_fields = ["added_at", "updated_at", "status"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        # Each user only sees their own vault
        return UserGame.objects.filter(
            user=self.request.user
        ).select_related("game").prefetch_related("game__genres")


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        game_id = self.kwargs.get("game_pk")
        if game_id:
            return Review.objects.filter(game_id=game_id).select_related("user")
        return Review.objects.filter(user=self.request.user).select_related("game")
```

-----

## URL Routing with DRF Router 🛣️

```python
# gamelib/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from games.views import GameViewSet, GenreViewSet
from vault.views import UserGameViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r"games",  GameViewSet,     basename="game")
router.register(r"genres", GenreViewSet,    basename="genre")
router.register(r"vault",  UserGameViewSet, basename="usergame")
router.register(r"reviews", ReviewViewSet,  basename="review")

urlpatterns = [
    path("admin/",          admin.site.urls),
    path("api/",            include(router.urls)),
    path("api/auth/token/", TokenObtainPairView.as_view(),    name="token_obtain"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
```

This generates the full REST surface automatically:

|Method  |URL               |Action                     |
|--------|------------------|---------------------------|
|`GET`   |`/api/games/`     |List all games (filterable)|
|`POST`  |`/api/games/`     |Create game (admin only)   |
|`GET`   |`/api/games/{id}/`|Get one game               |
|`PATCH` |`/api/games/{id}/`|Update game (admin only)   |
|`GET`   |`/api/vault/`     |Your library entries       |
|`POST`  |`/api/vault/`     |Add game to vault          |
|`PATCH` |`/api/vault/{id}/`|Update status / hours      |
|`DELETE`|`/api/vault/{id}/`|Remove from vault          |
|`GET`   |`/api/reviews/`   |Your reviews               |
|`POST`  |`/api/reviews/`   |Post a review              |

-----

## Settings: Connecting the Database 🔌

```python
# gamelib/settings.py (excerpt)
import os
from pathlib import Path

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME":     os.environ.get("DB_NAME", "gamelib_db"),
        "USER":     os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST":     os.environ.get("DB_HOST", "localhost"),
        "PORT":     os.environ.get("DB_PORT", "5432"),
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "corsheaders",
    "django_filters",
    "rest_framework_simplejwt",
    # Local apps
    "games",
    "vault",
    "users",
    "xml_bridge",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",    # Angular dev server
]
```

-----

## Run the Migrations and Seed Data 🌱

```bash
python manage.py makemigrations games vault users
python manage.py migrate

# Seed some initial genres
python manage.py shell -c "
from games.models import Genre
genres = ['Action', 'RPG', 'Strategy', 'Puzzle', 'FPS', 'Adventure', 'Simulation']
for g in genres:
    Genre.objects.get_or_create(name=g, slug=g.lower())
print('Genres seeded.')
"
```

The catalogue is built. The Vault is ready. In **Episode 3**, we add the locks — JWT authentication — so each gamer only sees their own shelf.

-----

**🔗 Resources**

- **Django models**: [docs.djangoproject.com/en/5.x/topics/db/models](https://docs.djangoproject.com/en/5.x/topics/db/models/)
- **DRF ViewSets**: [django-rest-framework.org/api-guide/viewsets](https://www.django-rest-framework.org/api-guide/viewsets/)
- **django-filter**: [django-filter.readthedocs.io](https://django-filter.readthedocs.io)

-----

*🎮 Game on Djangular Series is a series about building GameLib with Django REST Framework, Angular, XML exchange, TLS/mTLS, SailPoint IAM, and PKI management.*
