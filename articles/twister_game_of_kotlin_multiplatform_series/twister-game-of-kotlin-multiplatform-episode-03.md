-----

## title: “Twister Game of Kotlin Multiplatform! Ep.3: The Referee’s Call — expect/actual”
published: false
description: “Episode 3: In Twister, the referee calls a move and every player must execute it — but each from their own position, in their own way. In Kotlin Multiplatform, expect/actual is that referee call. commonMain declares the expectation — the move that must be made. Each platform provides the actual — the specific way they execute it from where they stand. The platform bridge, explained completely.”
tags: [kotlin, multiplatform, expectactual, android]
cover_image: “<https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/twister-kmp-episode-03.png>”
series: “Twister Game of Kotlin Multiplatform”
canonical_url: “”
organization: “the-software-s-journey”
part: 1

# Twister Game of Kotlin Multiplatform! 🎯

## Episode 3: The Referee’s Call — expect/actual

-----

## “Right Foot on Blue!” 📢

When the Twister referee calls “right foot on blue,” every player hears the same instruction. But each player executes it differently — from a different starting position, stretching in a different direction, maintaining a different balance. The *instruction* is universal. The *execution* is individual.

This is precisely how `expect`/`actual` works in Kotlin Multiplatform.

**`expect`** is the referee’s call: a declaration in `commonMain` that says “there must exist something with this name and this contract — I do not care how you implement it, but you must.”

**`actual`** is each player’s execution: a platform-specific implementation that fulfils the contract declared in `expect`, written using whatever native APIs that platform has available.

Without `expect`/`actual`, the only code you could share in `commonMain` would be code using APIs that are literally identical on every platform. With it, you can share interfaces and let platforms speak their own native language underneath.

-----

## 🗂️ SIPOC — The expect/actual Contract

|**Suppliers**       |**Inputs**                                                                                |**Process**                                                                                    |**Outputs**                                                                           |**Customers**                                                                                     |
|--------------------|------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
|commonMain developer|A platform-dependent API need (e.g., “get current time”, “generate UUID”, “format a date”)|Declare an `expect` declaration — the contract without implementation                          |A compilation checkpoint: the compiler enforces that every target provides an `actual`|The platform developers — who must write `actual` for their target                                |
|Android developer   |`actual` implementation using JVM/Android APIs                                            |Kotlin/JVM compiler sees `actual` satisfies `expect`; links them                               |Android-specific implementation compiled into the Android artefact                    |Any commonMain code that calls the `expect` — it transparently runs the Android version on Android|
|iOS developer       |`actual` implementation using Kotlin/Native + Apple frameworks                            |Kotlin/Native compiler links `expect` to `actual`                                              |iOS-specific implementation compiled into the Objective-C framework                   |Any commonMain code that calls the `expect` — it transparently runs the iOS version on iOS        |
|The Kotlin compiler |Both `expect` and `actual` declarations                                                   |Verifies: does every `actual` signature match its `expect`? Does every target have an `actual`?|Compile-time guarantee: no target ships without a correct implementation              |The entire KMP project — which ships only when all moves are correctly executed                   |

-----

## The Four Forms of expect/actual 📋

### Form 1: `expect fun` / `actual fun` — The Function Call

The simplest form — a function with platform-specific behaviour:

```kotlin
// commonMain/kotlin/com/example/shared/Platform.kt

// The referee's call: "everyone must be able to give me a UUID"
expect fun generateUUID(): String
```

```kotlin
// androidMain/kotlin/com/example/shared/Platform.android.kt

import java.util.UUID

// Android's execution: uses java.util.UUID
actual fun generateUUID(): String = UUID.randomUUID().toString()
```

```kotlin
// iosMain/kotlin/com/example/shared/Platform.ios.kt

import platform.Foundation.NSUUID

// iOS's execution: uses NSFoundation's NSUUID
actual fun generateUUID(): String = NSUUID().UUIDString()
```

```kotlin
// jvmMain/kotlin/com/example/shared/Platform.jvm.kt

import java.util.UUID

// Desktop JVM execution: same as Android (both run on JVM!)
actual fun generateUUID(): String = UUID.randomUUID().toString()
```

Now in `commonMain`, you can call `generateUUID()` anywhere. The compiler knows Android will execute the JVM version and iOS will execute the Native version — automatically, transparently.

-----

### Form 2: `expect class` / `actual class` — The Class

When an entire class needs platform-specific internals:

```kotlin
// commonMain/kotlin/com/example/shared/PlatformInfo.kt

expect class PlatformInfo() {
    val operatingSystem: String
    val version: String
    val isDebugBuild: Boolean
}
```

```kotlin
// androidMain/kotlin/com/example/shared/PlatformInfo.android.kt

import android.os.Build

actual class PlatformInfo {
    actual val operatingSystem: String = "Android"
    actual val version: String         = Build.VERSION.RELEASE
    actual val isDebugBuild: Boolean   = BuildConfig.DEBUG
}
```

```kotlin
// iosMain/kotlin/com/example/shared/PlatformInfo.ios.kt

import platform.UIKit.UIDevice
import platform.Foundation.NSBundle

actual class PlatformInfo {
    actual val operatingSystem: String =
        UIDevice.currentDevice.systemName()

    actual val version: String =
        UIDevice.currentDevice.systemVersion

    actual val isDebugBuild: Boolean =
        NSBundle.mainBundle.objectForInfoDictionaryKey("DEBUG") != null
}
```

-----

### Form 3: `expect object` / `actual object` — The Singleton

For singleton services with platform-specific backing:

```kotlin
// commonMain/kotlin/com/example/shared/Logger.kt

expect object Logger {
    fun debug(tag: String, message: String)
    fun error(tag: String, message: String, throwable: Throwable? = null)
}
```

```kotlin
// androidMain/kotlin/com/example/shared/Logger.android.kt

import android.util.Log

actual object Logger {
    actual fun debug(tag: String, message: String) {
        Log.d(tag, message)
    }

    actual fun error(tag: String, message: String, throwable: Throwable?) {
        Log.e(tag, message, throwable)
    }
}
```

```kotlin
// iosMain/kotlin/com/example/shared/Logger.ios.kt

import platform.Foundation.NSLog

actual object Logger {
    actual fun debug(tag: String, message: String) {
        NSLog("[DEBUG] %@: %@", tag, message)
    }

    actual fun error(tag: String, message: String, throwable: Throwable?) {
        NSLog("[ERROR] %@: %@ (%@)", tag, message, throwable?.message ?: "")
    }
}
```

-----

### Form 4: `actual typealias` — The Efficient Redirect

When a platform already has a perfect class that matches the `expect` — use `actual typealias` to point directly to it without wrapping:

```kotlin
// commonMain/kotlin/com/example/shared/AtomicRef.kt

// We expect an atomic reference implementation
expect class AtomicRef<T>(value: T) {
    fun get(): T
    fun set(value: T)
    fun compareAndSet(expected: T, new: T): Boolean
}
```

```kotlin
// jvmMain/kotlin/com/example/shared/AtomicRef.jvm.kt

import java.util.concurrent.atomic.AtomicReference

// Instead of wrapping AtomicReference, just alias it!
// This is zero-overhead — no wrapper class created
actual typealias AtomicRef<T> = AtomicReference<T>
```

For iOS/Native, Kotlin/Native has its own `AtomicRef` in `kotlin.concurrent`:

```kotlin
// iosMain/kotlin/com/example/shared/AtomicRef.ios.kt

import kotlin.concurrent.AtomicReference

actual typealias AtomicRef<T> = AtomicReference<T>
```

-----

## Real-World Pattern: DateTime Formatting 📅

One of the most common `expect`/`actual` use cases — formatting dates and times in a localised way:

```kotlin
// commonMain/kotlin/com/example/shared/DateFormatter.kt

import kotlinx.datetime.LocalDate

// The contract: format a date for display to the user
expect class DateFormatter() {
    fun formatShort(date: LocalDate): String   // e.g. "15 Jun"
    fun formatLong(date: LocalDate): String    // e.g. "15 June 2026"
    fun formatISO(date: LocalDate): String     // e.g. "2026-06-15"
}
```

```kotlin
// androidMain/kotlin/com/example/shared/DateFormatter.android.kt

import android.icu.text.SimpleDateFormat
import kotlinx.datetime.LocalDate
import kotlinx.datetime.toJavaLocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

actual class DateFormatter {
    private val locale = Locale.getDefault()

    actual fun formatShort(date: LocalDate): String =
        DateTimeFormatter.ofPattern("d MMM", locale)
            .format(date.toJavaLocalDate())

    actual fun formatLong(date: LocalDate): String =
        DateTimeFormatter.ofPattern("d MMMM yyyy", locale)
            .format(date.toJavaLocalDate())

    actual fun formatISO(date: LocalDate): String =
        date.toString()  // kotlinx.datetime.LocalDate.toString() is ISO 8601
}
```

```kotlin
// iosMain/kotlin/com/example/shared/DateFormatter.ios.kt

import kotlinx.datetime.LocalDate
import kotlinx.datetime.toNSDateComponents
import platform.Foundation.*

actual class DateFormatter {
    private val formatter = NSDateFormatter()

    private fun toNSDate(date: LocalDate): NSDate {
        val components = NSDateComponents()
        components.setYear(date.year.toLong())
        components.setMonth(date.monthNumber.toLong())
        components.setDay(date.dayOfMonth.toLong())
        return NSCalendar.currentCalendar
            .dateFromComponents(components)!!
    }

    actual fun formatShort(date: LocalDate): String {
        formatter.dateFormat = "d MMM"
        return formatter.stringFromDate(toNSDate(date))
    }

    actual fun formatLong(date: LocalDate): String {
        formatter.dateStyle = NSDateFormatterLongStyle
        formatter.timeStyle = NSDateFormatterNoStyle
        return formatter.stringFromDate(toNSDate(date))
    }

    actual fun formatISO(date: LocalDate): String = date.toString()
}
```

-----

## Real-World Pattern: File System Access 📂

```kotlin
// commonMain/kotlin/com/example/shared/FileStorage.kt

expect class FileStorage() {
    fun read(filename: String): String?
    fun write(filename: String, content: String)
    fun exists(filename: String): Boolean
    fun delete(filename: String): Boolean
}
```

```kotlin
// androidMain/kotlin/com/example/shared/FileStorage.android.kt

import android.content.Context
import java.io.File

// Android needs the Context — injected via DI (Koin, Episode 5)
actual class FileStorage(private val context: Context) {
    private val dir: File get() = context.filesDir

    actual fun read(filename: String): String? =
        File(dir, filename).takeIf { it.exists() }?.readText()

    actual fun write(filename: String, content: String) {
        File(dir, filename).writeText(content)
    }

    actual fun exists(filename: String): Boolean =
        File(dir, filename).exists()

    actual fun delete(filename: String): Boolean =
        File(dir, filename).delete()
}
```

```kotlin
// iosMain/kotlin/com/example/shared/FileStorage.ios.kt

import platform.Foundation.*

actual class FileStorage {
    private val dir: String = NSSearchPathForDirectoriesInDomains(
        NSDocumentDirectory, NSUserDomainMask, true
    ).first() as String

    actual fun read(filename: String): String? {
        val path = "$dir/$filename"
        return if (NSFileManager.defaultManager.fileExistsAtPath(path))
            NSString.stringWithContentsOfFile(path, encoding = NSUTF8StringEncoding, error = null)
        else null
    }

    actual fun write(filename: String, content: String) {
        val path = "$dir/$filename"
        (content as NSString).writeToFile(path, atomically = true,
            encoding = NSUTF8StringEncoding, error = null)
    }

    actual fun exists(filename: String): Boolean =
        NSFileManager.defaultManager.fileExistsAtPath("$dir/$filename")

    actual fun delete(filename: String): Boolean =
        NSFileManager.defaultManager.removeItemAtPath("$dir/$filename", error = null)
}
```

-----

## The Compiler as Referee: What Happens When You Miss a Move 🚨

```kotlin
// commonMain declares:
expect fun getPlatformName(): String

// androidMain and iosMain both have actual fun getPlatformName() ...
// But what if someone adds a new target to Gradle without an actual?

kotlin {
    androidTarget()
    iosArm64()
    jvm("desktop")  // ← NEW TARGET ADDED
}

// Now the compiler acts as referee:
// Error: Expected function 'getPlatformName' has no actual declaration
// in module 'myapp.shared' for JVM target.
//
// 👉 You MUST add:
// jvmMain/kotlin/.../Platform.jvm.kt:
actual fun getPlatformName(): String = "Desktop JVM"
```

This is the safety net of KMP — you cannot accidentally forget a platform. The compiler will not let the game proceed until every player has executed every move.

-----

## When NOT to Use expect/actual 🤔

`expect`/`actual` is powerful but not always the right tool. Prefer alternatives when:

|Situation                                                                              |Better approach                                      |
|---------------------------------------------------------------------------------------|-----------------------------------------------------|
|The API is identical on all platforms (use coroutines, stdlib)                         |Just use it in `commonMain` — no expect/actual needed|
|A library already provides a multiplatform abstraction (Ktor engines, kotlinx.datetime)|Use the library — it handles expect/actual internally|
|You need dependency injection of platform objects (Context)                            |Use Koin modules per platform (Episode 5)            |
|Just wrapping a third-party class that already exists on all platforms                 |`actual typealias` to avoid boilerplate              |

-----

## What’s Next: The Double Stretch 🤸

In **Episode 4**, two players reach for the same circle simultaneously — the networking circle. Ktor is a multiplatform HTTP client that uses the `expect`/`actual` mechanism internally to provide the right engine on each platform. We build a complete shared data layer with Ktor and `kotlinx.serialization`, calling a real API from both Android and iOS with the same code.

*Right hand on blue — stretch!* 🔵

-----

**🔗 Resources**

- **expect/actual documentation**: [kotlinlang.org/docs/multiplatform/multiplatform-expect-actual](https://kotlinlang.org/docs/multiplatform/multiplatform-expect-actual.html)
- **kotlinx.datetime**: [github.com/Kotlin/kotlinx-datetime](https://github.com/Kotlin/kotlinx-datetime)

-----

*🎯 Twister Game of Kotlin Multiplatform — one mat, many platforms, perfect balance.*
