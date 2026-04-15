---
title: "Game on Djangular 🎮 Ep.4"
part: 4
published: false
description: "Episode 4: The front of the Vault opens. Angular components consume the DRF API, display your game shelf with status badges, genre filters, and review forms. Services wrap the HTTP calls, RxJS keeps state reactive, and the router connects it all."
tags: [angular, typescript, frontend, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/game_on_djangular_series/game-on-djangular-episode-04.png"
series: "Game on Djangular Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 4: Loading Your Shelf

> *“The best game interface is the one that gets out of the way and shows you your games.”*

-----

## What the Shelf Looks Like 🖥️

When a logged-in gamer opens the Vault, they see a shelf. Their games, sorted by last-updated. Each entry has a cover image, a title, a developer, a genre tag, and a status badge — a coloured indicator showing whether the game is Playing, Finished, Planned, or Dropped.

Filter the shelf by genre. Filter by status. Search by title. Click a game to see the detail view: full description, your review, your score, other players’ reviews. Click “Update Status” to move a game from Playing to Finished. The experience should feel fast, reactive, and local — even though every piece of data is coming from a Django REST API.

This episode builds that shelf.

-----

## 🗂️ SIPOC — The Angular Frontend

|**Suppliers**          |**Inputs**                             |**Process**                                                        |**Outputs**                           |**Customers**                                                       |
|-----------------------|---------------------------------------|-------------------------------------------------------------------|--------------------------------------|--------------------------------------------------------------------|
|DRF API (Episodes 2–3) |HTTP responses: JSON arrays and objects|Angular `HttpClient` + service layer                               |Observable streams of typed data      |Components subscribing via `async` pipe                             |
|Gamer (UI interactions)|Click, filter change, form submit      |Component event handlers → service methods → HTTP POST/PATCH/DELETE|UI state update + API mutation        |PostgreSQL (via DRF) updated; component re-renders                  |
|Angular Router         |URL path + query parameters            |Route matching → component activation → data resolved from services|A rendered page appropriate to the URL|The gamer — browser URL and back/forward navigation work as expected|

-----

## The Game Service: One API, One Place 🔧

The service pattern keeps HTTP logic out of components. All API calls go through one injectable service:

```typescript
// src/app/features/catalogue/game.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Genre {
  id: number;
  name: string;
  slug: string;
}

export interface Game {
  id: number;
  title: string;
  description: string;
  cover_image: string;
  release_year: number;
  developer: string;
  genres: Genre[];
  review_count: number;
  average_score: number | null;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({ providedIn: 'root' })
export class GameService {
  private base = `${environment.apiUrl}/games`;

  constructor(private http: HttpClient) {}

  getGames(filters: Record<string, string> = {}): Observable<PaginatedResponse<Game>> {
    let params = new HttpParams();
    for (const [key, val] of Object.entries(filters)) {
      if (val) params = params.set(key, val);
    }
    return this.http.get<PaginatedResponse<Game>>(this.base + '/', { params });
  }

  getGame(id: number): Observable<Game> {
    return this.http.get<Game>(`${this.base}/${id}/`);
  }

  getGenres(): Observable<Genre[]> {
    return this.http.get<Genre[]>(`${environment.apiUrl}/genres/`);
  }
}
```

### The Vault Service

```typescript
// src/app/features/vault/vault.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export type GameStatus = 'playing' | 'finished' | 'planned' | 'dropped';

export interface UserGame {
  id: number;
  game: import('../catalogue/game.service').Game;
  status: GameStatus;
  hours_played: number;
  added_at: string;
  updated_at: string;
}

export interface Review {
  id: number;
  username: string;
  game: number;
  score: number;
  body: string;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class VaultService {
  private vaultUrl  = `${environment.apiUrl}/vault`;
  private reviewUrl = `${environment.apiUrl}/reviews`;

  constructor(private http: HttpClient) {}

  getVault(filters: Record<string, string> = {}): Observable<{ results: UserGame[] }> {
    let params = new URLSearchParams(filters).toString();
    return this.http.get<{ results: UserGame[] }>(
      this.vaultUrl + '/' + (params ? '?' + params : '')
    );
  }

  addGame(gameId: number, status: GameStatus = 'planned'): Observable<UserGame> {
    return this.http.post<UserGame>(this.vaultUrl + '/', { game_id: gameId, status });
  }

  updateStatus(entryId: number, status: GameStatus, hoursPlayed?: number): Observable<UserGame> {
    return this.http.patch<UserGame>(`${this.vaultUrl}/${entryId}/`, {
      status,
      ...(hoursPlayed !== undefined && { hours_played: hoursPlayed }),
    });
  }

  removeGame(entryId: number): Observable<void> {
    return this.http.delete<void>(`${this.vaultUrl}/${entryId}/`);
  }

  postReview(gameId: number, score: number, body: string): Observable<Review> {
    return this.http.post<Review>(this.reviewUrl + '/', { game: gameId, score, body });
  }
}
```

-----

## The Vault Component: Rendering the Shelf 📚

```typescript
// src/app/features/vault/vault.component.ts
import { Component, OnInit }    from '@angular/core';
import { CommonModule }          from '@angular/common';
import { FormsModule }           from '@angular/forms';
import { RouterLink }            from '@angular/router';
import { VaultService, UserGame, GameStatus } from './vault.service';
import { GameService, Genre }    from '../catalogue/game.service';
import { StatusBadgeComponent }  from '../../shared/status-badge.component';

@Component({
  selector: 'app-vault',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, StatusBadgeComponent],
  template: `
    <div class="vault-header">
      <h1>🎮 Your Vault</h1>
      <span class="count">{{ entries.length }} games</span>
    </div>

    <!-- Filters -->
    <div class="filters">
      <select [(ngModel)]="statusFilter" (ngModelChange)="loadVault()">
        <option value="">All statuses</option>
        <option value="playing">Playing</option>
        <option value="finished">Finished</option>
        <option value="planned">Planned</option>
        <option value="dropped">Dropped</option>
      </select>
      <select [(ngModel)]="genreFilter" (ngModelChange)="loadVault()">
        <option value="">All genres</option>
        <option *ngFor="let g of genres" [value]="g.slug">{{ g.name }}</option>
      </select>
    </div>

    <!-- Game cards -->
    <div class="shelf" *ngIf="!loading; else spinner">
      <div class="game-card" *ngFor="let entry of entries">
        <img [src]="entry.game.cover_image || 'assets/placeholder.png'"
             [alt]="entry.game.title" />
        <div class="card-body">
          <h3>{{ entry.game.title }}</h3>
          <p class="developer">{{ entry.game.developer }}</p>
          <div class="genres">
            <span class="tag" *ngFor="let g of entry.game.genres">{{ g.name }}</span>
          </div>
          <app-status-badge [status]="entry.status" />
          <div class="hours" *ngIf="entry.status === 'playing'">
            {{ entry.hours_played }}h played
          </div>
        </div>
        <div class="card-actions">
          <select [ngModel]="entry.status"
                  (ngModelChange)="onStatusChange(entry, $event)">
            <option value="playing">Playing</option>
            <option value="finished">Finished</option>
            <option value="planned">Planned</option>
            <option value="dropped">Dropped</option>
          </select>
          <button class="remove-btn" (click)="removeEntry(entry)">Remove</button>
          <a [routerLink]="['/games', entry.game.id]">View details</a>
        </div>
      </div>
      <p class="empty" *ngIf="entries.length === 0">
        Your vault is empty. <a routerLink="/games">Browse the catalogue!</a>
      </p>
    </div>

    <ng-template #spinner>
      <div class="loading">Loading your vault...</div>
    </ng-template>
  `,
})
export class VaultComponent implements OnInit {
  entries:      UserGame[] = [];
  genres:       Genre[]    = [];
  statusFilter  = '';
  genreFilter   = '';
  loading       = true;

  constructor(
    private vaultSvc: VaultService,
    private gameSvc:  GameService,
  ) {}

  ngOnInit(): void {
    this.gameSvc.getGenres().subscribe(g => this.genres = g);
    this.loadVault();
  }

  loadVault(): void {
    this.loading = true;
    const filters: Record<string, string> = {};
    if (this.statusFilter) filters['status'] = this.statusFilter;
    if (this.genreFilter)  filters['game__genres__slug'] = this.genreFilter;

    this.vaultSvc.getVault(filters).subscribe({
      next: res => { this.entries = res.results; this.loading = false; },
      error: () => { this.loading = false; },
    });
  }

  onStatusChange(entry: UserGame, newStatus: GameStatus): void {
    this.vaultSvc.updateStatus(entry.id, newStatus).subscribe(updated => {
      const idx = this.entries.findIndex(e => e.id === entry.id);
      if (idx !== -1) this.entries[idx] = updated;
    });
  }

  removeEntry(entry: UserGame): void {
    if (!confirm(`Remove "${entry.game.title}" from your vault?`)) return;
    this.vaultSvc.removeGame(entry.id).subscribe(() => {
      this.entries = this.entries.filter(e => e.id !== entry.id);
    });
  }
}
```

-----

## The Status Badge: Coloured Indicators 🏷️

```typescript
// src/app/shared/status-badge.component.ts
import { Component, Input } from '@angular/core';
import { CommonModule }     from '@angular/common';
import { GameStatus }       from '../features/vault/vault.service';

const STATUS_CONFIG: Record<GameStatus, { label: string; colour: string }> = {
  playing:  { label: '▶ Playing',  colour: '#22c55e' },   // green
  finished: { label: '✓ Finished', colour: '#3b82f6' },   // blue
  planned:  { label: '◷ Planned',  colour: '#f59e0b' },   // amber
  dropped:  { label: '✕ Dropped',  colour: '#ef4444' },   // red
};

@Component({
  selector: 'app-status-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="badge" [style.background-color]="config.colour">
      {{ config.label }}
    </span>
  `,
  styles: [`
    .badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      color: white;
      font-size: 0.75rem;
      font-weight: 600;
    }
  `]
})
export class StatusBadgeComponent {
  @Input({ required: true }) status!: GameStatus;
  get config() { return STATUS_CONFIG[this.status]; }
}
```

-----

## The Catalogue Component: Browsing and Adding to Vault 🌐

```typescript
// src/app/features/catalogue/catalogue.component.ts
import { Component, OnInit }   from '@angular/core';
import { CommonModule }         from '@angular/common';
import { FormsModule }          from '@angular/forms';
import { RouterLink }           from '@angular/router';
import { GameService, Game, Genre } from './game.service';
import { VaultService }         from '../vault/vault.service';
import { AuthService }          from '../../core/auth/auth.service';

@Component({
  selector: 'app-catalogue',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="catalogue-header">
      <h1>🗂️ Game Catalogue</h1>
      <input [(ngModel)]="searchTerm"
             (ngModelChange)="loadGames()"
             placeholder="Search games..."
             class="search-input" />
    </div>

    <div class="genre-pills">
      <button [class.active]="!selectedGenre"
              (click)="selectGenre('')">All</button>
      <button *ngFor="let g of genres"
              [class.active]="selectedGenre === g.slug"
              (click)="selectGenre(g.slug)">
        {{ g.name }}
      </button>
    </div>

    <div class="catalogue-grid" *ngIf="!loading">
      <div class="game-card" *ngFor="let game of games">
        <img [src]="game.cover_image || 'assets/placeholder.png'"
             [alt]="game.title" />
        <h3>
          <a [routerLink]="['/games', game.id]">{{ game.title }}</a>
        </h3>
        <p>{{ game.developer }} · {{ game.release_year }}</p>
        <div class="genres">
          <span *ngFor="let g of game.genres" class="tag">{{ g.name }}</span>
        </div>
        <div class="score" *ngIf="game.average_score">
          ⭐ {{ game.average_score }} / 10
          ({{ game.review_count }} reviews)
        </div>
        <button *ngIf="isLoggedIn"
                class="add-btn"
                (click)="addToVault(game)">
          + Add to Vault
        </button>
      </div>
    </div>
  `,
})
export class CatalogueComponent implements OnInit {
  games:         Game[]  = [];
  genres:        Genre[] = [];
  selectedGenre  = '';
  searchTerm     = '';
  loading        = true;
  isLoggedIn     = false;

  constructor(
    private gameSvc:   GameService,
    private vaultSvc:  VaultService,
    private authSvc:   AuthService,
  ) {}

  ngOnInit(): void {
    this.isLoggedIn = this.authSvc.isLoggedIn();
    this.gameSvc.getGenres().subscribe(g => this.genres = g);
    this.loadGames();
  }

  loadGames(): void {
    this.loading = true;
    const filters: Record<string, string> = {};
    if (this.selectedGenre) filters['genres__slug'] = this.selectedGenre;
    if (this.searchTerm)    filters['search']       = this.searchTerm;

    this.gameSvc.getGames(filters).subscribe({
      next: res => { this.games = res.results; this.loading = false; },
      error: () => { this.loading = false; },
    });
  }

  selectGenre(slug: string): void {
    this.selectedGenre = slug;
    this.loadGames();
  }

  addToVault(game: Game): void {
    this.vaultSvc.addGame(game.id, 'planned').subscribe({
      next: () => alert(`"${game.title}" added to your vault as Planned!`),
      error: err => {
        if (err.status === 400 && err.error?.non_field_errors) {
          alert('Already in your vault.');
        }
      }
    });
  }
}
```

-----

In **Episode 5**, we leave the browser and go server-to-server. The Django backend needs to send and receive XML files with an external Linux server. Plain HTTP by default, HTTPS on demand. The `requests` library, XML serialisation with `lxml`, and a configurable transport layer.

-----

**🔗 Resources**

- **Angular standalone components**: [angular.dev/guide/components](https://angular.dev/guide/components)
- **Angular HttpClient**: [angular.dev/guide/http](https://angular.dev/guide/http)
- **RxJS operators**: [rxjs.dev/guide/operators](https://rxjs.dev/guide/operators)

-----

*🎮 Game on Djangular Series is a series about building GameLib with Django REST Framework, Angular, XML exchange, TLS/mTLS, SailPoint IAM, and PKI management.*
