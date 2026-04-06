---
title: "🃏 Card Deck — Episode 10: The Card Shop (EAS Submit, OTA Updates & Workflows)"
published: false
description: "The deck is printed. The courier delivers it to the card shop — the App Store and Google Play. And when a card needs replacing? OTA updates swap it silently, without reprinting the whole deck."
tags: expo, eassubmit, otaupdates, reactnative
series: Card Deck
cover_image: ""
canonical_url: ""
---

# 🃏 Card Deck — Episode 10: The Card Shop (EAS Submit, OTA Updates & Workflows)

> *“The card manufacturer does not sell direct. They supply the card shops — the retailers who put decks in the hands of players around the world. Your job is to get the deck on the shelf.”*
> — Playing card distribution.

---

## 🏪 The Card Shop

The production binary exists. The deck is printed. Now it needs to reach the players — the users who will open the App Store or Google Play, search for your app, and tap **Get** or **Install**.

The card shops are:

- **Apple App Store** — iOS and iPadOS users globally
- **Google Play Store** — Android users globally

Getting a deck on the shelf requires:

1. **Submission** — delivering the binary to the store for review
1. **App Store review** — Apple and Google inspect the deck (Apple: 1–3 days; Google: hours to days)
1. **Release** — the deck goes live on the shelf
1. **Ongoing updates** — new versions when cards need replacing

This episode covers the full distribution pipeline — from submission to over-the-air updates to automation — so that shipping future versions costs minutes, not days.

-----

## 📋 SIPOC — The Card Shop

|**Suppliers**          |**Inputs**                        |**Process**                                              |**Outputs**                                         |**Customers**                           |
|-----------------------|----------------------------------|---------------------------------------------------------|----------------------------------------------------|----------------------------------------|
|Apple App Store Connect|Signed `.ipa` from EAS Build      |`eas submit --platform ios` → TestFlight → App Review    |Your app live on the App Store                      |iOS users, globally                     |
|Google Play Console    |Signed `.aab` from EAS Build      |`eas submit --platform android` → Internal track → Review|Your app live on Google Play                        |Android users, globally                 |
|EAS Update (OTA)       |JavaScript/TypeScript changes only|`eas update --branch production --message "Fix"`         |Users receive the update silently on next app launch|All your existing users, within minutes |
|EAS Workflows          |`eas.json` + workflow YAML        |Define CI/CD pipeline → Trigger on git push              |Automated build → submit → update pipeline          |Your future self, shipping in 3 commands|

-----

## 📱 Part 1 — Submitting to the App Stores

### Prerequisites

**For iOS:**

- Apple Developer Program membership ($99/year) — provides access to App Store Connect
- An app record in App Store Connect (create it at [appstoreconnect.apple.com](https://appstoreconnect.apple.com))
- Your app’s App Store Connect App ID (a 10-digit number found in App Store Connect)

**For Android:**

- Google Play Console account ($25 one-time fee)
- An app record created in Google Play Console
- Your first APK uploaded manually at least once (Google Play API requirement; every subsequent submission can be automated)

### Configure `eas.json` for Submission

```json
{
  "submit": {
    "production": {
      "ios": {
        "ascAppId": "1234567890"   // Your App Store Connect App ID
      },
      "android": {
        "track": "internal",       // Start with internal track, promote to production
        "serviceAccountKeyPath": "./google-service-account.json"
      }
    }
  }
}
```

### Submit

```bash
# Submit iOS (will open a browser for Apple credentials if not configured)
eas submit --platform ios --profile production

# Submit Android
eas submit --platform android --profile production

# Submit both simultaneously
eas submit --platform all --profile production
```

EAS Submit:

1. Picks up the latest production build from EAS Build (or prompts you to select one)
1. Uploads it to App Store Connect (iOS) or Google Play Console (Android)
1. Places it in the queue: TestFlight for iOS, the selected track for Android

-----

## 🍎 iOS — TestFlight to App Store

The iOS submission pipeline has two stages:

**Stage 1: TestFlight (internal and external beta)**

After `eas submit` completes, visit App Store Connect → TestFlight. Your build will appear after 10–15 minutes of processing. Add internal testers (up to 100 Apple IDs in your developer team) immediately — no additional review required. For external testers (up to 10,000 via email invite), TestFlight requires a **Beta App Review** (usually < 24 hours).

**Stage 2: App Store submission**

When you are satisfied with testing, go to App Store Connect → Your App → **+ Version**. Select the TestFlight build, fill in:

- Release notes (What’s New)
- Screenshots (required for each device size — iPhone 6.5”, iPad 12.9”, etc.)
- App description and keywords
- Privacy policy URL
- Age rating

Submit for review. Apple’s review team inspects your app (1–3 business days on average). If approved, it goes live. If rejected, you receive detailed rejection reasons and can resubmit after fixing the issue.

-----

## 🤖 Android — Track Promotion

Google Play uses **tracks** to control rollout:

|Track             |Who sees it                 |Review required              |
|------------------|----------------------------|-----------------------------|
|**Internal**      |Up to 100 testers (by email)|No review                    |
|**Closed (Alpha)**|Specific testers            |No review                    |
|**Open (Beta)**   |Anyone who opts in          |No review                    |
|**Production**    |All users globally          |Google review (hours to days)|

Start by submitting to the Internal track:

```json
"android": { "track": "internal" }
```

Test thoroughly. Then promote to production via the Google Play Console UI:

1. Production track → **Create new release**
1. Select the build from a previous track
1. Add release notes
1. Set rollout percentage (start at 10% to monitor crash rates before full release)
1. Submit for review

-----

## ⚡ Part 2 — Over-the-Air Updates

Here is the most powerful card in the Expo deck.

Once your app is live in the stores, users download the current binary. Normally, changing anything requires:

1. Building a new binary (15–20 minutes)
1. Submitting for App Store review (1–3 days)
1. Users manually updating (or waiting for auto-update)

**Over-the-air (OTA) updates** bypass all of this for JavaScript/TypeScript changes. Because React Native apps are a native shell (the binary in the store) running a JavaScript bundle (the actual app logic), you can replace the JavaScript bundle independently of the native shell.

EAS Update delivers a new JavaScript bundle to users the next time they open the app — no App Store submission, no review, no wait.

### What OTA Updates CAN Change

- Any TypeScript / JavaScript code
- All screen layouts, styles, and components
- Business logic, API calls, data processing
- Navigation structure (routes, layouts)
- Strings, copy, translations
- Bug fixes in non-native code
- Feature flags and configuration

### What OTA Updates CANNOT Change

- Native modules (anything compiled into the binary)
- Permissions (`Info.plist`, `AndroidManifest.xml`)
- App icon, splash screen, bundle identifier
- SDK version or native dependencies

### Configure `expo-updates`

```bash
npx expo install expo-updates
```

In `app.json`:

```json
{
  "expo": {
    "updates": {
      "url": "https://u.expo.dev/your-project-id",
      "enabled": true,
      "fallbackToCacheTimeout": 0
    },
    "runtimeVersion": {
      "policy": "appVersion"
    }
  }
}
```

The **runtime version** ties a JavaScript bundle to the native binary version it was built with. If you push a new native binary (new SDK version, new native module), users on old binaries will not receive bundles built for the new binary. This prevents crashes from version mismatches.

### Sending an OTA Update

```bash
# Fix a bug in your TypeScript code, then:
eas update --branch production --message "Fix checkout total calculation"
```

EAS bundles your current JavaScript code and pushes it to all users on the `production` branch. Users receive the update silently on the next app launch — or immediately if you configure `updates.checkOnLaunch`.

### Branches for Staged Rollouts

Use update channels to manage staged releases:

```bash
# Push to preview branch for testing
eas update --branch preview --message "New onboarding flow"

# When satisfied, promote to production
eas update --branch production --message "New onboarding flow"
```

Users running builds linked to the `preview` branch (your testers’ installation) receive the update first. If it breaks something, you do not promote to `production`. The bug never reaches your users.

-----

## 🔄 Part 3 — EAS Workflows (The Automated Printing Press)

Manually running `eas build` and `eas submit` works. But the real velocity gain comes from automating the entire pipeline with **EAS Workflows**.

Create a workflow file at `.eas/workflows/build-and-submit.yml`:

```yaml
name: Build and Submit to Stores

on:
  push:
    branches:
      - main

jobs:
  build_android:
    name: Build Android
    type: build
    params:
      platform: android
      profile: production

  build_ios:
    name: Build iOS
    type: build
    params:
      platform: ios
      profile: production

  submit_android:
    name: Submit Android to Play Store
    type: submit
    needs: [build_android]
    params:
      profile: production
      build_id: ${{ needs.build_android.outputs.build_id }}

  submit_ios:
    name: Submit iOS to TestFlight
    type: submit
    needs: [build_ios]
    params:
      profile: production
      build_id: ${{ needs.build_ios.outputs.build_id }}
```

With this workflow, every push to the `main` branch automatically:

1. Builds the Android `.aab` and iOS `.ipa` in parallel
1. Submits both to their respective stores after successful builds

Your entire shipping process becomes:

```bash
git add .
git commit -m "Release 1.1.0: new card shuffling feature"
git push origin main
```

And then: wait, review in App Store Connect, click **Release**. That is the entire deployment process.

-----

## 🃏 The Full Lifecycle — One Deck, End to End

Looking back at the complete card deck lifecycle we have built over ten episodes:

|Stage           |Episode|Card Analogy          |Command / Action                 |
|----------------|-------|----------------------|---------------------------------|
|Concept         |1      |Understanding the deck|Read this                        |
|Setup           |2      |Unboxing              |`npx create-expo-app@latest`     |
|Preview         |3      |Borrowed deck         |Expo Go + QR scan                |
|Routing         |4      |Card arrangement      |Files in `app/`                  |
|Navigation      |5      |Suits and hands       |Stack + Tabs layouts             |
|Features        |6      |Face cards            |`npx expo install`               |
|Dev build       |7      |Custom back design    |`eas build --profile development`|
|Device testing  |8      |Real table            |`npx expo start --dev-client`    |
|Production build|9      |Printing press        |`eas build --profile production` |
|Distribution    |10     |Card shop             |`eas submit` + OTA updates       |

-----

## 🔭 Beyond the Basic Deck — What Comes Next

The deck is in the card shop. Users are playing. But a well-maintained app never stops evolving. Some directions worth exploring from here:

- **Expo Router API Routes** — server-side endpoints within your Expo project (edge functions, streaming, AI)
- **Expo Hosting** — deploy your Expo web app to Expo’s CDN with one command (`eas deploy`)
- **EAS Insights** — monitor crash rates, user populations, and update adoption
- **Local modules with Expo Modules API** — write custom native code (Swift/Kotlin) without leaving the Expo ecosystem
- **Monorepo setup** — share code between your Expo app and a web frontend or backend
- **expo-updates rollbacks** — instantly roll back a bad OTA update to the previous working version

-----

## 🎴 The Final Card

Ten episodes. One complete app lifecycle. From `npx create-expo-app` to a live app in two card shops, with an automated pipeline that ships new versions on every `git push`.

The Bicycle blue-back deck — your app — is on the shelf. Sealed. Cellophaned. Ready to be opened by the players who have been waiting for it.

> *“The best card trick is the one the audience did not see coming. The best app is the one users cannot imagine living without.”*
> — This series, final card.

-----

*🃏 Card Deck is a series about building mobile apps with Expo — from first `npx create-expo-app` to live on the App Store and Google Play.*
