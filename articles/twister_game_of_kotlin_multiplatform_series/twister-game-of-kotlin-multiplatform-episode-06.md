-----

## title: “Twister Game of Kotlin Multiplatform! Ep.6: Shared Moves — Compose Multiplatform”
published: false
description: “Episode 6: The boldest move in Twister is when everyone simultaneously reaches for the same yellow circle — and stays balanced. Compose Multiplatform is that move: one @Composable function rendering on Android, iOS, and Desktop simultaneously. Stable since May 2025. Shared navigation, shared resources, shared UI with platform-specific tweaks where needed. The mat becomes a stage.”
tags: [kotlin, compose, multiplatform, ui]
cover_image: “<https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/twister-kmp-episode-06.png>”
series: “Twister Game of Kotlin Multiplatform”
canonical_url: “”
organization: “the-software-s-journey”
part: 1

# Twister Game of Kotlin Multiplatform! 🎯

## Episode 6: Shared Moves — Compose Multiplatform

-----

## Everyone on Yellow, Simultaneously 🟡🟡🟡

The boldest move in Twister is when the referee calls yellow for every player at once and everyone must reach the same circle. In a well-played game, this is possible — each player approaches from their own angle, maintains their own balance, but they all touch the same point.

Compose Multiplatform is that move for UI. One `@Composable` function. Every platform touches it simultaneously. Android from one angle, iOS from another, Desktop from a third — but the same circle, the same code, the same rendering logic.

JetBrains declared **Compose Multiplatform iOS Stable** in May 2025 (CMP 1.8.0). Android has been stable since the beginning. Desktop (Windows, macOS, Linux) is stable. Kotlin/Wasm support is in Beta. The mat is ready. The move is safe.

-----

## 🗂️ SIPOC — The Shared UI Layer

|**Suppliers**           |**Inputs**                                                     |**Process**                                                                                                     |**Outputs**                                                                             |**Customers**                                                  |
|------------------------|---------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|---------------------------------------------------------------|
|JetBrains               |Compose Multiplatform framework (fork of Jetpack Compose)      |Compiles `@Composable` functions to each target: Skia on iOS/Desktop, Jetpack Compose on Android, Canvas on Wasm|Platform-native rendering with consistent Compose semantics                             |Users on every platform — who see a consistent, high-quality UI|
|Developer               |`@Composable` UI code in `commonMain`                          |Same function compiled and run on each platform                                                                 |One set of UI components, screens, and navigation across all targets                    |The product team — who ship one UI codebase instead of three   |
|Platform-specific tweaks|`expect`/`actual` for platform styling, `LocalContext`, haptics|Applied per platform where needed                                                                               |Native-feeling app: iOS scroll physics, Android back gesture, Desktop keyboard shortcuts|The end user — who feels at home on their platform             |

-----

## Part 1: Setting Up Compose Multiplatform 🔧

Compose Multiplatform ships as a separate Gradle plugin alongside KMP:

```kotlin
// shared/build.gradle.kts

plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
    alias(libs.plugins.jetbrainsCompose)      // ← CMP plugin
    alias(libs.plugins.compose.compiler)      // ← Compose compiler plugin
}

kotlin {
    androidTarget()
    iosArm64()
    iosSimulatorArm64()
    iosX64()
    jvm("desktop")
    wasmJs { browser(); binaries.executable() }

    sourceSets {
        commonMain.dependencies {
            // Compose Multiplatform — all in commonMain!
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)
            implementation(compose.components.resources)    // Shared resources
            implementation(compose.components.uiToolingPreview)

            // Navigation
            implementation(libs.navigation.compose)         // CMP navigation

            // Your shared business logic from previous episodes
            implementation(projects.shared.logic)
        }

        androidMain.dependencies {
            implementation(compose.preview)
            implementation(libs.androidx.activity.compose)
        }

        val desktopMain by getting {
            dependencies {
                implementation(compose.desktop.currentOs)
            }
        }
    }
}

// libs.versions.toml additions
// [plugins]
// jetbrainsCompose = { id = "org.jetbrains.compose", version = "1.8.0" }
// compose-compiler = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
```

-----

## Part 2: Your First Shared Composable Screen 🎨

```kotlin
// shared/src/commonMain/kotlin/com/example/shared/ui/PostsScreen.kt

import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.layout.*

@Composable
fun PostsScreen(viewModel: PostsViewModel) {
    val state by viewModel.state.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Posts") },
                actions = {
                    IconButton(onClick = viewModel::refresh) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(modifier = Modifier.padding(paddingValues)) {
            when (val current = state) {
                is NetworkResult.Loading -> {
                    Box(
                        modifier        = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
                is NetworkResult.Success -> {
                    PostsList(posts = current.data)
                }
                is NetworkResult.Error -> {
                    ErrorView(
                        message  = current.message,
                        onRetry  = viewModel::refresh
                    )
                }
            }
        }
    }
}

@Composable
private fun PostsList(posts: List<Post>) {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(8.dp),
        contentPadding      = PaddingValues(16.dp)
    ) {
        items(posts, key = { it.id }) { post ->
            PostCard(post = post)
        }
    }
}

@Composable
private fun PostCard(post: Post) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text  = post.title,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text  = post.body.take(100) + "...",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun ErrorView(message: String, onRetry: () -> Unit) {
    Column(
        modifier            = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(text = "Error: $message")
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onRetry) { Text("Try Again") }
    }
}
```

This `@Composable` function compiles and renders on every target. Not a single line of platform-specific code.

-----

## Part 3: Navigation — Moving Across the Mat 🧭

```kotlin
// shared/src/commonMain/kotlin/com/example/shared/ui/Navigation.kt

import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.toRoute
import kotlinx.serialization.Serializable

// Type-safe route definitions (Compose Navigation 2.x)
@Serializable object PostsList
@Serializable data class PostDetail(val postId: Int)

@Composable
fun AppNavigation(postsViewModel: PostsViewModel) {
    val navController = rememberNavController()

    NavHost(
        navController    = navController,
        startDestination = PostsList
    ) {
        composable<PostsList> {
            PostsScreen(
                viewModel = postsViewModel,
                onPostClick = { post ->
                    navController.navigate(PostDetail(post.id))
                }
            )
        }

        composable<PostDetail> { backStackEntry ->
            val route: PostDetail = backStackEntry.toRoute()
            PostDetailScreen(postId = route.postId)
        }
    }
}
```

-----

## Part 4: Shared Resources — Images, Strings, Fonts 📦

Compose Multiplatform provides a **shared resources** system. Place assets in `commonMain/composeResources`:

```
shared/src/commonMain/composeResources/
├── drawable/
│   ├── logo.svg          ← Works everywhere!
│   └── placeholder.svg
├── font/
│   └── Roboto-Regular.ttf
├── values/
│   └── strings.xml       ← Shared localised strings
└── values-nl/
    └── strings.xml       ← Dutch translation
```

```xml
<!-- shared/src/commonMain/composeResources/values/strings.xml -->
<resources>
    <string name="app_name">My App</string>
    <string name="posts_title">Posts</string>
    <string name="error_retry">Try Again</string>
    <string name="loading">Loading...</string>
</resources>
```

```kotlin
// Using resources in a composable
import com.example.shared.generated.resources.Res
import com.example.shared.generated.resources.logo
import com.example.shared.generated.resources.posts_title
import org.jetbrains.compose.resources.painterResource
import org.jetbrains.compose.resources.stringResource

@Composable
fun Header() {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Image(
            painter            = painterResource(Res.drawable.logo),
            contentDescription = null,
            modifier           = Modifier.size(48.dp)
        )
        Text(
            text  = stringResource(Res.string.posts_title),
            style = MaterialTheme.typography.headlineMedium
        )
    }
}
```

-----

## Part 5: Platform-Specific Tweaks — Individual Stretches 🤸

Even with shared UI, platforms sometimes need individual adjustments. `expect`/`actual` handles these:

```kotlin
// commonMain/kotlin/com/example/shared/ui/PlatformHaptics.kt

expect class HapticsController() {
    fun lightImpact()
    fun mediumImpact()
    fun selectionChanged()
}
```

```kotlin
// androidMain/kotlin/com/example/shared/ui/PlatformHaptics.android.kt

import android.content.Context
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager

actual class HapticsController {
    // In real code, inject context via Koin
    actual fun lightImpact()       { /* Android haptics via Vibrator */ }
    actual fun mediumImpact()      { /* Android haptics via Vibrator */ }
    actual fun selectionChanged()  { /* Android haptics via Vibrator */ }
}
```

```kotlin
// iosMain/kotlin/com/example/shared/ui/PlatformHaptics.ios.kt

import platform.UIKit.*

actual class HapticsController {
    actual fun lightImpact() {
        UIImpactFeedbackGenerator(UIImpactFeedbackStyleLight)
            .impactOccurred()
    }
    actual fun mediumImpact() {
        UIImpactFeedbackGenerator(UIImpactFeedbackStyleMedium)
            .impactOccurred()
    }
    actual fun selectionChanged() {
        UISelectionFeedbackGenerator().selectionChanged()
    }
}
```

**Platform-specific colours and themes:**

```kotlin
// commonMain
@Composable
expect fun PlatformTheme(content: @Composable () -> Unit)
```

```kotlin
// androidMain
@Composable
actual fun PlatformTheme(content: @Composable () -> Unit) {
    // Android can use dynamic colour (Material You)
    val colorScheme = if (Build.VERSION.SDK_INT >= 31) {
        dynamicLightColorScheme(LocalContext.current)
    } else {
        lightColorScheme()
    }
    MaterialTheme(colorScheme = colorScheme, content = content)
}
```

```kotlin
// iosMain
@Composable
actual fun PlatformTheme(content: @Composable () -> Unit) {
    // iOS uses a fixed colour scheme that matches iOS conventions
    MaterialTheme(
        colorScheme = lightColorScheme(
            primary = Color(0xFF007AFF)  // iOS system blue
        ),
        content = content
    )
}
```

-----

## Part 6: The Platform Entry Points 🚪

Each platform needs a minimal entry point that hands control to the shared Compose code:

**Android:**

```kotlin
// androidApp/src/main/kotlin/com/example/android/MainActivity.kt

import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.example.shared.ui.AppNavigation
import org.koin.androidx.viewmodel.ext.android.viewModel

class MainActivity : ComponentActivity() {
    private val postsVM: PostsAndroidViewModel by viewModel()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            PlatformTheme {           // Platform-specific theme wrapper
                AppNavigation(postsVM.sharedViewModel)
            }
        }
    }
}
```

**iOS:**

```swift
// iosApp/ContentView.swift
import SwiftUI
import Shared

struct ContentView: View {
    var body: some View {
        // Compose Multiplatform renders inside a UIKitView
        ComposeView()
    }
}

// The Kotlin side provides the Compose entry point
// iosApp/src/.../MainViewController.kt
import androidx.compose.ui.window.ComposeUIViewController
import com.example.shared.ui.AppNavigation

fun MainViewController() = ComposeUIViewController {
    AppNavigation(/* inject viewModel */)
}
```

**Desktop:**

```kotlin
// desktopApp/src/main/kotlin/com/example/desktop/Main.kt

import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import androidx.compose.ui.window.rememberWindowState
import com.example.shared.ui.AppNavigation

fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        state          = rememberWindowState(width = 800.dp, height = 600.dp),
        title          = "My App"
    ) {
        PlatformTheme {
            AppNavigation(/* inject viewModel */)
        }
    }
}
```

-----

## Part 7: The UI Architecture — Everything Shared 🏗️

With Compose Multiplatform, the sharing ratio is dramatically higher:

```
Traditional KMP (business logic only):
├── commonMain:     30% of total codebase (business logic, data layer)
├── androidMain:    35% (Android UI, Android-specific code)
└── iosMain:        35% (iOS UI/SwiftUI, iOS-specific code)
Total reuse: ~30%

Compose Multiplatform KMP (shared UI):
├── commonMain:     90% of total codebase
│   ├── UI layer:        all @Composable screens and components
│   ├── Navigation:      all routes and navigation graph
│   ├── Business logic:  all repositories, viewmodels, use cases
│   └── Data layer:      all networking, caching, persistence
├── androidMain:     5% (entry point, AndroidManifest, platform tweaks)
└── iosMain:         5% (entry point, Info.plist, platform tweaks)
Total reuse: ~90%
```

-----

## What’s Next: Tournament Play 🏆

*The game enters the advanced rounds. More players, more circles, more simultaneous positions.*

In **Episode 7**, we enter tournament territory — multi-module KMP architecture, the K2 compiler’s advantages, SKIE for seamless Swift interoperability, Kotlin/Wasm for browser targets, and how to build and publish a KMP library without needing macOS in your CI pipeline. The full competitive game.

-----

**🔗 Resources**

- **Compose Multiplatform**: [jb.gg/compose](https://jb.gg/compose)
- **CMP iOS stable announcement**: [blog.jetbrains.com/kotlin/2025/05/compose-multiplatform-ios-stable](https://blog.jetbrains.com/kotlin/2025/05)
- **Compose Multiplatform resources**: [kotlinlang.org/docs/compose-multiplatform-resources](https://kotlinlang.org/docs/compose-multiplatform-resources-usage.html)
- **Navigation Compose**: [kotlinlang.org/docs/compose-navigation-routing](https://kotlinlang.org/docs/compose-navigation-routing.html)

-----

*🎯 Twister Game of Kotlin Multiplatform — one mat, many platforms, perfect balance.*
