---
title: "Twister Game of Kotlin Multiplatform 🎯 Ep.1"
published: false
description: "Episode 1: Roll up the mat, call the players, spin the wheel. Kotlin Multiplatform is a physical game of code — shared circles everyone touches, platform-specific reaches no one else can make, and the constant challenge of keeping every player balanced without anyone falling off. Welcome to the Twister Game of Kotlin Multiplatform."
tags: [kotlin, multiplatform, android, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/twister-kmp-episode-01.png"
series: "Twister Game of Kotlin Multiplatform"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 1: Welcome to the Mat

-----

## Unroll the Mat! 🟡🔴🟢🔵

Imagine Twister — the game where players twist themselves into improbable shapes, reaching left hand to red, right foot to blue, all while trying not to fall over in a heap on the floor. More players join. The mat fills up. The positions get increasingly creative. Yet somehow, the best players stay connected to every circle they need, never losing balance.

Now imagine that mat is your codebase.

The circles are your platforms: **Android** stretched out in the left corner, **iOS** across the right, **Desktop** standing tall in the middle, **WebAssembly** balancing on one foot at the edge. Every player must touch the circles on the shared mat — the **common code** — while also making platform-specific reaches that nobody else can make.

When everyone stays up, you have shipped one codebase to five platforms. When someone falls, you have a compilation error.

Welcome to **Kotlin Multiplatform** — the Twister game of modern software development.

-----

## 🗂️ SIPOC — The Game Setup

|**Suppliers**                    |**Inputs**                                                         |**Process**                                                                              |**Outputs**                                                                     |**Customers**                                                                                             |
|---------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
|JetBrains (the game manufacturer)|Kotlin language, KMP Gradle plugin, K2 compiler, standard libraries|Compiles commonMain to JVM bytecode (Android/Desktop), native binary (iOS), or WASM (Web)|Platform-specific library artefacts that look completely native to each platform|Android developers, iOS developers, web engineers — each gets code that feels like it was written for them|
|The developer                    |Business logic, domain models, network calls, database queries     |Write once in commonMain; use platform source sets for native APIs                       |A shared module that all platform apps depend on                                |The end user — who gets consistent behaviour across every platform they use                               |
|The Gradle build system          |`build.gradle.kts` with the kotlin{} block                         |Spins the metaphorical wheel — resolves targets, wires source sets, triggers compilation |Build artefacts per target (`.jar`, `.framework`, `.wasm`)                      |Platform teams — who import the artefact into their native build                                          |

-----

## The Game Board: What KMP Actually Does 🗺️

Kotlin Multiplatform is not a framework that renders a shared UI (though Compose Multiplatform can). At its core, KMP is a **compilation technology** — it lets one Kotlin codebase compile to multiple platform targets.

```
One Kotlin source
       │
       ├─── Kotlin/JVM ──────► .jar / .aar  (Android, Desktop)
       ├─── Kotlin/Native ───► .framework   (iOS, macOS, tvOS, watchOS)
       ├─── Kotlin/Wasm ─────► .wasm        (Browser, embedded WASM)
       └─── Kotlin/JS ───────► .js          (Browser, Node.js)
```

Each compiled output looks **completely native** to the consuming platform. Android sees an `.aar` library. iOS sees an Objective-C framework (that Swift can use directly). The web sees WebAssembly. Nobody on the consuming side needs to know that Kotlin wrote any of it.

-----

## The Players: Understanding the Targets 👥

In Twister, each player occupies one corner of the mat and reaches for circles. In KMP, each **target** is a platform that will consume the shared code:

|Target               |Kotlin Runtime|Output                |Real-world use             |
|---------------------|--------------|----------------------|---------------------------|
|`android()`          |Kotlin/JVM    |`.aar` library        |Android apps               |
|`jvm()`              |Kotlin/JVM    |`.jar`                |Desktop, server, unit tests|
|`iosArm64()`         |Kotlin/Native |`.framework`          |Real iPhones (ARM)         |
|`iosSimulatorArm64()`|Kotlin/Native |`.framework`          |Apple Silicon simulator    |
|`iosX64()`           |Kotlin/Native |`.framework`          |Intel Mac simulator        |
|`wasmJs()`           |Kotlin/Wasm   |`.wasm`               |Browser (Beta, 2025)       |
|`macosArm64()`       |Kotlin/Native |`.kexe` / `.framework`|Apple Silicon Macs         |
|`linuxX64()`         |Kotlin/Native |binary                |Linux desktop              |

-----

## The Mat: The Project Structure 🗂️

Every KMP project has a **shared module** — the mat on which all players stretch. Inside this module, code lives in **source sets** — the coloured circles on the mat.

```
myapp/
├── androidApp/              ← Android-specific UI
├── iosApp/                  ← iOS-specific UI (Xcode project)
├── desktopApp/              ← Desktop-specific UI
└── shared/                  ← THE MAT
    ├── build.gradle.kts     ← The spinner — declares targets
    └── src/
        ├── commonMain/      ← 🟡 The shared yellow circle everyone touches
        │   └── kotlin/
        │       └── com/example/shared/
        │           └── Greeting.kt
        ├── androidMain/     ← 🟢 Android's exclusive green circles
        │   └── kotlin/
        ├── iosMain/         ← 🔵 iOS's exclusive blue circles
        │   └── kotlin/
        └── jvmMain/         ← 🔴 Desktop's exclusive red circles
            └── kotlin/
```

-----

## The Spinner: Your First `build.gradle.kts` 🎰

The Gradle build file is the spinner that decides which targets are in play. Every time you add a target here, you add another player to the game:

```kotlin
// shared/build.gradle.kts

plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
}

kotlin {
    // ── PLAYERS (Targets) ────────────────────────────────────────
    androidTarget {
        compilations.all {
            kotlinOptions { jvmTarget = "17" }
        }
    }

    // iOS targets — all three needed to cover:
    // real devices, Apple Silicon simulators, Intel Mac simulators
    iosArm64()
    iosSimulatorArm64()
    iosX64()

    jvm("desktop")           // Desktop JVM target

    wasmJs {                 // Browser WebAssembly (Beta)
        browser()
    }

    // ── CIRCLES (Source Sets) ─────────────────────────────────────
    sourceSets {
        commonMain.dependencies {
            // Libraries that work on ALL targets go here
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.kotlinx.datetime)
        }

        androidMain.dependencies {
            // Android-only libraries
            implementation(libs.kotlinx.coroutines.android)
        }

        val iosMain by getting {
            // iOS-only libraries (covers all three iOS targets)
        }

        val desktopMain by getting {
            dependencies {
                implementation(libs.kotlinx.coroutines.swing)
            }
        }
    }
}
```

-----

## Your First Shared Code: Standing on the Yellow Circle 🟡

The simplest piece of shared code — a function that runs identically on every platform:

```kotlin
// shared/src/commonMain/kotlin/com/example/shared/Greeting.kt

package com.example.shared

class Greeting {
    private val platform = getPlatform()

    fun greet(): String =
        "Hello from Kotlin Multiplatform! Running on ${platform.name}"
}

// This interface exists in commonMain — every platform must implement it
interface Platform {
    val name: String
}

// This function is declared in commonMain but IMPLEMENTED per platform
expect fun getPlatform(): Platform
```

Each platform provides its actual implementation:

```kotlin
// androidMain/kotlin/com/example/shared/Platform.android.kt

class AndroidPlatform : Platform {
    override val name: String =
        "Android ${android.os.Build.VERSION.SDK_INT}"
}

actual fun getPlatform(): Platform = AndroidPlatform()
```

```kotlin
// iosMain/kotlin/com/example/shared/Platform.ios.kt

import platform.UIKit.UIDevice

class IOSPlatform : Platform {
    override val name: String =
        UIDevice.currentDevice.systemName() + " " +
        UIDevice.currentDevice.systemVersion
}

actual fun getPlatform(): Platform = IOSPlatform()
```

The `expect`/`actual` keywords are the heart of KMP — the **reach** that connects common code to platform-specific behaviour. Episode 3 explores this mechanism in full forensic detail.

-----

## Setting Up: Getting the Tools 🔧

**Prerequisites:**

```bash
# 1. Install JDK 17 or later
brew install openjdk@17          # macOS
# or use SDKMAN: sdk install java 17-jbr

# 2. Install Android Studio Meerkat (includes Kotlin Multiplatform plugin)
# Download from: developer.android.com/studio

# 3. On macOS: Xcode command-line tools (for iOS targets)
xcode-select --install

# 4. Install the KMP plugin in Android Studio:
#    Preferences → Plugins → search "Kotlin Multiplatform"
```

**Create your first project:**

The fastest way is the Kotlin Multiplatform Wizard:

```
1. Visit: kmp.jetbrains.com
2. Name your project
3. Select targets: Android, iOS, Desktop, Web
4. Download the generated project
5. Open in Android Studio Meerkat
```

Or use the new KMP module template in Android Studio Meerkat:

```
File → New → New Module → Kotlin Multiplatform Library
```

-----

## The Stability Status: Who Is a Confident Player? 🏆

Before you spin the wheel for every target, understand the current stability:

|Target / Feature    |Status (2025/2026)|Notes                                           |
|--------------------|------------------|------------------------------------------------|
|Android             |✅ Stable          |Production-ready since 2023                     |
|iOS                 |✅ Stable          |KMP stable; Compose MP iOS stable since May 2025|
|Desktop (JVM)       |✅ Stable          |Windows, macOS, Linux                           |
|Kotlin/Wasm (wasmJs)|🟡 Beta            |Browser-only, near production                   |
|Kotlin/JS           |✅ Stable          |Mature, but Wasm is the future                  |
|macOS native        |✅ Stable          |Kotlin/Native target                            |
|Linux               |✅ Stable          |Kotlin/Native target                            |

-----

## The Series: Eight Rounds of Twister 🎯

|#|Episode                             |The Move       |What We Learn                                  |
|-|------------------------------------|---------------|-----------------------------------------------|
|1|*This one* — Welcome to the Mat     |Setup          |KMP overview, targets, first project           |
|2|Left Hand Red — Source Sets         |Source sets    |commonMain hierarchy, Gradle DSL mastery       |
|3|The Referee’s Call — expect/actual  |Platform bridge|expect/actual patterns, platform APIs          |
|4|The Double Stretch — Ktor           |Networking     |Ktor multiplatform, serialization, repositories|
|5|Two Players, One Circle — SQLDelight|Persistence    |SQLDelight, Koin DI, multiplatform settings    |
|6|Shared Moves — Compose Multiplatform|Shared UI      |@Composable across platforms, navigation       |
|7|Tournament Play — Architecture      |Advanced       |Clean Architecture, SKIE, Wasm, multi-module   |
|8|Winning the Game — Production       |Shipping       |Testing, CI, Jetpack KMP libs, full deployment |

In **Episode 2**, we map every circle on the mat — understanding the source set hierarchy that is the foundation of everything KMP does.

*Left hand on yellow. The game has begun!* 🟡

-----

**🔗 Resources**

- **Kotlin Multiplatform**: [kotlinlang.org/docs/multiplatform](https://kotlinlang.org/docs/multiplatform.html)
- **KMP Wizard**: [kmp.jetbrains.com](https://kmp.jetbrains.com)
- **klibs.io**: [klibs.io](https://klibs.io)
- **Compose Multiplatform**: [jb.gg/compose](https://jb.gg/compose)

-----

*🎯 Twister Game of Kotlin Multiplatform — one mat, many platforms, perfect balance.*
