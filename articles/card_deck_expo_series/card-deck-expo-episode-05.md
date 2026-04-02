-----

## title: “🃏 Card Deck — Episode 5: Suits and Hands (Stacks, Tabs & Navigation Layouts)”
published: false
description: “Suits are dealt in sequence or in parallel. Stacks push cards onto a pile; Tabs lay suits side by side. These two navigation patterns cover 90% of all mobile apps.”
tags: expo, exporouter, navigation, tabs
series: Card Deck
cover_image: “”
canonical_url: “”

# 🃏 Card Deck — Episode 5: Suits and Hands (Stacks, Tabs & Navigation Layouts)

> *“In Poker, you are dealt five cards — your hand. In Blackjack, cards are added to your hand one at a time. Two completely different ways of managing the same deck. The cards are identical; the structure changes everything.”*
> — Card games, navigation metaphor.

-----

## 🃏 Two Ways to Arrange the Cards

The 52 cards in your deck can be arranged in fundamentally different ways:

- **A stack** — cards placed on top of each other, one at a time. Lifting a card reveals the one below. Press Back; the current card slides off and the previous one appears. This is a **Stack navigator**.
- **Suits laid side by side** — four separate groups, each selectable from a tab bar at the bottom of the screen. Tapping a tab switches between groups instantly. This is a **Tab navigator**.

Nearly every mobile app you use is some combination of these two patterns. Instagram: tabs for Feed, Search, Reels, Shop, Profile — each tab has its own stack of pushed cards. Email apps: a tab for Inbox, one for Sent, one for Drafts — each backed by a stack.

This episode builds both from scratch.

-----

## 📋 SIPOC — Suits and Hands

|**Suppliers**                      |**Inputs**                                    |**Process**                                               |**Outputs**                                          |**Customers**                                         |
|-----------------------------------|----------------------------------------------|----------------------------------------------------------|-----------------------------------------------------|------------------------------------------------------|
|Expo Router (Stack, Tabs)          |Your `app/` directory structure               |Create `_layout.tsx` with Stack or Tabs → Add screen files|A navigable app with stacked and/or tabbed screens   |Your users, tapping and swiping naturally             |
|React Navigation (underlying)      |Screen files (`index.tsx`, `detail.tsx`, etc.)|Configure screen options (title, header, icons)           |Native-feeling navigation with platform animations   |iOS users (swipe-back) and Android users (back button)|
|Expo Vector Icons                  |Route group directories for tab organisation  |Import Ionicons → Assign to `tabBarIcon`                  |Tab icons that match iOS/Android platform conventions|Users who recognise the icons intuitively             |
|Your app’s information architecture|A clear mental model of your app’s screens    |Nest navigators: Stack inside Tabs, or vice versa         |A navigation structure that maps to user expectations|Your future self, not debugging confusing deep links  |

-----

## 📚 Part 1 — The Stack Navigator

A Stack is the most fundamental navigation pattern in mobile apps. Each new screen is pushed onto a stack; going back pops the top screen off.

### File Structure for a Stack

```
app/
├── _layout.tsx         ← Stack navigator definition
├── index.tsx           ← Screen 1 (URL: /)
├── detail.tsx          ← Screen 2 (URL: /detail)
└── settings.tsx        ← Screen 3 (URL: /settings)
```

### The Stack Layout File

```tsx
// app/_layout.tsx
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen
        name="index"
        options={{ title: 'Home' }}
      />
      <Stack.Screen
        name="detail"
        options={{ title: 'Detail' }}
      />
      <Stack.Screen
        name="settings"
        options={{
          title: 'Settings',
          presentation: 'modal',   // Slides up from bottom on iOS
        }}
      />
    </Stack>
  );
}
```

> 💡 You do not need to explicitly list every screen in `<Stack>`. Files in the directory are automatically treated as valid stack routes. The `<Stack.Screen>` components are optional and only needed when you want to customise options like the title, header visibility, or presentation style.

### Navigating Within a Stack

```tsx
// app/index.tsx
import { Link, useRouter } from 'expo-router';
import { View, Text, Button, StyleSheet } from 'react-native';

export default function HomeScreen() {
  const router = useRouter();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>The Deck</Text>

      {/* Declarative navigation */}
      <Link href="/detail">View Detail Card</Link>

      {/* Imperative navigation */}
      <Button
        title="Open Settings"
        onPress={() => router.push('/settings')}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 24, marginBottom: 20 },
});
```

On iOS, navigating to `/detail` slides the detail screen in from the right. Pressing the back button (or swiping from the left edge) slides it back off. On Android, the transition animates from the bottom. These are **native animations** — no CSS, no JavaScript animation library. Expo Router uses the actual platform navigation primitives.

### Passing Parameters to a Card

Dynamic routes (the `[param].tsx` pattern from Episode 4) let you pass data between cards:

```tsx
// Navigating with a parameter
router.push({ pathname: '/user/[id]', params: { id: '42' } });

// Receiving the parameter
// app/user/[id].tsx
import { useLocalSearchParams } from 'expo-router';
import { Text } from 'react-native';

export default function UserScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return <Text>Showing user: {id}</Text>;
}
```

-----

## 📑 Part 2 — The Tab Navigator

Tabs place multiple suits side by side, each accessible from a persistent bar at the bottom of the screen (iOS convention) or top (Android convention, though bottom is now common on both).

### File Structure for Tabs

```
app/
├── _layout.tsx               ← Root Stack (wraps everything)
└── (tabs)/                   ← Route group: suits in parallel
    ├── _layout.tsx           ← Tab navigator definition
    ├── index.tsx             ← Tab 1: Home (URL: /)
    ├── search.tsx            ← Tab 2: Search (URL: /search)
    ├── library.tsx           ← Tab 3: Library (URL: /library)
    └── profile.tsx           ← Tab 4: Profile (URL: /profile)
```

The `(tabs)` directory is a **route group** — the parentheses mean it does not add `tabs/` to any URL. The root `_layout.tsx` wraps everything in a Stack so the `+not-found` and modal routes work correctly.

### The Root Layout (Stack Wrapping Tabs)

```tsx
// app/_layout.tsx
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="+not-found" />
    </Stack>
  );
}
```

`headerShown: false` on the `(tabs)` screen prevents a duplicate header — the tab navigator has its own header per tab.

### The Tabs Layout

```tsx
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';
import Ionicons from '@expo/vector-icons/Ionicons';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#1a1aff',   // Blue — our Bicycle blue
        tabBarInactiveTintColor: '#666',
        headerShown: true,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, focused }) => (
            <Ionicons
              name={focused ? 'home' : 'home-outline'}
              size={24}
              color={color}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="search"
        options={{
          title: 'Search',
          tabBarIcon: ({ color, focused }) => (
            <Ionicons
              name={focused ? 'search' : 'search-outline'}
              size={24}
              color={color}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="library"
        options={{
          title: 'Library',
          tabBarIcon: ({ color, focused }) => (
            <Ionicons
              name={focused ? 'library' : 'library-outline'}
              size={24}
              color={color}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, focused }) => (
            <Ionicons
              name={focused ? 'person' : 'person-outline'}
              size={24}
              color={color}
            />
          ),
        }}
      />
    </Tabs>
  );
}
```

### Installing Expo Vector Icons

If `@expo/vector-icons` is not already in your project (it is included by default in the template):

```bash
npx expo install @expo/vector-icons
```

Expo manages the exact version compatible with your SDK — use `npx expo install` rather than `npm install` for any Expo-managed package.

-----

## 🔀 Part 3 — Nesting: Stack Inside a Tab

The real power emerges when you nest navigators. Each tab in a Tab navigator can have its own Stack — so navigating within a tab does not leave the tab bar.

```
app/
├── _layout.tsx               ← Root Stack
└── (tabs)/
    ├── _layout.tsx           ← Tab navigator (4 tabs)
    ├── index.tsx             ← Home tab (no stack)
    ├── search.tsx            ← Search tab (no stack)
    └── library/              ← Library tab — has its own stack
        ├── _layout.tsx       ← Stack navigator for library
        ├── index.tsx         ← Library home (URL: /library)
        └── [albumId].tsx     ← Album detail (URL: /library/123)
```

In `app/(tabs)/library/_layout.tsx`:

```tsx
import { Stack } from 'expo-router';

export default function LibraryLayout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ title: 'My Library' }} />
      <Stack.Screen name="[albumId]" options={{ title: 'Album' }} />
    </Stack>
  );
}
```

Now, tapping an album in the Library tab pushes the album detail screen — but the tab bar stays visible at the bottom. Pressing back returns to the library list. Tapping another tab switches tabs, preserving the library stack’s state.

This is the Instagram model: tabs at the bottom, independent stacks within each tab, persistent tab bar throughout.

-----

## 🃏 Hiding a Tab (Without Removing the Route)

Sometimes you want a route to exist — navigable via `router.push()` or a deep link — but not appear in the tab bar. Pass `href: null`:

```tsx
<Tabs.Screen
  name="onboarding"
  options={{
    href: null,   // Not shown in tab bar
    title: 'Onboarding',
  }}
/>
```

The route still exists at `/onboarding`. The tab bar simply does not show a button for it. This is useful for onboarding flows, settings screens, and other destinations that should be reachable but not permanently visible in the navigation chrome.

-----

## 📱 Platform-Specific Tab Styling

iOS 26 and the new Expo Router v6 (included in SDK 54) support **native tabs** — system-level tab bars that use Liquid Glass on iOS 26, native scroll-to-top behaviour, and the full platform tab API. Enable them:

```bash
npx expo install expo-router
```

In `app/(tabs)/_layout.tsx`, import from the native tabs module:

```tsx
import { NativeTabs } from 'expo-router/unstable-native-tabs';
```

> 📌 Native tabs are still marked `unstable-` in SDK 54 — the API may change. For production apps, the JavaScript Tabs (`import { Tabs } from 'expo-router'`) are stable and battle-tested. Native tabs are worth experimenting with for the visual polish they provide on iOS 26 devices.

-----

## 🛸 What’s Next

In **Episode 6**, we add value to the cards themselves — the **Expo SDK**, the library of 100+ production-ready modules that give your app access to hardware features, push notifications, local storage, camera, and more. The navigation is set; now the cards need content.

> *“The deck is arranged. The hand is dealt. Now the cards need to mean something.”*

-----

*🃏 Card Deck is a series about building mobile apps with Expo — from first `npx create-expo-app` to live on the App Store and Google Play.*
