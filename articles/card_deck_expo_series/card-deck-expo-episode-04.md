-----

## title: “🃏 Card Deck — Episode 4: The Order of the Cards (Expo Router & File-Based Routing)”
published: false
description: “A deck with no order is just noise. Expo Router arranges your screens into a navigable structure — the app directory is your deck, each file is a card, and the layout files are the rules.”
tags: expo, exporouter, navigation, reactnative
series: Card Deck
cover_image: “”
canonical_url: “”

# 🃏 Card Deck — Episode 4: The Order of the Cards (Expo Router & File-Based Routing)

> *“In a new deck order, the cards are arranged by suit, in sequence, from Ace to King. There is a reason for every position. When you understand the arrangement, you can control everything.”*
> — Card magic, new deck order.

-----

## 📚 The New Deck Order

When a Bicycle deck arrives from the factory, its cards are in **new deck order** — a specific, deliberate sequence: spades Ace through King, then diamonds King through Ace (reversed), then hearts Ace through King, then clubs. Every card in a known position. Every position traceable by logic.

**Expo Router** brings new deck order to your app’s screens.

Every file in your `app/` directory is a card — a screen your users can navigate to. The filename is its position in the deck. The directory structure defines which suit it belongs to. The `_layout.tsx` files are the rules that govern how the cards within a group relate to each other.

This is **file-based routing**: the file structure of your project *is* the navigation structure of your app. No route objects to define. No switch statements. No manual registration. If the file exists, the route exists. If the file is gone, the route is gone.

-----

## 📋 SIPOC — The Order of the Cards

|**Suppliers**                        |**Inputs**                             |**Process**                                       |**Outputs**                                         |**Customers**                                        |
|-------------------------------------|---------------------------------------|--------------------------------------------------|----------------------------------------------------|-----------------------------------------------------|
|Expo Router (built into SDK 54+)     |Your `app/` directory                  |Create `.tsx` files → Expo Router generates routes|Navigable screens mapped to file paths              |Your users, tapping between screens                  |
|React Navigation (underlying library)|`_layout.tsx` files defining navigators|File structure determines navigation hierarchy    |Stack, Tab, and Drawer navigators — auto-wired      |Your app’s navigation graph                          |
|TypeScript (typed routes)            |`[param].tsx` files for dynamic routes |Expo Router generates type-safe `href` values     |No typos in navigation links, caught at compile time|Your future self, not debugging broken navigation    |
|Your creativity                      |Route group directories `(groupname)/` |Group routes without affecting URLs               |Clean URL structure with logical file organisation  |Your teammates, understanding the project at a glance|

-----

## 🗂️ The `app/` Directory — Your Deck

The `app/` directory is the only place where Expo Router looks for routes. Everything inside it is a potential card in your deck. Everything outside it — `components/`, `hooks/`, `constants/` — is invisible to the routing system.

Here is the simplest possible deck:

```
app/
├── _layout.tsx      ← The box (root navigator)
├── index.tsx        ← The Ace (home screen, URL: /)
└── about.tsx        ← The Two (URL: /about)
```

That is it. Two screens. Two files. No router configuration written by hand.

And here is a more realistic deck, matching the default template:

```
app/
├── _layout.tsx              ← Root layout (Stack navigator)
├── (tabs)/                  ← A suit group (tabbed navigation)
│   ├── _layout.tsx          ← Rules for the tabs suit
│   ├── index.tsx            ← Ace of tabs (URL: /)
│   └── explore.tsx          ← Two of tabs (URL: /explore)
└── +not-found.tsx           ← Joker (catches all invalid URLs)
```

Let us understand the notation.

-----

## 🃏 Notation — The Markings on the Cards

Expo Router uses special notation in file and directory names to encode routing behaviour. Like the suit symbols and indices printed on a playing card, these markings carry specific meaning.

### Plain files — Static Routes

```
app/home.tsx        →  URL: /home
app/settings.tsx    →  URL: /settings
app/profile.tsx     →  URL: /profile
```

Simple. The filename is the URL segment. No surprise.

### `index.tsx` — The Ace

```
app/index.tsx              →  URL: /
app/(tabs)/index.tsx       →  URL: / (within the tabs group)
app/products/index.tsx     →  URL: /products
```

An `index.tsx` matches the URL of its parent directory — it is the Ace that wins the position of its suit without adding a segment. The home screen is always `app/index.tsx` (or `app/(tabs)/index.tsx`).

### `[param].tsx` — Dynamic Routes (Wild Cards)

```
app/user/[id].tsx          →  URL: /user/123  or  /user/abc
app/product/[slug].tsx     →  URL: /product/bicycle-blue-deck
```

Square brackets mark **dynamic segments** — the wild card of routing. The value in the URL is captured and made available to the screen as a parameter:

```tsx
// app/user/[id].tsx
import { useLocalSearchParams, Text } from 'expo-router';

export default function UserProfile() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return <Text>User profile for: {id}</Text>;
}
```

### `(groupname)/` — Route Groups (Suits)

```
app/(tabs)/index.tsx        →  URL: /   (NOT /tabs/)
app/(auth)/login.tsx        →  URL: /login  (NOT /auth/login)
```

Parentheses mark a **route group** — a directory that organises files logically but does not add a URL segment. This is how you create the tabs layout without having `/tabs/` appear in every URL. The group is invisible to the URL; it only affects the file structure and the navigation layout.

### `_layout.tsx` — The Rules File

Every directory can have a `_layout.tsx`. This file:

- Defines how the routes within its directory relate to each other (Stack? Tabs? Drawer?)
- Is rendered *before* any route within its directory
- Is where you put shared UI (headers, tab bars, authentication guards)
- Is the equivalent of “these are the rules for this suit”

If there is no `_layout.tsx` in a directory, Expo Router applies a default behaviour (usually a Stack).

### `+not-found.tsx` — The Joker

```
app/+not-found.tsx
```

The `+` prefix marks special Expo Router files. `+not-found.tsx` catches any URL that does not match any other route in your app — the equivalent of a 404 page, rendered whenever a user navigates to a non-existent card. Keep it; do not delete it.

-----

## 🏗️ The Root Layout — The Box

Every Expo Router app needs a `_layout.tsx` directly inside `app/`. This is the **root layout** — the first thing rendered, before any route. It is the box that holds the deck.

```tsx
// app/_layout.tsx
import { Stack } from 'expo-router';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [fontsLoaded] = useFonts({
    'SpaceMono': require('../assets/fonts/SpaceMono-Regular.ttf'),
  });

  useEffect(() => {
    if (fontsLoaded) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded]);

  if (!fontsLoaded) return null;

  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="+not-found" />
    </Stack>
  );
}
```

Notice what happens here:

1. **Splash screen** is held open until fonts are loaded — the deck is not shown until it is ready
1. A **Stack** navigator wraps everything — even if your app primarily uses tabs, the root is usually a Stack (so modals, full-screen overlays, and the `+not-found` route can appear on top)
1. The `(tabs)` group and `+not-found` are registered as named screens in the root Stack

-----

## 🧭 Navigating Between Cards

Expo Router provides two ways to navigate: declaratively with the `<Link>` component, and imperatively with the `useRouter()` hook.

### Declarative — `<Link>`

```tsx
import { Link } from 'expo-router';
import { View, Text } from 'react-native';

export default function Home() {
  return (
    <View>
      <Text>Welcome to the deck</Text>
      <Link href="/about">Go to About</Link>
      <Link href="/user/42">View User 42</Link>
      <Link href={{ pathname: '/product/[slug]', params: { slug: 'bicycle-blue' } }}>
        View Product
      </Link>
    </View>
  );
}
```

### Imperative — `useRouter()`

```tsx
import { useRouter } from 'expo-router';
import { Button } from 'react-native';

export default function Home() {
  const router = useRouter();

  return (
    <Button
      title="Go to Settings"
      onPress={() => router.push('/settings')}
    />
  );
}
```

The `router` object has several navigation methods:

|Method                            |What it does                                 |
|----------------------------------|---------------------------------------------|
|`router.push('/path')`            |Navigate forward — adds to history           |
|`router.replace('/path')`         |Navigate and replace current — no back button|
|`router.back()`                   |Go back one step                             |
|`router.dismiss()`                |Dismiss a modal or pop from stack            |
|`router.setParams({ key: value })`|Update URL params without navigating         |

-----

## 🎯 Type-Safe Routes

Expo Router 3+ (included in SDK 54) generates TypeScript types for all your routes. This means typos in `href` values are caught at compile time rather than at runtime — the navigation equivalent of a spell-checker.

Enable typed routes in `app.json`:

```json
{
  "expo": {
    "experiments": {
      "typedRoutes": true
    }
  }
}
```

Now, passing a non-existent route to `<Link href="...">` is a TypeScript error. You cannot navigate to a card that is not in the deck.

-----

## 🛸 What’s Next

In **Episode 5**, we arrange our cards into **Stacks and Tabs** — the two most common navigation layouts in mobile apps. Stacks are the suits dealt in sequence; Tabs are the suits dealt in parallel. Understanding both unlocks 90% of all mobile navigation patterns.

> *“Knowing where every card is in the deck is the foundation of every trick. Now let’s deal them.”*

-----

*🃏 Card Deck is a series about building mobile apps with Expo — from first `npx create-expo-app` to live on the App Store and Google Play.*
