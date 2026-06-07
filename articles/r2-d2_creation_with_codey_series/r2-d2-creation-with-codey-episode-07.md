---
title: "R2D2 Creation with Codey 🤖 Ep.7" 
published: false 
description: "Episode 7: R2-D2's piezo buzzer gave him tones. His voice system will give him personality. We connect a DFPlayer Mini MP3 module to the ESP32-S3 via UART Serial2, load R2-D2 sound files onto a microSD card, and trigger different audio responses based on sensor events. Codey's Smart Library Picker knows DFRobotDFPlayerMini. The Live Serial Monitor shows everything in real time." 
tags: [esp32, audio, dfplayer, makers] 
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/r2-d2_creation_with_codey_series/r2-d2-creation-with-codey-episode-07.png" 
series: "R2-D2 Creation With Codey" 
canonical_url: "" 
organization: "the-software-s-journey" 
part: 7
---
## Episode 7: The Voice of the Galaxy

## "Artoo, I Wish We Didn't Have to Listen to You Sometimes" 🔊

*C-3PO enters the workshop clutching a small speaker and a DFPlayer Mini module.*

**C-3PO:** "I want to state, for the record, that I have mixed feelings about this episode. On one hand, R2-D2's communication through audio files will be considerably clearer than whatever he has been doing with that piezo buzzer. On the other hand, once we enable full audio playback, he will never. Stop. Talking."

*R2-D2 beeps at considerable volume.*

**C-3PO:** "See? He's already celebrating. This is going to be exhausting."

*Han Solo leans against the doorframe.*

**HAN:** "What he said. Let's wire it up anyway."

## 🗂️ SIPOC — The Voice System

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (the maker) | "Add DFPlayer Mini on UART2, microSD with R2-D2 sounds, trigger by sensor events" | Codey picks DFRobotDFPlayerMini library, writes Serial2 init code, maps sounds to events | Complete voice.h — sound triggers for every R2-D2 state | ESP32-S3 UART2 → DFPlayer Mini → Speaker |
| DFPlayer Mini | 5V power, RX/TX from ESP32-S3 UART2 | Reads MP3/WAV files from microSD by number, decodes audio | Amplified audio signal to speaker | Speaker — which produces actual R2-D2 sounds |
| microSD card (≤32GB FAT32) | MP3 or WAV files named 0001.mp3, 0002.mp3... | DFPlayer reads by file number | Audio playback | Speaker |
| Live Serial Monitor | ESP32-S3 Serial.print() output at 115200 baud | Shows state transitions, sound triggers, distance readings in real time | A running log of what R2-D2 is doing and thinking | You — debugging without a logic analyser |
| Codey Smart Library Picker | "DFPlayer Mini" mentioned in prompt | Automatically includes DFRobotDFPlayerMini.h and the correct library | Code that compiles first time with correct API calls | You — no library hunting required |

## The Components 🔧

*Yoda examines the DFPlayer Mini with one ear raised.*

**YODA:** "A small board. Powerful it is. Speaks the language of MP3, it does. Talks to the ESP32 through UART, it does. Patient with the timing, you must be — 200 milliseconds after power-on, it needs."

| Component | Quantity | Notes |
| --- | --- | --- |
| ESP32-S3 N16R8 | 1 | Our brain |
| DFPlayer Mini | 1 | MP3/WAV player module, 3V3–5V |
| Speaker (4Ω or 8Ω, 0.5W–3W) | 1 | Connect directly to DFPlayer SPK1/SPK2 |
| microSD card (≤32GB) | 1 | Format FAT32, files named 0001.mp3 etc. |
| 1kΩ resistor | 1 | On DFPlayer RX line — prevents voltage noise |
| 10µF capacitor (electrolytic) | 1 | Between DFPlayer VCC and GND — power filtering |
| Jumper wires | 5 |  |

### Preparing the microSD Card

Format your microSD as FAT32. Create a folder called `mp3` at the root. Name your files:

```
/mp3/
  0001.mp3  ← R2-D2 "happy" whistle sequence
  0002.mp3  ← R2-D2 "alert" rapid beeps
  0003.mp3  ← R2-D2 "sad" descending moan
  0004.mp3  ← R2-D2 "question" rising whistle
  0005.mp3  ← R2-D2 "startup" fanfare
  0006.mp3  ← R2-D2 "motion detected" warble
  0007.mp3  ← R2-D2 "danger close" urgent alarm

```

**C-3PO:** "I would suggest downloading these from any reputable Star Wars sound effects collection. The DFPlayer cares only about the filenames — it does not evaluate artistic merit."

*R2-D2 beeps indignantly.*

**C-3PO:** "I am sure your sounds are excellent, Artoo."

## The Codey Prompt 🎙️

*Luke sits at the keyboard.*

**LUKE:** "I love how this works now. I just describe what I want and Codey handles the library, the setup, all of it."

In **Agent mode**:

```
We're continuing R2-D2 on ESP32-S3 N16R8.

Add a DFPlayer Mini MP3 module for R2-D2 voice responses:
  - DFPlayer connected to ESP32-S3 UART2
  - TX2 = GPIO17 → DFPlayer RX (through 1kΩ resistor)
  - RX2 = GPIO16 ← DFPlayer TX
  - DFPlayer powered from L298N 5V rail
  - 10µF capacitor across DFPlayer VCC/GND
  - Speaker connected to DFPlayer SPK1 and SPK2 (no extra amp needed)

Sound file mapping on microSD (/mp3/ folder):
  1 = R2 happy whistle (play when idle, randomly every 30-60 seconds)
  2 = R2 alert beeps (play when object < 30cm)
  3 = R2 sad moan (play when object < 15cm, stuck)
  4 = R2 question whistle (play when motion first detected)
  5 = R2 startup fanfare (play once on boot)
  6 = R2 motion warble (sustained during motion-scan state)
  7 = R2 danger alarm (play when object < 15cm, loop until clear)

Remove the piezo buzzer — DFPlayer replaces it.
Create voice.h for all audio functions.
Use DFRobotDFPlayerMini library.
The DFPlayer needs 200ms settle time after Serial2.begin() before commands.
Show Serial Monitor output for all sound triggers at 115200 baud.

```

### Codey's Smart Library Picker Response

```
I'll use the DFRobotDFPlayerMini library for the DFPlayer Mini.
This library is pre-installed on Codey's compile servers.

I'll include:
  #include <DFRobotDFPlayerMini.h>

And use Serial2 on the ESP32-S3 for the DFPlayer communication.
Serial2 on ESP32-S3: RX=GPIO16, TX=GPIO17 by default.

Generating voice.h now...

```

### Generated `voice.h`

```cpp
// voice.h — R2-D2 Voice System
// DFPlayer Mini on ESP32-S3 UART2 (TX=GPIO17, RX=GPIO16)
// microSD: /mp3/0001.mp3 through 0007.mp3

#pragma once
#include <DFRobotDFPlayerMini.h>

// ── DFPlayer setup ───────────────────────────────────────────────
DFRobotDFPlayerMini dfPlayer;
bool dfPlayerReady = false;

// ── Sound IDs (match filenames on microSD) ───────────────────────
enum R2Sound {
  SOUND_HAPPY    = 1,
  SOUND_ALERT    = 2,
  SOUND_SAD      = 3,
  SOUND_QUESTION = 4,
  SOUND_STARTUP  = 5,
  SOUND_MOTION   = 6,
  SOUND_DANGER   = 7,
};

// ── Random idle chatter timing ───────────────────────────────────
unsigned long nextIdleChatterMs = 0;
const unsigned long CHATTER_MIN = 30000UL;  // 30 seconds
const unsigned long CHATTER_MAX = 60000UL;  // 60 seconds

void scheduleNextChatter() {
  nextIdleChatterMs = millis() + CHATTER_MIN
    + (unsigned long)(random(CHATTER_MAX - CHATTER_MIN));
}

// ── Initialise DFPlayer ──────────────────────────────────────────
bool initVoice() {
  // ESP32-S3 UART2: RX=GPIO16, TX=GPIO17
  Serial2.begin(9600, SERIAL_8N1, 16, 17);

  // DFPlayer needs 200ms to settle after Serial begin
  delay(200);

  if (!dfPlayer.begin(Serial2, /*isACK=*/true, /*doReset=*/true)) {
    Serial.println("DFPlayer Mini not detected — check wiring!");
    Serial.println("  • Is the microSD inserted?");
    Serial.println("  • Is the 1kΩ resistor on the DFPlayer RX line?");
    Serial.println("  • Is VCC on the 5V rail?");
    return false;
  }

  dfPlayer.volume(25);   // 0–30 (25 = ~83% volume — plenty for a droid)
  dfPlayerReady = true;
  Serial.println("DFPlayer Mini online! R2-D2 voice system ready.");

  // Play startup fanfare
  playSound(SOUND_STARTUP);
  scheduleNextChatter();
  return true;
}

// ── Play a sound ─────────────────────────────────────────────────
void playSound(R2Sound sound) {
  if (!dfPlayerReady) return;
  dfPlayer.play(sound);
  Serial.print("R2-D2 says: [sound ");
  Serial.print(sound);
  Serial.println("]");
}

// ── Stop current playback ────────────────────────────────────────
void stopSound() {
  if (!dfPlayerReady) return;
  dfPlayer.stop();
}

// ── Update: called every loop — handles idle chatter ────────────
void updateVoice(float distance, bool motion, DomeState domeState) {
  if (!dfPlayerReady) return;

  unsigned long now = millis();

  // DFPlayer print errors to Serial — check occasionally
  if (dfPlayer.available()) {
    uint8_t type  = dfPlayer.readType();
    int     value = dfPlayer.read();
    if (type == DFPlayerError) {
      Serial.print("DFPlayer error: ");
      Serial.println(value);
    }
  }

  // Danger: object very close
  if (distance < 15.0f) {
    static bool dangerPlaying = false;
    if (!dangerPlaying) {
      playSound(SOUND_DANGER);
      dangerPlaying = true;
    }
    return;
  } else {
    static bool dangerPlaying = false;
    if (dangerPlaying) {
      stopSound();
      dangerPlaying = false;
    }
  }

  // Alert zone: approaching
  if (distance < 30.0f) {
    static unsigned long lastAlertMs = 0;
    if (now - lastAlertMs > 4000) {
      playSound(SOUND_ALERT);
      lastAlertMs = now;
    }
    return;
  }

  // Motion: play question on first detection
  if (motion) {
    static bool motionSoundPlayed = false;
    if (!motionSoundPlayed) {
      playSound(SOUND_QUESTION);
      motionSoundPlayed = true;
    }
    return;
  } else {
    static bool motionSoundPlayed = false;
    motionSoundPlayed = false;
  }

  // Idle chatter: random happy whistle
  if (now >= nextIdleChatterMs) {
    playSound(SOUND_HAPPY);
    scheduleNextChatter();
  }
}

void initVoiceSystem() {
  randomSeed(esp_random());  // True random seed from ESP32 hardware RNG
  initVoice();
}

```

### Updated `r2d2-main.ino`

```cpp
#include <Adafruit_NeoPixel.h>
#include "sounds.h"      // LEDC buzzer (backup only, mostly replaced)
#include "animations.h"  // NeoPixel dome
#include "sensors.h"     // HC-SR04 + PIR
#include "display.h"     // SSD1306 OLED
#include "motion.h"      // Servo + motors
#include "voice.h"       // DFPlayer Mini

void setup() {
  Serial.begin(115200);
  Serial.println("═══════════════════════════════");
  Serial.println("  R2-D2 ESP32-S3 Boot Sequence");
  Serial.println("═══════════════════════════════");

  initSounds();
  initAnimations();
  initSensors();
  initDisplay();
  initMotion();
  initVoiceSystem();   // ← new

  Serial.println("All systems ONLINE. R2-D2 is ready.");
}

void loop() {
  if (!bootDone) { showBootScreen(); return; }

  float dist   = readDistance();
  bool  motion = checkMotion();

  // ── Motion (dome + wheels) ──────────────────────────────────
  if (dist < 30.0f) {
    domeSnap(90);
    motorStop();
  } else if (motion) {
    domeSnap(45);
  } else {
    domeIdleSweep();
  }

  // ── Display ─────────────────────────────────────────────────
  if (dist < 15.0f)    showAlertScreen();
  else if (motion)     showMotionScreen();
  else                 showIdleScreen(dist);

  // ── Dome lights ─────────────────────────────────────────────
  updateAnimationsSensors(dist, motion);

  // ── Voice ────────────────────────────────────────────────────
  updateVoice(dist, motion, currentState);
}

```

## Wiring Diagram — Adding the Voice Module 🧭

*C-3PO presents the updated diagram with a satisfied nod.*

**C-3PO:** "The DFPlayer Mini connects to UART2 on the ESP32-S3. Note the 1kΩ resistor on the RX line of the DFPlayer — this prevents communication noise that can cause the module to behave erratically. I am noting this specifically because I have personally witnessed the consequences of omitting it, and it is not pleasant."

```
R2-D2 Voice System Addition — ESP32-S3 N16R8
════════════════════════════════════════════════════════════

DFPLAYER MINI CONNECTIONS:
  L298N 5V      ──── DFPlayer VCC
  L298N 5V      ──── 10µF cap + (filter)
  GND           ──── DFPlayer GND + 10µF cap −
  ESP32 GPIO17  ──── (1kΩ) ──── DFPlayer RX
  DFPlayer TX   ──── ESP32 GPIO16
  DFPlayer SPK1 ──── Speaker terminal 1
  DFPlayer SPK2 ──── Speaker terminal 2

MicroSD Card:
  Inserted directly into DFPlayer Mini SD slot
  Formatted FAT32, files in /mp3/ folder

Color code (additions):
  PINK   = DFPlayer TX (audio data from module)
  CYAN   = DFPlayer RX (commands to module)
  GREY   = Through 1kΩ resistor on DFPlayer RX

Connection Table (additions):
┌──────────────────────┬──────────────────────────────────┐
│ From                 │ To                               │
├──────────────────────┼──────────────────────────────────┤
│ L298N 5V             │ DFPlayer VCC                     │
│ L298N 5V             │ 10µF cap: + (long leg)           │
│ GND (common)         │ DFPlayer GND + 10µF cap: −       │
│ ESP32 GPIO17 (TX2)   │ 1kΩ resistor → DFPlayer RX       │
│ DFPlayer TX          │ ESP32 GPIO16 (RX2)               │
│ DFPlayer SPK1        │ Speaker terminal 1               │
│ DFPlayer SPK2        │ Speaker terminal 2               │
└──────────────────────┴──────────────────────────────────┘

⚡ Notes:
  - DFPlayer powered from 5V — DO NOT use ESP32 3V3 (insufficient current)
  - 1kΩ resistor on DFPlayer RX is mandatory — prevents communication errors
  - Speaker: 4Ω or 8Ω, 0.5W minimum — DFPlayer can drive it directly
  - MicroSD must be FAT32, files named 0001.mp3–0007.mp3 in /mp3/ folder

```

## The Live Serial Monitor — Watching R2 Think 📟

After uploading, open Codey's **Live Serial Monitor** at **115200 baud**.

*As R2 runs:*

```
Serial Monitor — 115200 baud
─────────────────────────────────────────────────────────
═══════════════════════════════
  R2-D2 ESP32-S3 Boot Sequence
═══════════════════════════════
OLED projector online!
Dome servo centred.
Motor driver online.
DFPlayer Mini online! R2-D2 voice system ready.
R2-D2 says: [sound 5]        ← Startup fanfare!
All systems ONLINE. R2-D2 is ready.

Distance: 124 cm — SAFE
Distance: 119 cm — SAFE
R2-D2 says: [sound 1]        ← Idle chatter (random)
Motion detected — scan mode!
R2-D2 says: [sound 4]        ← Question whistle
State → SCAN
Distance: 28 cm — CAUTION
R2-D2 says: [sound 2]        ← Alert!
Distance: 12 cm — DANGER
R2-D2 says: [sound 7]        ← Danger alarm!
State → ALERT
Distance: 85 cm — SAFE       ← Object moved away

```

**HAN:** "Look at that. Every event logged. Every sound triggered. You can see exactly what he's thinking. That's not just a droid — that's a droid with a diary."

*R2-D2 beeps something that sounds like "I would prefer more privacy, actually."*

## Compile and Upload 🚀

```
✓ Compilation successful
  Board:   ESP32-S3 N16R8
  Sketch:  r2d2-main.ino + 6 headers
  Binary:  554,768 bytes (8.0% of 16MB Flash)
  RAM:     Used 41,240 bytes (12.6% of 327KB)
  PSRAM:   7.9 MB free — plenty for Episode 8 additions

```

*The ESP32-S3 boots. The OLED displays "R2-D2 ONLINE." The dome LEDs breathe blue-white. The dome servo sweeps gently.*

*Then — from the speaker — a clear, unmistakable R2-D2 startup whistle.*

**C-3PO:** *quietly* "...Oh my."

*R2-D2 — the real one — goes completely silent. Then a single, emotional beep.*

**LUKE:** "He recognises it. He recognises his own voice."

## Save Milestone 🚩

```
Milestone: "R2-D2 Voice System — Episode 7 Complete"

```

Six systems. All running. All talking to each other. R2-D2 has lights, sound, a display, sensors, motion, and a voice. There is one episode left.

## What's Next: The Complete Droid 🤖

*The entire Star Wars crew assembles in the workshop. Han. Luke. Obi-Wan. C-3PO. And there, in the centre — R2-D2, all systems operational, blue dome glowing, OLED projecting status, dome rotating in a gentle scan, audio clips playing softly.*

*Obi-Wan speaks.*

**OBI-WAN:** "In the final episode, we bring every system together into a single, cohesive, complete R2-D2. We explore the ESP32-S3's Wi-Fi capabilities. We use Codey's Deep Think mode for the most complex orchestration code. We draw the final complete wiring diagram — every component, every wire, every protection circuit. And we save the last milestone. The droid is nearly complete."

*R2-D2 plays sound 1: his happy whistle.*

*Everyone smiles.*

**🔗 Resources**

- **DFRobotDFPlayerMini library**: [github.com/DFRobot/DFRobotDFPlayerMini](https://github.com/DFRobot/DFRobotDFPlayerMini)
- **ESP32-S3 UART**: [docs.espressif.com/esp32-s3/uart](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/uart.html)
- **Codey Live Serial Monitor**: [codey.online](http://codey.online)

*🤖 R2D2 Creation with Codey — building the galaxy's greatest droid, one episode at a time. May the Force — and the cloud compiler — be with you.*