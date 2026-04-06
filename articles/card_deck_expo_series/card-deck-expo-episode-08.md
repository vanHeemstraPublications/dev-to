---
title: "🃏 Card Deck — Episode 8: Dealing at the Real Table (Dev Build on a Physical Phone)"
published: false
description: "The custom deck is printed and in your hands. This episode is the complete workflow for running your development build on a real phone — connection, hot-reload, debugging, and common pitfalls."
tags: expo, devbuild, physicaldevice, reactnative
series: Card Deck
cover_image: ""
canonical_url: ""
---

# 🃏 Card Deck — Episode 8: Dealing at the Real Table (Dev Build on a Physical Phone)

> *“Practising card handling in your bedroom is one thing. Dealing at a real card table, with real players, is where you discover what you actually know.”*
> — Card handling, the reality gap.

---

## 🃏 The Real Table

Emulators and simulators are useful. They run on your Mac, they respond quickly, and you can use them without a physical device. But they are the equivalent of practising in your bedroom — the conditions are controlled, and many things that matter on real hardware simply do not show up.

Real hardware has:

- Actual camera hardware (not a simulated green screen)
- Real network conditions (cellular, weak Wi-Fi, switching between networks)
- Real touch sensitivity and gesture recognition
- Real performance characteristics (the iPhone 12 handles your animations differently from the iPhone 16 Pro Max)
- Real permission dialogs that look and behave as users will actually see them

This episode is about dealing at the real table — running your development build from Episode 7 on a physical phone, establishing the daily iteration workflow, and knowing how to debug when things go wrong.

-----

## 📋 SIPOC — Dealing at the Real Table

|**Suppliers**                             |**Inputs**                                           |**Process**                            |**Outputs**                                                |**Customers**                                     |
|------------------------------------------|-----------------------------------------------------|---------------------------------------|-----------------------------------------------------------|--------------------------------------------------|
|Your physical phone                       |Development build installed (from Episode 7)         |`npx expo start --dev-client` → Scan QR|Your app running on real hardware with hot-reload          |You, catching real-device bugs before users do    |
|Your development machine (Mac Mini M4 Pro)|Same Wi-Fi for phone and Mac                         |Open dev build → Scan QR → Iterate     |A fast feedback loop — save file, see change in 1–2 seconds|Your design instincts, calibrated on real hardware|
|Metro bundler                             |Your project’s TypeScript/React Native code          |Edit → Save → Fast Refresh             |Real-device hot-reload without rebuild                     |Every hour of development from here to Episode 10 |
|Expo DevTools                             |Error messages, console.log output, network inspector|Debug via browser DevTools → Fix → Save|A debugged, hardware-tested app                            |App Store and Play Store users (Episodes 9–10)    |

-----

## 🚀 The Daily Start Command

With your development build installed on your phone, your daily workflow begins with one command:

```bash
npx expo start --dev-client
```

The `--dev-client` flag tells Metro to serve the bundle to your custom development build rather than Expo Go. You will see output like:

```
› Metro waiting on exp://192.168.1.42:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)

› Press a │ open Android
› Press i │ open iOS simulator  
› Press w │ open web

› Press j │ open debugger
› Press r │ reload app
```

> 💡 Despite saying “Expo Go” in the QR prompt, scanning with your development build app — not Expo Go — is what you want. Open your **installed development build** on your phone; it will show a QR scanner or a connect screen. Scan the QR from there.

-----

## 📱 Connecting Your Phone

### Scenario A — Same Wi-Fi (Standard)

Your phone and Mac are on the same Wi-Fi network. Expo uses **LAN networking** — the fastest path. Open your development build, tap **Scan QR code**, and scan the code in your terminal. Connection happens within 3–5 seconds.

### Scenario B — Different Networks or Restricted Wi-Fi

Some networks (corporate, hotel, certain home setups with AP isolation) block device-to-device communication. Metro cannot reach the phone via LAN.

**Solution — Tunnel mode:**

```bash
npx expo start --dev-client --tunnel
```

This routes the connection through Expo’s servers rather than directly over LAN. Slower to connect initially (10–30 seconds), but works on any network. Hot-reload is slightly slower but still practical.

### Scenario C — USB Connection (Android Only)

For maximum reliability and speed — particularly useful on congested networks or when debugging network-sensitive features:

```bash
# Connect Android phone via USB cable, enable USB debugging in Developer Options
adb reverse tcp:8081 tcp:8081

# Then start normally
npx expo start --dev-client
```

The `adb reverse` command maps port 8081 on your phone to port 8081 on your Mac. Metro traffic flows over the USB cable — zero network dependency, fastest possible connection.

-----

## 🔄 The Hot-Reload Loop in Practice

Once connected, the iteration loop is:

1. **Open** `app/(tabs)/index.tsx` in VS Code
1. **Edit** something — change a string, adjust a style, modify a component
1. **Save** (`⌘S`)
1. **Watch** your phone — the change appears within 1–2 seconds via Fast Refresh

Fast Refresh preserves component state where possible. If you are on a screen and you change only the JSX/styles of the current screen’s component, the screen updates *in place* — you do not lose your scroll position or form state.

If you need a full reload (clearing all state and re-rendering from scratch), press `r` in the terminal.

-----

## 🐛 Debugging Tools

### 1. Console Output — Your Terminal

All `console.log()`, `console.warn()`, and `console.error()` output from your JavaScript code appears in your terminal where Metro is running. This is the first place to look when something goes wrong.

```tsx
// In any screen or component:
console.log('User ID:', userId);
console.warn('This might be a problem:', someValue);
console.error('Something broke:', error);
```

### 2. In-App Developer Menu

**iOS:** Shake the device (or press `Ctrl+D` in the simulator)
**Android:** Shake the device (or press `Ctrl+M` in the emulator)

The developer menu appears with options:

- **Reload** — full JavaScript bundle reload
- **Go to Home** — return to the dev build’s home screen (useful for testing deep links)
- **Toggle Performance Monitor** — shows FPS and memory usage
- **Toggle Element Inspector** — tap any element to see its styles and props

### 3. React DevTools

With Metro running, press `j` in the terminal to open the **JavaScript debugger** in your browser. This connects Chrome DevTools to your running app — you can:

- Set breakpoints in your TypeScript code
- Inspect the component tree
- Monitor network requests
- Profile performance

For React-specific component inspection (props, state, hooks), install React Native DevTools separately and open it with:

```bash
npx react-devtools
```

### 4. Error Overlays

When your JavaScript code throws an unhandled error, Expo displays a red error overlay on the phone screen with:

- The error message
- A stack trace with file names and line numbers
- A button to reload

Most errors are caught before they reach users (in a production build, errors are handled more gracefully). In development, the red overlay is your friend — it tells you exactly where the problem is.

-----

## 📡 Network Requests — Checking API Calls

If your app makes API requests and something is not working, inspect network traffic directly from Metro. With the debugger open (`j` in terminal), the **Network** tab in Chrome DevTools shows all `fetch()` calls, their status codes, request and response bodies.

Alternatively, use **Flipper** (standalone desktop app) for a more complete native debugging experience including network inspection, Redux state, and database queries.

-----

## ⚠️ Common Pitfalls and Their Playing Card Fixes

|Symptom                                  |Likely cause                       |Fix                                             |
|-----------------------------------------|-----------------------------------|------------------------------------------------|
|QR code scans but nothing happens        |Phone and Mac on different networks|Use `--tunnel` mode                             |
|“Unable to connect to development server”|Metro bundler not running          |Restart with `npx expo start --dev-client`      |
|App opens to blank white screen          |JavaScript error on startup        |Check terminal for error logs                   |
|Camera / Notifications not working       |Module requires native rebuild     |Did you rebuild after installing the module?    |
|Changes not appearing after save         |Fast Refresh limitation            |Press `r` in terminal for full reload           |
|“Reload” button loops or hangs           |Stale Metro cache                  |Run `npx expo start --dev-client --clear`       |
|Different UI on iOS vs Android           |Platform-specific default styles   |Add explicit styles; avoid assuming defaults    |
|Build installed but won’t open (iOS)     |UDID not in provisioning profile   |Register device via `eas device:create`, rebuild|

-----

## 🧪 Testing on Multiple Devices Simultaneously

Your development build can be installed on multiple phones. Once installed, each phone can scan the QR code from your terminal and connect to the same Metro server. Edit a file; all connected devices update simultaneously.

This is invaluable for:

- Checking that your layout works on different screen sizes (iPhone SE vs iPhone 16 Pro Max)
- Verifying iOS and Android behaviour simultaneously
- Testing features that require two devices (real-time messaging, multiplayer, etc.)

-----

## 🎯 The Expo Orbit Alternative

[**Expo Orbit**](https://expo.dev/orbit) is a macOS menu bar app that streamlines development build management:

- Install builds on connected devices with one click (no QR scanning)
- Launch simulators/emulators without opening Android Studio or Xcode
- Browse and install recent EAS builds directly
- See which builds are available for which platforms

Install it from [expo.dev/orbit](https://expo.dev/orbit) or via Homebrew:

```bash
brew install expo-orbit
```

It is especially useful for iOS — instead of navigating to the EAS build page on your iPhone’s Safari browser, Expo Orbit detects the connected device and installs the build directly.

-----

## 🃏 The State of the Deck

You now have a complete, real-hardware development workflow:

|Step                                                  |Status|
|------------------------------------------------------|------|
|Development build installed on physical device        |✅     |
|Hot-reload iteration via `npx expo start --dev-client`|✅     |
|Console output and error overlays                     |✅     |
|Native debugging tools available                      |✅     |
|Multiple device testing                               |✅     |

The deck is dealing at the real table. The cards respond correctly in real hands.

In **Episode 9**, we take the deck to the printing press — EAS Build, where we produce the finished, production-grade `.ipa` and `.aab` binaries ready for the App Store and Google Play.

> *“The proof deck is perfect. Now print ten thousand copies.”*

-----

*🃏 Card Deck is a series about building mobile apps with Expo — from first `npx create-expo-app` to live on the App Store and Google Play.*
