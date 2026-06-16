---
title: "Twister Game of Kotlin Multiplatform 🎯 Ep.8"
published: false
description: "Episode 8: The finale. The mat is full. Every player holds their position. The game is won not by the boldest move but by staying balanced the longest. Testing strategy across platforms. Jetpack libraries in KMP. Version management. Performance profiling. The complete production deployment checklist. And a look at where the game goes next — Kotlin/Wasm maturing, Swift interop improving, the mat growing."
tags: [kotlin, multiplatform, testing, production]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/twister-kmp-episode-08.png"
series: "Twister Game of Kotlin Multiplatform"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 8: Winning the Game — Production and Beyond

-----

## The Final Round 🏆

The music has stopped. Every player is balanced on the mat. No more new moves from the spinner. The question now is not “can you reach the next circle?” — the question is “how long can you stay where you are?”

Winning at Twister is about endurance, not acrobatics. It is about the sustainable position — balanced, stable, maintainable across time. The most impressive stretch in Episode 3 means nothing if the player falls over in Episode 8.

Production software is identical. The most elegant `expect`/`actual` implementation means nothing if there are no tests to verify it works. The most beautiful shared Compose UI means nothing if it does not meet the performance bar of the native competition. The most comprehensive architecture means nothing if the team cannot maintain it.

This final episode is about staying on the mat. Production quality. Testing. Performance. The Jetpack libraries that now play on the same mat. And where the game goes next.

-----

## 🗂️ SIPOC — The Production Deployment

|**Suppliers**        |**Inputs**                                                           |**Process**                                                                                 |**Outputs**                                                             |**Customers**                                                                            |
|---------------------|---------------------------------------------------------------------|--------------------------------------------------------------------------------------------|------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
|Testing framework    |Unit tests in `commonTest`, platform tests in `androidTest`/`iosTest`|`./gradlew allTests` runs Kotlin/JVM tests on Desktop, Kotlin/Native tests on iOS simulators|A test suite that verifies behaviour across all platforms               |The CI pipeline — which gates deployment on test success                                 |
|Jetpack KMP libraries|Room, DataStore, ViewModel, Paging — now multiplatform               |Same Jetpack library used in both Android app and shared KMP module                         |Shared persistence and architecture components with a single Jetpack API|Android developers who already know Jetpack; iOS developers who benefit from shared logic|
|Production build     |Release-flavoured KMP artifacts                                      |`./gradlew :shared:assembleRelease` + XCFramework build + Wasm distribution                 |Signed APK/AAB, iOS XCFramework, Desktop installer, Wasm bundle         |App Store Connect, Google Play, desktop distribution, web server                         |

-----

## Part 1: The Testing Strategy — Referee with a Stopwatch ⏱️

**Test pyramid for KMP:**

```
                    ┌────────────────────────────┐
                    │  E2E / Integration Tests   │ ← Platform-specific
                    │  (Maestro, XCTest, Appium) │   Few, expensive, slow
                    └────────────────────────────┘
              ┌─────────────────────────────────────────┐
              │      Platform-specific Unit Tests       │ ← androidTest, iosTest
              │ (JUnit on Android, Kotlin/Native on iOS) │
              └─────────────────────────────────────────┘
        ┌─────────────────────────────────────────────────────┐
        │             commonTest (The Bulk of Tests)          │ ← ~80% of all tests
        │   Runs on JVM + iOS Simulator via kotlin.test       │
        └─────────────────────────────────────────────────────┘
```

**Writing tests in `commonTest`:**

```kotlin
// shared/src/commonTest/kotlin/com/example/shared/repository/PostRepositoryTest.kt

import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class PostRepositoryTest {

    private val mockClient = createMockHttpClient(
        responseBody = """
            [
                {"id": 1, "title": "First Post", "body": "Hello", "userId": 1},
                {"id": 2, "title": "Second Post", "body": "World", "userId": 1}
            ]
        """.trimIndent()
    )

    private val repository = PostRepository(mockClient)

    @Test
    fun `getPosts returns list of posts`() = runTest {
        val result = repository.getPosts()

        assertTrue(result.isSuccess)
        assertEquals(2, result.getOrThrow().size)
        assertEquals("First Post", result.getOrThrow().first().title)
    }

    @Test
    fun `getPost by id returns correct post`() = runTest {
        val result = repository.getPost(1)

        assertIs<Result.Success>(result)
        assertEquals(1, result.getOrThrow().id)
    }

    @Test
    fun `getPosts on network failure returns failure result`() = runTest {
        val failingClient = createMockHttpClient(shouldFail = true)
        val failingRepo   = PostRepository(failingClient)

        val result = failingRepo.getPosts()

        assertTrue(result.isFailure)
    }
}
```

**Testing the `expect`/`actual` implementation:**

```kotlin
// shared/src/commonTest/kotlin/com/example/shared/PlatformInfoTest.kt

import kotlin.test.Test
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class PlatformInfoTest {

    @Test
    fun `platformInfo provides a non-empty OS name`() {
        val info = PlatformInfo()

        assertNotNull(info.operatingSystem)
        assertTrue(info.operatingSystem.isNotBlank())
    }

    @Test
    fun `platformInfo provides a version string`() {
        val info = PlatformInfo()

        assertNotNull(info.version)
        assertTrue(info.version.isNotBlank())
    }
}

// This test runs on both JVM (via Android/Desktop) AND Kotlin/Native (via iOS simulator)
// If the expect/actual implementation is broken on any platform, this test catches it
```

**Running tests on all platforms:**

```bash
# Run all tests (JVM + iOS simulator if on macOS)
./gradlew :shared:allTests

# Run only JVM tests (works everywhere, including Linux CI)
./gradlew :shared:jvmTest

# Run only Android unit tests
./gradlew :shared:testDebugUnitTest

# Run Kotlin/Native tests on iOS simulator (requires macOS)
./gradlew :shared:iosSimulatorArm64Test

# Run with test reporting
./gradlew :shared:allTests --tests "com.example.shared.*"
```

-----

## Part 2: Testing with SQLDelight 🗄️

```kotlin
// shared/src/commonTest/kotlin/com/example/shared/repository/LocalPostRepositoryTest.kt

import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver
import com.example.shared.cache.AppDatabase
import kotlinx.coroutines.test.runTest
import kotlin.test.*

class LocalPostRepositoryTest {

    // In-memory database for tests — no file system required
    private val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).also {
        AppDatabase.Schema.create(it)
    }
    private val database    = AppDatabase(driver)
    private val repository  = LocalPostRepository(database)

    @AfterTest
    fun cleanup() = runTest {
        repository.clearAll()
    }

    @Test
    fun `insertPosts stores posts correctly`() = runTest {
        val posts = listOf(
            Post(id = 1, title = "Test", body = "Body", userId = 1)
        )

        repository.insertPosts(posts)
        val stored = repository.getPostById(1L)

        assertNotNull(stored)
        assertEquals("Test", stored.title)
    }

    @Test
    fun `getAllPostsFlow emits updates when data changes`() = runTest {
        val results = mutableListOf<List<Post>>()

        // Collect the first two emissions
        val job = launch {
            repository.getAllPostsFlow()
                .take(2)
                .collect { results.add(it) }
        }

        // Insert data — Flow should emit again
        repository.insertPosts(listOf(Post(1, "Post 1", "Body 1", 1)))
        delay(100)
        job.join()

        assertEquals(2, results.size)  // Initial emission + after insert
        assertEquals(1, results.last().size)
    }
}
```

*Note: The in-memory JdbcSqliteDriver works in commonTest via JVM. For pure Kotlin/Native, use `NativeSqliteDriver` in an iOS-specific test.*

-----

## Part 3: Jetpack Libraries in KMP — The Familiar Circles 🔵

Google has expanded Jetpack library support for KMP significantly. These libraries no longer require Android — they share their implementation across platforms:

|Jetpack Library|KMP Status              |Available targets    |
|---------------|------------------------|---------------------|
|**Room**       |✅ Stable                |Android, iOS, Desktop|
|**DataStore**  |✅ Stable                |Android, iOS, Desktop|
|**Collections**|✅ Stable                |All                  |
|**ViewModel**  |✅ Stable                |Android, iOS, Desktop|
|**SavedState** |✅ Stable                |Android, iOS, Desktop|
|**Paging 3**   |✅ Stable                |Android, iOS, Desktop|
|**Navigation** |✅ Stable (Compose Nav 3)|Android, iOS, Desktop|
|**Annotation** |✅ Stable                |All                  |
|**Lifecycle**  |✅ Stable                |Android, iOS, Desktop|

**Room in KMP — the alternative to SQLDelight:**

```kotlin
// shared/src/commonMain/kotlin/com/example/shared/db/PostDao.kt

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface PostDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(posts: List<PostEntity>)

    @Query("SELECT * FROM posts ORDER BY id")
    fun getAllPosts(): Flow<List<PostEntity>>

    @Query("SELECT * FROM posts WHERE id = :id")
    suspend fun getPostById(id: Int): PostEntity?

    @Query("DELETE FROM posts")
    suspend fun clearAll()
}

// shared/src/commonMain/kotlin/com/example/shared/db/AppDatabase.kt

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [PostEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun postDao(): PostDao
}
```

```kotlin
// androidMain/kotlin/com/example/shared/db/DatabaseFactory.android.kt

import android.content.Context
import androidx.room.Room

fun createDatabase(context: Context): AppDatabase =
    Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
        .build()

// iosMain/kotlin/com/example/shared/db/DatabaseFactory.ios.kt

import androidx.room.Room
import platform.Foundation.NSHomeDirectory

fun createDatabase(): AppDatabase {
    val dbFile = NSHomeDirectory() + "/Library/Databases/app.db"
    return Room.databaseBuilder<AppDatabase>(
        name = dbFile
    ).build()
}
```

-----

## Part 4: Performance — Staying Balanced Under Pressure ⚡

**Compose Multiplatform on iOS — CMP 1.8.0 performance:**

```kotlin
// For smooth 60fps rendering on iOS, be aware of:

// ✅ DO: Use lazy layouts for long lists
LazyColumn { items(posts) { PostCard(it) } }
LazyVerticalGrid(columns = GridCells.Fixed(2)) { /* ... */ }

// ❌ DON'T: Column with thousands of items
Column { posts.forEach { PostCard(it) } }  // Renders ALL at once — OOM risk

// ✅ DO: Key your list items for efficient diffing
items(posts, key = { it.id }) { PostCard(it) }

// ✅ DO: Use remember for expensive calculations
val processedPosts by remember(rawPosts) {
    derivedStateOf { rawPosts.sortedByDescending { it.date } }
}

// ✅ DO: Use Dispatchers.Default for CPU-intensive work
viewModelScope.launch(Dispatchers.Default) {
    val processed = expensiveDataProcessing(input)
    withContext(Dispatchers.Main) { _state.value = processed }
}
```

**Profiling KMP code:**

```kotlin
// Use the Kotlin/Native memory profiler for iOS
// In your shared code, you can check the current platform for debug decisions:

expect fun isDebugBuild(): Boolean

// androidMain:
actual fun isDebugBuild(): Boolean = BuildConfig.DEBUG

// iosMain:
actual fun isDebugBuild(): Boolean {
    return platform.Foundation.NSBundle.mainBundle
        .objectForInfoDictionaryKey("CFBundleDevelopmentRegion") != null
    // More robust: check DEBUG flag in scheme environment
}
```

-----

## Part 5: Version Management — The Stable Grip 📋

```toml
# gradle/libs.versions.toml — full production version catalogue (2025/2026)

[versions]
kotlin                = "2.1.0"
agp                   = "8.5.0"
compose-multiplatform = "1.8.0"
coroutines            = "1.9.0"
serialization         = "1.7.3"
ktor                  = "3.0.3"
sqldelight            = "2.0.2"
datetime              = "0.6.1"
koin                  = "4.1.0"
room                  = "2.7.0"
datastore             = "1.1.1"
lifecycle             = "2.8.3"
navigation            = "2.9.0"
multiplatform-settings = "1.2.0"
skie                  = "0.10.0"

[libraries]
# Core
kotlinx-coroutines-core    = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core",    version.ref = "coroutines" }
kotlinx-serialization-json = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version.ref = "serialization" }
kotlinx-datetime           = { module = "org.jetbrains.kotlinx:kotlinx-datetime",           version.ref = "datetime" }

# Ktor
ktor-client-core                 = { module = "io.ktor:ktor-client-core",                       version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation",        version.ref = "ktor" }
ktor-serialization-kotlinx-json  = { module = "io.ktor:ktor-serialization-kotlinx-json",       version.ref = "ktor" }
ktor-client-okhttp               = { module = "io.ktor:ktor-client-okhttp",                     version.ref = "ktor" }
ktor-client-darwin               = { module = "io.ktor:ktor-client-darwin",                     version.ref = "ktor" }
ktor-client-cio                  = { module = "io.ktor:ktor-client-cio",                        version.ref = "ktor" }
ktor-client-js                   = { module = "io.ktor:ktor-client-js",                         version.ref = "ktor" }
ktor-client-mock                 = { module = "io.ktor:ktor-client-mock",                       version.ref = "ktor" }

# Persistence
sqldelight-runtime        = { module = "app.cash.sqldelight:runtime",               version.ref = "sqldelight" }
sqldelight-coroutines     = { module = "app.cash.sqldelight:coroutines-extensions", version.ref = "sqldelight" }
sqldelight-android-driver = { module = "app.cash.sqldelight:android-driver",        version.ref = "sqldelight" }
sqldelight-native-driver  = { module = "app.cash.sqldelight:native-driver",         version.ref = "sqldelight" }
sqldelight-sqlite-driver  = { module = "app.cash.sqldelight:sqlite-driver",         version.ref = "sqldelight" }
room-runtime              = { module = "androidx.room:room-runtime",                 version.ref = "room" }
room-compiler             = { module = "androidx.room:room-compiler",                version.ref = "room" }
datastore-preferences     = { module = "androidx.datastore:datastore-preferences",  version.ref = "datastore" }

# Architecture
lifecycle-viewmodel    = { module = "androidx.lifecycle:lifecycle-viewmodel",      version.ref = "lifecycle" }
navigation-compose     = { module = "androidx.navigation:navigation-compose",      version.ref = "navigation" }
koin-core              = { module = "io.insert-koin:koin-core",                   version.ref = "koin" }
koin-android           = { module = "io.insert-koin:koin-android",                version.ref = "koin" }
koin-compose           = { module = "io.insert-koin:koin-compose",                version.ref = "koin" }
multiplatform-settings = { module = "com.russhwolf:multiplatform-settings",       version.ref = "multiplatform-settings" }

[plugins]
kotlinMultiplatform  = { id = "org.jetbrains.kotlin.multiplatform",         version.ref = "kotlin" }
androidApplication   = { id = "com.android.application",                    version.ref = "agp" }
androidLibrary       = { id = "com.android.library",                        version.ref = "agp" }
jetbrainsCompose     = { id = "org.jetbrains.compose",                      version.ref = "compose-multiplatform" }
composeCompiler      = { id = "org.jetbrains.kotlin.plugin.compose",        version.ref = "kotlin" }
kotlinSerialization  = { id = "org.jetbrains.kotlin.plugin.serialization",  version.ref = "kotlin" }
sqlDelight           = { id = "app.cash.sqldelight",                        version.ref = "sqldelight" }
skie                 = { id = "co.touchlab.skie",                           version.ref = "skie" }
```

-----

## Part 6: The Complete Production Checklist ✅

```
CODE QUALITY:
  [✓] All expect declarations have actual for every target
  [✓] commonMain never imports platform-specific APIs (checked by compiler)
  [✓] No Android Context leaked into domain/data commonMain
  [✓] Coroutines structured concurrency — no GlobalScope in shared code
  [✓] Sealed Result types for all async operations (no raw exceptions)

TESTING:
  [✓] commonTest covers all business logic (>80% of test suite)
  [✓] expect/actual implementations tested with platform-specific tests
  [✓] Mock HTTP engine used in all networking tests
  [✓] In-memory SQLite driver used in database tests
  [✓] allTests passes on CI for every PR

PERFORMANCE:
  [✓] LazyColumn/LazyRow for all lists (not Column with forEach)
  [✓] Items keyed by stable ID for list diffing
  [✓] CPU-intensive work on Dispatchers.Default
  [✓] No blocking calls on Dispatchers.Main
  [✓] SKIE configured for natural Swift async API

SECURITY:
  [✓] Secrets never in source code — use BuildConfig/plist/env vars
  [✓] HTTPS enforced in Ktor (no HTTP in production)
  [✓] Sensitive data cleared from memory when not needed
  [✓] Database encrypted on Android (SQLCipher) if app requires it

BUILD:
  [✓] libs.versions.toml with all dependencies pinned
  [✓] Release builds signed (Android: keystore, iOS: Xcode signing)
  [✓] ProGuard/R8 rules for Android (KMP-generated code preserved)
  [✓] Static framework (isStatic = true) for iOS — simpler to embed
  [✓] CI runs on Linux for Android/Desktop/Wasm
  [✓] macOS runner for XCFramework production build
  [✓] Version code/name automated from git tags

DISTRIBUTION:
  [✓] Android: Google Play Console, AAB format
  [✓] iOS: App Store Connect, XCFramework embedded in Xcode project
  [✓] Desktop: platform-specific installer (DMG, MSI, DEB/RPM)
  [✓] Web/Wasm: static hosting (Netlify, Vercel, GitHub Pages, CDN)
```

-----

## Part 7: The Sharing Calculator 🧮

A realistic code sharing breakdown for a production KMP app:

```kotlin
// Estimated code sharing with full KMP + Compose Multiplatform stack

// Business Logic Layer (100% shared):
//   - Domain entities
//   - Repository interfaces and implementations
//   - Use cases
//   - ViewModels

// Data Layer (95% shared):
//   - Ktor networking (100% shared)
//   - SQLDelight schemas and queries (100% shared)
//   - Platform drivers (platform-specific — ~5%)

// UI Layer (85-95% shared with Compose Multiplatform):
//   - All screens and components
//   - Navigation
//   - Resources (strings, images)
//   - Platform theme tweaks (~5-15%)

// Overall: 90%+ code shared across Android, iOS, Desktop, and Web
```

-----

## Part 8: Where the Game Goes Next 🔮

The KMP game is still developing new rules:

**Near-term (2025-2026):**

- Kotlin/Wasm reaching stable — full browser-parity with mobile
- Swift export improvements — direct Kotlin-Swift interop without Obj-C layer
- Declarative Kotlin Gradle DSL — simpler `build.gradle.kts` for KMP
- Multi-module Wasm compilation — faster builds, dynamic loading

**The JetBrains 2025 roadmap prioritises:**

1. iOS developer experience (faster compilation, better debugging)
1. Web targets (Wasm Beta → Stable)
1. IDE improvements for multiplatform development

-----

## The Game Is Won — But the Mat Stays Unrolled 🎯

*The referee lowers the spinner. Every player holds their position.*

*Android — right hand on yellow. iOS — left foot on blue. Desktop — right foot on red. Wasm — left hand on green.*

*The mat holds. The code ships. The users don’t know or care that one Kotlin codebase powers every app they just opened.*

**That is the win.**

-----

## The Full Series Recap 🗺️

|Episode|The Twister Move       |KMP Concept          |What We Built                                    |
|-------|-----------------------|---------------------|-------------------------------------------------|
|1      |Unrolling the mat      |KMP overview         |First project, targets, basic Gradle             |
|2      |Left hand red          |Source sets          |Complete source set hierarchy, intermediate sets |
|3      |Referee’s call         |expect/actual        |Platform bridge, 4 forms, real-world patterns    |
|4      |The double stretch     |Ktor networking      |Full shared data layer with Ktor + serialization |
|5      |Two players, one circle|SQLDelight + Koin    |Database, DI, multiplatform settings             |
|6      |Shared moves           |Compose Multiplatform|Shared UI, navigation, resources, platform tweaks|
|7      |Tournament play        |Advanced architecture|Clean Architecture, SKIE, Wasm, multi-module     |
|8      |*Winning the game*     |Production           |Testing, Jetpack KMP, performance, CI/CD         |

-----

**🔗 Resources**

- **KMP Documentation**: [kotlinlang.org/docs/multiplatform](https://kotlinlang.org/docs/multiplatform.html)
- **Compose Multiplatform**: [jb.gg/compose](https://jb.gg/compose)
- **klibs.io**: [klibs.io](https://klibs.io) — Discover KMP-ready libraries
- **KMP Wizard**: [kmp.jetbrains.com](https://kmp.jetbrains.com) — Generate your project
- **KMP Sample Apps**: [github.com/JetBrains/compose-multiplatform](https://github.com/JetBrains/compose-multiplatform/tree/master/examples)
- **SKIE**: [skie.touchlab.co](https://skie.touchlab.co)
- **Kotlin/Wasm**: [kotlinlang.org/docs/wasm-overview](https://kotlinlang.org/docs/wasm-overview.html)

-----

*🎯 Twister Game of Kotlin Multiplatform — one mat, many platforms, perfect balance.*

*The game never really ends. The mat just gets bigger.*
