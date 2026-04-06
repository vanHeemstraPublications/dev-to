---
title: "🃏 Card Deck — Episode 2: Unboxing the Deck (Prerequisites & Project Creation)"
published: false
description: "Every deck starts in a sealed tuck box. This episode covers what you need installed before you can deal a single card — Node.js, the Expo CLI, and your first create-expo-app."
tags: expo, reactnative, nodejs, setup
series: Card Deck
cover_image: ""
canonical_url: ""
---


# 🃏 Card Deck — Episode 2: Unboxing the Deck (Prerequisites & Project Creation)

> *“Before you can do a single card trick, you need to be able to do a perfect riffle shuffle. Not impressive. Not magic. Just mechanics. But everything else depends on it.”*
> — Card magic, fundamentals.

## 📦 The Sealed Tuck Box

A brand new Bicycle deck arrives sealed. Cellophane wrapper. Paper tuck box. A small flap you lift to slide out the cards. Nothing impressive yet — just the packaging that makes everything else possible.

Setting up an Expo project is the same. There is a sequence of mechanical steps — install this, configure that, run this command — that are not magic, not impressive, and entirely necessary. Everything else in this series depends on them being done correctly.

Let us go through the unboxing.

-----

## 📋 SIPOC — Unboxing the Deck

|**Suppliers**          |**Inputs**                                    |**Process**                                        |**Outputs**                                |**Customers**                             |
|-----------------------|----------------------------------------------|---------------------------------------------------|-------------------------------------------|------------------------------------------|
|Node.js project        |Your development machine (Mac, Windows, Linux)|Install Node.js → Install Expo CLI → Create project|A working Expo project scaffold            |Every subsequent episode                  |
|npm / npx              |A terminal / shell                            |Run `npx create-expo-app` → Choose template        |`app/`, `components/`, `package.json` ready|You, in Episode 3                         |
|Expo project template  |VS Code (or your editor of choice)            |Understand the file structure                      |A mental model of where things live        |Your future self, adding cards to the deck|
|Expo account (expo.dev)|15 minutes                                    |Create Expo account → Login via CLI                |`npx expo whoami` returns your username    |EAS Build and Submit (Episodes 9–10)      |

-----

## ✅ Prerequisites

### 1. Node.js (LTS version)

Expo requires Node.js. Install the **LTS (Long-Term Support)** version from [nodejs.org](https://nodejs.org) — not the “Current” version, which may have rough edges that cause tooling issues.

Verify after installation:

```bash
node --version   # Should be v20.x or v22.x
npm --version    # Should be 10.x or higher
```

> 💡 **On macOS**, the easiest path is via [Homebrew](https://brew.sh): `brew install node@22`. On Windows, use the official installer. On Linux, use your package manager or [nvm](https://github.com/nvm-sh/nvm) for version management.

### 2. A Code Editor

VS Code is the standard choice for React Native and Expo development. Install it from [code.visualstudio.com](https://code.visualstudio.com). The extensions worth adding immediately:

- **ESLint** — catches errors before you run anything
- **Prettier** — consistent code formatting
- **React Native Tools** — IntelliSense for React Native
- **Expo Tools** — app.json schema validation and autocompletion

### 3. An Expo Account

Create a free account at [expo.dev/signup](https://expo.dev/signup). You need this for EAS Build and Submit later. The free plan is generous — enough for any learning project or small app.

### 4. EAS CLI (Install Now, Use Later)

```bash
npm install -g eas-cli
```

We will not use this until Episode 9, but installing it now means it is ready when we need it.

Verify:

```bash
eas --version
```

-----

## 🃏 Creating Your First Deck

With prerequisites in place, create your first Expo project. Open your terminal, navigate to wherever you keep your projects, and run:

```bash
npx create-expo-app@latest my-card-deck
```

This command:

1. Downloads the latest `create-expo-app` scaffolding tool
1. Creates a new directory called `my-card-deck`
1. Installs all dependencies
1. Sets up the default template with **Expo Router**, TypeScript, and the Expo SDK

> 📌 **SDK version note:** As of early 2026, `create-expo-app@latest` creates an SDK 54 project by default. If you want SDK 55 (with native tabs and other cutting-edge features), use:
> 
> ```bash
> npx create-expo-app@latest my-card-deck --template default@sdk-55
> ```
> 
> For this series, SDK 54 is our target — it is stable, widely supported, and works with Expo Go on physical devices.

The command takes a minute or two. When it finishes, you have a complete Expo project ready to run.

-----

## 🗂️ The Tuck Box Contents — Understanding the File Structure

Navigate into your project:

```bash
cd my-card-deck
```

Open it in VS Code:

```bash
code .
```

Here is what you will see, and what it means in card deck terms:

```
my-card-deck/
├── app/                    ← The 52 cards: your screens and routes
│   ├── _layout.tsx         ← The box rules: root navigation layout
│   ├── (tabs)/             ← A suit: a group of tabbed screens
│   │   ├── _layout.tsx     ← Rules for this suit
│   │   ├── index.tsx       ← The Ace of this suit: home screen
│   │   └── explore.tsx     ← Another card in the suit
│   └── +not-found.tsx      ← The Joker: catches invalid routes
├── assets/                 ← The back design: images, fonts, icons
│   └── images/
│       ├── icon.png        ← Your app icon (the back design)
│       └── splash.png      ← Your splash screen
├── components/             ← Reusable card components
├── constants/              ← Theme colours, typography
├── hooks/                  ← Reusable React hooks
├── app.json                ← The tuck box label: app name, bundle ID, version
├── package.json            ← The card catalogue: dependencies and scripts
├── tsconfig.json           ← TypeScript configuration
└── eas.json                ← EAS Build profiles (the printing press settings)
```

Let us look at the most important files in detail.

### `app.json` — The Tuck Box Label

```json
{
  "expo": {
    "name": "my-card-deck",
    "slug": "my-card-deck",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/images/icon.png",
    "scheme": "mycarddeckscheme",
    "userInterfaceStyle": "automatic",
    "splash": {
      "image": "./assets/images/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.yourname.mycarddk"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/images/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.yourname.mycarddk"
    }
  }
}
```

The key fields:

- **`name`** — what appears under your app icon on the device’s home screen
- **`slug`** — URL-safe identifier, used by Expo services
- **`version`** — your app version, shown in the app stores
- **`bundleIdentifier`** (iOS) / **`package`** (Android) — the unique reverse-domain identifier that Apple and Google use to distinguish your app from every other app on Earth. Set these once; changing them later is painful. Use your own domain, reversed: `com.vanheemstra.mycarddk`.
- **`scheme`** — deep link URL scheme (e.g. `mycarddeckscheme://`) — required for Expo Router

### `app/(tabs)/index.tsx` — The Ace of the Default Suit

Open `app/(tabs)/index.tsx`. This is the first screen your users see. Right now it shows the default Expo “Hello World” content. In later episodes, you will replace this with your own cards.

### `package.json` — The Card Catalogue

The key scripts:

```json
{
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "test": "jest --watchAll"
  }
}
```

`expo start` is the command you will run most often. It starts the Metro bundler and development server, and presents a QR code for Expo Go (Episode 3) or your development build (Episode 8).

-----

## 🔐 Log In to Expo

Before we can use any Expo cloud services, log in:

```bash
npx expo login
```

Enter your expo.dev credentials. Verify:

```bash
npx expo whoami
# → yourusername
```

You are now authenticated. The card manufacturer knows who you are.

-----

## 🎯 Your First Run

Start the development server:

```bash
npx expo start
```

You will see the Metro bundler start up and display a QR code in your terminal, along with a menu of options:

```
› Metro waiting on exp://192.168.1.x:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)

› Press a │ open Android
› Press i │ open iOS simulator
› Press w │ open web

› Press j │ open debugger
› Press r │ reload app
› Press m │ toggle menu
```

In **Episode 3**, we use Expo Go to scan this QR code and see your app on a physical phone for the first time. For now, just confirm that the server starts without errors. If it does — the deck is unboxed. The cards are in your hands.

-----

## 🃏 The State of the Deck

|Requirement     |Status                          |
|----------------|--------------------------------|
|Node.js LTS     |✅ Installed                     |
|EAS CLI         |✅ Installed globally            |
|Expo account    |✅ Created and authenticated     |
|Project scaffold|✅ Created with `create-expo-app`|
|Dev server      |✅ Starts cleanly                |

The tuck box is open. The cards are shuffled and ready. In **Episode 3**, we deal the first hand.

> *“The deck is ready. Now you need somewhere to play.”*
> — This series, transitioning to Expo Go.

-----

*🃏 Card Deck is a series about building mobile apps with Expo — from first `npx create-expo-app` to live on the App Store and Google Play.*
