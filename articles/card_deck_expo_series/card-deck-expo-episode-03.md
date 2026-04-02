-----

## title: “🃏 Card Deck — Episode 3: The Borrowed Practice Deck (Expo Go)”
published: false
description: “Before you print your own deck, you practise with a borrowed one. Expo Go is that borrowed deck — install it on your phone, scan a QR code, and your app appears instantly.”
tags: expo, expogo, mobile, reactnative
series: Card Deck
cover_image: “”
canonical_url: “”

# 🃏 Card Deck — Episode 3: The Borrowed Practice Deck (Expo Go)

> *“Every magician starts by borrowing a deck. Not because they can’t afford their own — but because what matters first is learning the moves, not the props.”*
> — Card magic, fundamentals.

-----

## 🎴 The Borrowed Deck

When you are learning card magic, your first deck is often borrowed. A friend’s deck. The one in the common room. The beat-up Bicycle from the junk drawer. The back design is not yours. The stock is not what you would choose. But it works for learning — and it teaches you the moves before you commit to your own custom-printed deck.

**Expo Go** is the borrowed practice deck.

It is a free app, published by Expo, that runs any standard Expo project instantly — no build step, no App Store submission, no Apple Developer account, no waiting. You scan a QR code; your app appears on your physical phone within seconds. Every time you save a file, the app updates. Hot reload. Instant feedback. Real hardware.

The trade-off: Expo Go only supports **Expo-managed apps using standard SDK features**. The moment you add a custom native module or a third-party plugin that requires native code, Expo Go cannot run your app — you need a development build (Episode 7). For everything else, Expo Go is exactly the borrowed deck you need.

-----

## 📋 SIPOC — The Borrowed Practice Deck

|**Suppliers**                |**Inputs**                              |**Process**                                     |**Outputs**                                       |**Customers**                                       |
|-----------------------------|----------------------------------------|------------------------------------------------|--------------------------------------------------|----------------------------------------------------|
|Apple App Store / Google Play|A physical phone (iOS or Android)       |Install Expo Go → Run `npx expo start` → Scan QR|Your app running on a real device, instantly      |You, seeing your code on hardware for the first time|
|Expo CLI                     |Your running dev server (from Episode 2)|Save a file → Observe hot reload                |Real-time feedback loop without any build step    |Any teammate who also has Expo Go installed         |
|Your local network (Wi-Fi)   |Same Wi-Fi for phone and Mac/PC         |Expo Go connects to Metro bundler via LAN       |Frictionless development iteration                |Your design sense, getting immediate visual feedback|
|The Expo SDK                 |SDK 54-compatible code                  |Expo Go bundles the SDK — no extra install      |Feature-complete preview for standard SDK features|Episodes 3–6 (everything before native modules)     |

-----

## 📲 Step 1 — Install Expo Go

### On iOS

Open the **App Store** on your iPhone or iPad. Search for **Expo Go**. Install the app published by **Expo** (650 SW Mill Avenue, etc.). It is free.

### On Android

Open the **Google Play Store**. Search for **Expo Go**. Install the app published by **Expo**. Also free.

> 📌 **SDK version alignment:** Expo Go on your phone supports a specific Expo SDK version. The version currently available in the stores supports **SDK 54**. Since we created our project with `create-expo-app@latest` (which targets SDK 54 as of early 2026), these are perfectly aligned. If you create a project with SDK 55, you will need a development build — but we are getting ahead of ourselves.

-----

## 🚀 Step 2 — Start the Dev Server

In your project directory:

```bash
npx expo start
```

The terminal will display a QR code and a URL like:

```
› Metro waiting on exp://192.168.1.42:8081
```

This is the address your phone needs to reach the Metro bundler — the development server running on your Mac or PC.

> ⚠️ **Your phone and your computer must be on the same Wi-Fi network.** If they are on different networks, the QR scan will time out. If you are on a network that blocks device-to-device communication (some corporate or hotel Wi-Fi does this), use the **tunnel** option:
> 
> ```bash
> npx expo start --tunnel
> ```
> 
> This routes the connection through Expo’s servers rather than directly over LAN. Slower, but works everywhere.

-----

## 📸 Step 3 — Scan the QR Code

### On iOS

Open the default **Camera app** on your iPhone/iPad. Point it at the QR code in your terminal. A notification banner will appear at the top of your screen: *“Open in Expo Go”*. Tap it.

### On Android

Open the **Expo Go app**. Tap **Scan QR code**. Point at the QR code.

Either way: within a few seconds, the Metro bundler will bundle your JavaScript, send it to the phone, and your app will appear on screen.

You are looking at your code running on real hardware. The borrowed deck is in play.

-----

## ⚡ Step 4 — Experience Hot Reload

Open `app/(tabs)/index.tsx` in VS Code. Find the `<Text>` component that shows the app’s welcome message. Change the text to anything you like:

```tsx
<Text>Hello from my Bicycle blue-back deck!</Text>
```

Save the file (⌘S / Ctrl+S).

On your phone, the app updates automatically — usually within 1–2 seconds. No restart. No rebuild. No QR scan. The borrowed deck shows your latest card immediately.

This is the core development loop with Expo Go:

```
Edit file → Save → See change on phone → Repeat
```

For learning and prototyping, this loop is unbeatable. The feedback is so fast it feels like thinking on paper.

-----

## 🎴 What Expo Go Can and Cannot Do

Understanding the limits of the borrowed deck is as important as understanding its powers.

### Expo Go CAN do:

- Run any app using standard **Expo SDK** modules (camera, notifications, location, filesystem, etc.)
- Hot-reload JavaScript and TypeScript changes instantly
- Render React Native components, Expo Router navigation, animations, and most UI libraries
- Test on **multiple phones simultaneously** — have teammates scan the same QR code
- Run on both iOS and Android from the same dev server, at the same time
- Display your app’s actual fonts, colours, and layouts on real hardware

### Expo Go CANNOT do:

- Run apps that use **custom native modules** (third-party plugins that contain native iOS/Android code not included in the Expo SDK)
- Run apps that use **Config Plugins** that modify native projects (e.g., `expo-camera` with custom settings, Stripe native SDK, Facebook SDK, etc.)
- Test **push notification** behaviour fully (requires a real bundle identifier)
- Run apps targeting **SDK 55** or later (when Expo Go updates to match, this will change)
- Simulate **app store behaviour** (splash screen timing, app icon, permissions dialogs on first launch)

When you hit these limits — and you will, as soon as your app needs something custom native — you graduate to a **development build** (Episode 7). Think of it as getting your own deck.

-----

## 🔄 The Hot Reload Types

Not all changes are equal. Expo handles different types of changes differently:

|Change type         |What happens                                         |Time                       |
|--------------------|-----------------------------------------------------|---------------------------|
|Text, styles, layout|**Fast Refresh** — updates only the changed component|< 1 second                 |
|New component added |**Fast Refresh** — re-renders affected tree          |1–2 seconds                |
|New `import` added  |**Full reload** — rebundles the affected module      |2–5 seconds                |
|New `npm` package   |**Restart required** — `npx expo start` again        |~30 seconds                |
|Change to `app.json`|**Dev server restart** — full project metadata change|~30 seconds                |
|Native module added |**Rebuild required** — cannot use Expo Go anymore    |Minutes (development build)|

Understanding this table saves hours of confusion. When a change does not appear on your phone after saving, the answer is almost always: press `r` in the terminal to force a full reload.

-----

## 🌐 Expo Go on Multiple Platforms Simultaneously

One of Expo’s signature capabilities: you can preview your app on multiple platforms at once.

With `npx expo start` running:

- Press **`a`** — opens an Android emulator (requires Android Studio installed)
- Press **`i`** — opens an iOS simulator (requires macOS + Xcode)
- Press **`w`** — opens the app in your default web browser

And separately, your physical iPhone and Android phone (both running Expo Go) can scan the same QR code and both be live at the same time. You can edit a component and watch it update simultaneously across three or four different surfaces.

This is the cross-platform promise made visible in real time. The same 52 cards, dealt to four tables at once.

-----

## 🛸 What’s Next

In **Episode 4**, we look at the cards themselves — **Expo Router**, the file-based routing system that turns your `app/` directory into a navigable set of screens. Understanding how the cards are arranged is the foundation of everything you build next.

The borrowed deck is in your hand. It is time to learn the arrangement.

> *“Now that you can handle the deck, let’s talk about the order of the cards.”*
> — Expo Router, Episode 4.

-----

*🃏 Card Deck is a series about building mobile apps with Expo — from first `npx create-expo-app` to live on the App Store and Google Play.*
