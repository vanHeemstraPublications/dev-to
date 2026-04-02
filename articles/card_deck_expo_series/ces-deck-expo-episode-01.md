---
title: "Card Deck Expo — Ep.1"
part: 1
published: false
description: "A mobile app is like a Bicycle playing card deck. One standard format. Runs on every table. Ships in a box. This series teaches Expo by teaching you to print your own deck."
tags: [expo, reactnative, beginners, mobile]
series: "Card Deck Expo Series"
cover_image: ""
canonical_url: ""
organization: "the-software-s-journey"
---

# 🃏 Your App Is a Bicycle Deck in Blue

> *“A deck of cards is the most democratic object in the world. Fifty-two cards. Four suits. The same rules for everyone. And yet in the right hands, it can produce infinite surprises.”*
> — Every magician who has ever written a book.

## 🎴 The Deck

Walk into any magic shop, any casino, any card table in any country on Earth, and you will find a **Bicycle playing card deck**. Red or blue back. Standard index. 52 cards plus two jokers. Cellophane wrapper. Cardboard tuck box.

It is the universal format. It runs on every table. It is understood by every player. And while the rules of the game are the same everywhere, what you do with the cards is entirely up to you.

A **mobile app** is exactly this.

Your app runs on iOS. It runs on Android. Optionally it runs in a browser. The underlying format — React Native components, JavaScript logic, native modules — is the standard deck. The specific app you build is the hand you deal.

And **Expo** is the card manufacturer, the printing press, the tuck box designer, and the courier to the card shop — all in one.

-----

## 📱 What Is Expo?

Expo is a **full-stack React Native framework** with a cloud build and distribution service attached. It is the fastest way to go from *“I have an idea for an app”* to *“My app is live on the App Store and Google Play”*.

More specifically, Expo is several things working together:

- **Expo SDK** — over 100 production-ready libraries for camera, notifications, location, file system, sensors, biometrics, and more. The cards in your deck.
- **Expo CLI** — the tool you run in your terminal to create, start, and manage your project.
- **Expo Router** — a file-based routing framework for React Native and web. The rules for how your cards are arranged.
- **Expo Go** — a development app you install on your phone to instantly preview any Expo project. A borrowed deck, for practice.
- **EAS (Expo Application Services)** — hosted build, submit, and update services. The printing press, the courier, and the distribution network.

You can use all of these together, or adopt them individually. Most people start with the SDK and CLI, reach for EAS when they need to ship, and discover that Expo Router makes their life considerably easier once they understand how it works.

-----

## 📋 SIPOC — The Series at a Glance

|**Suppliers**              |**Inputs**                  |**Process**                                           |**Outputs**                                             |**Customers**                         |
|---------------------------|----------------------------|------------------------------------------------------|--------------------------------------------------------|--------------------------------------|
|Expo (expo.dev)            |Node.js + npm               |Create project → Develop with Expo Go → Build with EAS|A working mobile app for iOS, Android, and web          |App Store and Google Play users       |
|React Native (Meta)        |A code editor (VS Code)     |Add screens with Expo Router → Add features with SDK  |A development build for testing on physical devices     |Your teammates and testers            |
|EAS (Expo cloud services)  |An Expo account (free)      |Build production binary → Submit to stores            |A shipped, published app                                |Your users, holding your deck         |
|Apple / Google (app stores)|A physical phone for testing|Over-the-air updates for fast iteration               |A live app that updates without going through app review|Your future self, fixing bugs silently|

-----

## 🃏 The Card Deck Metaphor — In Full

Let us establish the vocabulary that will carry us through this entire series:

|Card Concept                      |Expo Concept                                                                             |
|----------------------------------|-----------------------------------------------------------------------------------------|
|The **deck itself**               |Your Expo app (the whole project)                                                        |
|The **back design** (blue Bicycle)|Your app’s visual identity — icon, splash screen, colours                                |
|The **52 cards**                  |Your app’s screens and routes                                                            |
|The **four suits**                |Your target platforms: iOS ♥️, Android ♠️, Web ♣️, Desktop ♦️                                |
|The **tuck box**                  |The app bundle — `.ipa` for iOS, `.apk/.aab` for Android                                 |
|**Expo Go**                       |A borrowed practice deck — real cards, not your custom back                              |
|A **development build**           |Your custom-printed proof deck — your back design, your native modules                   |
|**EAS Build**                     |The printing press that produces the finished tuck boxes                                 |
|**EAS Submit**                    |The courier who delivers the tuck box to the card shop (App Store / Play Store)          |
|**OTA updates**                   |Swapping a card in the deck without reprinting the whole thing                           |
|**Expo Router**                   |The rules for how the 52 cards are arranged and navigated                                |
|**The SDK**                       |The quality of the card stock — premium modules that make the deck feel right in the hand|

This metaphor will hold. When something does not make sense technically, reach for the metaphor. When the metaphor gets stretched, the technical explanation is waiting one paragraph below.

-----

## 🎨 The Blue-Back Bicycle

Why blue, specifically?

Because the blue-backed Bicycle deck is the standard. Not flashy. Not gimmicky. Not a marked deck or a gaff. It is what every card player expects when someone says “get a deck of cards.”

Your first Expo app will feel like this. A single codebase. Standard React Native components. Clean, unsurprising structure. It will run on iOS and Android from exactly the same code — the same 52 cards, dealt to different tables simultaneously.

That universality is the point. You write it once; Expo handles the platform-specific differences. The deck looks the same from the back, no matter who is holding it.

-----

## 🗺️ What This Series Covers

Ten episodes. One complete app lifecycle, from first `npm` command to live on both stores:

|# |Episode                                    |Card Concept                             |
|--|-------------------------------------------|-----------------------------------------|
|1 |*This one* — what Expo is                  |The deck                                 |
|2 |Prerequisites and project creation         |Unboxing the deck                        |
|3 |Expo Go — instant preview on your phone    |The borrowed practice deck               |
|4 |Expo Router — file-based routing           |How the 52 cards are arranged            |
|5 |Stacks and Tabs — navigation layouts       |Suits and hands                          |
|6 |The Expo SDK — adding features             |High-value face cards                    |
|7 |Development builds — your custom proof deck|The custom back design                   |
|8 |Running your dev build on a physical phone |Dealing your proof deck at the real table|
|9 |EAS Build — the printing press             |Manufacturing the finished tuck box      |
|10|EAS Submit + OTA Updates — the card shop   |Shipping and maintaining the deck        |

By Episode 10, your Bicycle blue-back deck will be in the card shop. Sealed. Cellophaned. Ready to be opened by users who did not know they were waiting for it.

-----

## 🛸 What’s Next

In **Episode 2**, we unbox the deck — installing the prerequisites, creating your first Expo project, and understanding what the default file structure is telling you.

The tuck box is on the table. Let us open it.

-----

*🃏 Card Deck is a series about building mobile apps with Expo — from first `npx create-expo-app` to live on the App Store and Google Play.*
