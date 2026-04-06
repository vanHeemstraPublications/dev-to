---
title: "🃏 Card Deck — Episode 6: The Face Cards (Expo SDK — Camera, Notifications & Storage)"
published: false
description: "Face cards carry the most value. The Expo SDK is your deck’s face cards — Camera, Push Notifications, Local Storage, Location, and more, all production-ready and one install away."
tags: expo, sdk, camera, notifications
series: Card Deck
cover_image: ""
canonical_url: ""
---

# 🃏 Card Deck — Episode 6: The Face Cards (Expo SDK — Camera, Notifications & Storage)

> *“In most card games, the face cards — Jack, Queen, King — carry disproportionate value. Three cards out of thirteen, yet they determine the outcome of most hands.”*
> — Card games, face card weighting.

---

## 👑 The Face Cards

In your standard 52-card deck, the face cards are thirteen out of fifty-two — but they carry most of the weight. The King wins most trick-taking hands. The Jack and Queen appear in the most rules. In Poker, a pair of Kings beats almost everything.

The **Expo SDK** is your deck’s face cards. In a project of 100+ available modules, a handful carry the most everyday value: the camera, push notifications, secure storage, location services, and the filesystem. Master these, and you can build the vast majority of consumer apps.

This episode covers the most frequently reached-for SDK modules, how to install them properly, and how they fit into the card deck.

-----

## 📋 SIPOC — The Face Cards

|**Suppliers**           |**Inputs**                           |**Process**                              |**Outputs**                                         |**Customers**                                                |
|------------------------|-------------------------------------|-----------------------------------------|----------------------------------------------------|-------------------------------------------------------------|
|Expo SDK (100+ modules) |Your running Expo project            |`npx expo install` → import → use        |Native hardware features in your JavaScript code    |Users who take photos, receive notifications, log in         |
|Apple/Google native APIs|Permission declarations in `app.json`|Request user permission → Use the feature|A device feature accessible with 5 lines of code    |Your app’s reviews (“easy to use”, “polished”)               |
|`@expo/vector-icons`    |TypeScript + React Native            |Compose SDK modules with your UI         |A feature-complete screen backed by real native APIs|Future episodes (development builds — some modules need them)|
|Your `app.json`         |Your design for each feature         |Configure SDK via config plugins         |`Info.plist` and `AndroidManifest.xml` auto-updated |EAS Build (Episodes 9–10), which reads these configs         |

-----

## 📦 Installing SDK Modules — Always Use `npx expo install`

The Expo SDK versions are carefully coordinated with the React Native version your project uses. Installing the wrong version breaks builds. Always use:

```bash
npx expo install expo-camera
# NOT: npm install expo-camera
```

`npx expo install` resolves the correct version for your SDK automatically. It is the difference between a well-shuffled deck and a random pile of cards.

-----

## 📷 Face Card 1 — Camera (`expo-camera`)

The camera module gives you access to the device’s camera for taking photos and recording video.

```bash
npx expo install expo-camera
```

Add the permission strings to `app.json`:

```json
{
  "expo": {
    "plugins": [
      [
        "expo-camera",
        {
          "cameraPermission": "Allow $(BUNDLE_DISPLAY_NAME) to access your camera."
        }
      ]
    ]
  }
}
```

A minimal camera screen:

```tsx
// app/(tabs)/camera.tsx
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Button, StyleSheet, Text, View } from 'react-native';

export default function CameraScreen() {
  const [permission, requestPermission] = useCameraPermissions();

  if (!permission) {
    // Permissions are still loading
    return <View />;
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text>We need your permission to show the camera.</Text>
        <Button onPress={requestPermission} title="Grant Permission" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView style={styles.camera} facing="back" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  camera: { flex: 1 },
});
```

> ⚠️ **`expo-camera` requires a development build** (Episode 7) — it cannot run in Expo Go because it requires a native module compiled into the binary. This is the first face card you will need your own deck to play.

-----

## 🔔 Face Card 2 — Push Notifications (`expo-notifications`)

Push notifications are the single most powerful re-engagement tool in mobile apps. The Expo SDK makes them significantly less painful than the raw APNs/FCM APIs.

```bash
npx expo install expo-notifications
```

Add to `app.json`:

```json
{
  "expo": {
    "plugins": [
      [
        "expo-notifications",
        {
          "icon": "./assets/images/notification-icon.png",
          "color": "#1a1aff"
        }
      ]
    ]
  }
}
```

Request permission and get the push token:

```tsx
import * as Notifications from 'expo-notifications';
import { useEffect, useState } from 'react';
import { Platform } from 'react-native';

async function registerForPushNotifications() {
  const { status: existingStatus } = await Notifications.getPermissionsAsync();

  let finalStatus = existingStatus;
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    return null;  // User denied
  }

  const token = await Notifications.getExpoPushTokenAsync({
    projectId: 'your-expo-project-id',  // Found in app.json or expo.dev dashboard
  });

  // Android requires a notification channel
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
    });
  }

  return token.data;
}
```

Send the token to your backend and use [Expo’s push notification service](https://docs.expo.dev/push-notifications/sending-notifications/) or Firebase/APNs directly to send messages.

-----

## 💾 Face Card 3 — Secure Storage (`expo-secure-store`)

For storing sensitive data — auth tokens, API keys, user credentials — use SecureStore. It uses iOS Keychain and Android Keystore: hardware-backed, encrypted, not accessible outside your app.

```bash
npx expo install expo-secure-store
```

```tsx
import * as SecureStore from 'expo-secure-store';

// Store a token after login
async function saveAuthToken(token: string) {
  await SecureStore.setItemAsync('auth_token', token);
}

// Retrieve it on app start
async function getAuthToken(): Promise<string | null> {
  return await SecureStore.getItemAsync('auth_token');
}

// Delete it on logout
async function deleteAuthToken() {
  await SecureStore.deleteItemAsync('auth_token');
}
```

For non-sensitive data (user preferences, app state, cached data), use `AsyncStorage` (`@react-native-async-storage/async-storage`) — it is not encrypted but has no size limit and is faster for large datasets.

-----

## 📍 Face Card 4 — Location (`expo-location`)

```bash
npx expo install expo-location
```

Add to `app.json`:

```json
{
  "expo": {
    "plugins": [
      [
        "expo-location",
        {
          "locationWhenInUsePermission": "Allow $(BUNDLE_DISPLAY_NAME) to use your location."
        }
      ]
    ]
  }
}
```

Get the current position:

```tsx
import * as Location from 'expo-location';

async function getCurrentLocation() {
  const { status } = await Location.requestForegroundPermissionsAsync();

  if (status !== 'granted') {
    console.log('Location permission denied');
    return;
  }

  const location = await Location.getCurrentPositionAsync({
    accuracy: Location.Accuracy.Balanced,
  });

  return {
    latitude: location.coords.latitude,
    longitude: location.coords.longitude,
  };
}
```

-----

## 📂 Face Card 5 — File System (`expo-file-system`)

Access, read, write, and download files in the app’s sandboxed file system — useful for caching images, saving user-generated content, downloading documents.

```bash
npx expo install expo-file-system
```

```tsx
import * as FileSystem from 'expo-file-system';

// Download an image and cache it locally
async function downloadAndCache(url: string, filename: string) {
  const localUri = `${FileSystem.cacheDirectory}${filename}`;
  const fileInfo = await FileSystem.getInfoAsync(localUri);

  if (fileInfo.exists) {
    return localUri;  // Already cached — return immediately
  }

  const { uri } = await FileSystem.downloadAsync(url, localUri);
  return uri;
}

// Read a text file
async function readTextFile(uri: string): Promise<string> {
  return await FileSystem.readAsStringAsync(uri);
}
```

-----

## 🃏 Managing Permissions — The Permission Deck

Nearly every SDK module that accesses device hardware requires a user permission. The pattern is consistent across all modules:

1. **Check** if permission is already granted (`getPermissionsAsync()`)
1. **Request** if not granted (`requestPermissionsAsync()`)
1. **Handle denial** gracefully — explain why you need it, offer a Settings link
1. **Proceed** only when granted

```tsx
import { Alert, Linking } from 'react-native';
import * as Camera from 'expo-camera';

async function requestCameraWithFallback() {
  const { status } = await Camera.requestCameraPermissionsAsync();

  if (status === 'denied') {
    Alert.alert(
      'Camera Permission Required',
      'Please enable camera access in Settings to use this feature.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Open Settings', onPress: () => Linking.openSettings() },
      ]
    );
  }
}
```

-----

## 📝 Adding Permissions to `app.json`

When using Config Plugins (the `plugins` array in `app.json`), Expo automatically inserts the correct permission strings into:

- iOS: `Info.plist` — `NSCameraUsageDescription`, `NSLocationWhenInUseUsageDescription`, etc.
- Android: `AndroidManifest.xml` — `<uses-permission android:name="android.permission.CAMERA" />`, etc.

You never need to hand-edit native files. The plugin does it during the build step. This is **Continuous Native Generation (CNG)** — your `app.json` is the source of truth for native configuration, and Expo generates the native projects from it.

-----

## 🛸 What’s Next

You now have the full card deck in your hands — navigation sorted, SDK modules integrated. But there is a limit to what Expo Go can run. Camera, notifications, and other native modules require your **own compiled binary**.

In **Episode 7**, we create a **development build** — your custom-printed proof deck. It has your back design, your native modules, your bundle identifier. It is the first time the deck is truly yours.

> *“The borrowed deck has served its purpose. Time to print your own.”*

-----

*🃏 Card Deck is a series about building mobile apps with Expo — from first `npx create-expo-app` to live on the App Store and Google Play.*
