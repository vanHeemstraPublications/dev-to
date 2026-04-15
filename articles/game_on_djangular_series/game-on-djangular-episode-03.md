-----

## title: “Game on Djangular! 🎮 Ep.3: Your Login Token”
published: false
description: “Episode 3: Your guild membership card — JWT authentication in GameLib. djangorestframework-simplejwt on the Django side, an Angular HttpInterceptor that attaches the token automatically, route guards that protect the vault, and token refresh that keeps you logged in.”
tags: [django, angular, jwt, authentication]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/djangular-gamelib-episode-03.png”
series: “Game on Djangular Series”
canonical_url: “”
organization: “the-software-s-journey”

# Game on Djangular! 🎮

## Episode 3: Your Login Token

> *“Every guild has a membership card. Without it, the vault door stays closed.”*

-----

## The Membership Card Problem 🃏

GameLib has public data — any visitor can browse the game catalogue. But the Vault is private. Ahmed’s backlog should not be visible to Maria. Maria’s reviews should not be editable by Ahmed. Every time someone makes a request to the `/api/vault/` endpoint, the server needs to know who they are.

The answer is **JWT — JSON Web Token** authentication. When a gamer logs in, the server issues a digitally-signed token. That token goes with every subsequent request. The server reads the token, validates the signature, and knows exactly who is making the request — without touching the database on every call.

Your login token is your guild membership card. Present it at the door, or the vault stays closed.

-----

## 🗂️ SIPOC — Authentication

|**Suppliers**           |**Inputs**                                          |**Process**                                         |**Outputs**                                                            |**Customers**                                                         |
|------------------------|----------------------------------------------------|----------------------------------------------------|-----------------------------------------------------------------------|----------------------------------------------------------------------|
|The gamer (browser)     |`POST /api/auth/token/` with `username` + `password`|`simplejwt` validates credentials, signs two tokens |`access` token (short-lived, 5 min) + `refresh` token (long-lived, 24h)|Angular `AuthService` — stores both tokens                            |
|Angular `JwtInterceptor`|Every outgoing HTTP request                         |Adds `Authorization: Bearer <access>` header        |An authenticated HTTP request the backend trusts                       |DRF backend — reads the header, validates the JWT signature           |
|Django DRF              |Each incoming API request with a JWT header         |`JWTAuthentication.authenticate()` decodes the token|`request.user` populated with the authenticated user                   |ViewSets that gate writes behind `IsAuthenticated`                    |
|Angular `AuthGuard`     |Route navigation event                              |Checks `localStorage` for a valid token             |Allow or redirect to `/login`                                          |The Angular Router — users without tokens never reach protected routes|

-----

## Django Side: simplejwt Configuration ⚙️

```bash
pip install djangorestframework-simplejwt
```

In `settings.py`:

```python
from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # ... rest of REST_FRAMEWORK settings from Episode 2
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=24),
    "ROTATE_REFRESH_TOKENS":  True,       # new refresh token on each refresh
    "BLACKLIST_AFTER_ROTATION": True,     # old refresh tokens become invalid
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    # Signing algorithm — RS256 for production (asymmetric), HS256 for dev
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}
```

In `urls.py` (from Episode 2, already wired):

```python
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns += [
    path("api/auth/token/",         TokenObtainPairView.as_view(), name="token_obtain"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(),    name="token_refresh"),
    path("api/auth/token/verify/",  TokenVerifyView.as_view(),     name="token_verify"),
]
```

### Custom Token with User Info

The default `access` token only encodes `user_id`. For the Angular frontend, it is useful to also include `username` and `is_staff` without an extra API call:

```python
# users/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class GameLibTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims — these appear in the decoded JWT payload
        token["username"] = user.username
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        return token
```

```python
# users/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import GameLibTokenObtainPairSerializer


class GameLibTokenObtainView(TokenObtainPairView):
    serializer_class = GameLibTokenObtainPairSerializer
```

Wire this in `urls.py` instead of the default `TokenObtainPairView`.

-----

## Angular Side: AuthService 🅰️

```typescript
// src/app/core/auth/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient }  from '@angular/common/http';
import { Router }      from '@angular/router';
import { Observable, tap } from 'rxjs';
import { jwtDecode }   from 'jwt-decode';
import { environment } from '../../environments/environment';

interface JwtPayload {
  user_id: number;
  username: string;
  email: string;
  is_staff: boolean;
  exp: number;
}

interface TokenResponse {
  access:  string;
  refresh: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly accessKey  = 'gamelib_access';
  private readonly refreshKey = 'gamelib_refresh';

  constructor(private http: HttpClient, private router: Router) {}

  login(username: string, password: string): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(
      `${environment.apiUrl}/auth/token/`,
      { username, password }
    ).pipe(
      tap(tokens => {
        localStorage.setItem(this.accessKey,  tokens.access);
        localStorage.setItem(this.refreshKey, tokens.refresh);
      })
    );
  }

  logout(): void {
    localStorage.removeItem(this.accessKey);
    localStorage.removeItem(this.refreshKey);
    this.router.navigate(['/login']);
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.accessKey);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.refreshKey);
  }

  isLoggedIn(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;
    try {
      const payload = jwtDecode<JwtPayload>(token);
      return payload.exp * 1000 > Date.now();    // check expiry
    } catch {
      return false;
    }
  }

  getCurrentUser(): JwtPayload | null {
    const token = this.getAccessToken();
    if (!token) return null;
    try {
      return jwtDecode<JwtPayload>(token);
    } catch {
      return null;
    }
  }

  refreshAccessToken(): Observable<{ access: string }> {
    return this.http.post<{ access: string }>(
      `${environment.apiUrl}/auth/token/refresh/`,
      { refresh: this.getRefreshToken() }
    ).pipe(
      tap(res => localStorage.setItem(this.accessKey, res.access))
    );
  }
}
```

-----

## The HttpInterceptor: Automatic Token Attachment 🪝

Without an interceptor, every component would need to manually add the `Authorization` header. The interceptor does it once for all requests:

```typescript
// src/app/core/auth/jwt.interceptor.ts
import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpErrorResponse } from '@angular/common/http';
import { inject }        from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService }   from './auth.service';
import { Router }        from '@angular/router';

export const jwtInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
) => {
  const auth   = inject(AuthService);
  const router = inject(Router);
  const token  = auth.getAccessToken();

  // Attach token if present
  const authReq = token
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && auth.getRefreshToken()) {
        // Try to refresh the access token
        return auth.refreshAccessToken().pipe(
          switchMap(res => {
            const retried = req.clone({
              setHeaders: { Authorization: `Bearer ${res.access}` }
            });
            return next(retried);
          }),
          catchError(() => {
            // Refresh also failed — send to login
            auth.logout();
            return throwError(() => error);
          })
        );
      }
      return throwError(() => error);
    })
  );
};
```

Register it in `app.config.ts`:

```typescript
// src/app/app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideRouter }     from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { routes }            from './app.routes';
import { jwtInterceptor }    from './core/auth/jwt.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([jwtInterceptor])),
  ]
};
```

-----

## Route Guards: The Vault Door 🚪

The `AuthGuard` blocks unauthenticated navigation to protected routes:

```typescript
// src/app/core/auth/auth.guard.ts
import { inject }        from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { Router }        from '@angular/router';
import { AuthService }   from './auth.service';

export const authGuard: CanActivateFn = () => {
  const auth   = inject(AuthService);
  const router = inject(Router);

  if (auth.isLoggedIn()) {
    return true;
  }
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: router.url }
  });
};
```

Apply it to vault routes:

```typescript
// src/app/app.routes.ts
import { Routes }   from '@angular/router';
import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  { path: 'login',    loadComponent: () => import('./features/auth/login.component') },
  { path: 'register', loadComponent: () => import('./features/auth/register.component') },
  { path: 'games',    loadComponent: () => import('./features/catalogue/catalogue.component') },
  {
    path: 'vault',
    canActivate: [authGuard],                  // ← protected
    loadComponent: () => import('./features/vault/vault.component'),
  },
  {
    path: 'vault/:id',
    canActivate: [authGuard],
    loadComponent: () => import('./features/vault/game-detail.component'),
  },
  { path: '', redirectTo: '/games', pathMatch: 'full' },
  { path: '**', redirectTo: '/games' },
];
```

-----

## The Login Component 🖥️

```typescript
// src/app/features/auth/login.component.ts
import { Component }         from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { AuthService }       from '../../core/auth/auth.service';
import { CommonModule }      from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule, RouterLink],
  template: `
    <div class="login-container">
      <h2>🎮 GameLib Login</h2>
      <form [formGroup]="form" (ngSubmit)="onSubmit()">
        <input formControlName="username" placeholder="Username" type="text" />
        <input formControlName="password" placeholder="Password" type="password" />
        <button type="submit" [disabled]="form.invalid || loading">
          {{ loading ? 'Logging in...' : 'Enter the Vault' }}
        </button>
        <p class="error" *ngIf="error">{{ error }}</p>
      </form>
      <p>New gamer? <a routerLink="/register">Create account</a></p>
    </div>
  `,
})
export class LoginComponent {
  form = this.fb.group({
    username: ['', Validators.required],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });
  loading = false;
  error   = '';

  constructor(
    private fb:    FormBuilder,
    private auth:  AuthService,
    private router: Router,
    private route: ActivatedRoute,
  ) {}

  onSubmit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.error   = '';
    const { username, password } = this.form.getRawValue();

    this.auth.login(username!, password!).subscribe({
      next: () => {
        const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/vault';
        this.router.navigateByUrl(returnUrl);
      },
      error: () => {
        this.error   = 'Invalid credentials. Check your username and password.';
        this.loading = false;
      },
    });
  }
}
```

-----

## Production JWT Hardening 🔒

For production deployments, switch from `HS256` (symmetric — single secret key) to `RS256` (asymmetric — private key signs, public key verifies). This is especially relevant when the external Linux server from Episodes 5–7 also needs to validate JWTs:

```python
# settings.py — RS256 JWT signing
import os

SIMPLE_JWT = {
    "ALGORITHM": "RS256",
    "SIGNING_KEY":   open(os.environ.get("JWT_PRIVATE_KEY_PATH")).read(),
    "VERIFYING_KEY": open(os.environ.get("JWT_PUBLIC_KEY_PATH")).read(),
    # Generate keys:
    # openssl genrsa -out jwt_private.pem 2048
    # openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
}
```

The public key can be distributed to any service that needs to verify tokens — without sharing the private key. The external Linux server receives a request from Django, validates the JWT using the public key, and confirms the request comes from an authorised GameLib backend.

-----

In **Episode 4**, the Angular frontend renders the vault. Components, services, status badges, genre filters, and the reactive state that keeps the UI in sync with the API.

-----

**🔗 Resources**

- **djangorestframework-simplejwt**: [django-rest-framework-simplejwt.readthedocs.io](https://django-rest-framework-simplejwt.readthedocs.io)
- **Angular HttpInterceptorFn**: [angular.dev/guide/http/interceptors](https://angular.dev/guide/http/interceptors)
- **jwt-decode**: [github.com/auth0/jwt-decode](https://github.com/auth0/jwt-decode)

-----

*🎮 Game on Djangular Series is a series about building GameLib with Django REST Framework, Angular, XML exchange, TLS/mTLS, SailPoint IAM, and PKI management.*
