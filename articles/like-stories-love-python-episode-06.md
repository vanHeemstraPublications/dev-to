---
title: "Like Stories? Love Python! 📖🐍 Ep.6 - The Broadcast (Observer)"
published: false
description: “Learn the Observer design pattern through The Truman Show’s surveillance system - because sometimes everyone needs to know when state changes!“
tags: [python, beginners, tutorial, designpatterns]
series: “Like Stories? Love Python!"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-stories-love-python-episode-06.png"
canonical_url: ""
organization: "the-software-s-journey“
---

## Episode 6: The Broadcast (Observer Pattern)

Accompanying source code repository: [`Learning Python Object-Oriented`](https://github.com/vanHeemstraSystems/learning-python-object-oriented)

*Gather ‘round, storytellers. Today we’re talking about watching. About being watched. About the relationship between one and many - when something changes and everyone needs to know. This is broadcast television. This is social media. This is the Observer Pattern.*

### The One-Line Logline

**“Define a one-to-many dependency where when one object changes state, all dependents are notified automatically - decoupled event notification.”**

This is your **broadcast system**, your **notification infrastructure**, your **publish-subscribe architecture**. When the Subject changes, all Observers receive the update automatically. No polling. No checking. **Instant notification**.

-----

### The Short Story (The Elevator Pitch)

Picture this: A stock ticker changes. Instantly, thousands of traders’ screens update. Millions of portfolio apps refresh. Countless news feeds publish the change. The stock price (the **Subject**) doesn’t know who’s watching or why. It just **broadcasts** the change. Every interested party (the **Observers**) receives the notification automatically.

The stock exchange - our **notification hub** - doesn’t care who subscribes. Traders come and go. Apps attach and detach. The broadcast continues, oblivious to its audience.

That’s your **premise**. One source, many listeners, **automatic propagation**.

-----

### The Fictional Match 🎬

**The Surveillance System from *The Truman Show* ([IMDB: tt0120382](https://www.imdb.com/title/tt0120382/))**

*Folks, Peter Weir and Andrew Niccol created the ULTIMATE Observer Pattern metaphor.*

Truman Burbank is the **Subject** - the one being observed. His life is the **state** that changes. Every moment, every action, every decision.

The 5,000+ cameras hidden throughout Seahaven? Those are **Observers** - attached to the subject, watching, waiting for state changes. When Truman moves, the cameras update. When Truman speaks, microphones capture it. When Truman does ANYTHING, the entire observation system reacts.

But here’s the brilliant part - and this is CRUCIAL to understanding Observer Pattern:

**Truman doesn’t know he’s being watched.** The Subject is **decoupled** from the Observers. He lives his life. The cameras observe. He doesn’t maintain a list of “things watching me.” He doesn’t call `camera1.update()`, `camera2.update()`. He just EXISTS, and the observation happens automatically.

The broadcast control room? That’s the **mediating layer** - it manages which observers are active, routes notifications, handles the subscriber list. When Christof wants a new angle, he attaches a new observer. When a camera breaks, he detaches it. The observation infrastructure handles everything.

That iconic shot of the control room walls - thousands of screens, each one an observer - is the **visual representation** of the pattern. One subject. Countless observers. Automatic synchronization.

And the viewers at home? They’re **meta-observers** - observers of the observation system. It’s Observer Pattern all the way up.

**One life. Infinite watchers. Zero coupling.**

-----

### The Robert McKee Story Breakdown

Robert McKee teaches in “*Story*” about the relationship between **protagonist and ensemble** - how one character’s journey affects everyone around them. Observer Pattern is ensemble storytelling as system architecture.

Let’s break this down using McKee’s **structural analysis**:

- **Protagonist**: The Subject (holds state, changes over time, affects others)
- **Desire (objective)**: Maintain internal state without being coupled to dependents - the *want* is autonomy, the *need* is influence
- **Antagonistic force**: **Tight coupling** and **brittle dependencies** - when objects directly reference each other, changes cascade catastrophically
- **Central conflict**: The **gap between independence and notification** - “I need to notify others without knowing who they are”
- **Turning point** (The **Inciting Incident**): The moment you realize hardcoded notification calls make the system unmaintainable - 50 different objects all checking if something changed
- **Resolution** (The **Climax**): Observers subscribe to the subject, receive automatic notifications when state changes - **decoupled communication achieved**
- **Controlling idea** (The **Thematic Statement**): *Influence transcends awareness* - you can affect others without knowing they exist

This is McKee’s **principle of dramatic irony** - the audience (observers) knows something the protagonist (subject) doesn’t. The subject acts, the observers react, the **dramatic tension** comes from the gap between action and observation.

-----

### Real-World Implementations (The Production Examples)

Observer Pattern is **fundamental** to modern software. These are your **mission-critical applications**:

- **Event systems** - GUI frameworks (button click → multiple handlers fire)
- **Model-View-Controller** - Model changes → Views update automatically
- **Stock tickers / Trading platforms** - Price changes → thousands of subscribers notified
- **Chat applications** - Message sent → all participants receive it
- **Social media feeds** - Post created → followers’ timelines update
- **Configuration management** - Config changes → dependent services reload
- **Database triggers** - Row updated → trigger functions execute
- **Reactive programming** - RxJS, Redux, React hooks - all Observer Pattern

Every **event listener** you’ve written? Observer Pattern. Every **callback** you’ve registered? Observer Pattern. Every `addEventListener()`? **Observer Pattern**.

-----

### The Minimal Python Example (The Visual Effects Sequence)

*Time to build this broadcast system. From concept to production-ready code.*

Here’s Observer Pattern in **textbook form** - the **canonical implementation**:

```python
# ACT ONE: THE SUBJECT - The one being watched
class Subject:
    """
    THE BROADCAST STATION - manages observers, sends notifications.
    This is Truman, unaware he's the center of attention.
    This is the stock price, broadcasting changes.
    """
    
    def __init__(self):
        """
        Start with empty observer list - THE SUBSCRIBER DATABASE.
        Subject doesn't know WHO will observe, just that someone CAN.
        """
        self._observers = []  # The camera network
    
    def attach(self, observer):
        """
        SUBSCRIBE - an observer joins the notification list.
        Like installing a new camera in Seahaven.
        """
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"Observer {observer.name} attached")
    
    def detach(self, observer):
        """
        UNSUBSCRIBE - an observer leaves the notification list.
        Like removing a broken camera.
        """
        try:
            self._observers.remove(observer)
            print(f"Observer {observer.name} detached")
        except ValueError:
            pass
    
    def notify(self, event):
        """
        BROADCAST - tell all observers about the state change.
        This is the KEY METHOD - the notification mechanism.
        
        Subject doesn't care what observers DO with the notification.
        It just sends it. FIRE AND FORGET.
        """
        print(f"\nNotifying {len(self._observers)} observers about: {event}")
        for observer in self._observers:
            observer.update(event)

# ACT TWO: CONCRETE SUBJECT - A real-world example
class StockPrice(Subject):
    """
    ASML STOCK - the thing being observed.
    State changes trigger notifications automatically.
    """
    
    def __init__(self, symbol):
        super().__init__()  # Initialize observer list
        self.symbol = symbol
        self._price = 0
    
    def set_price(self, price):
        """
        STATE CHANGE - the crucial moment.
        When price changes, AUTOMATIC notification happens.
        """
        self._price = price
        # This is the magic - state change triggers notification
        self.notify({
            'symbol': self.symbol,
            'price': price,
            'change': 'price_update'
        })
    
    @property
    def price(self):
        return self._price

# ACT THREE: THE OBSERVERS - The watchers
class Observer:
    """
    BASE OBSERVER - the contract all observers must follow.
    Every camera must have a way to receive the broadcast.
    """
    def update(self, event):
        """RECEIVE NOTIFICATION - must be implemented"""
        raise NotImplementedError

class Investor(Observer):
    """
    INVESTOR - reacts to price changes.
    This is a CAMERA focusing on financial data.
    """
    def __init__(self, name):
        self.name = name
    
    def update(self, event):
        """
        REACT to notification - the observer's response.
        Each observer can react DIFFERENTLY to the same event.
        """
        print(f"  💰 {self.name} notified: {event['symbol']} "
              f"is now €{event['price']}")
        
        # Observer can take action based on the event
        if event['price'] > 900:
            print(f"     → {self.name} considering selling...")
        elif event['price'] < 700:
            print(f"     → {self.name} considering buying...")

class TradingBot(Observer):
    """
    AUTOMATED TRADER - different reaction to same events.
    This is a different CAMERA with different purpose.
    """
    def __init__(self, name, strategy):
        self.name = name
        self.strategy = strategy
    
    def update(self, event):
        """Different observer, different behavior"""
        print(f"  🤖 Bot '{self.name}' analyzing: {event['symbol']} "
              f"at €{event['price']}")
        
        if self.strategy == "momentum" and event['price'] > 850:
            print(f"     → Auto-buying on momentum!")
        elif self.strategy == "contrarian" and event['price'] < 750:
            print(f"     → Auto-buying on dip!")

class NewsService(Observer):
    """
    NEWS AGGREGATOR - publishes updates.
    Yet another type of CAMERA/OBSERVER.
    """
    def __init__(self, name):
        self.name = name
    
    def update(self, event):
        """Publishes news based on price movements"""
        print(f"  📰 {self.name}: Breaking - {event['symbol']} "
              f"moves to €{event['price']}")

# ACT FOUR: THE BROADCAST - Watch the system work
# Create the subject - TRUMAN enters the scene
asml_stock = StockPrice("ASML")

# Create observers - INSTALL THE CAMERAS
investor1 = Investor("Willem")
investor2 = Investor("Alice")
bot = TradingBot("MomentumBot", "momentum")
news = NewsService("TechNews")

# Subscribe observers - CAMERAS GO LIVE
asml_stock.attach(investor1)
asml_stock.attach(investor2)
asml_stock.attach(bot)
asml_stock.attach(news)

# State changes trigger automatic notifications - TRUMAN ACTS
print("\n=== Price Update 1 ===")
asml_stock.set_price(850)

print("\n=== Price Update 2 ===")
asml_stock.set_price(920)

# Observer can unsubscribe - CAMERA GOES OFFLINE
print("\n=== Detaching investor ===")
asml_stock.detach(investor2)

print("\n=== Price Update 3 ===")
asml_stock.set_price(705)
# Note: investor2 no longer receives notification!

"""
Output:
Observer Willem attached
Observer Alice attached
Observer MomentumBot attached
Observer TechNews attached

=== Price Update 1 ===
Notifying 4 observers about: {'symbol': 'ASML', 'price': 850, 'change': 'price_update'}
  💰 Willem notified: ASML is now €850
  💰 Alice notified: ASML is now €850
  🤖 Bot 'MomentumBot' analyzing: ASML at €850
     → Auto-buying on momentum!
  📰 TechNews: Breaking - ASML moves to €850

=== Price Update 2 ===
Notifying 4 observers about: {'symbol': 'ASML', 'price': 920, 'change': 'price_update'}
  💰 Willem notified: ASML is now €920
     → Willem considering selling...
  💰 Alice notified: ASML is now €920
     → Alice considering selling...
  🤖 Bot 'MomentumBot' analyzing: ASML at €920
     → Auto-buying on momentum!
  📰 TechNews: Breaking - ASML moves to €920

=== Detaching investor ===
Observer Alice detached

=== Price Update 3 ===
Notifying 3 observers about: {'symbol': 'ASML', 'price': 705, 'change': 'price_update'}
  💰 Willem notified: ASML is now €705
     → Willem considering buying...
  🤖 Bot 'MomentumBot' analyzing: ASML at €705
  📰 TechNews: Breaking - ASML moves to €705
"""
```

**The Director’s Commentary:**

Here’s your **technical dissection**, the **production breakdown**:

1. **Loose Coupling** - Subject doesn’t know observer details, just that they implement `update()`. **Abstraction layer**.
1. **Dynamic Subscription** - Observers can attach/detach at runtime. **Flexible membership**.
1. **One-to-Many** - Single subject, unlimited observers. **Broadcast topology**.
1. **Push Model** - Subject pushes data to observers. Alternative: observers pull from subject.
1. **Different Reactions** - Each observer can respond differently to the same event. **Polymorphic behavior**.

-----

### The Pythonic Approach: Property Observers (Modern Technique)

*Now let me show you Python’s ELEGANT solution - using properties and callbacks.*

```python
class ObservableProperty:
    """
    Python-style observer using DESCRIPTORS - advanced technique.
    This makes ANY attribute observable automatically.
    """
    def __init__(self, initial_value=None):
        self.value = initial_value
        self.observers = []
    
    def __get__(self, instance, owner):
        return self.value
    
    def __set__(self, instance, new_value):
        old_value = self.value
        self.value = new_value
        # Automatic notification on assignment!
        for callback in self.observers:
            callback(old_value, new_value)
    
    def observe(self, callback):
        """Subscribe a callback - simplified attach()"""
        self.observers.append(callback)

class ModernStock:
    """Stock with observable price - PYTHONIC approach"""
    price = ObservableProperty(0)
    
    def __init__(self, symbol):
        self.symbol = symbol

# Usage - cleaner, more Pythonic
stock = ModernStock("ASML")

# Attach observers as simple functions - no class needed
def investor_reaction(old, new):
    print(f"Price changed: €{old} → €{new}")

def bot_reaction(old, new):
    if new > old:
        print("📈 BUYING on price increase!")

stock.price.observe(investor_reaction)
stock.price.observe(bot_reaction)

# Any assignment triggers observers automatically!
stock.price = 850  # Observers fire
stock.price = 920  # Observers fire again
```

This is **descriptor-based observation** - Python’s elegant take on the pattern.

-----

### When Should You Use Observer? (The Green Light Decision)

McKee teaches about **ensemble dynamics** - when multiple characters need to react to one event. Same principle:

**✅ Green-lit projects (Good use cases):**

- **Event-driven systems** - GUI applications, real-time dashboards (Click → multiple handlers)
- **Model-View separation** - Data changes → UI updates automatically (MVC, MVVM patterns)
- **Pub/Sub systems** - Message queues, event buses (Kafka, RabbitMQ, Redis)
- **State synchronization** - Multiple components need consistent state (Game state, distributed systems)
- **Reactive programming** - Data flows, streams (RxJS, reactive frameworks)

**❌ Development hell (When to avoid):**

- **Simple one-to-one** relationships (Just call the method directly)
- **Performance critical** - notifying thousands of observers has cost (Measure first)
- **Complex notification chains** create hard-to-debug cascades (Observer triggers observer triggers observer…)
- **Memory leaks** from forgetting to detach observers (Objects stay alive because they’re still subscribed)

-----

### The Plot Twist (The Third Act Reversal)

*Here’s what they don’t tell you about Observer Pattern.*

Observers can create **memory leaks** if you’re not careful. An object that subscribes but never unsubscribes keeps a reference in the subject’s observer list. The object can’t be garbage collected. It’s a camera that’s powered off but still wired to the control room.

```python
# MEMORY LEAK scenario:
class LeakyObserver(Observer):
    def __init__(self, subject):
        self.subject = subject
        subject.attach(self)  # Subscribes
    
    # Oops - no unsubscribe when object is done
    # Subject keeps reference forever!

# Fix: Always detach
class GoodObserver(Observer):
    def __init__(self, subject):
        self.subject = subject
        subject.attach(self)
    
    def __del__(self):
        # Clean up when garbage collected
        self.subject.detach(self)
```

Modern Python gives us **WeakRef observers** to prevent leaks:

```python
import weakref

class WeakSubject(Subject):
    """Subject that uses weak references - prevents leaks"""
    def __init__(self):
        self._observers = weakref.WeakSet()
    
    # attach/detach work the same, but references are weak
    # When observer is deleted, it's automatically removed!
```

But understand Observer Pattern because:

1. It’s **fundamental** to GUI frameworks, web sockets, event systems
1. **Reactive programming** is Observer Pattern evolved
1. **Job interviews** test it constantly
1. Understanding it makes you better at **event-driven design**

-----

**🎯 Key Takeaways (The Trailer Moments):**

- Observer Pattern implements **one-to-many dependencies** with automatic notification
- Subject maintains **observer list**, notifies all on state change
- **Loose coupling** - subject doesn’t know observer details
- Perfect for **event systems**, **MVC**, **reactive programming**
- *The Truman Show* perfectly illustrates - **observed without knowing**
- McKee’s **ensemble dynamics** - one action affects many
- Python’s **descriptors** enable elegant property observation
- **Memory leak danger** - always detach when done
- Foundation of **modern reactive architectures**

-----

**🎬 Coming Up Next: (The Post-Credits Tease)**

In Episode 7, we’re strategizing with the **Strategy Pattern** - and I’m explaining it through *Ocean’s Eleven*.

How do you encapsulate algorithms? How do you swap behavior at runtime? How does Danny Ocean have a Plan A, Plan B, and Plan C ready to go?

We’re talking **interchangeable algorithms**, **runtime flexibility**, and why heist planning is actually brilliant software architecture.

**Different plans. Same goal. Maximum adaptability.**

The con is on, folks.

-----

*If this broadcast reached you, hit that ❤️! Share your favorite Observer Pattern implementation in the comments - or your worst memory leak horror story. Got a film that captures a pattern perfectly? Let’s discuss!*

*You’re not just coding. You’re **orchestrating the surveillance network** of your application’s state.*

**Cut to black. Everyone’s watching.**

-----

**Further Reading (The Bonus Features):**

- [Learning Python Object-Oriented - Design Patterns](https://github.com/vanHeemstraSystems/learning-python-object-oriented/tree/main/800) - *The source code*
- Robert McKee - [*Story: Substance, Structure, Style, and the Principles of Screenwriting*](https://www.mckee.com/story/) - **Ensemble dynamics chapter**
- [Gang of Four Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns) - **Observer Pattern** (The definitive guide)
- [Python WeakRef](https://docs.python.org/3/library/weakref.html) - **Preventing memory leaks**
- [Reactive Programming](https://en.wikipedia.org/wiki/Reactive_programming) - **Observer Pattern evolved**
- [The Truman Show on IMDB](https://www.imdb.com/title/tt0120382/) - **Observation without awareness** - Weir’s surveillance masterwork
