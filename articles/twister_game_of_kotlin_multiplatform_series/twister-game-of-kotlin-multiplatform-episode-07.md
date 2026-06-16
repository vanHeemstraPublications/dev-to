---
title: "Twister Game of Kotlin Multiplatform 🎯 Ep.7"
published: false
description: "Episode 7: Tournament Twister. More players, more circles, longer games, higher stakes. Clean Architecture in KMP with multi-module projects. SKIE for natural Swift interoperability with Kotlin coroutines. Kotlin/Wasm for browser targets. klib cross-compilation enabling CI without macOS. The techniques that separate production KMP apps from prototypes."
tags: [kotlin, multiplatform, architecture, advanced]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/twister-kmp-episode-07.png"
series: "Twister Game of Kotlin Multiplatform"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 7: Tournament Play — Advanced Architecture

-----

## The Stakes Get Higher 🏆

Tournament Twister is different from the casual backyard game. The mat is the same. The circles are the same. But the players are more skilled, the combinations are more complex, the game runs longer, and falling is not an option. The moves have names. There are specific strategies for multi-player coordination. The equipment matters more.

Production Kotlin Multiplatform has the same character. The fundamentals of Episodes 1-6 still apply — source sets, expect/actual, Ktor, SQLDelight, Compose. But at scale, with multiple teams, with real users, with CI/CD pipelines and Swift interoperability requirements, the techniques deepen.

This is the tournament episode.

-----

## 🗂️ SIPOC — The Production Architecture

|**Suppliers**                                  |**Inputs**                                                              |**Process**                                                                                                   |**Outputs**                                                              |**Customers**                                                                  |
|-----------------------------------------------|------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------------|
|Architecture team                              |Clean Architecture principles, domain-driven design                     |Modularise the KMP project into feature modules; each module has domain, data, and presentation layers        |A scalable codebase where features are independently developed and tested|All platform teams — who add new features in one module without touching others|
|SKIE (Swift/Kotlin Interoperability Extensions)|Kotlin Coroutines, Sealed classes, Default parameters in iOS-facing code|Transforms Kotlin APIs into idiomatic Swift: `StateFlow` → `AsyncSequence`, `Result<T>` → native Swift pattern|Swift code that reads like Swift, not like generated Kotlin wrappers     |iOS developers — who write natural Swift against shared Kotlin logic           |
|Kotlin/Wasm                                    |Kotlin commonMain code targeting the browser                            |Compiles to WebAssembly; CMP renders via Skia Canvas in the browser                                           |A browser app with the same UI and business logic as mobile              |Web users — who get native performance via WebAssembly                         |
|klib cross-compilation                         |KMP library source code                                                 |Build iOS frameworks on any OS (not just macOS) using the klib format                                         |CI pipelines on Linux that produce iOS-compatible artefacts              |Development teams on Linux/Windows — who no longer need macOS machines for CI  |

-----

## Part 1: Clean Architecture in KMP 🏛️

The canonical architecture for large KMP projects follows Clean Architecture principles, expressed as a multi-module project:

```
:shared
    │
    ├── :shared:domain          ← Pure Kotlin, zero platform dependency
    │   ├── src/commonMain/
    │   │   └── kotlin/
    │   │       ├── entity/       (User, Post, Product — pure data)
    │   │       ├── repository/   (interfaces ONLY — no implementation)
    │   │       └── usecase/      (business rules, orchestration)
    │   └── build.gradle.kts     (no platform dependencies at all)
    │
    ├── :shared:data            ← Ktor + SQLDelight implementations
    │   ├── src/
    │   │   ├── commonMain/
    │   │   │   └── kotlin/
    │   │   │       ├── remote/   (Ktor implementations of remote repos)
    │   │   │       └── local/    (SQLDelight implementations of local repos)
    │   │   ├── androidMain/      (Android drivers)
    │   │   └── iosMain/          (iOS drivers)
    │   └── build.gradle.kts     (Ktor, SQLDelight, depends on :shared:domain)
    │
    ├── :shared:presentation    ← ViewModels (no Compose)
    │   ├── src/commonMain/
    │   │   └── kotlin/
    │   │       └── viewmodel/    (StateFlow-based ViewModels)
    │   └── build.gradle.kts     (Coroutines, depends on :shared:domain)
    │
    └── :shared:ui              ← Compose Multiplatform screens
        ├── src/commonMain/
        │   └── kotlin/
        │       └── screen/       (Composable screens, components)
        └── build.gradle.kts     (Compose MP, depends on :shared:presentation)
```

**The domain module — pure Kotlin:**

```kotlin
// shared/domain/src/commonMain/kotlin/com/example/domain/entity/User.kt

// Zero imports from any library — pure domain model
data class User(
    val id:        String,
    val name:      String,
    val email:     String,
    val avatarUrl: String?
)

// shared/domain/src/commonMain/kotlin/com/example/domain/repository/UserRepository.kt

import kotlinx.coroutines.flow.Flow

// Repository interface — no implementation details
interface UserRepository {
    suspend fun getUser(id: String): Result<User>
    fun observeUsers(): Flow<List<User>>
    suspend fun saveUser(user: User): Result<Unit>
}

// shared/domain/src/commonMain/kotlin/com/example/domain/usecase/GetUserUseCase.kt

class GetUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(id: String): Result<User> =
        repository.getUser(id)
}
```

**Why separate the domain module?**

The domain module has **zero external dependencies** — no Ktor, no SQLDelight, no kotlinx.coroutines in the `api` scope. It can be tested with pure Kotlin, runs everywhere, and never changes because of infrastructure decisions.

```kotlin
// :shared:domain/build.gradle.kts — zero platform dependencies
kotlin {
    androidTarget()
    iosArm64(); iosSimulatorArm64(); iosX64()
    jvm()

    sourceSets {
        commonMain.dependencies {
            // NOTHING external except stdlib — this is intentional
            implementation(libs.kotlinx.coroutines.core)  // Only for Flow
        }
    }
}
```

-----

## Part 2: Feature Modules — Independent Sections of the Mat 🟡🔵🟢

Large KMP apps benefit from **feature modules** that slice vertically through the architecture:

```
:feature:posts
    ├── :feature:posts:domain          (Post entity, PostRepository interface)
    ├── :feature:posts:data            (PostRepository implementation)
    ├── :feature:posts:presentation    (PostsViewModel)
    └── :feature:posts:ui              (PostsScreen, PostDetailScreen)

:feature:profile
    ├── :feature:profile:domain
    ├── :feature:profile:data
    ├── :feature:profile:presentation
    └── :feature:profile:ui

:feature:settings
    ├── :feature:settings:domain
    ├── :feature:settings:data
    ├── :feature:settings:presentation
    └── :feature:settings:ui
```

Each feature module is a complete, independently compilable unit. Android team and iOS team can work in `:feature:posts` simultaneously without merge conflicts in `:feature:profile`.

**Feature dependency rule — the tournament rule:** A feature module may depend on `:shared:domain` and `:shared:data`. It may NEVER depend on another feature module directly. Cross-feature navigation happens through shared navigation contracts.

-----

## Part 3: SKIE — The Swift Interpreter 🔀

Kotlin and Swift have fundamental interoperability mismatches. Kotlin `StateFlow` has no Swift equivalent. Kotlin sealed classes expose awkwardly in Swift. Kotlin functions with default parameters look terrible from Swift.

**SKIE (Swift/Kotlin Interoperability Extensions)** from Touchlab solves this by post-processing the generated Objective-C header, transforming Kotlin APIs into idiomatic Swift.

```kotlin
// Gradle setup — :shared module only
plugins {
    id("co.touchlab.skie") version "0.10.0"
}
```

**Without SKIE — what iOS developers see:**

```swift
// Without SKIE — painful Swift interop
Task {
    for await state in AsyncStream<NetworkResult<NSArray>>(
        viewModel.state.toAsyncStream()  // Manual bridging required
    ) {
        // state is NetworkResult<NSArray>, not NetworkResult<[Post]>
        // Sealed classes don't pattern-match cleanly
    }
}
```

**With SKIE — idiomatic Swift:**

```swift
// With SKIE — StateFlow becomes AsyncSequence automatically
Task {
    for await state in viewModel.state {  // Clean AsyncSequence
        switch state {
        case .loading:
            showSpinner()
        case .success(let posts):          // Sealed class as Swift enum!
            showPosts(posts)
        case .error(let message, _):
            showError(message)
        }
    }
}

// SKIE also handles:
// - suspend functions → async/throws functions
// - Kotlin enums → Swift enums with associated values
// - Default parameters → Swift function overloads
// - @ObjCName → natural Swift names
```

**Annotating Kotlin code for SKIE:**

```kotlin
// In your Kotlin code — SKIE picks these up automatically
// But you can also use annotations for fine control:

import co.touchlab.skie.configuration.annotations.SealedInterop

@SealedInterop.Enabled  // Ensure this sealed class gets Swift enum treatment
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val message: String, val code: Int? = null) : NetworkResult<Nothing>()
    data object Loading : NetworkResult<Nothing>()
}

// Functions with default parameters — SKIE generates all overloads
suspend fun fetchData(
    id:      String,
    timeout: Int    = 30,
    cached:  Boolean = true
): Result<Data>
// In Swift: await fetchData(id:), await fetchData(id:timeout:), etc.
```

-----

## Part 4: Kotlin/Wasm — The New Circle on the Mat 🌐

Kotlin/Wasm reached Beta in September 2025. It compiles Kotlin to WebAssembly, enabling Compose Multiplatform to run in the browser with the same performance characteristics as native.

```kotlin
// shared/build.gradle.kts

kotlin {
    wasmJs {
        browser {
            commonWebpackConfig {
                cssSupport { enabled.set(true) }
            }
        }
        binaries.executable()
    }

    sourceSets {
        wasmJsMain.dependencies {
            implementation(libs.ktor.client.js)  // Fetch API engine
        }
    }
}
```

**The wasmJs entry point:**

```kotlin
// shared/src/wasmJsMain/kotlin/com/example/shared/Main.kt

import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.window.CanvasBasedWindow
import com.example.shared.ui.AppNavigation

@OptIn(ExperimentalComposeUiApi::class)
fun main() {
    CanvasBasedWindow(canvasElementId = "ComposeTarget") {
        AppNavigation()  // Same composable as mobile!
    }
}
```

```html
<!-- webApp/index.html -->
<!DOCTYPE html>
<html>
<head><title>My App</title></head>
<body>
    <canvas id="ComposeTarget"></canvas>
    <script src="composeApp.js"></script>
</body>
</html>
```

**Running the web target:**

```bash
# Development server
./gradlew :shared:wasmJsBrowserDevelopmentRun

# Production build
./gradlew :shared:wasmJsBrowserDistribution
# Output: shared/build/dist/wasmJs/productionExecutable/
```

-----

## Part 5: klib Cross-Compilation — CI Without macOS 🐧

One of the most significant recent KMP improvements: **klib cross-compilation**. Previously, building an iOS framework *required macOS*. CI pipelines had to run on Mac agents — expensive, slow, and limiting.

klib format allows the Kotlin compiler to produce an intermediate `.klib` format on any OS, which can then be linked on iOS. In practice, many KMP projects can now run their CI pipelines on Linux:

```yaml
# .github/workflows/ci.yml — runs entirely on Linux!

name: CI
on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'jbr'

    - name: Build shared module
      run: ./gradlew :shared:build

    - name: Run common tests
      run: ./gradlew :shared:allTests

    - name: Build klib for iOS
      # klib cross-compilation — no macOS required!
      run: ./gradlew :shared:compileKotlinIosArm64

    - name: Build Android artefacts
      run: ./gradlew :shared:assembleRelease

    - name: Build Desktop distribution
      run: ./gradlew :desktopApp:packageDistributionForCurrentOS

    - name: Build Wasm
      run: ./gradlew :shared:wasmJsBrowserDistribution
```

*Note: Final XCFramework linking for App Store distribution still requires macOS. But the Kotlin compilation and testing can run on Linux.*

-----

## Part 6: Publishing a KMP Library 📦

If you are building a KMP library for others to use:

```kotlin
// build.gradle.kts for a KMP library

plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
    id("maven-publish")
}

group    = "com.example"
version  = "1.0.0"

kotlin {
    androidTarget { publishLibraryVariants("release") }
    iosArm64()
    iosSimulatorArm64()
    iosX64()
    jvm()
    wasmJs { browser() }

    // Publish an XCFramework for iOS consumers
    val xcfName = "MyLibrary"
    val xcfTargets = listOf(iosArm64(), iosX64(), iosSimulatorArm64())
    xcfTargets.forEach {
        it.binaries.framework {
            baseName = xcfName
            isStatic = true
        }
    }
}

// The XCFramework task bundles all iOS slices into one distributable
tasks.register("buildXCFramework", org.jetbrains.kotlin.gradle.tasks.FatFrameworkTask::class) {
    destinationDir = file("build/XCFrameworks/release")
    from(
        kotlin.targets.withType(org.jetbrains.kotlin.gradle.plugin.mpp.KotlinNativeTarget::class)
            .filter { "ios" in it.name }
            .map { it.binaries.getFramework("RELEASE") }
    )
}
```

-----

## Part 7: The K2 Compiler Advantage ⚡

The K2 compiler (GA since 2024) dramatically improves KMP development:

|Benefit          |Before K2                     |With K2                                  |
|-----------------|------------------------------|-----------------------------------------|
|Build time       |~100s for large KMP modules   |~60s (up to 40% faster)                  |
|Analysis pipeline|Per-target                    |Unified — all targets analysed together  |
|IDE support      |Separate analysis per platform|Unified — one analysis serves all targets|
|Error messages   |Could differ between targets  |Consistent across all targets            |
|Language features|Sometimes delayed for KMP     |Simultaneous rollout to all targets      |

```kotlin
// In gradle.properties — ensure K2 is enabled (default since Kotlin 2.0)
kotlin.experimental.tryK2=true  // Already default in 2.x

// K2 compiler enables better type inference in expect/actual:
// Before K2: Some complex generic types required explicit annotation
// With K2:   The compiler infers correctly in more cases
```

-----

## What’s Next: Winning the Game 🏆

*The final round. Every player holds their position. The referee calls the last move.*

In **Episode 8** — the finale — we cover everything needed to ship a production KMP app: the testing strategy across platforms, the Jetpack libraries that now support KMP natively, version management, profiling, and the complete production deployment checklist. The game is won not by the boldest move, but by staying balanced longest.

-----

**🔗 Resources**

- **SKIE**: [skie.touchlab.co](https://skie.touchlab.co)
- **Kotlin/Wasm**: [kotlinlang.org/docs/wasm-overview](https://kotlinlang.org/docs/wasm-overview.html)
- **KMP roadmap 2025**: [blog.jetbrains.com/kotlin/2025/08/kmp-roadmap-aug-2025](https://blog.jetbrains.com/kotlin/2025/08/kmp-roadmap-aug-2025/)
- **klibs.io**: [klibs.io](https://klibs.io)

-----

*🎯 Twister Game of Kotlin Multiplatform — one mat, many platforms, perfect balance.*
