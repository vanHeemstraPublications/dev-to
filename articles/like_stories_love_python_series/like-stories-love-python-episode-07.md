---
title: "Like Stories? Love Python! 📖🐍 Ep.7"
published: false
description: "Learn the Strategy design pattern through Ocean’s Eleven’s contingency planning - because sometimes you need interchangeable algorithms!"
tags: [python, beginners, tutorial, designpatterns]
series: “Like Stories? Love Python!"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-stories-love-python-episode-07.png"
canonical_url: ""
organization: “the-software-s-journey"
---

## Episode 7: The Heist Plans (Strategy Pattern)

Accompanying source code repository: [`Learning Python Object-Oriented`](https://github.com/vanHeemstraSystems/learning-python-object-oriented)

*Welcome back, masterminds. Today we’re talking about planning. About options. About having multiple ways to achieve the same goal and choosing the right approach for the situation. This is contingency planning. This is adaptive intelligence. This is the Strategy Pattern.*

### The One-Line Logline

**“Define a family of interchangeable algorithms, encapsulate each one, and make them swappable at runtime - same interface, different implementations.”**

This is your **playbook**, your **tactical options**, your **algorithm selector**. Instead of hardcoding HOW you do something, you define WHAT you want to do and choose the HOW at runtime. **Flexibility through substitution**.

-----

### The Short Story (The Elevator Pitch)

Picture this: You need to get to Paris. You could fly (fast, expensive), drive (flexible, slower), or take the train (comfortable, moderate speed). The **goal** is the same - Paris. The **strategy** varies based on your constraints: budget, time, comfort preference.

A travel planner - our **context** - doesn’t care HOW you get there. It just knows you need a transportation strategy. You can **swap strategies** based on the situation without changing the planning system.

That’s your **premise**. Same goal, **interchangeable methods**, **runtime selection**.

-----

### The Fictional Match 🎬

**The Contingency Plans from *Ocean’s Eleven* ([IMDB: tt0240772](https://www.imdb.com/title/tt0240772/))**

*Folks, Steven Soderbergh and Ted Griffin created the ULTIMATE Strategy Pattern masterclass.*

Danny Ocean doesn’t have ONE plan to rob three casinos. He has **multiple strategies** ready to deploy based on how the situation unfolds:

- **Plan A**: The primary approach - infiltration through construction crew
- **Plan B**: The backup - if security catches on, shift to the casino floor diversion
- **Plan C**: The contingency - Benedict finds out, deploy the fake SWAT team
- **Plan D**: The ultimate fallback - “We blow the vault”

Each plan is a **different strategy** for achieving the same objective: get into the vault. The **interface** is identical - “execute the plan” - but the **implementation** varies wildly.

And here’s the brilliant cinematic moment - when Rusty asks Danny “What if Benedict changes the security protocols mid-heist?” Danny’s response? “We change strategies mid-execution.” That’s **runtime strategy swapping** right there.

Soderbergh shoots these contingency discussions with **split-screen**, showing parallel timelines - visual representation of **alternate strategies existing simultaneously**. The team isn’t committed to ONE approach. They’re **prepared with options**, ready to **pivot** based on runtime conditions.

The crew meeting scene where they discuss approaches? That’s your **strategy pattern planning session** - evaluating different algorithms for the same problem, understanding the tradeoffs, keeping options available.

**One goal. Multiple approaches. Adaptive execution.**

-----

### The Robert McKee Story Breakdown

Robert McKee writes in “*Story*” about **subplot structures** and **alternative approaches** to achieving the protagonist’s goal. The Strategy Pattern is subplot architecture as code design.

Let’s analyze using McKee’s **dramatic framework**:

- **Protagonist**: The Context (needs to accomplish a task but wants flexibility in HOW)
- **Desire (objective)**: Execute an algorithm without being locked into one implementation - the *want* is results, the *need* is adaptability
- **Antagonistic force**: **Algorithm hardcoding** and **inflexible design** - when you have `if type == "paypal": do_paypal()` scattered everywhere
- **Central conflict**: The **gap between commitment and flexibility** - “I need to choose an approach but I can’t predict all scenarios”
- **Turning point** (The **Inciting Incident**): The moment you realize different situations need different algorithms - credit cards for online, cash for in-person, crypto for international
- **Resolution** (The **Climax**): Strategies are encapsulated, swappable at runtime based on conditions - **tactical flexibility achieved**
- **Controlling idea** (The **Thematic Statement**): *Wisdom comes from having options* - master tacticians don’t have one plan, they have adaptable approaches

This is McKee’s **principle of narrative flexibility**. Great stories have the protagonist trying different approaches until one works. Strategy Pattern is that flexibility built into architecture - don’t hardcode the approach, **parametrize** it.

-----

### Real-World Implementations (The Production Examples)

Strategy Pattern is **everywhere** in professional software. These are your **production deployments**:

- **Payment processing** - CreditCard, PayPal, Crypto, ApplePay - same interface, different strategies
- **Compression algorithms** - ZIP, GZIP, BZIP2 - context chooses based on file type/size
- **Sorting algorithms** - QuickSort, MergeSort, BubbleSort - choose based on data characteristics
- **Route planning** - Shortest, fastest, scenic - different strategies for navigation
- **Validation strategies** - Email, phone, address - different rules, same validation interface
- **Pricing strategies** - Regular, discount, premium, wholesale - runtime pricing logic
- **Authentication** - Password, OAuth, JWT, Biometric - swappable auth strategies
- **Export formats** - PDF, Excel, CSV, JSON - same data, different export strategy

Every time you’ve had **multiple ways to do the same thing** and wanted to **choose at runtime** - that’s Strategy Pattern territory.

-----

### The Minimal Python Example (The Visual Effects Sequence)

*Time to plan this heist. From blueprint to execution, multiple strategies ready.*

Here’s Strategy Pattern in **pure form** - the **heist planning session**:

```python
# ACT ONE: THE STRATEGY INTERFACE - The playbook contract
class PaymentStrategy:
    """
    ABSTRACT STRATEGY - defines the contract.
    Every payment method must implement this interface.
    This is Danny Ocean saying "I don't care HOW you get in,
    but you MUST be able to get in."
    """
    def pay(self, amount):
        """Execute payment - THE INTERFACE all strategies share"""
        raise NotImplementedError("Strategy must implement pay()")

# ACT TWO: CONCRETE STRATEGIES - The different plans
class CreditCardStrategy(PaymentStrategy):
    """
    PLAN A - Credit card payment.
    One approach to achieving the goal.
    """
    def __init__(self, card_number, cvv):
        self.card_number = card_number
        self.cvv = cvv
    
    def pay(self, amount):
        """Execute THIS strategy's algorithm"""
        # Simulate credit card processing logic
        return (f"💳 Paid €{amount} with credit card "
                f"ending in {self.card_number[-4:]}")

class PayPalStrategy(PaymentStrategy):
    """
    PLAN B - PayPal payment.
    Different algorithm, same goal.
    """
    def __init__(self, email):
        self.email = email
    
    def pay(self, amount):
        """Different implementation, same interface"""
        # Simulate PayPal processing
        return f"💰 Paid €{amount} via PayPal ({self.email})"

class CryptoStrategy(PaymentStrategy):
    """
    PLAN C - Cryptocurrency payment.
    Yet another approach to the same problem.
    """
    def __init__(self, wallet_address, currency="BTC"):
        self.wallet = wallet_address
        self.currency = currency
    
    def pay(self, amount):
        """Third strategy, still same interface"""
        # Simulate crypto transaction
        rate = 0.000025  # Simulated BTC conversion
        crypto_amount = amount * rate
        return (f"₿ Paid {crypto_amount:.6f} {self.currency} "
                f"(€{amount}) to wallet {self.wallet[:8]}...")

# ACT THREE: THE CONTEXT - The heist coordinator
class ShoppingCart:
    """
    THE CONTEXT - uses strategies without knowing details.
    This is Danny Ocean - he has a plan, but which plan gets
    executed depends on the situation.
    
    The context delegates to the strategy - COMPOSITION.
    """
    
    def __init__(self, payment_strategy):
        """
        Initialize with a strategy - THE INITIAL PLAN.
        But this can change! Runtime flexibility!
        """
        self._strategy = payment_strategy
        self.items = []
    
    def set_strategy(self, strategy):
        """
        CHANGE STRATEGIES - switch plans mid-execution!
        This is Danny saying "Plan A's compromised, switch to Plan B!"
        """
        print(f"\n🔄 Switching payment strategy...")
        self._strategy = strategy
    
    def add_item(self, item, price):
        """Add items to cart - not strategy-dependent"""
        self.items.append((item, price))
    
    def checkout(self):
        """
        EXECUTE THE CURRENT STRATEGY.
        Context doesn't know HOW payment works,
        it just delegates to the strategy.
        
        This is POLYMORPHISM - same call, different behavior.
        """
        total = sum(price for item, price in self.items)
        print(f"\n🛒 Cart total: €{total}")
        print("Processing payment...")
        
        # DELEGATE to the strategy - let IT handle the HOW
        result = self._strategy.pay(total)
        print(result)
        print("✅ Purchase complete!\n")
        
        return result

# ACT FOUR: THE HEIST EXECUTION - Watch strategies in action
# Create different payment strategies - THE CREW ASSEMBLES
credit_card = CreditCardStrategy("4532-1234-5678-9010", "123")
paypal = PayPalStrategy("willem@example.com")
crypto = CryptoStrategy("1A2B3C4D5E6F7G8H9I", "BTC")

# Create cart with initial strategy - START WITH PLAN A
cart = ShoppingCart(credit_card)

# Add items - normal shopping flow
cart.add_item("Python Book", 45)
cart.add_item("Coffee", 5)
cart.add_item("Laptop", 1200)

# Execute with credit card strategy - PLAN A EXECUTES
cart.checkout()
# Output: 💳 Paid €1250 with credit card ending in 9010

# Situation changes - credit card declined! RUNTIME ADAPTATION!
print("⚠️  Credit card declined! Switching to backup payment...")
cart.set_strategy(paypal)  # SWITCH TO PLAN B

# Retry with different strategy - SAME GOAL, DIFFERENT APPROACH
cart.checkout()
# Output: 💰 Paid €1250 via PayPal (willem@example.com)

# Another customer, different preference - NEW SCENARIO
crypto_cart = ShoppingCart(crypto)  # START WITH PLAN C
crypto_cart.add_item("NFT", 500)
crypto_cart.checkout()
# Output: ₿ Paid 0.012500 BTC (€500) to wallet 1A2B3C4D...

"""
The beauty? 
- ShoppingCart doesn't know payment details
- Strategies are SWAPPABLE at runtime
- Adding new payment methods = new strategy class, zero cart changes
- Each strategy encapsulates its own algorithm
- Same interface (pay), different implementations
"""
```

**The Director’s Commentary:**

Here’s your **production breakdown**, the **technical playbook**:

1. **Strategy Interface** - Defines the contract all strategies must implement. **Polymorphic foundation**.
1. **Concrete Strategies** - Each encapsulates a different algorithm. **Separation of concerns**.
1. **Context** - Uses strategies without knowing their internals. **Loose coupling**.
1. **Runtime Swapping** - Change strategies on the fly based on conditions. **Dynamic adaptation**.
1. **Open-Closed Principle** - Adding new strategies doesn’t modify existing code. **Extensibility**.

-----

### The Pythonic Approach: Functions as Strategies (Elegant Simplification)

*Now let me show you Python’s ELEGANT solution - first-class functions.*

```python
# PYTHONIC APPROACH - strategies as simple functions
def credit_card_payment(amount, card_number):
    """Strategy as a function - no class needed!"""
    return f"💳 Paid €{amount} with card {card_number[-4:]}"

def paypal_payment(amount, email):
    """Another strategy function"""
    return f"💰 Paid €{amount} via PayPal ({email})"

def crypto_payment(amount, wallet):
    """Third strategy function"""
    return f"₿ Paid €{amount} to wallet {wallet[:8]}..."

class SimpleCart:
    """Context using functions as strategies - LIGHTWEIGHT"""
    def __init__(self, payment_function, **payment_config):
        """
        Store the payment function (strategy) and its config.
        Python's first-class functions make this elegant.
        """
        self.payment_function = payment_function
        self.payment_config = payment_config
        self.total = 0
    
    def checkout(self):
        """Execute whichever function was provided"""
        return self.payment_function(self.total, **self.payment_config)

# Usage - cleaner, more Pythonic
cart1 = SimpleCart(credit_card_payment, card_number="4532-1234-5678-9010")
cart1.total = 100
print(cart1.checkout())

cart2 = SimpleCart(paypal_payment, email="willem@example.com")
cart2.total = 50
print(cart2.checkout())

# Or pass strategies at runtime
def process_order(amount, payment_strategy, **config):
    """One function, multiple strategies"""
    return payment_strategy(amount, **config)

# Choose strategy based on conditions
payment_method = "crypto"  # Runtime decision

strategy_map = {
    "card": credit_card_payment,
    "paypal": paypal_payment,
    "crypto": crypto_payment
}

chosen_strategy = strategy_map[payment_method]
result = process_order(200, chosen_strategy, wallet="ABC123")
```

This is **functional programming** meets Strategy Pattern - Python’s **first-class functions** eliminate the need for strategy classes in simple cases.

-----

### When Should You Use Strategy? (The Green Light Decision)

McKee teaches **subplot variety** - different approaches keep narrative interesting. Same with code:

**✅ Green-lit projects (Good use cases):**

- **Multiple algorithms** for same task (Sorting, compression, routing)
- **Runtime selection** based on conditions (Payment type, user preference, environment)
- **Avoiding conditional complexity** - replace giant if/else chains (Each strategy encapsulates its logic)
- **Plugin-style extensibility** - add new strategies without touching old code (Open-closed principle)
- **Testing different approaches** - swap strategies to compare performance (A/B testing algorithms)

**❌ Development hell (When to avoid):**

- **Only one algorithm** exists and always will (No need for flexibility)
- **Strategy is simple** - one-liners don’t need separate classes (Use simple functions)
- **Strategies rarely/never change** at runtime (Just pick one and hardcode it)
- **Overhead exceeds benefit** - creating 5 classes for 5-line functions (Python functions are strategies!)

-----

### The Plot Twist (The Third Act Reversal)

*Here’s the secret about Strategy Pattern that textbooks skip.*

Strategy Pattern can create **class explosion** if you’re not careful. Need 10 different payment methods? That’s 11 classes (10 strategies + 1 context). For simple cases, Python’s **first-class functions** or **lambda expressions** are often better:

```python
# Class explosion approach:
class DiscountStrategy: pass
class NoDiscountStrategy: pass
class PercentageDiscountStrategy: pass
class FixedDiscountStrategy: pass
class VolumeDiscountStrategy: pass
# ... 20 more discount types

# Pythonic approach:
discount_strategies = {
    'none': lambda price: price,
    'percent': lambda price: price * 0.9,
    'fixed': lambda price: max(0, price - 10),
    'volume': lambda price: price * 0.85 if price > 100 else price
}

# Choose and apply
strategy = discount_strategies['percent']
final_price = strategy(100)  # €90
```

But understand Strategy Pattern because:

1. It’s **foundational** to plugin architectures and frameworks
1. **Interview gold** - commonly tested
1. Teaches **polymorphism** and **composition** principles
1. Framework designers use it everywhere (Django forms, pytest fixtures)

-----

**🎯 Key Takeaways (The Trailer Moments):**

- Strategy Pattern **encapsulates interchangeable algorithms**
- **Same interface, different implementations** - runtime selection
- Perfect for **payment systems**, **sorting**, **compression**, **routing**
- *Ocean’s Eleven* perfectly illustrates - **multiple plans ready**
- McKee’s **subplot flexibility** - different approaches to same goal
- Python’s **first-class functions** often replace strategy classes
- Avoid **conditional complexity** - each strategy knows its own logic
- Can **swap strategies** at runtime - tactical flexibility
- **Open-closed principle** - extend without modifying

-----

**🎬 Coming Up Next: (The Post-Credits Tease)**

In Episode 8, our FINALE, we’re executing with the **Command Pattern** - and I’m explaining it through *Westworld*.

How do you encapsulate requests as objects? How do you queue operations? How do you undo/redo actions? How does Ford program the hosts with narrative commands?

We’re talking **action objects**, **undo/redo**, **macro recording**, and why programming conscious beings is actually the Command Pattern at existential scale.

**Requests as objects. History as data. Reality as executable commands.**

This is the final episode, folks. Let’s make it count.

-----

*If these strategies worked for you, hit that ❤️! Share your favorite Strategy Pattern use case in the comments - or tell me about your most complex if/else chain that SHOULD have been strategies. Got heist movie recommendations? I’m listening!*

*You’re not just coding. You’re **planning the perfect heist** with contingencies and adaptability.*

**Cut. That’s a wrap on Strategy. One more to go.**

-----

**Further Reading (The Bonus Features):**

- [Learning Python Object-Oriented - Design Patterns](https://github.com/vanHeemstraSystems/learning-python-object-oriented/tree/main/800) - *The master plan*
- Robert McKee - [*Story: Substance, Structure, Style, and the Principles of Screenwriting*](https://www.mckee.com/story/) - **Subplot structures chapter**
- [Gang of Four Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns) - **Strategy Pattern** (The playbook)
- [Python First-Class Functions](https://realpython.com/python-first-class-functions/) - **Functional strategies**
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID) - **Open-closed principle** explained
- [Ocean’s Eleven on IMDB](https://www.imdb.com/title/tt0240772/) - **Contingency planning masterclass** - Soderbergh’s heist blueprint
