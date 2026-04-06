---
title: "🃏 Card Deck — Episode 9: The Printing Press (EAS Build — Production Binaries)"
published: false
description: "The proof deck is perfect. Now we run the printing press — EAS Build produces the finished, signed, production-grade binaries ready for the App Store and Google Play."
tags: expo, easbuild, production, ios
series: Card Deck
cover_image: ""
canonical_url: ""
---

# 🃏 Card Deck — Episode 9: The Printing Press (EAS Build — Production Binaries)

> *“The printing press does not improve the design. It replicates it — perfectly, consistently, at scale. The design must be finalised before the press runs.”*
> — Playing card manufacturing.

---

## 🖨️ The Printing Press

The proof deck is done. Your app looks right. It behaves correctly on real hardware. The navigation flows. The SDK features work. The edge cases are handled.

Now we run the **printing press**.

**EAS Build** is Expo’s hosted build service. It takes your project, compiles it to native code on Expo’s servers (iOS builds on Apple Silicon Mac runners; Android builds on Linux GCP runners), signs it with your credentials, and produces a finished binary:

- **iOS**: `.ipa` — the signed archive that Apple accepts for App Store submission
- **Android**: `.aab` — Android App Bundle, the format Google Play requires for store submission (or `.apk` for direct installation)

These are not debug builds. They are not development clients. They are the final, production-grade deck — no developer tools included, optimised for performance, signed with your distribution credentials. They run on any device, not just ones registered in your developer team.

-----

## 📋 SIPOC — The Printing Press

|**Suppliers**                     |**Inputs**                                     |**Process**                                            |**Outputs**                                     |**Customers**                                      |
|----------------------------------|-----------------------------------------------|-------------------------------------------------------|------------------------------------------------|---------------------------------------------------|
|EAS Build (Expo cloud servers)    |Your project with `eas.json` production profile|`eas build --platform all --profile production`        |Signed `.ipa` (iOS) and `.aab` (Android)        |EAS Submit (Episode 10) → App Store and Google Play|
|Apple Developer Program ($99/yr)  |Distribution Certificate + Provisioning Profile|EAS manages credentials automatically                  |A properly signed iOS binary                    |Apple’s review team, then your users               |
|Google Play Console ($25 one-time)|Upload Keystore (EAS-managed)                  |EAS manages the Android keystore                       |A properly signed Android bundle                |Google’s review process, then your users           |
|`eas.json` production profile     |Cleaned, tested, version-bumped codebase       |Cloud build — no Xcode or Android Studio needed locally|Build artefact stored on EAS servers for 90 days|`eas submit` in Episode 10                         |

-----

## ✅ Pre-Build Checklist

Before running the production build, go through this checklist. Like reviewing the proof deck before committing to the print run:

### App Identity

```json
// app.json
{
  "expo": {
    "name": "My Card Deck",
    "slug": "my-card-deck",
    "version": "1.0.0",          // ← Increment this for each release
    "ios": {
      "bundleIdentifier": "com.yourname.mycarddk",   // ← Unique, never changes
      "buildNumber": "1"         // ← iOS build number, increment each build
    },
    "android": {
      "package": "com.yourname.mycarddk",   // ← Unique, never changes
      "versionCode": 1           // ← Android version code, increment each build
    }
  }
}
```

- **`version`**: semantic version shown to users in app stores (“1.0.0”)
- **`buildNumber`** (iOS) / **`versionCode`** (Android): internal incrementing counter. App Store Connect and Google Play both require this to increase with each submission. Set `"autoIncrement": "version"` in your `eas.json` production profile and EAS will manage it automatically.

### Icons and Splash Screen

Your production app needs properly sized icons. Expo handles the resizing from your master image, but the master must be right:

- `assets/images/icon.png` — at least **1024×1024 pixels**, no transparency (iOS App Store requirement), PNG format
- `assets/images/adaptive-icon.png` — the Android adaptive icon foreground, **1024×1024**, can have transparency
- `assets/images/splash.png` — your splash screen image

Run:

```bash
npx expo install expo-splash-screen
```

And ensure your `app.json` `splash` configuration matches what you want users to see on first launch.

### Environment Variables

Production builds should use production API endpoints, not development ones. Set environment variables in `eas.json`:

```json
{
  "build": {
    "production": {
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.myapp.com",
        "EXPO_PUBLIC_ENVIRONMENT": "production"
      }
    },
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "env": {
        "EXPO_PUBLIC_API_URL": "http://localhost:3000",
        "EXPO_PUBLIC_ENVIRONMENT": "development"
      }
    }
  }
}
```

In your code, access these with `process.env.EXPO_PUBLIC_API_URL`. Variables prefixed with `EXPO_PUBLIC_` are bundled into the binary and available at runtime. Other variables are only available during the build process itself.

-----

## ⚙️ The Production `eas.json` Profile

A complete production build configuration:

```json
{
  "cli": {
    "version": ">= 10.0.0"
  },
  "build": {
    "production": {
      "autoIncrement": "version",
      "ios": {
        "resourceClass": "m-medium"
      },
      "android": {
        "buildType": "app-bundle"
      },
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.myapp.com"
      }
    },
    "preview": {
      "extends": "production",
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "resourceClass": "m-medium"
      }
    }
  }
}
```

Key decisions in the production profile:

- **`autoIncrement: "version"`** — EAS automatically increments `buildNumber` and `versionCode` before each production build
- **`android.buildType: "app-bundle"`** — produces `.aab` (required for Google Play; smaller download, dynamic delivery)
- **`ios.resourceClass: "m-medium"`** — uses M-series Mac build runners (faster and more compatible with latest Xcode)

The **preview** profile is useful for sharing a production-like binary with testers before App Store submission — no developer tools, production code, but distributed internally via a link rather than through the stores.

-----

## 🔑 Credentials — The Signing Authority

Before building for production, you need signing credentials. EAS can generate and manage these for you:

### iOS — Distribution Certificate & Provisioning Profile

```bash
eas credentials
```

Select:

1. **iOS → Distribution Certificate** → Generate new (EAS stores it securely on their servers)
1. **iOS → Provisioning Profile** → Generate new App Store distribution profile

EAS stores your credentials on its servers, associated with your Expo account. If you lose your local machine, the credentials are safe. If you prefer to manage credentials yourself, you can export them at any time.

### Android — Upload Keystore

```bash
eas credentials
```

Select **Android → Keystore** → Generate new keystore.

> ⚠️ **Back up your Android keystore.** If you lose it, you cannot update your app on Google Play — you would have to publish a new app with a different package name. EAS stores it, but export a backup copy to somewhere safe (`eas credentials --platform android` → Export).

-----

## 🚀 Running the Production Build

```bash
# Build for both platforms
eas build --platform all --profile production

# Or build one platform at a time
eas build --platform ios --profile production
eas build --platform android --profile production
```

EAS CLI confirms the build configuration and credentials, then uploads your project to the build servers. A link to the build detail page appears immediately — you can follow the logs there or close your terminal.

**Typical build times:**

- Android: 5–12 minutes
- iOS: 8–18 minutes (Xcode compilation takes time even on M-series hardware)

On the free EAS plan, builds queue behind paid subscribers during busy periods. On a paid plan, you get higher build concurrency and priority access.

-----

## 📊 The Build Dashboard

Visit [expo.dev](https://expo.dev) → Your project → **Builds** to see all your builds:

- Build status (queued, in progress, finished, errored)
- Platform and profile
- Build duration
- Downloadable artefacts
- Full build logs (essential for diagnosing failures)

Builds are stored for **90 days**. After that, they are deleted — you will need to rebuild if you want to resubmit. Tag important builds or submit promptly.

-----

## ✅ Verifying the Production Build

Before submitting to the stores, install the production binary on a test device to verify it behaves correctly without the development client:

### Android Preview Build

The `preview` profile in `eas.json` produces a production binary (no dev tools) distributed internally — you can install it directly from a QR code or link:

```bash
eas build --platform android --profile preview
```

Install on your phone via the link EAS provides. Test everything: all screens, all features, push notifications, deep links.

### iOS TestFlight

For iOS, production builds go to **Apple TestFlight** — Apple’s official beta distribution platform. We cover the full submission in Episode 10, but the testing flow is:

1. Submit iOS production build to TestFlight via EAS Submit
1. Wait 10–15 minutes for TestFlight to process the build
1. Add internal testers in App Store Connect
1. Install TestFlight on your phone, accept the invite, install the build

TestFlight builds are identical to App Store builds — the only difference is the distribution method. Testing via TestFlight is the closest possible representation of the App Store user experience.

-----

## 🔧 When Builds Fail

Build failures are a normal part of app development. Common causes and solutions:

|Error                           |Cause                                                    |Fix                                                           |
|--------------------------------|---------------------------------------------------------|--------------------------------------------------------------|
|`Xcode version not found`       |SDK requires newer Xcode                                 |Check `ios.image` in `eas.json` or let EAS auto-select        |
|`Gradle build failed`           |Dependency conflict or incompatible native module version|Check the build logs for the specific error; update the module|
|`Provisioning profile not found`|Expired or missing certificate                           |Run `eas credentials` and regenerate                          |
|`Bundle ID already in use`      |Another app has your bundle identifier                   |Choose a unique reverse-domain identifier                     |
|`Version code must be greater`  |Android versionCode not incremented                      |Increment `versionCode` in `app.json` or use `autoIncrement`  |
|`Duplicate app icon`            |`icon.png` not matching expected dimensions              |Ensure 1024×1024, no transparency on iOS                      |

When in doubt, the full build log in the EAS dashboard has the exact error with the stack trace. Most errors are version mismatches resolved by checking the module’s compatibility table and using `npx expo install` to get the right version.

-----

## 🃏 The Deck Is Printed

Your production binary is ready. The cards are printed. The finish is right. The ink is dry.

In **Episode 10**, we send the box to the card shop — submitting to the App Store and Google Play, configuring over-the-air updates for fast post-launch iteration, and automating the whole pipeline with EAS Workflows.

The printing press has done its job. The courier is waiting.

> *“The cards are printed. Now find them a table.”*

-----

*🃏 Card Deck is a series about building mobile apps with Expo — from first `npx create-expo-app` to live on the App Store and Google Play.*
