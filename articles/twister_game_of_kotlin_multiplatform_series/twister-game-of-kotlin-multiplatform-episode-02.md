-----

## title: “Twister Game of Kotlin Multiplatform! Ep.2: Left Hand Red — The Source Set Circles”
published: false
description: “Episode 2: The Twister mat has coloured circles — yellow, red, blue, green. In Kotlin Multiplatform, source sets are those circles. commonMain is the shared yellow circle everyone touches. androidMain, iosMain, jvmMain are the platform-exclusive colours. But there are also intermediate circles — appleMain, nativeMain — that some players share but others cannot reach. Every circle, mapped and explained.”
tags: [kotlin, multiplatform, gradle, architecture]
cover_image: “<https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/twister-kmp-episode-02.png>”
series: “Twister Game of Kotlin Multiplatform”
canonical_url: “”
organization: “the-software-s-journey”
part: 1

# Twister Game of Kotlin Multiplatform! 🎯

## Episode 2: Left Hand Red — The Source Set Circles

-----

## The Coloured Circles 🟡🔴🟢🔵

In a real Twister game, the mat has four rows of circles: yellow, red, blue, and green. The referee calls a colour and a body part — *left hand, red* — and every player reaches for that circle. Crucially, some circles are reachable from certain positions and not others. The player in the corner can easily reach red. The player at the edge has to make an enormous stretch.

Kotlin Multiplatform source sets work exactly the same way. The **colour** of each source set determines which targets (players) it belongs to:

- **commonMain** 🟡 — the yellow circle in the very middle. Every single target touches it.
- **androidMain** 🟢 — the green circle only the Android player reaches.
- **iosMain** 🔵 — the blue circle the iOS players reach together.
- **jvmMain** 🔴 — the red circle for Desktop.
- **wasmJsMain** ⚪ — the grey circle for browser WebAssembly.

But there are also **intermediate circles** — not quite as universal as yellow, not as exclusive as the platform circles. `nativeMain` is shared by iOS, macOS, and Linux — a circle that native targets can reach, but JVM and Wasm targets cannot.

-----

## 🗂️ SIPOC — The Source Set Machinery

|**Suppliers**                 |**Inputs**                                                    |**Process**                                                                                                                                |**Outputs**                                                                                              |**Customers**                                                                              |
|------------------------------|--------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
|The developer                 |Kotlin source files placed in the correct source set directory|Gradle resolves the source set hierarchy; the Kotlin compiler includes the correct source sets per target                                  |Compiled code where each target sees exactly the code it should: commonMain + its own source set         |The platform apps: Android gets `commonMain + androidMain`, iOS gets `commonMain + iosMain`|
|The Kotlin Gradle Plugin (KGP)|Target declarations in the kotlin{} block                     |Automatically creates source sets with conventional names and wires them according to the hierarchy                                        |A complete dependency graph: `androidMain` *depends on* `commonMain`, `iosMain` *depends on* `commonMain`|The compiler — which uses the graph to know which code is visible to each target           |
|Intermediate source sets      |`appleMain`, `nativeMain`, `posixMain` declarations           |Acts as an intermediate dependency: `iosMain` inherits from `appleMain`, which inherits from `nativeMain`, which inherits from `commonMain`|A source set visible to iOS, macOS, tvOS, and watchOS but NOT to Android or JVM                          |Any code that uses Apple or POSIX APIs shared across Apple platforms                       |

-----

## The Complete Source Set Hierarchy 📐

The hierarchy is a tree. Code flows downward — from general to specific. Code in a parent source set is visible in all children:

```
commonMain                    ← 🟡 Every target sees this
    │
    ├── nativeMain            ← Seen by all Kotlin/Native targets
    │   ├── appleMain         ← Seen by all Apple targets
    │   │   ├── iosMain       ← Seen by all iOS targets
    │   │   │   ├── iosArm64Main     (real iPhone)
    │   │   │   ├── iosX64Main       (Intel Mac simulator)
    │   │   │   └── iosSimulatorArm64Main  (Apple Silicon sim)
    │   │   ├── macosMain     ← macOS desktop
    │   │   │   ├── macosArm64Main
    │   │   │   └── macosX64Main
    │   │   ├── tvosMain
    │   │   └── watchosMain
    │   ├── linuxMain
    │   │   └── linuxX64Main
    │   └── mingwMain         ← Windows (MinGW)
    │       └── mingwX64Main
    │
    ├── jvmMain               ← JVM (Desktop, server)
    │
    ├── androidMain           ← Android
    │
    └── jsMain / wasmJsMain   ← Web targets
```

**The key insight:** Code in `iosMain` is automatically available to `iosArm64Main`, `iosX64Main`, and `iosSimulatorArm64Main`. You almost never write code directly in the leaf target source sets.

-----

## The Complete `build.gradle.kts` — Mapping Every Circle 🎰

```kotlin
// shared/build.gradle.kts

plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
    alias(libs.plugins.kotlinSerialization)
}

kotlin {
    // ── Declare all players (targets) ────────────────────────────

    androidTarget {
        compilations.all {
            kotlinOptions { jvmTarget = "17" }
        }
    }

    // Group iOS targets: one framework name covers all three variants
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "Shared"
            isStatic = true    // Static framework — simpler to link
        }
    }

    jvm("desktop")

    wasmJs {
        browser()
        binaries.executable()
    }

    // ── Map the circles (source sets and dependencies) ────────────

    sourceSets {
        // 🟡 The yellow circle — shared by EVERYONE
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.kotlinx.datetime)
            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.kotlinx.json)
        }

        // 🟢 The Android-exclusive green circle
        androidMain.dependencies {
            implementation(libs.ktor.client.okhttp)
            implementation(libs.kotlinx.coroutines.android)
        }

        // 🔵 The iOS-exclusive blue circle
        // iosMain automatically covers iosArm64, iosX64, iosSimulatorArm64
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
        }

        // 🔴 The Desktop-exclusive red circle
        val desktopMain by getting {
            dependencies {
                implementation(libs.ktor.client.cio)
                implementation(libs.kotlinx.coroutines.swing)
            }
        }

        // ⚪ The Wasm-exclusive circle
        wasmJsMain.dependencies {
            implementation(libs.ktor.client.js)
        }
    }
}
```

-----

## Intermediate Source Sets: The Shared Stretch 🤸

Sometimes two platform-specific source sets share code that only they can use — code that is not universal enough for `commonMain` but is common enough between, say, all Apple platforms.

**Creating an `appleMain` intermediate source set:**

```kotlin
// shared/build.gradle.kts

kotlin {
    iosArm64()
    iosSimulatorArm64()
    iosX64()
    macosArm64()
    macosX64()
    tvosArm64()

    sourceSets {
        // Declare the intermediate "apple" circle
        // This source set is visible to all Apple targets above
        val appleMain by creating {
            dependsOn(commonMain.get())
        }

        // Wire each Apple leaf source set to the intermediate
        listOf(
            iosArm64Main, iosSimulatorArm64Main, iosX64Main,
            macosArm64Main, macosX64Main, tvosArm64Main
        ).forEach { it.dependsOn(appleMain.get()) }

        // Now code in appleMain can use Apple-only APIs like
        // platform.Foundation.* and platform.UIKit.*
        // but NOT use Android-only APIs
    }
}
```

**What goes in `appleMain`:**

```kotlin
// shared/src/appleMain/kotlin/com/example/shared/PlatformLogger.kt

import platform.Foundation.NSLog

// NSLog is available on ALL Apple platforms (iOS, macOS, tvOS)
// but not on Android or JVM — so it belongs in appleMain, not commonMain

actual class PlatformLogger {
    actual fun log(message: String) {
        NSLog("[APP] %@", message)
    }
}
```

-----

## The Conventional Directory Structure 📁

Kotlin’s source sets follow a strict naming convention. The directory name IS the source set name:

```
shared/
└── src/
    ├── commonMain/kotlin/             ← MUST be exactly this name
    ├── commonTest/kotlin/             ← Test code shared across all targets
    ├── androidMain/kotlin/
    ├── androidUnitTest/kotlin/        ← Android unit tests
    ├── iosMain/kotlin/
    ├── iosTest/kotlin/
    ├── jvmMain/kotlin/
    ├── jvmTest/kotlin/
    ├── wasmJsMain/kotlin/
    └── appleMain/kotlin/              ← Custom intermediate (must be declared in Gradle)
```

**One critical rule:** If a source set is declared in Gradle but has no directory, it silently has no code — no error. If a directory exists but is not declared in Gradle, its code is simply never compiled. **The Gradle declaration and the directory must both exist.**

-----

## The Hierarchy in Practice: What Sees What 👁️

Here is a concrete example of visibility:

```kotlin
// commonMain/kotlin/com/example/shared/Repository.kt
// ✅ Every target sees this

class UserRepository {
    fun getUsers(): List<User> = listOf(User("Alice"), User("Bob"))
}

data class User(val name: String)
```

```kotlin
// androidMain/kotlin/com/example/shared/AndroidHelper.kt
// ✅ Only Android sees this

import android.content.Context

class AndroidHelper(private val context: Context) {
    fun getCacheDir(): String = context.cacheDir.absolutePath
}
```

```kotlin
// iosMain/kotlin/com/example/shared/IOSHelper.kt
// ✅ Only iOS sees this

import platform.Foundation.NSTemporaryDirectory

class IOSHelper {
    fun getCacheDir(): String = NSTemporaryDirectory()
}
```

```kotlin
// ❌ This would NOT compile — AndroidHelper is only visible in androidMain
// If you tried this in commonMain:
class BrokenClass {
    val helper = AndroidHelper(context)  // ERROR: Unresolved reference
}
```

The compiler is the referee. Try to use a circle that your position cannot reach and it calls a foul immediately.

-----

## The `libs.versions.toml`: The Game Equipment Manifest 📋

Modern KMP projects use a version catalogue — the equipment list that makes all the pieces fit together:

```toml
# gradle/libs.versions.toml

[versions]
kotlin             = "2.1.0"
coroutines         = "1.9.0"
ktor               = "3.0.3"
serialization      = "1.7.3"
datetime           = "0.6.1"
sqldelight         = "2.0.2"
koin               = "4.1.0"
agp                = "8.5.0"

[libraries]
# ── KotlinX ──────────────────────────────────────────────────────
kotlinx-coroutines-core    = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core",    version.ref = "coroutines" }
kotlinx-coroutines-android = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-android", version.ref = "coroutines" }
kotlinx-coroutines-swing   = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-swing",   version.ref = "coroutines" }
kotlinx-serialization-json = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version.ref = "serialization" }
kotlinx-datetime            = { module = "org.jetbrains.kotlinx:kotlinx-datetime",           version.ref = "datetime" }

# ── Ktor ──────────────────────────────────────────────────────────
ktor-client-core             = { module = "io.ktor:ktor-client-core",                       version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation",    version.ref = "ktor" }
ktor-serialization-kotlinx-json = { module = "io.ktor:ktor-serialization-kotlinx-json",    version.ref = "ktor" }
ktor-client-okhttp           = { module = "io.ktor:ktor-client-okhttp",                     version.ref = "ktor" }
ktor-client-darwin           = { module = "io.ktor:ktor-client-darwin",                     version.ref = "ktor" }
ktor-client-cio              = { module = "io.ktor:ktor-client-cio",                         version.ref = "ktor" }
ktor-client-js               = { module = "io.ktor:ktor-client-js",                         version.ref = "ktor" }

[plugins]
kotlinMultiplatform   = { id = "org.jetbrains.kotlin.multiplatform",    version.ref = "kotlin" }
androidLibrary        = { id = "com.android.library",                   version.ref = "agp" }
kotlinSerialization   = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
```

-----

## Source Sets vs Source Directories: Don’t Confuse Them 🚨

A common beginner mistake: thinking that files in `androidMain` magically become Android-only because of where they sit. That is true — but it is the **Gradle source set declaration** that enforces it, not the directory name alone.

```kotlin
// The source set declaration is the authoritative contract
sourceSets {
    androidMain {
        // Only code targeting Android JVM compilation ends up here
        // Trying to use platform.UIKit.* here would fail
    }
    iosMain {
        // Only code targeting iOS Kotlin/Native compilation ends up here
        // Trying to use android.os.Build here would fail
    }
}
```

**The Twister analogy:** The colour of the circle on the mat is determined by the spinner result (Gradle), not by where your hand happens to land. You cannot call a green circle red just because you coloured it differently with a marker.

-----

## What’s Next: The Referee’s Call 📢

*Right foot on blue — that is the next move.*

In **Episode 3**, the referee calls `expect/actual` — the mechanism that allows the shared circle (`commonMain`) to declare a *promise* that each platform-specific circle must fulfil. Without `expect/actual`, KMP would only let you share code that uses APIs common to every platform. With it, you can share *interfaces* and let each platform deliver its *own implementation*.

-----

**🔗 Resources**

- **KMP Source Sets**: [kotlinlang.org/docs/multiplatform/multiplatform-discover-project](https://kotlinlang.org/docs/multiplatform/multiplatform-discover-project.html)
- **Hierarchical project structure**: [kotlinlang.org/docs/multiplatform/multiplatform-hierarchy](https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html)
- **libs.versions.toml**: [docs.gradle.org/current/userguide/platforms.html](https://docs.gradle.org/current/userguide/platforms.html)

-----

*🎯 Twister Game of Kotlin Multiplatform — one mat, many platforms, perfect balance.*
