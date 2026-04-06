---
title: "🃏 Card Deck — Episode 7: Your Custom Back Design (Development Builds)"
published: false
description: "The borrowed practice deck was fine for learning. Now you print your own — a development build is your custom Bicycle deck with your back design, your native modules, your bundle identifier."
tags: expo, devbuild, easbuild, reactnative
series: Card Deck
cover_image: ""
canonical_url: ""
---

# 🃏 Card Deck — Episode 7: Your Custom Back Design (Development Builds)

> *“Every serious card worker eventually orders custom decks. The back design is theirs. The card stock is theirs. The finish is exactly what they need. It costs more and takes longer than borrowing a deck — but it handles exactly right.”*
> — Custom playing card production.

---

## 🎨 The Custom Back Design

Expo Go — the borrowed practice deck — served us well through Episodes 3–6. We learned the moves. We built screens. We understood routing and navigation. We integrated SDK modules.

But the borrowed deck has limits. The moment you add `expo-camera`, or a push notification plugin, or any SDK module that contains native code not pre-bundled into Expo Go, the borrowed deck cannot play the card. The camera module compiles into native code that must be part of the binary — it cannot be hot-loaded from JavaScript.

A **development build** is the solution. It is:

- Your own compiled app (`.ipa` for iOS, `.apk` for Android)
- With your bundle identifier (`com.yourname.myapp`) embedded
- With all your native modules compiled in
- With the `expo-dev-client` library included — which provides the same QR-scan hot-reload workflow as Expo Go, but for your custom binary

You install the development build once on your phone. Then you iterate on JavaScript/TypeScript code exactly as before — save a file, see the change on the phone within seconds. You only rebuild when you change native code (add a new module, change a permission, upgrade the SDK).

This is your **custom Bicycle deck with your own back design**. It handles exactly right. It is entirely yours.

-----

## 📋 SIPOC — Your Custom Back Design

|**Suppliers**            |**Inputs**                                                    |**Process**                                          |**Outputs**                                             |**Customers**                                                      |
|-------------------------|--------------------------------------------------------------|-----------------------------------------------------|--------------------------------------------------------|-------------------------------------------------------------------|
|EAS Build (Expo cloud)   |Your Expo project with native modules                         |`eas build --profile development`                    |A `.ipa` (iOS) or `.apk` (Android) dev client binary    |Your physical phone (and teammates’ phones)                        |
|Your Expo account        |Apple Developer account (iOS) or Google Play account (Android)|EAS manages signing credentials automatically        |A signed, installable development build                 |The development workflow — fast iteration on real hardware         |
|`expo-dev-client` library|`eas.json` with a `development` profile                       |Install build on device → Scan QR to connect to Metro|Hot-reload dev environment inside your own native binary|Episodes 8 onward                                                  |
|`eas.json` configuration |A physical phone for testing                                  |Daily: `npx expo start --dev-client`                 |QR code connecting to your personal dev binary          |Teammates who install the same dev build and share the Metro server|

-----

## 🛠️ Step 1 — Install `expo-dev-client`

```bash
npx expo install expo-dev-client
```

This adds the development client layer to your project — the UI and networking code that allows your development build to scan a QR code and connect to a Metro bundler, exactly like Expo Go.

Import it at the top of your root layout to initialise it:

```tsx
// app/_layout.tsx
import 'expo-dev-client';  // Must be the very first import
import { Stack } from 'expo-router';
// ...rest of your layout
```

-----

## 📝 Step 2 — Configure `eas.json`

If your project does not yet have an `eas.json`, create it by running:

```bash
eas build:configure
```

This creates `eas.json` with three default profiles. For our purposes, the development profile is what matters:

```json
{
  "cli": {
    "version": ">= 10.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "resourceClass": "m-medium"
      },
      "android": {}
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {
      "autoIncrement": "version"
    }
  },
  "submit": {
    "production": {}
  }
}
```

The key settings in the `development` profile:

- **`developmentClient: true`** — tells EAS this is a dev client build (not a production build; never submitted to the app stores)
- **`distribution: "internal"`** — makes the build directly installable without going through the App Store or Google Play
- **`ios.resourceClass: "m-medium"`** — uses an M-series Mac runner for iOS builds (faster than Intel runners)

-----

## 🔑 Step 3 — Log In and Configure Credentials

Log in to EAS CLI if you have not already:

```bash
eas login
```

### iOS (Apple Developer Account Required)

Building for iOS requires an **Apple Developer Program membership** ($99/year). If you have one, EAS can manage your signing certificates and provisioning profiles automatically:

```bash
eas credentials
```

Follow the prompts. EAS will:

1. Ask you to authenticate with your Apple ID
1. Generate a Distribution Certificate (or use an existing one)
1. Create a Provisioning Profile for your bundle identifier
1. Register your test device’s UDID for internal distribution

> 💡 **No Apple Developer account yet?** Build for Android first — it requires no paid account. Come back to iOS when you are ready to invest in the membership. The Android development build gives you the same fast iteration workflow.

### Android (No Account Required for Development)

Android development builds use a debug keystore automatically managed by EAS. No Google Play account needed until you want to publish to the store (Episode 10).

-----

## 🖨️ Step 4 — Build the Development Client

**For Android:**

```bash
eas build --platform android --profile development
```

**For iOS:**

```bash
eas build --platform ios --profile development
```

**For both simultaneously:**

```bash
eas build --platform all --profile development
```

After running the command, EAS uploads your project to Expo’s build servers. For a small app, the queue wait is typically a few minutes; the build itself takes 5–15 minutes.

EAS CLI will output a link to the build dashboard where you can watch the build logs in real time. You can also safely close your terminal — the build happens in the cloud, not on your machine.

When complete, EAS provides:

- A **QR code** to install the build directly on your phone
- A **download link** for the `.ipa` / `.apk` file
- A link to the build in your EAS dashboard

-----

## 📱 Step 5 — Install the Development Build

### Android

Scan the QR code from the EAS build output, or download the `.apk` and install it directly. Android allows direct APK installation (sideloading) — no Play Store required.

You may need to enable **“Install unknown apps”** in your Android settings for your browser or file manager. This is a one-time permission.

### iOS

For iOS internal distribution builds, you need to install via one of:

1. **EAS build page** — visit the EAS dashboard on your iPhone’s Safari browser and tap “Install”
1. **Expo Orbit** — a macOS menu bar app that installs builds on connected devices with one click
1. **Apple TestFlight** — for preview/production builds (Episodes 9–10)

> 📌 Your iPhone’s UDID must be registered in your Apple Developer team’s provisioning profile before the internal distribution build will install. EAS handles this automatically when you run `eas credentials` and select “Register new device”.

-----

## ⚡ The Daily Development Workflow

Once the development build is installed on your phone, you never need to rebuild for JavaScript-only changes. The daily workflow is:

```bash
# Start the dev server in dev-client mode
npx expo start --dev-client
```

A QR code appears — but this time, instead of opening Expo Go, you open **your installed development build** on your phone and scan the QR code. The Metro bundler connects; your app loads with full hot-reload capability.

From here, the loop is identical to Expo Go:

```
Edit TypeScript → Save → See change on phone in 1–2 seconds → Repeat
```

### When You Need to Rebuild

Rebuild your development build only when you:

- ✅ Add a new native SDK module (`npx expo install some-module`)
- ✅ Change a Config Plugin in `app.json`
- ✅ Change iOS or Android permissions
- ✅ Upgrade the Expo SDK version

You do **NOT** need to rebuild when you:

- ❌ Change TypeScript / JavaScript code
- ❌ Change styles, layouts, or component logic
- ❌ Add/edit screens in `app/`
- ❌ Update non-native npm packages
- ❌ Change colours, fonts, or UI logic

This distinction matters — rebuilding takes 5–15 minutes; hot-reload takes 1–2 seconds. Understanding where the boundary lies keeps your iteration loop fast.

-----

## 👥 Sharing the Dev Build with Teammates

Your development build is shareable. Any teammate can:

1. Install the same `.apk` / `.ipa` from the EAS build page
1. Run `npx expo start --dev-client` on their machine
1. Scan the QR code from their Metro server

> 🃏 **The card deck analogy:** you have printed enough copies of your custom back-design deck for the whole team. Everyone is playing with the same deck. Each player (Metro server) deals their own hand.

On iOS, teammates’ UDIDs need to be registered in the provisioning profile. Add them via `eas device:create` and rebuild once.

-----

## 🛸 What’s Next

The development build is installed. The custom deck is printed. In **Episode 8**, we deal it at the real table — running the dev build on a physical phone and walking through the complete iteration workflow, including debugging tools and common pitfalls.

> *“The deck is printed. The finish is exactly right. Now we sit at the table and play.”*

-----

*🃏 Card Deck is a series about building mobile apps with Expo — from first `npx create-expo-app` to live on the App Store and Google Play.*
