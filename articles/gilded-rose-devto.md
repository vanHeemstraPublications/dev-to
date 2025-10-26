---
title: "The Gilded Rose Kata: Composition Over Inheritance"
published: false
description: "A deep dive into solving the Gilded Rose refactoring kata using composition and the Strategy pattern instead of inheritance"
tags: ["python", "designpatterns", "refactoring", "tutorial"]
series: ""
canonical_url: ""
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/windows-1694867_1920.jpg"
organization: "the-software-s-journey"
---

# The Gilded Rose Kata: Composition Over Inheritance

The [Gilded Rose refactoring kata](https://github.com/emilybache/GildedRose-Refactoring-Kata) is a classic coding exercise that challenges developers to refactor legacy code while adding new functionality. Most solutions reach for inheritance as the primary design pattern, but I want to show you a different approach: **composition over inheritance**. 

In this article, I’ll walk you through my solution that leverages composition and the Strategy pattern to create a more flexible and maintainable design. By the end, you’ll see why composition often leads to better software architecture.

Credit to [Emily Bache’s GitHub repository](https://github.com/emilybache?tab=repositories&q=kata&type=&language=&sort=) for the excellent kata resources.

## The Problem

Here’s the legacy code we need to refactor:

```python
class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            if item.name != "Aged Brie" and item.name != "Backstage passes to a TAFKAL80ETC concert":
                if item.quality > 0:
                    if item.name != "Sulfuras, Hand of Ragnaros":
                        item.quality = item.quality - 1
            else:
                if item.quality < 50:
                    item.quality = item.quality + 1
                    if item.name == "Backstage passes to a TAFKAL80ETC concert":
                        if item.sell_in < 11:
                            if item.quality < 50:
                                item.quality = item.quality + 1
                        if item.sell_in < 6:
                            if item.quality < 50:
                                item.quality = item.quality + 1
            if item.name != "Sulfuras, Hand of Ragnaros":
                item.sell_in = item.sell_in - 1
            if item.sell_in < 0:
                if item.name != "Aged Brie":
                    if item.name != "Backstage passes to a TAFKAL80ETC concert":
                        if item.quality > 0:
                            if item.name != "Sulfuras, Hand of Ragnaros":
                                item.quality = item.quality - 1
                    else:
                        item.quality = item.quality - item.quality
                else:
                    if item.quality < 50:
                        item.quality = item.quality + 1
```

The task is to:

- Refactor this nested conditional nightmare
- Add support for “Conjured” items that degrade twice as fast
- Cannot modify the `Item` class
- Cannot modify the `items` property

## Why Composition Over Inheritance?

Many developers instinctively create subclasses like `NormalItem`, `AgedItem`, `LegendaryItem`, etc. While this works, it has several drawbacks:

### Problems with Inheritance:

1. **Tight coupling**: Subclasses are bound to their parent implementation
1. **Inflexibility**: Hard to change behavior at runtime
1. **Fragile base class problem**: Changes to the parent affect all children
1. **Requirement violation**: The kata says we can’t modify `Item`, but creating subclasses still requires consumers to know which class to instantiate
1. **Limited reusability**: Can’t easily combine behaviors

### Benefits of Composition:

1. **Loose coupling**: Components are independent and interchangeable
1. **Runtime flexibility**: Can swap strategies on the fly
1. **Better testability**: Each strategy can be tested in isolation
1. **Follows SOLID principles**: Especially Open/Closed and Single Responsibility
1. **Easier to extend**: Adding new item types doesn’t require inheritance chains

## The Composition Solution

Let’s build our solution using the Strategy pattern. Each item type gets its own update strategy.

### Step 1: Define the Strategy Interface

```python
from abc import ABC, abstractmethod

class UpdateStrategy(ABC):
    """Abstract strategy for updating item quality."""
    
    @abstractmethod
    def update(self, item):
        """Update the quality and sell_in for an item."""
        pass
    
    def _decrease_quality(self, item, amount=1):
        """Helper to decrease quality with lower bound."""
        item.quality = max(0, item.quality - amount)
    
    def _increase_quality(self, item, amount=1):
        """Helper to increase quality with upper bound."""
        item.quality = min(50, item.quality + amount)
    
    def _decrease_sell_in(self, item):
        """Helper to decrease sell_in."""
        item.sell_in -= 1
```

### Step 2: Implement Concrete Strategies

```python
class NormalItemStrategy(UpdateStrategy):
    """Strategy for normal items that degrade in quality."""
    
    def update(self, item):
        # Normal items degrade by 1 before sell date
        self._decrease_quality(item, 1)
        self._decrease_sell_in(item)
        
        # After sell date, degrade twice as fast
        if item.sell_in < 0:
            self._decrease_quality(item, 1)


class AgedItemStrategy(UpdateStrategy):
    """Strategy for items that improve with age (e.g., Aged Brie)."""
    
    def update(self, item):
        # Aged items increase by 1 before sell date
        self._increase_quality(item, 1)
        self._decrease_sell_in(item)
        
        # After sell date, increase twice as fast
        if item.sell_in < 0:
            self._increase_quality(item, 1)


class LegendaryItemStrategy(UpdateStrategy):
    """Strategy for legendary items that never degrade or expire."""
    
    def update(self, item):
        # Legendary items never change
        pass


class BackstagePassStrategy(UpdateStrategy):
    """Strategy for backstage passes with complex quality rules."""
    
    def update(self, item):
        # Base increase
        self._increase_quality(item, 1)
        
        # Additional increases based on sell_in
        if item.sell_in <= 10:
            self._increase_quality(item, 1)
        if item.sell_in <= 5:
            self._increase_quality(item, 1)
        
        self._decrease_sell_in(item)
        
        # After concert, passes are worthless
        if item.sell_in < 0:
            item.quality = 0


class ConjuredItemStrategy(UpdateStrategy):
    """Strategy for conjured items that degrade twice as fast."""
    
    def update(self, item):
        # Conjured items degrade by 2 before sell date
        self._decrease_quality(item, 2)
        self._decrease_sell_in(item)
        
        # After sell date, degrade twice as fast (4x total)
        if item.sell_in < 0:
            self._decrease_quality(item, 2)
```

### Step 3: Create a Strategy Factory

```python
class StrategyFactory:
    """Factory to create appropriate update strategies based on item name."""
    
    # Strategy mapping
    STRATEGIES = {
        "Aged Brie": AgedItemStrategy,
        "Sulfuras, Hand of Ragnaros": LegendaryItemStrategy,
        "Backstage passes to a TAFKAL80ETC concert": BackstagePassStrategy,
    }
    
    @classmethod
    def get_strategy(cls, item_name: str) -> UpdateStrategy:
        """
        Get the appropriate strategy for an item.
        
        Returns the specific strategy if item name matches,
        ConjuredItemStrategy if name starts with "Conjured",
        otherwise NormalItemStrategy.
        """
        # Check for exact matches
        if item_name in cls.STRATEGIES:
            return cls.STRATEGIES[item_name]()
        
        # Check for conjured items
        if item_name.startswith("Conjured"):
            return ConjuredItemStrategy()
        
        # Default to normal item
        return NormalItemStrategy()
```

### Step 4: Refactor the GildedRose Class

```python
class GildedRose:
    """Inn that manages item quality updates."""
    
    def __init__(self, items):
        self.items = items
        # Assign strategies to items
        self._strategies = {
            item: StrategyFactory.get_strategy(item.name)
            for item in items
        }
    
    def update_quality(self):
        """Update quality for all items using their strategies."""
        for item in self.items:
            strategy = self._strategies[item]
            strategy.update(item)
```

That’s it! Look how clean and simple the `GildedRose` class has become.

## The Advantages in Action

### 1. Easy to Test

Each strategy can be unit tested independently:

```python
def test_normal_item_degrades():
    strategy = NormalItemStrategy()
    item = Item("Normal Item", 10, 20)
    
    strategy.update(item)
    
    assert item.quality == 19
    assert item.sell_in == 9


def test_conjured_item_degrades_twice_as_fast():
    strategy = ConjuredItemStrategy()
    item = Item("Conjured Item", 10, 20)
    
    strategy.update(item)
    
    assert item.quality == 18
    assert item.sell_in == 9
```

### 2. Easy to Extend

Want to add a new item type? Just create a new strategy:

```python
class VolatileItemStrategy(UpdateStrategy):
    """Items that have random quality changes."""
    
    def update(self, item):
        import random
        change = random.randint(-5, 5)
        if change > 0:
            self._increase_quality(item, change)
        else:
            self._decrease_quality(item, abs(change))
        self._decrease_sell_in(item)
```

Then register it in the factory:

```python
STRATEGIES = {
    # ... existing strategies ...
    "Volatile Essence": VolatileItemStrategy,
}
```

### 3. Runtime Flexibility

With composition, you could even change an item’s strategy at runtime if needed:

```python
# Switch an item to a different strategy
gilded_rose._strategies[item] = AgedItemStrategy()
```

This would be impossible with inheritance.

### 4. Better Separation of Concerns

Each strategy has a single responsibility: updating one type of item. The `GildedRose` class has a single responsibility: orchestrating updates. The factory has a single responsibility: creating strategies.

## Comparing Approaches

Let’s put inheritance and composition side by side:

|Aspect           |Inheritance                   |Composition                  |
|-----------------|------------------------------|-----------------------------|
|Adding new types |Create new subclass           |Create new strategy          |
|Changing behavior|Override methods              |Swap strategy                |
|Testing          |Must test full class hierarchy|Test strategies independently|
|Flexibility      |Fixed at compile time         |Can change at runtime        |
|Code reuse       |Through inheritance chain     |Through strategy composition |
|Coupling         |Tight (parent-child)          |Loose (interface-based)      |
|Complexity       |Grows with hierarchy depth    |Stays flat                   |

## When to Use Each Pattern

**Use Inheritance When:**

- You have a clear “is-a” relationship
- The hierarchy is shallow and unlikely to change
- Subclasses genuinely need to override behavior
- You’re modeling domain concepts

**Use Composition When:**

- You need runtime flexibility
- Behaviors might be combined or swapped
- You want to avoid fragile base class problems
- You have many orthogonal variations
- You’re implementing algorithms or strategies

For the Gilded Rose kata, composition is the superior choice because:

1. Items don’t have an “is-a” relationship with update logic
1. We need to handle many item types without modifying core classes
1. The update logic is orthogonal to the item’s identity
1. We might want to add complex item combinations later

## The Complete Solution

Here’s the full refactored solution:

```python
from abc import ABC, abstractmethod

class UpdateStrategy(ABC):
    """Abstract strategy for updating item quality."""
    
    @abstractmethod
    def update(self, item):
        pass
    
    def _decrease_quality(self, item, amount=1):
        item.quality = max(0, item.quality - amount)
    
    def _increase_quality(self, item, amount=1):
        item.quality = min(50, item.quality + amount)
    
    def _decrease_sell_in(self, item):
        item.sell_in -= 1


class NormalItemStrategy(UpdateStrategy):
    def update(self, item):
        self._decrease_quality(item, 1)
        self._decrease_sell_in(item)
        if item.sell_in < 0:
            self._decrease_quality(item, 1)


class AgedItemStrategy(UpdateStrategy):
    def update(self, item):
        self._increase_quality(item, 1)
        self._decrease_sell_in(item)
        if item.sell_in < 0:
            self._increase_quality(item, 1)


class LegendaryItemStrategy(UpdateStrategy):
    def update(self, item):
        pass


class BackstagePassStrategy(UpdateStrategy):
    def update(self, item):
        self._increase_quality(item, 1)
        if item.sell_in <= 10:
            self._increase_quality(item, 1)
        if item.sell_in <= 5:
            self._increase_quality(item, 1)
        self._decrease_sell_in(item)
        if item.sell_in < 0:
            item.quality = 0


class ConjuredItemStrategy(UpdateStrategy):
    def update(self, item):
        self._decrease_quality(item, 2)
        self._decrease_sell_in(item)
        if item.sell_in < 0:
            self._decrease_quality(item, 2)


class StrategyFactory:
    STRATEGIES = {
        "Aged Brie": AgedItemStrategy,
        "Sulfuras, Hand of Ragnaros": LegendaryItemStrategy,
        "Backstage passes to a TAFKAL80ETC concert": BackstagePassStrategy,
    }
    
    @classmethod
    def get_strategy(cls, item_name: str) -> UpdateStrategy:
        if item_name in cls.STRATEGIES:
            return cls.STRATEGIES[item_name]()
        if item_name.startswith("Conjured"):
            return ConjuredItemStrategy()
        return NormalItemStrategy()


class GildedRose:
    def __init__(self, items):
        self.items = items
        self._strategies = {
            item: StrategyFactory.get_strategy(item.name)
            for item in items
        }
    
    def update_quality(self):
        for item in self.items:
            strategy = self._strategies[item]
            strategy.update(item)
```

## Conclusion

The composition-based approach to the Gilded Rose kata demonstrates several important software engineering principles:

1. **Composition over inheritance** leads to more flexible code
1. **Strategy pattern** separates algorithms from the objects that use them
1. **Single Responsibility Principle** keeps classes focused
1. **Open/Closed Principle** makes the code open for extension, closed for modification

While inheritance has its place, composition often provides a more maintainable and extensible solution, especially for behavior-heavy problems like this kata.

The next time you’re tempted to create a deep inheritance hierarchy, ask yourself: “Could composition work better here?” You might be surprised at how often the answer is yes.

## Resources

- [Gilded Rose Kata on GitHub](https://github.com/emilybache/GildedRose-Refactoring-Kata)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Composition vs Inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance)

Happy coding, and remember: favor composition over inheritance!

*What's your take on composition vs inheritance? Have you solved the Gilded Rose kata differently? I'd love to hear your approach in the comments!*
