---
title: "Like LEGO? Love Python! 🧱🐍 Ep.6"
part: 6
published: false
description: "Episode 6: Discover how punq, Python’s unintrusive IoC container, is like a perfectly organised LEGO parts bin — you describe what brick you need, and the bin hands you exactly the right one."
tags: [python, beginners, dependencyinjection, tutorial]
cover_image: ""
series: "Like LEGO? Love Python!"
canonical_url: ""
organization: "the-software-s-journey"
---

# Like LEGO? Love Python! 🧱🐍

## The LEGO Parts Bin (Dependency Injection with punq)

You know that moment when you are in the middle of building a magnificent LEGO castle and you need a 2×4 red brick? A sensible person reaches into their **organised parts bin**, pulls out exactly the right brick, and continues building.

A *less* sensible person — let us call this person Past You — has all the bricks tumbled into one enormous cardboard box. You spend twelve minutes excavating through a geological layer of flat grey pieces before finding the one brick you need. By the time you find it, you have forgotten what you were building.

**Dependency Injection** is the parts bin approach, applied to software. And **punq** is the tidiest parts bin in the Python ecosystem.

-----

## 🧱 Wait. What Even IS Dependency Injection?

Let’s start with the problem it solves, because “dependency injection” sounds like the kind of phrase someone invented to make simple things sound complicated at job interviews.

Imagine you are writing a Python class that sends emails:

```python
class OrderProcessor:
    def __init__(self):
        # 😬 OrderProcessor is building its own email sender
        self.email_sender = SmtpEmailSender(
            host="smtp.gmail.com",
            port=587,
            username="myapp@gmail.com",
            password="hunter2"
        )

    def process(self, order):
        # ... process the order ...
        self.email_sender.send(f"Your order {order.id} is confirmed!")
```

This looks harmless. It is not harmless. The `OrderProcessor` is building its own `SmtpEmailSender` — it knows all the details of SMTP, the credentials, the host. This is like building a LEGO castle where the drawbridge is permanently glued to the tower. You cannot test the tower without the drawbridge working. You cannot swap the drawbridge for a portcullis without surgery.

**Dependency Injection** says: instead of building your own dependencies, *ask for them from outside*:

```python
class OrderProcessor:
    def __init__(self, email_sender: EmailSender):
        # 🎉 Someone else provides the email sender
        self.email_sender = email_sender

    def process(self, order):
        self.email_sender.send(f"Your order {order.id} is confirmed!")
```

Now `OrderProcessor` does not know or care whether it gets an SMTP sender, a mock sender for tests, or a “print to console” sender for development. It just knows it gets *something* that can send an email. The bricks are interchangeable.

But then… who assembles all the pieces? Who provides the `EmailSender` to `OrderProcessor`? Who keeps track of all the dependencies?

That is the **IoC Container**. That is **punq**.

-----

## 📦 The Parts Bin: punq in a Nutshell

**punq** (a portmanteau of “Python” and “Funq”, its inspiration) is an unintrusive IoC container for Python 3.8+. Its design goals are beautiful in their simplicity:

- No global state
- No decorators
- No weird syntax applied to arguments
- Small and simple codebase with 100% test coverage

In other words: it does not try to take over your code. It is a parts bin, not a factory floor.

Install it:

```bash
pip install punq
```

-----

## 🗂️ Step 1: Create the Container

First, create the container at the entrypoint of your application. punq deliberately avoids global state — you create it explicitly rather than importing a magic singleton:

```python
import punq

container = punq.Container()
```

That is your parts bin. Currently empty. Let us fill it.

-----

## 🟥 Step 2: Register Your Bricks

**Registering** a dependency is like placing a brick in the correct compartment of the parts bin and labelling it. When something needs that type of brick, punq knows exactly where to look.

### Registering a plain value

The simplest case — store an arbitrary value under a label:

```python
container.register("connection_string", instance="postgresql://localhost/mydb")
```

Retrieve it later:

```python
conn_str = container.resolve("connection_string")
# "postgresql://localhost/mydb"
```

Like writing “DATABASE” on a compartment and putting the connection string inside.

### Registering an abstract service and its implementation

Here is where it gets interesting. You have an abstract `EmailSender` and a concrete `SmtpEmailSender`:

```python
from abc import ABC, abstractmethod

class EmailSender(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass

class SmtpEmailSender(EmailSender):
    def send(self, message: str) -> None:
        print(f"📧 Sending via SMTP: {message}")

class ConsoleEmailSender(EmailSender):
    def send(self, message: str) -> None:
        print(f"🖥️ Console: {message}")
```

Register which concrete type backs the abstract one:

```python
# In production: use the real SMTP sender
container.register(EmailSender, SmtpEmailSender)
```

Now resolve it:

```python
sender = container.resolve(EmailSender)
sender.send("Hello!")
# 📧 Sending via SMTP: Hello!
```

punq returned a fully constructed `SmtpEmailSender`, assembled automatically. The label on the compartment says `EmailSender`; the brick inside is `SmtpEmailSender`.

-----

## 🔗 Step 3: Automatic Deep Injection

Here is the magic of the parts bin — if the brick you pull out *itself* needs other bricks, punq assembles the whole chain for you. Like reaching in for a LEGO window frame and getting the window, the frame, and the hinges all assembled and ready to clip in.

```python
class ConfigReader(ABC):
    @abstractmethod
    def get_config(self) -> dict:
        pass

class EnvironmentConfigReader(ConfigReader):
    def get_config(self) -> dict:
        import os
        return {
            "greeting": os.environ.get("GREETING", "Hello, world!")
        }

class Greeter:
    def __init__(self, config_reader: ConfigReader):
        # Greeter needs a ConfigReader — punq will provide one
        self.config = config_reader.get_config()

    def greet(self) -> None:
        print(self.config["greeting"])
```

Register both:

```python
container.register(ConfigReader, EnvironmentConfigReader)
container.register(Greeter)
```

Resolve `Greeter` — punq inspects its `__init__` type hints, notices it needs a `ConfigReader`, resolves *that* automatically, and hands everything to `Greeter`’s constructor:

```python
container.resolve(Greeter).greet()
# Hello, world!
```

You did not wire anything together manually. punq read the type hints and did it for you. The parts bin noticed that the castle tower kit needs a drawbridge bracket and included one automatically.

> 💡 **How does punq know what to inject?** It uses Python’s `typing.get_type_hints()` on `__init__`. This is why type annotations matter — they are not just documentation, they are instructions for the container.

-----

## 🔁 Step 4: Transient vs. Singleton Scope

LEGO compartments come in two flavours for our purposes:

**Transient** — every time you reach in, you get a *brand new brick*. Default behaviour.

**Singleton** — every time you reach in, you get *the same brick*. Useful for expensive-to-create objects you want to reuse (database connections, shared state, etc.).

```python
from punq import Scope

# Transient: new instance on every resolve (default)
container.register(EmailSender, ConsoleEmailSender, scope=Scope.transient)

sender_a = container.resolve(EmailSender)
sender_b = container.resolve(EmailSender)
assert sender_a is not sender_b  # ✅ Different instances

# Singleton: same instance every time
container.register(EmailSender, ConsoleEmailSender, scope=Scope.singleton)

sender_c = container.resolve(EmailSender)
sender_d = container.resolve(EmailSender)
assert sender_c is sender_d  # ✅ Same instance
```

You can also pre-register an *already-constructed* object as a singleton:

```python
real_sender = SmtpEmailSender()
container.register(EmailSender, instance=real_sender)
# Now container.resolve(EmailSender) always returns real_sender
assert container.resolve(EmailSender) is real_sender  # ✅
```

This is the “I already built this brick assembly, just store it in the bin” approach.

-----

## 🏭 Step 5: Factory Functions

Sometimes you need logic to *create* the brick — not just a class constructor. punq accepts any callable as a factory:

```python
import os

def make_email_sender() -> EmailSender:
    if os.environ.get("ENV") == "production":
        return SmtpEmailSender()
    return ConsoleEmailSender()

container.register(EmailSender, make_email_sender)
```

Now when punq resolves `EmailSender`, it calls `make_email_sender()` and returns whatever it produces. The factory is the instructions written on the side of the compartment.

-----

## 🗝️ Step 6: Late-Bound Arguments

Sometimes you know most of what you need at registration time, but some arguments only become available later (like a request ID, a user context, or a file path that comes from user input):

**Arguments at resolve time:**

```python
container.register(Greeter, FileWritingGreeter)

# Provide the path only when resolving
greeter = container.resolve(Greeter, path="/tmp/output.txt", greeting="Hello!")
```

**Arguments at registration time:**

```python
# Pin arguments to the registration itself
container.register(Greeter, FileWritingGreeter, path="/tmp/output.txt", greeting="Hello!")
```

The first is like leaving a slot in the compartment for something you will add later. The second is like pre-stuffing the compartment completely before anyone opens the bin.

-----

## 🔢 Step 7: Multiple Implementations — `resolve_all`

Some patterns need *all* registered implementations of a service at once. Think of a chain of authenticators — you want to try each one in turn:

```python
class Authenticator(ABC):
    @abstractmethod
    def matches(self, request: dict) -> bool:
        pass

    @abstractmethod
    def authenticate(self, request: dict) -> bool:
        pass

class BasicAuthAuthenticator(Authenticator):
    def matches(self, request: dict) -> bool:
        return request.get("auth_type") == "basic"

    def authenticate(self, request: dict) -> bool:
        return request.get("password") == "correct-horse-battery-staple"

class ApiKeyAuthenticator(Authenticator):
    def matches(self, request: dict) -> bool:
        return "X-API-Key" in request

    def authenticate(self, request: dict) -> bool:
        return request["X-API-Key"] == "my-secret-key"

# Register both implementations under the same service
container.register(Authenticator, BasicAuthAuthenticator)
container.register(Authenticator, ApiKeyAuthenticator)

# Resolve all of them
authenticators = container.resolve_all(Authenticator)
# → [BasicAuthAuthenticator instance, ApiKeyAuthenticator instance]
```

You can now iterate over all authenticators and apply the first matching one. Multiple bricks in the same compartment, all retrievable at once.

-----

## 🧪 Step 8: Testing is the Payoff

This is where the parts bin approach really earns its keep. Your `OrderProcessor` from the beginning no longer builds its own `SmtpEmailSender`. It accepts an `EmailSender` from outside. In tests, give it a fake one:

```python
# In production code
container = punq.Container()
container.register(EmailSender, SmtpEmailSender)
container.register(OrderProcessor)

# In tests
test_container = punq.Container()

class FakeEmailSender(EmailSender):
    def __init__(self):
        self.sent_messages = []

    def send(self, message: str) -> None:
        self.sent_messages.append(message)

fake_sender = FakeEmailSender()
test_container.register(EmailSender, instance=fake_sender)
test_container.register(OrderProcessor)

processor = test_container.resolve(OrderProcessor)
processor.process(Order(id=42))

assert "order 42 is confirmed" in fake_sender.sent_messages[0].lower()
```

No SMTP server needed. No credentials. No integration test infrastructure. Just a fake brick in the test compartment, and the `OrderProcessor` never knew the difference.

This is the reason dependency injection exists. The castle tower should work perfectly with a cardboard drawbridge during prototyping, and you should only glue on the permanent one when you are ready.

-----

## 🔤 Bonus: String Keys and Forward References

If your dependency is not a class but an arbitrary value — or if you are dealing with forward references — punq supports string keys:

```python
container.register("database_url", instance="sqlite:///dev.db")
container.register("max_retries", instance=3)

db_url = container.resolve("database_url")
# "sqlite:///dev.db"
```

For forward references in type annotations (where the class is not yet defined when the annotation is written), punq also handles those gracefully using `InvalidForwardReferenceError` to tell you when it cannot resolve a string annotation — and you can fix it by pre-registering the named type.

-----

## 🧱 The LEGO Analogy, Complete

|LEGO concept                                |punq concept                                   |
|--------------------------------------------|-----------------------------------------------|
|The parts bin                               |`punq.Container()`                             |
|A labelled compartment                      |A registered service key (type or string)      |
|Placing a brick in a compartment            |`container.register(Service, Implementation)`  |
|Reaching in and grabbing a brick            |`container.resolve(Service)`                   |
|The bin auto-assembles sub-components       |Automatic deep injection via type hints        |
|One brick per grab (new each time)          |`scope=Scope.transient` (default)              |
|The same brick every time                   |`scope=Scope.singleton`                        |
|Pre-assembled piece stored in the bin       |`container.register(Service, instance=obj)`    |
|Custom assembly instructions on the bin wall|`container.register(Service, factory_function)`|
|All bricks of one type, at once             |`container.resolve_all(Service)`               |
|Swapping a test brick during prototyping    |Override registration in a test container      |

The key insight: your classes describe *what brick shapes they need*. The container figures out *which brick to put in the slot* and *how to assemble anything that brick itself needs*. Your components stay loosely coupled. Your tests stay fast and isolated. Your castle stays modular.

-----

## 🚀 Putting It All Together

Here is a small but complete example — a notification system with two channels, a router, and automatic wiring:

```python
import punq
from abc import ABC, abstractmethod

# Abstractions
class NotificationChannel(ABC):
    @abstractmethod
    def notify(self, message: str) -> None:
        pass

class NotificationRouter:
    def __init__(self, channel: NotificationChannel):
        self.channel = channel

    def send(self, message: str) -> None:
        print(f"Routing: {message}")
        self.channel.notify(message)

# Concrete implementations
class SlackChannel(NotificationChannel):
    def notify(self, message: str) -> None:
        print(f"[Slack] {message}")

class EmailChannel(NotificationChannel):
    def notify(self, message: str) -> None:
        print(f"[Email] {message}")

# Wire it up
container = punq.Container()
container.register(NotificationChannel, SlackChannel)
container.register(NotificationRouter)

# Use it
router = container.resolve(NotificationRouter)
router.send("Deployment successful! 🚀")
# Routing: Deployment successful! 🚀
# [Slack] Deployment successful! 🚀

# Swap to email for a test (just change one registration)
test_container = punq.Container()
test_container.register(NotificationChannel, EmailChannel)
test_container.register(NotificationRouter)

test_router = test_container.resolve(NotificationRouter)
test_router.send("Test notification")
# Routing: Test notification
# [Email] Test notification
```

Two different behaviours. One line changed. No castle walls demolished.

-----

## 🎯 Key Takeaways

- **Dependency Injection** = your classes ask for what they need instead of building it themselves
- **IoC Container** = the parts bin that assembles and hands out the right pieces
- **punq** = a tiny, no-magic, no-global-state IoC container for Python
- `container.register(Service, Implementation)` = place a brick in a compartment
- `container.resolve(Service)` = reach in and get the assembled brick
- Type hints on `__init__` drive automatic deep injection
- `Scope.transient` = new brick every time; `Scope.singleton` = same brick always
- Factories, pre-built instances, and `resolve_all` cover advanced scenarios
- The real payoff: **testing becomes trivial** because dependencies are swappable

-----

## 🔗 Resources

- **punq on GitHub**: [github.com/bobthemighty/punq](https://github.com/bobthemighty/punq)
- **punq documentation**: [bobthemighty.github.io/punq](https://bobthemighty.github.io/punq/)
- **punq on PyPI**: [pypi.org/project/punq](https://pypi.org/project/punq/)
- **Previous episode**: *(link to previous episode in the series)*

-----

*Next time in “Like LEGO? Love Python!”: we explore yet another brick in the Python ecosystem. Until then — keep your parts bin organised, your bricks loosely coupled, and your drawbridges swappable!* 🏰🧱
