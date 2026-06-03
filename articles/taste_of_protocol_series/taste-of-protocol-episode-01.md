---
title: "Taste of Protocol 🍽️"
published: false
description: "Remy the rat knew that anyone can cook. We know that anyone can make an HTTP request — but only a chef with a Strategy Pattern knows how to swap the protocol without rewriting the kitchen. HTTP for meat-eaters, HTTPS for vegetarians, and one elegant Python design pattern that lets you change your mind between courses."
tags: [python, designpatterns, http, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/taste-of-protocol-episode-01.png"
series: "Taste of Protocol"
canonical_url: ""
organization: "the-software-s-journey"
---

## Anyone Can Cook an HTTP Request

> *“Not everyone can become a great artist, but a great artist can come from anywhere.”*
> — Chef Auguste Gusteau, *Ratatouille* (2007)

-----

## The Restaurant of the Internet 🐀

Imagine, if you will, a restaurant. Not just any restaurant — the finest restaurant in Paris, *Gusteau’s*, where the kitchen hums with purpose, the sauces reduce with dignity, and every order that leaves the pass has been constructed with intention.

Now imagine that the kitchen has two modes of service.

**Table One** — the carnivores. They like their protocols raw and unencrypted. They order over HTTP: *“Garçon, I would like the roast chicken at port eighty, please, transmitted in plain text for all the internet to see.”* They are perfectly happy. Nothing bad ever happens to them. (This is a lie. Many bad things happen to them.)

**Table Two** — the vegetarians. They order over HTTPS: *“Bonjour, I require the same roast chicken — no wait, the lentil — encrypted end-to-end with TLS, certificate verified, and signed by a trusted authority. Merci.”* They are also perfectly happy, and considerably more secure.

The **chef** — our `Rest` class — does not care which table is ordering. He just cooks. He has a trusted sous-chef at his elbow, a `RestStrategy`, whose only job is to decide how to write the URL on the order ticket. Change the sous-chef, change the URL. The dish itself is the same. The kitchen runs identically.

This, dear reader, is the **Strategy Pattern**. And it is, as Gusteau would say, *magnifique*.

-----

## 🗂️ SIPOC — The Kitchen in Full Service

|**Suppliers**        |**Inputs**                                                                                 |**Process**                                                                                                    |**Outputs**                                                                                |**Customers**                                                     |
|---------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|------------------------------------------------------------------|
|Your application code|`host` (the restaurant address), `path` (the menu item), optional `body` (special requests)|`Rest.get()` or `Rest.post()` calls `strategy.build_url()` to compose the full URL, then dispatches the request|A `dict` containing `method`, `url`, and optionally `body` — the plated dish, ready to send|Any downstream service, API, or test suite consuming the response |
|`HttpStrategy`       |`host` and `path`                                                                          |Prepends `http://` — the carnivore’s sauce                                                                     |`"http://api.example.com/health"`                                                          |The caller — who ordered plain, unencrypted service               |
|`HttpsStrategy`      |`host` and `path`                                                                          |Prepends `https://` — the vegetarian’s drizzle                                                                 |`"https://api.example.com/health"`                                                         |The caller — who ordered TLS-secured, certificate-verified service|
|`RestStrategy` (ABC) |The contract: `build_url(host, path) -> str`                                               |Defines what every strategy must deliver                                                                       |A guaranteed interface — the chef never wonders what the sous-chef will do                 |`Rest` — trusts the strategy completely, never inspects it        |

-----

## The Complete Menu — Every Line of Code 🍴

*Colette taught us that every dish must be shown completely before it is critiqued. So here is the full mise en place.*

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class RestStrategy(ABC):
    @abstractmethod
    def build_url(self, host: str, path: str) -> str:
        pass


class HttpStrategy(RestStrategy):
    def build_url(self, host: str, path: str) -> str:
        return f"http://{host}{path}"


class HttpsStrategy(RestStrategy):
    def build_url(self, host: str, path: str) -> str:
        return f"https://{host}{path}"


@dataclass
class Rest:
    host: str
    strategy: RestStrategy

    def get(self, path: str) -> dict[str, Any]:
        url = self.strategy.build_url(self.host, path)

        print(f"GET {url}")

        # Here you would call requests.get(url), httpx.get(url), etc.
        return {
            "method": "GET",
            "url": url,
        }

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = self.strategy.build_url(self.host, path)

        print(f"POST {url}")
        print(f"BODY {body}")

        return {
            "method": "POST",
            "url": url,
            "body": body,
        }


if __name__ == "__main__":
    rest = Rest(
        host="api.example.com",
        strategy=HttpStrategy(),
    )

    rest.get("/health")

    rest.strategy = HttpsStrategy()
    rest.get("/health")

    rest.post("/users", {"name": "John"})
```

And when you run this kitchen, the pass produces:

```
GET http://api.example.com/health
GET https://api.example.com/health
POST https://api.example.com/users
BODY {'name': 'John'}
```

-----

## Course by Course: What Every Section Does 🍽️

### The Amuse-Bouche: Imports

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
```

`from __future__ import annotations` enables **PEP 563 postponed evaluation** — type hints are treated as strings at runtime instead of being evaluated immediately. This allows forward references in type annotations and is considered good practice in Python 3.7+.

`ABC` and `abstractmethod` are Python’s way of declaring that a class is a blueprint, not a dish. You cannot serve an `ABC` — it exists only to be extended.

`@dataclass` is the kitchen shorthand for “make a class that mostly just holds data.” It auto-generates `__init__`, `__repr__`, and `__eq__` from the annotated fields, so we do not have to write thirty lines of boilerplate that Gusteau would consider beneath his dignity.

-----

### The Entrée: `RestStrategy` — The Abstract Sous-Chef

```python
class RestStrategy(ABC):
    @abstractmethod
    def build_url(self, host: str, path: str) -> str:
        pass
```

This is the **contract**. Like the handwritten menu that every section of the kitchen must honour, `RestStrategy` declares: *“I do not care how you build the URL. I only care that you do build it, that you take a `host` and a `path`, and that you return a `str`.”*

The `@abstractmethod` decorator ensures that any class inheriting from `RestStrategy` **must** implement `build_url`. If it does not, Python raises a `TypeError` at instantiation — the culinary equivalent of a dish arriving at the pass without its sauce. The chef will not plate it. It goes back.

```python
class BrokenStrategy(RestStrategy):
    pass  # forgot to implement build_url

BrokenStrategy()
# TypeError: Can't instantiate abstract class BrokenStrategy
# with abstract method build_url
```

Remy’s nose would have caught that before it left the stove.

-----

### The Plat Principal: `HttpStrategy` and `HttpsStrategy`

```python
class HttpStrategy(RestStrategy):
    def build_url(self, host: str, path: str) -> str:
        return f"http://{host}{path}"


class HttpsStrategy(RestStrategy):
    def build_url(self, host: str, path: str) -> str:
        return f"https://{host}{path}"
```

Two recipes. One dish. The only difference is the sauce — `http://` versus `https://`. Both honour the `RestStrategy` contract. Both are concrete, instantiable, deployable. Both can be handed to the `Rest` class with complete confidence.

Notice what is **not** here: no conditional logic, no `if secure: ... else: ...`, no boolean flag passed to a constructor. Each strategy is self-contained. This is the Strategy Pattern at its most elegant — the behaviour lives in the strategy object, not in a maze of if-else inside the context class.

-----

### The Pièce de Résistance: `Rest`

```python
@dataclass
class Rest:
    host: str
    strategy: RestStrategy

    def get(self, path: str) -> dict[str, Any]:
        url = self.strategy.build_url(self.host, path)
        print(f"GET {url}")
        return {
            "method": "GET",
            "url": url,
        }

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = self.strategy.build_url(self.host, path)
        print(f"POST {url}")
        print(f"BODY {body}")
        return {
            "method": "POST",
            "url": url,
            "body": body,
        }
```

`Rest` is the chef. He holds two things: the address of the restaurant he is calling (`host`) and his current sous-chef (`strategy`). When an order arrives — a `get()` or `post()` — he delegates the URL construction entirely to the sous-chef. He does not know or care whether the result starts with `http://` or `https://`. He plates the dish.

The `@dataclass` decorator means `Rest(host="api.example.com", strategy=HttpStrategy())` simply works — no `def __init__(self, host, strategy): self.host = host...` required. The kitchen is clean. Gusteau smiles.

Crucially: because `strategy` is a plain instance attribute on a `@dataclass`, it can be **reassigned at runtime**:

```python
rest.strategy = HttpsStrategy()
```

The chef just hired a new sous-chef between courses. The kitchen does not need to restart. The next order goes out differently. This is not a bug — it is a feature.

-----

### The Digestif: The `__main__` Block

```python
if __name__ == "__main__":
    rest = Rest(
        host="api.example.com",
        strategy=HttpStrategy(),
    )

    rest.get("/health")

    rest.strategy = HttpsStrategy()
    rest.get("/health")

    rest.post("/users", {"name": "John"})
```

The dining room. We seat the `rest` object with an `HttpStrategy`, check that the kitchen is alive (`/health`), then — mid-service — swap to `HttpsStrategy` and check again. The second health check goes out encrypted. Then we `POST` a new user named `Willem` (almost certainly a developer who insisted on putting his own name in the example data).

The strategy swap happens in one line. No subclassing `Rest`. No factory method. No configuration object. One line. New sous-chef. Service continues.

-----

## Why the Strategy Pattern? The Gusteau Principle 🎩

*“The only thing predictable about life is its unpredictability.”* — Remy, *Ratatouille*

The Strategy Pattern solves a specific, recurring problem: **you have a class that does something, and the way it does that something needs to vary independently of the class itself**.

Without the Strategy Pattern, the alternative looks like this:

```python
# The anti-pattern: if-else in the context
class RestWithoutPattern:
    def __init__(self, host: str, secure: bool = False):
        self.host = host
        self.secure = secure

    def build_url(self, path: str) -> str:
        if self.secure:
            return f"https://{self.host}{path}"
        else:
            return f"http://{self.host}{path}"
```

This works. For exactly two protocols. Then the requirements arrive:

*“We also need to support `ftp://` for the legacy import system.”*
*“Can we add `ws://` for WebSocket connections?”*
*“Marketing wants `mock://` for the demo environment.”*

Every new requirement is an edit to `RestWithoutPattern`. Every edit is a risk. Every edit must be tested against all existing behaviour. The `if-else` grows. The function grows. The tests multiply. Anton Ego arrives and writes a scathing review.

With the Strategy Pattern:

```python
class FtpStrategy(RestStrategy):
    def build_url(self, host: str, path: str) -> str:
        return f"ftp://{host}{path}"

class WebSocketStrategy(RestStrategy):
    def build_url(self, host: str, path: str) -> str:
        return f"ws://{host}{path}"

class MockStrategy(RestStrategy):
    def build_url(self, host: str, path: str) -> str:
        return f"mock://{host}{path}"
```

`Rest` is untouched. Zero lines changed. Zero existing tests broken. Each new strategy is isolated in its own class, tested in isolation, deployed without side effects. The kitchen added three new dishes without moving a single pan on the existing line.

### The Five Benefits, Plated 🍽️

**1. Open/Closed Principle** — The `Rest` class is open for extension (add a new strategy) and closed for modification (never touch `Rest` itself). Gusteau’s menu can grow without demolishing the kitchen.

**2. Single Responsibility** — `Rest` knows how to make HTTP requests. `HttpsStrategy` knows how to build HTTPS URLs. Neither poaches on the other’s territory. In a kitchen this clean, nobody shouts.

**3. Runtime Swappability** — `rest.strategy = HttpsStrategy()` is all it takes. No restart. No factory. The strategy is a value, not a compile-time decision. The chef can change sous-chefs between courses — and does, in our `__main__` block.

**4. Testability** — Unit-testing strategies in isolation requires no running server, no live network, no mock of `Rest`. You instantiate `HttpsStrategy()`, call `build_url("api.example.com", "/health")`, and assert the output. Clean. Simple. The kind of test Colette would approve of.

```python
def test_http_strategy_prepends_http():
    strategy = HttpStrategy()
    url = strategy.build_url("api.example.com", "/health")
    assert url == "http://api.example.com/health"

def test_https_strategy_prepends_https():
    strategy = HttpsStrategy()
    url = strategy.build_url("api.example.com", "/health")
    assert url == "https://api.example.com/health"

def test_rest_uses_injected_strategy():
    rest = Rest(host="api.example.com", strategy=HttpStrategy())
    result = rest.get("/health")
    assert result["url"] == "http://api.example.com/health"

def test_rest_strategy_is_swappable():
    rest = Rest(host="api.example.com", strategy=HttpStrategy())
    rest.strategy = HttpsStrategy()
    result = rest.get("/health")
    assert result["url"].startswith("https://")
```

**5. Dependency Injection** — `Rest` receives its strategy from outside, rather than creating it internally. This is the foundation of testable, loosely coupled code. The chef does not grow his own herbs — he accepts what the sous-chef brings. This also means in a real application you can inject a `MockStrategy` in tests and a `HttpsStrategy` in production without touching the class.

-----

## When to Use It — And When Not to 🤔

*“If you focus on what you left behind, you will never see what lies ahead.”* — Gusteau, *Ratatouille*

The Strategy Pattern is suitable when:

- You have a **family of algorithms** (URL-building, sorting, serialisation, authentication) that differ in implementation but share an interface
- You need to **switch behaviour at runtime** — not just at object creation time
- You want to **avoid conditional bloat** — if the alternatives are an if-else block that keeps growing, a strategy is the right refactor
- The variants need to be **independently testable** and deployable
- You are implementing something like payment processing, logging, notification channels, or connection handling — all classic strategy candidates

The Strategy Pattern is **not** suitable when:

- You only have one algorithm and one will never vary — do not create an interface for its own sake
- The variation is trivial (a parameter, a flag) — a simple function parameter is usually cleaner
- The strategies need to share significant state with each other — at that point the relationship is better modelled differently
- You are writing a quick script that will be deleted on Friday — YAGNI (You Ain’t Gonna Need It) is also a principle

-----

## HTTP vs HTTPS: The Actual Flavour Difference 🔒

Since the restaurant runs two menus, it is worth knowing what is actually different between the tables:

|Feature          |HTTP (Meat-Eaters’ Table)                    |HTTPS (Vegetarians’ Table)                                    |
|-----------------|---------------------------------------------|--------------------------------------------------------------|
|Transport        |Plain TCP — readable by anyone on the network|TLS — encrypted end-to-end                                    |
|Default port     |80                                           |443                                                           |
|Certificate      |None                                         |X.509 certificate from a trusted CA                           |
|Integrity        |None — data can be tampered in transit       |HMAC — tampering is detectable                                |
|Privacy          |None — ISPs, routers, Wolfgangs can read it  |Encrypted — only client and server can read                   |
|Speed (perceived)|Slightly faster (no TLS handshake)           |Negligible difference with HTTP/2 and TLS 1.3                 |
|Use case         |Internal services on trusted private networks|Anything touching the public internet, auth, or sensitive data|

In production today: use HTTPS everywhere. The performance argument against HTTPS died with TLS 1.3 and HTTP/2. The vegetarians were right all along.

In your code: `HttpStrategy` for internal test environments where you genuinely have no TLS (local `http://localhost:8080` style), `HttpsStrategy` for everything else. The Strategy Pattern means you can start with one and upgrade to the other without rewriting the kitchen.

-----

## Extending the Menu: A Third Course 🍰

Want to add a `MockStrategy` for testing — one that does not build a real URL at all, but returns a predictable value for assertions?

```python
class MockStrategy(RestStrategy):
    def build_url(self, host: str, path: str) -> str:
        return f"mock://{host}{path}"
```

Three lines. `Rest` unchanged. Tests now read:

```python
def test_rest_with_mock_strategy():
    rest = Rest(host="test-host", strategy=MockStrategy())
    result = rest.get("/anything")
    assert result["url"] == "mock://test-host/anything"
    # No real HTTP calls. No network. No surprises.
```

Or a `WebSocketStrategy` for a service that uses `ws://`:

```python
class WebSocketStrategy(RestStrategy):
    def build_url(self, host: str, path: str) -> str:
        return f"ws://{host}{path}"
```

The menu grows. The kitchen is unchanged. Linguini would approve. Even Skinner would struggle to find fault. (He would try. He would fail.)

-----

## The Critic’s Table: Anton Ego Weighs In 🍷

*“In many ways, the work of a critic is easy. We risk very little yet enjoy a position over those who offer up their work and their selves to our judgment.”*

Let us be Anton Ego for a moment and consider what this code does **not** do:

The `Rest` class currently returns a plain `dict`. In a real implementation, `get()` and `post()` would call `requests.get(url)` or `httpx.get(url, ...)` and handle responses. The code wisely delegates this to a comment — *“Here you would call requests.get(url), httpx.get(url), etc.”* — because the point of this episode is the Strategy Pattern, not HTTP client configuration.

The `build_url` method does not handle query parameters, authentication headers, or URL encoding. These are deliberate omissions in the spirit of showing the pattern cleanly. A production-grade version might extend `RestStrategy` to also produce headers, or might add a `build_headers()` abstractmethod alongside `build_url()`.

There is no error handling. Again: deliberate. The pattern is the lesson.

These are not flaws. They are boundaries. Gusteau’s kitchen does not put the entire French culinary tradition on one plate. It serves what was ordered, and it serves it well.

-----

## The Full Recipe Card 🗒️

For the kitchen wall, the Strategy Pattern in this code:

```
Pattern:         Strategy
Participants:    RestStrategy (abstract strategy)
                 HttpStrategy (concrete strategy A)
                 HttpsStrategy (concrete strategy B)
                 Rest (context — holds and delegates to strategy)
Variation:       Protocol scheme (http:// vs https://)
Injection:       Constructor injection via @dataclass field
Runtime swap:    Direct attribute assignment (rest.strategy = ...)
Contract:        build_url(host: str, path: str) -> str
Python tools:    ABC + abstractmethod, @dataclass, f-strings, type hints
```

The code is fourteen meaningful lines of production logic and eighteen lines of demonstration. It is clean. It is idiomatic Python. It follows SOLID principles without making a performance of it. Remy would taste it and nod slowly, the way he does when he finds something genuinely worth cooking again.

-----

*“Change is nature, the part that we can influence. And it starts when we decide.”* — Remy, *Ratatouille*

The Strategy Pattern is how we decide — cleanly, reversibly, and without touching the kitchen every time the menu changes. Start with `HttpStrategy`. Upgrade to `HttpsStrategy`. Add `MockStrategy` for tests. Add `WebSocketStrategy` next sprint. The `Rest` class never changes. The kitchen never closes.

Anyone can cook a protocol request. But only a chef with a Strategy Pattern can change the recipe between courses.

-----

**🔗 Resources**

- **Strategy Pattern (Refactoring.Guru)**: [refactoring.guru/design-patterns/strategy](https://refactoring.guru/design-patterns/strategy)
- **Python ABC module**: [docs.python.org/3/library/abc.html](https://docs.python.org/3/library/abc.html)
- **Python dataclasses**: [docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html)
- **PEP 563 — Postponed evaluation of annotations**: [peps.python.org/pep-0563](https://peps.python.org/pep-0563/)

-----

*🍽️ Taste of Protocol — where design patterns are plated, protocols are sauced, and anyone can code.*
