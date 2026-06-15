-----

## title: “Twister Game of Kotlin Multiplatform! Ep.5: Two Players, One Circle — SQLDelight and Persistence”
published: false
description: “Episode 5: Two players, one circle — Android and iOS both need local persistence, but each uses different database drivers. SQLDelight generates type-safe Kotlin from SQL that works on every platform. Koin dependency injection wires the right driver to the right platform. Multiplatform Settings handles simple key-value storage. The shared persistence layer, built completely.”
tags: [kotlin, multiplatform, sqldelight, persistence]
cover_image: “<https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/twister-kmp-episode-05.png>”
series: “Twister Game of Kotlin Multiplatform”
canonical_url: “”
organization: “the-software-s-journey”
part: 1

# Twister Game of Kotlin Multiplatform! 🎯

## Episode 5: Two Players, One Circle — SQLDelight and Persistence

-----

## One Circle, Two Hands 🔵🟢

There is a particular moment in Twister where two different players are reaching for the same circle simultaneously — neither wants to lift, both need to stay there, and the entire game depends on them both holding their position without toppling each other.

Android and iOS both need local storage. They both need a database. But they cannot share the same database driver — Android uses SQLite through Android’s built-in driver, while iOS uses SQLite through Kotlin/Native’s native driver. Same circle (SQLite), two completely different ways of reaching it.

**SQLDelight** is the mechanism that makes this work. You write SQL once. SQLDelight generates type-safe Kotlin code in `commonMain`. Each platform provides its own driver implementation. The game stays balanced.

-----

## 🗂️ SIPOC — The Persistence Layer

|**Suppliers**         |**Inputs**                                          |**Process**                                                                            |**Outputs**                                                                   |**Customers**                                                                               |
|----------------------|----------------------------------------------------|---------------------------------------------------------------------------------------|------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
|Developer             |SQL schema files (`.sq`) defining tables and queries|SQLDelight parses SQL at build time; generates Kotlin interfaces in `commonMain`       |A type-safe `AppDatabase` interface and generated query functions             |Any `commonMain` code — calls `database.postQueries.getAll()` without knowing the platform  |
|Platform developer    |A platform-specific `SqlDriver` implementation      |SQLDelight `AndroidSqliteDriver` (Android) or `NativeSqliteDriver` (iOS)               |The driver is the only platform-specific piece — the rest is generated Kotlin |The `AppDatabase` factory — which receives the driver and returns a usable database         |
|Koin DI               |A Koin module declaration per platform              |Registers the right driver for the current platform; injects it where needed           |Dependency injection that feels identical in commonMain regardless of platform|ViewModels, Repositories — which receive an `AppDatabase` without knowing how it was created|
|Multiplatform Settings|Key-value preference calls                          |Delegates to SharedPreferences (Android), NSUserDefaults (iOS), or Java Prefs (Desktop)|Persistent key-value storage in commonMain                                    |Any simple preference storage — without expect/actual boilerplate                           |

-----

## Part 1: SQLDelight Setup 🔧

**Gradle configuration:**

```kotlin
// shared/build.gradle.kts

plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
    alias(libs.plugins.sqlDelight)           // ← Add this plugin
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.sqldelight.runtime)       // The shared runtime
            implementation(libs.sqldelight.coroutines)    // Flow integration
        }

        androidMain.dependencies {
            implementation(libs.sqldelight.android.driver)
        }

        iosMain.dependencies {
            implementation(libs.sqldelight.native.driver)
        }

        val desktopMain by getting {
            dependencies {
                implementation(libs.sqldelight.sqlite.driver)  // Desktop JVM
            }
        }
    }
}

// Configure SQLDelight code generation
sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.shared.cache")
            generateAsync = true   // Generates coroutine-based async queries
        }
    }
}
```

**`libs.versions.toml` additions:**

```toml
[versions]
sqldelight = "2.0.2"

[libraries]
sqldelight-runtime         = { module = "app.cash.sqldelight:runtime",                  version.ref = "sqldelight" }
sqldelight-coroutines      = { module = "app.cash.sqldelight:coroutines-extensions",    version.ref = "sqldelight" }
sqldelight-android-driver  = { module = "app.cash.sqldelight:android-driver",           version.ref = "sqldelight" }
sqldelight-native-driver   = { module = "app.cash.sqldelight:native-driver",            version.ref = "sqldelight" }
sqldelight-sqlite-driver   = { module = "app.cash.sqldelight:sqlite-driver",            version.ref = "sqldelight" }

[plugins]
sqlDelight = { id = "app.cash.sqldelight", version.ref = "sqldelight" }
```

-----

## Part 2: Writing the SQL Schema 📝

SQLDelight schemas live in a specific directory structure. The `.sq` file name becomes the query class name:

```
shared/
└── src/
    └── commonMain/
        └── sqldelight/
            └── com/
                └── example/
                    └── shared/
                        └── cache/
                            ├── Post.sq        ← Generates PostQueries
                            └── User.sq        ← Generates UserQueries
```

```sql
-- shared/src/commonMain/sqldelight/com/example/shared/cache/Post.sq

CREATE TABLE Post (
    id      INTEGER NOT NULL PRIMARY KEY,
    title   TEXT    NOT NULL,
    body    TEXT    NOT NULL,
    user_id INTEGER NOT NULL
);

-- Named query: generates a function insertPost(id, title, body, userId)
insertPost:
INSERT OR REPLACE INTO Post(id, title, body, user_id)
VALUES (?, ?, ?, ?);

-- Named query: generates selectAll() returning Flow<List<Post>>
selectAll:
SELECT * FROM Post ORDER BY id;

-- Named query: generates selectById(id) returning Post?
selectById:
SELECT * FROM Post WHERE id = ?;

-- Named query: generates deleteAll()
deleteAll:
DELETE FROM Post;

-- Named query: generates deleteById(id)
deleteById:
DELETE FROM Post WHERE id = ?;

-- Named query: joins two tables — SQLDelight generates the result type!
selectPostWithUser:
SELECT Post.id, Post.title, Post.body, User.name AS author_name
FROM Post
INNER JOIN User ON Post.user_id = User.id
WHERE Post.id = ?;
```

SQLDelight generates a complete `PostQueries` interface with type-safe methods. Compile-time SQL validation — a typo in your SQL fails the build, not at runtime.

-----

## Part 3: The Database Driver Factory — expect/actual Pattern 🏭

```kotlin
// commonMain/kotlin/com/example/shared/cache/DatabaseDriverFactory.kt

import app.cash.sqldelight.db.SqlDriver

// The contract: create a driver for this platform
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}
```

```kotlin
// androidMain/kotlin/com/example/shared/cache/DatabaseDriverFactory.android.kt

import android.content.Context
import app.cash.sqldelight.driver.android.AndroidSqliteDriver
import com.example.shared.cache.AppDatabase

actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver =
        AndroidSqliteDriver(
            schema  = AppDatabase.Schema,
            context = context,
            name    = "app.db"
        )
}
```

```kotlin
// iosMain/kotlin/com/example/shared/cache/DatabaseDriverFactory.ios.kt

import app.cash.sqldelight.driver.native.NativeSqliteDriver
import com.example.shared.cache.AppDatabase

actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver =
        NativeSqliteDriver(
            schema   = AppDatabase.Schema,
            name     = "app.db"
        )
}
```

```kotlin
// jvmMain/kotlin/com/example/shared/cache/DatabaseDriverFactory.jvm.kt

import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver
import com.example.shared.cache.AppDatabase
import java.util.Properties

actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver =
        JdbcSqliteDriver(
            url        = JdbcSqliteDriver.IN_MEMORY,
            properties = Properties().apply { put("foreign_keys", "true") }
        ).also {
            AppDatabase.Schema.create(it)
        }
}
```

-----

## Part 4: The Database Repository 🏛️

```kotlin
// commonMain/kotlin/com/example/shared/repository/LocalPostRepository.kt

import app.cash.sqldelight.coroutines.asFlow
import app.cash.sqldelight.coroutines.mapToList
import com.example.shared.cache.AppDatabase
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.withContext

class LocalPostRepository(private val database: AppDatabase) {

    private val queries = database.postQueries

    // ── Read ──────────────────────────────────────────────────────

    // Returns a Flow that automatically emits when the database changes
    fun getAllPostsFlow(): Flow<List<Post>> =
        queries.selectAll()
            .asFlow()
            .mapToList(Dispatchers.Default)
            .map { dbPosts ->
                dbPosts.map { it.toPost() }    // Map DB type to domain type
            }

    suspend fun getPostById(id: Long): Post? =
        withContext(Dispatchers.Default) {
            queries.selectById(id).executeAsOneOrNull()?.toPost()
        }

    // ── Write ─────────────────────────────────────────────────────

    suspend fun insertPosts(posts: List<Post>) =
        withContext(Dispatchers.Default) {
            database.transaction {
                posts.forEach { post ->
                    queries.insertPost(
                        id      = post.id.toLong(),
                        title   = post.title,
                        body    = post.body,
                        user_id = post.userId.toLong()
                    )
                }
            }
        }

    suspend fun clearAll() = withContext(Dispatchers.Default) {
        queries.deleteAll()
    }

    suspend fun deletePost(id: Long) = withContext(Dispatchers.Default) {
        queries.deleteById(id)
    }
}

// Mapping from SQLDelight generated type to domain type
private fun com.example.shared.cache.Post.toPost(): Post =
    Post(
        id     = id.toInt(),
        title  = title,
        body   = body,
        userId = user_id.toInt()
    )
```

-----

## Part 5: Dependency Injection with Koin 💉

Koin 4.1 introduced `KoinMultiplatformApplication` — a single-line setup for KMP projects:

```kotlin
// commonMain/kotlin/com/example/shared/di/CommonModule.kt

import org.koin.core.module.Module
import org.koin.core.module.dsl.singleOf
import org.koin.dsl.module

val commonModule = module {
    // HTTP client — shared across platforms
    single { createHttpClient() }

    // Network repository — uses the shared HttpClient
    singleOf(::PostRepository)

    // Database repository — needs AppDatabase from the platform module
    singleOf(::LocalPostRepository)

    // The combined repository that caches remote data locally
    singleOf(::CachedPostRepository)

    // ViewModels
    factory { PostsViewModel(get(), get()) }
}

// Platform modules declare their specific dependencies
expect val platformModule: Module
```

```kotlin
// androidMain/kotlin/com/example/shared/di/PlatformModule.android.kt

import android.content.Context
import app.cash.sqldelight.driver.android.AndroidSqliteDriver
import com.example.shared.cache.AppDatabase
import com.example.shared.cache.DatabaseDriverFactory
import org.koin.android.ext.koin.androidContext
import org.koin.core.module.Module
import org.koin.dsl.module

actual val platformModule: Module = module {
    // Provide the Android-specific driver factory with the Android Context
    single { DatabaseDriverFactory(androidContext()) }

    // Create the database using the factory
    single {
        val factory: DatabaseDriverFactory = get()
        AppDatabase(factory.createDriver())
    }
}
```

```kotlin
// iosMain/kotlin/com/example/shared/di/PlatformModule.ios.kt

import com.example.shared.cache.AppDatabase
import com.example.shared.cache.DatabaseDriverFactory
import org.koin.core.module.Module
import org.koin.dsl.module

actual val platformModule: Module = module {
    // iOS doesn't need Context — the factory is simpler
    single { DatabaseDriverFactory() }

    single {
        val factory: DatabaseDriverFactory = get()
        AppDatabase(factory.createDriver())
    }
}
```

**Starting Koin:**

```kotlin
// commonMain/kotlin/com/example/shared/KoinSetup.kt

import org.koin.core.KoinApplication
import org.koin.core.context.startKoin

fun initKoin(additionalModules: List<org.koin.core.module.Module> = emptyList()): KoinApplication =
    startKoin {
        modules(commonModule, platformModule)
        modules(additionalModules)
    }
```

```kotlin
// androidApp — Application class
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        initKoin(
            additionalModules = listOf(
                module { single<Context> { applicationContext } }
            )
        )
    }
}
```

```swift
// iosApp — AppDelegate or @main App struct
@main
struct IOSApp: App {
    init() {
        KoinSetupKt.doInitKoin()  // SKIE makes the Kotlin function callable
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

-----

## Part 6: The Cached Repository — Putting It All Together 🔄

```kotlin
// commonMain/kotlin/com/example/shared/repository/CachedPostRepository.kt

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.onStart

class CachedPostRepository(
    private val remote: PostRepository,
    private val local:  LocalPostRepository
) {
    // Return cached data immediately, then refresh from network
    fun getPosts(): Flow<List<Post>> =
        local.getAllPostsFlow()
            .onStart {
                // Trigger a background refresh from the API
                refreshPosts()
            }

    suspend fun refreshPosts() {
        remote.getPosts()
            .onSuccess { posts ->
                local.insertPosts(posts)
            }
    }

    suspend fun getPostById(id: Int): Post? {
        // Try local first, fall back to remote
        return local.getPostById(id.toLong())
            ?: remote.getPost(id).getOrNull()?.also { post ->
                local.insertPosts(listOf(post))
            }
    }
}
```

This is the complete shared data layer: fetch from network, cache locally, serve from cache, emit updates reactively. Every line runs identically on Android, iOS, and Desktop.

-----

## Part 7: Multiplatform Settings — Key-Value Storage Without Boilerplate 🔑

For simple preferences (theme, login state, user ID), SQLDelight is overkill. Use **Multiplatform Settings**:

```kotlin
// commonMain/kotlin/com/example/shared/prefs/AppPreferences.kt

import com.russhwolf.settings.Settings
import com.russhwolf.settings.get
import com.russhwolf.settings.set

class AppPreferences(private val settings: Settings) {

    var isDarkMode: Boolean
        get()      = settings["dark_mode", false]
        set(value) { settings["dark_mode"] = value }

    var userId: String?
        get()      = settings.getStringOrNull("user_id")
        set(value) {
            if (value != null) settings["user_id"] = value
            else settings.remove("user_id")
        }

    var onboardingCompleted: Boolean
        get()      = settings["onboarding_done", false]
        set(value) { settings["onboarding_done"] = value }

    fun clearAll() = settings.clear()
}
```

Multiplatform Settings uses `SharedPreferences` on Android, `NSUserDefaults` on iOS, and `java.util.prefs.Preferences` on Desktop — all without a single line of `expect`/`actual`.

-----

## What’s Next: Shared Moves — Compose Multiplatform 🎨

*Both players maintain their position. The referee calls the next move: “left hand — yellow — Compose Multiplatform.”*

In **Episode 6**, we stop writing separate native UIs and start writing shared UIs with **Compose Multiplatform**. The same `@Composable` functions rendering on Android, iOS, and Desktop. Navigation. Resources. Platform-specific tweaks when the platform demands it. The move that turns KMP from a business logic sharing strategy into a full cross-platform UI framework.

-----

**🔗 Resources**

- **SQLDelight**: [cashapp.github.io/sqldelight](https://cashapp.github.io/sqldelight/)
- **Koin Multiplatform**: [insert-koin.io/docs/reference/koin-mp/kmp](https://insert-koin.io/docs/reference/koin-mp/kmp.html)
- **Multiplatform Settings**: [github.com/russhwolf/multiplatform-settings](https://github.com/russhwolf/multiplatform-settings)
- **KMP Ktor SQLDelight tutorial**: [kotlinlang.org/docs/multiplatform/multiplatform-ktor-sqldelight](https://kotlinlang.org/docs/multiplatform/multiplatform-ktor-sqldelight.html)

-----

*🎯 Twister Game of Kotlin Multiplatform — one mat, many platforms, perfect balance.*
