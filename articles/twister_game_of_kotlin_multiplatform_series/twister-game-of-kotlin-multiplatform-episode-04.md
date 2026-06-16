---
title: "Twister Game of Kotlin Multiplatform 🎯 Ep.4"
published: false
description: "Episode 4: The double stretch — left hand to yellow while right foot reaches blue. Two platforms, one API call. Ktor is Kotlin Multiplatform’s HTTP client: one shared interface in commonMain, platform-specific engines underneath (OkHttp on Android, Darwin/NSURLSession on iOS). Combined with kotlinx.serialization, it creates a complete shared networking layer that every platform executes with native performance."
tags: [kotlin, multiplatform, ktor, networking]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/twister-kmp-episode-04.png"
series: "Twister Game of Kotlin Multiplatform"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 4: The Double Stretch — Ktor and Networking

-----

## Both Hands on the Mat 🤸

The double stretch. In Twister, it is the move that tests whether you have been playing smart — keeping balanced, staying flexible, ready for the position where both hands and both feet are engaged simultaneously. The ambitious player who reached too far in the last move now struggles to maintain the new position.

Networking in Kotlin Multiplatform is the double stretch moment. It has to work on Android (with its OkHttp stack, its lifecycle, its thread model). It has to work on iOS (with its NSURLSession, its different concurrency model, its App Transport Security). It has to work in a Kotlin/Wasm browser tab, where the only available networking primitive is `fetch()`.

**Ktor** is the move that makes all of this possible without falling over. It is a coroutine-native, asynchronous HTTP client with a platform-agnostic API that uses platform-specific engines underneath — and you get to configure which engine runs on which platform, one per source set, exactly as we mapped circles in Episode 2.

-----

## 🗂️ SIPOC — The Networking Layer

|**Suppliers**             |**Inputs**                                 |**Process**                                                        |**Outputs**                                                               |**Customers**                                                               |
|--------------------------|-------------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------------------|----------------------------------------------------------------------------|
|commonMain developer      |A URL, HTTP method, request/response types |Call `client.get()`, `client.post()` — pure Kotlin, coroutine-based|The response as a typed data class — deserialized by kotlinx.serialization|Any commonMain code: ViewModel, Repository, UseCase                         |
|Ktor engine (per platform)|The Ktor request object                    |Routes to OkHttp (Android), Darwin (iOS), CIO (JVM), or JS (WASM)  |A completed HTTP response                                                 |The Ktor client core — which deserializes and returns to the caller         |
|kotlinx.serialization     |A `@Serializable` data class and JSON bytes|Generates serialization code at compile time — no reflection       |A Kotlin data class populated from JSON                                   |The calling code in commonMain — which works with typed objects, not strings|

-----

## The Engine Architecture: Why Ktor Fits the Mat Perfectly 🔌

Ktor’s design mirrors the KMP philosophy exactly. The core API lives in `ktor-client-core` — it belongs in `commonMain`. The engines live in platform-specific libraries — they belong in `androidMain`, `iosMain`, etc.

```
ktor-client-core (commonMain)
    │
    ├── ktor-client-okhttp (androidMain)     → OkHttp 4.x
    ├── ktor-client-darwin (iosMain)         → NSURLSession (native iOS/macOS)
    ├── ktor-client-cio    (jvmMain)         → Pure Kotlin async I/O
    ├── ktor-client-js     (wasmJsMain/jsMain) → Browser fetch()
    └── ktor-client-mock   (commonTest)      → Testing without a real server
```

Every engine runs at native performance — OkHttp on Android means all of OkHttp’s connection pooling and caching. Darwin on iOS means NSURLSession, which respects iOS App Transport Security policies.

-----

## Setting Up Ktor — The Full Gradle Configuration 🎰

```kotlin
// shared/build.gradle.kts

kotlin {
    sourceSets {
        commonMain.dependencies {
            // Core client API — everyone touches this yellow circle
            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.kotlinx.json)
            implementation(libs.ktor.client.logging)         // Request/response logging
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.kotlinx.coroutines.core)
        }

        androidMain.dependencies {
            // OkHttp engine — the Android green circle
            implementation(libs.ktor.client.okhttp)
        }

        iosMain.dependencies {
            // Darwin engine — the iOS blue circle
            implementation(libs.ktor.client.darwin)
        }

        val desktopMain by getting {
            dependencies {
                // CIO engine — pure Kotlin async I/O for Desktop
                implementation(libs.ktor.client.cio)
            }
        }

        wasmJsMain.dependencies {
            // JS engine uses browser fetch() API
            implementation(libs.ktor.client.js)
        }
    }
}
```

-----

## Creating the Shared HttpClient 🔧

The `HttpClient` is instantiated in `commonMain` using the `HttpClient()` constructor — which picks up the platform engine automatically. You provide configuration; the engine is injected:

```kotlin
// commonMain/kotlin/com/example/shared/network/HttpClientFactory.kt

import io.ktor.client.HttpClient
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.plugins.logging.LogLevel
import io.ktor.client.plugins.logging.Logging
import io.ktor.client.plugins.logging.Logger
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json

fun createHttpClient(): HttpClient = HttpClient {

    // ── JSON serialization ────────────────────────────────────────
    install(ContentNegotiation) {
        json(Json {
            prettyPrint          = false
            isLenient            = true     // Accept slightly malformed JSON
            ignoreUnknownKeys    = true     // Future-proof against new API fields
            encodeDefaults       = false    // Don't serialise default values
            coerceInputValues    = true     // null → default value for non-nullable
        })
    }

    // ── Request/Response logging ──────────────────────────────────
    install(Logging) {
        level = LogLevel.HEADERS
        logger = object : Logger {
            override fun log(message: String) {
                // In production: route to your platform logger
                println("[HTTP] $message")
            }
        }
    }

    // ── Timeouts ──────────────────────────────────────────────────
    install(io.ktor.client.plugins.HttpTimeout) {
        connectTimeoutMillis = 10_000
        requestTimeoutMillis = 30_000
        socketTimeoutMillis  = 30_000
    }

    // ── Retry on transient failures ───────────────────────────────
    install(io.ktor.client.plugins.HttpRequestRetry) {
        retryOnServerErrors(maxRetries = 3)
        exponentialDelay()
    }
}
```

The magic: no `if (isAndroid)` anywhere. The same `HttpClient {}` block runs on all platforms. Ktor routes internally to the right engine.

-----

## Building the Data Models: @Serializable 📦

```kotlin
// commonMain/kotlin/com/example/shared/model/Post.kt

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Post(
    val id:     Int,
    val title:  String,
    val body:   String,
    @SerialName("userId")
    val userId: Int
)

@Serializable
data class CreatePostRequest(
    val title:  String,
    val body:   String,
    @SerialName("userId")
    val userId: Int
)

@Serializable
data class ApiError(
    val code:    Int,
    val message: String
)
```

`@Serializable` triggers compile-time code generation — no reflection at runtime. This is essential for Kotlin/Native (iOS) where reflection is unavailable.

-----

## The Repository Pattern: The Shared Business Layer 🏛️

```kotlin
// commonMain/kotlin/com/example/shared/repository/PostRepository.kt

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.*
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.http.contentType
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class PostRepository(private val client: HttpClient) {

    private val baseUrl = "https://jsonplaceholder.typicode.com"

    // ── Get all posts ─────────────────────────────────────────────
    suspend fun getPosts(): Result<List<Post>> = runCatching {
        client.get("$baseUrl/posts").body<List<Post>>()
    }

    // ── Get a single post ─────────────────────────────────────────
    suspend fun getPost(id: Int): Result<Post> = runCatching {
        client.get("$baseUrl/posts/$id").body<Post>()
    }

    // ── Create a new post ─────────────────────────────────────────
    suspend fun createPost(request: CreatePostRequest): Result<Post> =
        runCatching {
            client.post("$baseUrl/posts") {
                contentType(ContentType.Application.Json)
                setBody(request)
            }.body<Post>()
        }

    // ── Stream posts as a Flow (for reactive UI) ──────────────────
    fun postsFlow(): Flow<List<Post>> = flow {
        while (true) {
            val result = getPosts()
            result.onSuccess { emit(it) }
            kotlinx.coroutines.delay(30_000) // Refresh every 30 seconds
        }
    }
}
```

This `PostRepository` compiles identically on every target. Android uses OkHttp under the hood. iOS uses Darwin/NSURLSession. Desktop uses CIO. Nobody outside this class knows or cares.

-----

## Error Handling: Catching Moves That Go Wrong 🚨

```kotlin
// commonMain/kotlin/com/example/shared/network/NetworkResult.kt

sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val message: String, val code: Int? = null) : NetworkResult<Nothing>()
    data object Loading : NetworkResult<Nothing>()
}

// Extension to convert Ktor exceptions to NetworkResult
suspend inline fun <reified T> safeApiCall(
    crossinline call: suspend () -> T
): NetworkResult<T> {
    return try {
        NetworkResult.Success(call())
    } catch (e: io.ktor.client.plugins.ClientRequestException) {
        // 4xx errors
        NetworkResult.Error(
            message = e.response.status.description,
            code    = e.response.status.value
        )
    } catch (e: io.ktor.client.plugins.ServerResponseException) {
        // 5xx errors
        NetworkResult.Error(
            message = "Server error: ${e.response.status.value}",
            code    = e.response.status.value
        )
    } catch (e: io.ktor.client.network.sockets.ConnectTimeoutException) {
        NetworkResult.Error("Connection timed out")
    } catch (e: io.ktor.client.engine.HttpClientEngineClosedException) {
        NetworkResult.Error("Network connection closed")
    } catch (e: Exception) {
        NetworkResult.Error(e.message ?: "Unknown error")
    }
}
```

-----

## The ViewModel Layer: Shared Presentation Logic 📱

With KMP, even the ViewModel can be shared. Using `kotlinx.coroutines` and `StateFlow` — both multiplatform:

```kotlin
// commonMain/kotlin/com/example/shared/viewmodel/PostsViewModel.kt

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class PostsViewModel(
    private val repository: PostRepository,
    private val scope: CoroutineScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
) {
    private val _state = MutableStateFlow<NetworkResult<List<Post>>>(NetworkResult.Loading)
    val state: StateFlow<NetworkResult<List<Post>>> = _state.asStateFlow()

    init { loadPosts() }

    fun loadPosts() {
        scope.launch {
            _state.value = NetworkResult.Loading
            _state.value = safeApiCall { repository.getPosts().getOrThrow() }
        }
    }

    fun refresh() = loadPosts()

    fun onCleared() {
        // Cancel the scope when the ViewModel is destroyed
        scope.coroutineContext[SupervisorJob]?.cancel()
    }
}
```

-----

## Platform Consumption: Using the Shared ViewModel 🎮

**Android (Compose UI):**

```kotlin
// androidApp/src/main/kotlin/com/example/android/PostsScreen.kt

import androidx.lifecycle.viewModelScope
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue

@Composable
fun PostsScreen(viewModel: PostsAndroidViewModel = viewModel()) {
    val state by viewModel.state.collectAsState()

    when (val s = state) {
        is NetworkResult.Loading -> CircularProgressIndicator()
        is NetworkResult.Success -> PostsList(posts = s.data)
        is NetworkResult.Error   -> ErrorMessage(message = s.message)
    }
}

// Thin Android ViewModel wrapper — just bridges lifecycle
class PostsAndroidViewModel : ViewModel() {
    private val sharedVM = PostsViewModel(
        repository = PostRepository(createHttpClient()),
        scope      = viewModelScope
    )
    val state = sharedVM.state
    fun refresh() = sharedVM.refresh()
}
```

**iOS (SwiftUI):**

```swift
// iosApp/PostsView.swift

import SwiftUI
import Shared  // The compiled KMP framework

class PostsViewState: ObservableObject {
    @Published var posts: [Post] = []
    @Published var isLoading = false
    @Published var errorMessage: String? = nil

    private let viewModel = PostsViewModel(
        repository: PostRepository(client: HttpClientFactoryKt.createHttpClient())
    )

    func startObserving() {
        // SKIE (Episode 7) turns StateFlow into async sequence
        Task {
            for await state in viewModel.state {
                await MainActor.run {
                    switch state {
                    case is NetworkResultLoading:     isLoading = true
                    case let s as NetworkResultSuccess<NSArray>:
                        isLoading = false
                        posts = s.data as! [Post]
                    case let e as NetworkResultError:
                        isLoading = false
                        errorMessage = e.message
                    default: break
                    }
                }
            }
        }
    }
}
```

-----

## Testing the Network Layer Without a Server 🧪

```kotlin
// commonTest/kotlin/com/example/shared/repository/PostRepositoryTest.kt

import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import io.ktor.utils.io.ByteReadChannel
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class PostRepositoryTest {

    private fun createMockClient(responseBody: String, status: HttpStatusCode): HttpClient {
        val mockEngine = MockEngine { request ->
            respond(
                content = ByteReadChannel(responseBody),
                status  = status,
                headers = headersOf(
                    HttpHeaders.ContentType, "application/json"
                )
            )
        }
        return HttpClient(mockEngine) {
            install(ContentNegotiation) {
                json(Json { ignoreUnknownKeys = true })
            }
        }
    }

    @Test
    fun testGetPostsSuccess() = runTest {
        val json = """[{"id":1,"title":"Test Post","body":"Test body","userId":1}]"""
        val repo = PostRepository(createMockClient(json, HttpStatusCode.OK))

        val result = repo.getPosts()

        assertTrue(result.isSuccess)
        assertEquals(1, result.getOrThrow().size)
        assertEquals("Test Post", result.getOrThrow().first().title)
    }

    @Test
    fun testGetPostsServerError() = runTest {
        val repo = PostRepository(
            createMockClient("{}", HttpStatusCode.InternalServerError)
        )

        val result = safeApiCall { repo.getPosts().getOrThrow() }

        assertTrue(result is NetworkResult.Error)
        assertEquals(500, (result as NetworkResult.Error).code)
    }
}
```

`runTest` from `kotlinx.coroutines.test` is multiplatform — the same test runs on Android, iOS (via Kotlin/Native), and Desktop JVM.

-----

## What’s Next: Two Players, One Circle 🔵🟢

*Two hands reach for the same circle — and somehow it works.*

In **Episode 5**, we tackle local data persistence — the circle that every platform needs but each reaches from a different direction. SQLDelight provides type-safe SQL that compiles to native on each platform. Koin provides dependency injection that wires the right driver to the right platform. Multiplatform Settings handles key-value storage. Two players, one very important circle.

-----

**🔗 Resources**

- **Ktor documentation**: [ktor.io/docs/client](https://ktor.io/docs/client/getting-started.html)
- **kotlinx.serialization**: [github.com/Kotlin/kotlinx.serialization](https://github.com/Kotlin/kotlinx.serialization)
- **Ktor mock engine**: [ktor.io/docs/client/testing](https://ktor.io/docs/client/testing.html)

-----

*🎯 Twister Game of Kotlin Multiplatform — one mat, many platforms, perfect balance.*
