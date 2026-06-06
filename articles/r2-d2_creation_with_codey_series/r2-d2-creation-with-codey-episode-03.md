---
title: "R2D2 Creation with Codey 🤖 Ep.3" 
published: false 
description: "Episode 3: R2-D2's dome lights are the most iconic visual of the galaxy's greatest droid — the blue-and-white LEDs that pulse, sweep, and glow with personality. We connect a NeoPixel ring, Codey picks the Adafruit NeoPixel library automatically, the voltage safety check fires a critical warning, and the dome comes alive in breathtaking color." 
tags: [arduino, neopixel, leds, makers] 
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/r2-d2_creation_with_codey_series/r2-d2-creation-with-codey-episode-03.png"
series: "R2-D2 Creation With Codey" 
canonical_url: "" 
organization: "the-software-s-journey" 
part: 3
---
## Episode 3: The Dome Awakens

## "I Have a Bad Feeling About These Voltage Levels" ⚡

*C-3PO enters the workshop carrying a 12-LED NeoPixel ring with the careful reverence of someone handling a thermal detonator.*

**C-3PO:** "I want to begin by saying that I have computed no fewer than twenty-three potential failure modes for this particular connection. NeoPixel WS2812B LED rings operate on 5V logic. The Arduino UNO R3 also operates on 5V logic. So far, so excellent. However, should anyone in this workshop be tempted — under any circumstances — to use an ESP32 instead, which operates on 3.3V logic, I must warn them in the strongest possible terms that—"

*R2-D2 beeps the equivalent of "get on with it."*

**C-3PO:** "Yes, well. Codey's voltage safety check will handle that conversation. Shall we begin?"

## 🗂️ SIPOC — The Dome Light System

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (the maker) | "Add a 12-LED NeoPixel ring to pin 6 for R2-D2 dome lights" | Codey picks Adafruit_NeoPixel library, generates light animation code | Complete .ino + .h header file for animation patterns | Arduino UNO R3 — which drives all 12 RGB LEDs |
| Codey Voltage Safety Check | NeoPixel ring (5V) + Arduino UNO (5V) | Cross-references board voltage vs component logic requirements | Green light: compatible — or warning with level shifter advice | You — who avoid magic smoke |
| NeoPixel Ring (12 LEDs) | 5V power + PWM data signal from Pin 6 | WS2812B protocol drives each RGB LED individually | 12 independently addressable full-color LEDs | R2-D2's dome — which lights up with personality |
| Cloud Compiler | Multi-file project: r2d2-dome.ino + animations.h | Compiles with Adafruit_NeoPixel pre-installed on Codey servers | Firmware ready for upload | Arduino UNO — via Web Serial |

## The Components 🔧

*Luke examines the new parts laid out on the bench.*

**LUKE:** "These are beautiful. The blue and white... it's exactly right. Like the dome in the movies."

| Component | Quantity | Notes |
| --- | --- | --- |
| Arduino UNO R3 | 1 | From Episode 1 |
| NeoPixel ring (12 LED, WS2812B) | 1 | 5V input — white text on back means 5V variant |
| 470Ω resistor | 1 | Data line protection — prevents signal ringing |
| 100µF capacitor (electrolytic) | 1 | Power supply decoupling — across 5V and GND |
| Jumper wires | 4 |  |
| USB cable | 1 |  |

**LUKE:** "Why the capacitor?"

*Yoda materialises near the component drawer.*

**YODA:** "Sudden power demand, NeoPixels have when they first turn on. Smooth that spike, the capacitor does. Without it, reset your Arduino might — mid-animation."

**LUKE:** "I had no idea—"

**YODA:** "Much to learn, you still have. But learn quickly with Codey, you will."

## Codey Prompt: Describing the Dome 🎙️

Open your Codey project. In **Plan mode** first (to review the plan), then **Agent mode** to build it:

```
Plan mode first, then agent:

I'm building R2-D2's dome light system.
Add a 12-LED NeoPixel ring (WS2812B) connected to digital pin 6
with a 470 ohm resistor on the data line.
Add a 100uF capacitor across the power pins for stability.

Create these light animations:
  1. "idle" — gentle blue-white breathing pattern, slow
  2. "alert" — fast red sweep around the ring, 3 times
  3. "happy" — rainbow sweep, then blue-white sparkle
  4. "scan" — single blue LED orbiting the ring slowly

Cycle through idle → scan → idle → happy → idle → alert.
Use non-blocking millis() timing throughout.
Split the animations into a separate animations.h file.
Keep the main .ino clean and readable.

```

### Plan Mode Preview

Codey shows the plan before writing:

```
Plan for R2-D2 Dome Light System:

1. Main file (r2d2-dome.ino):
   - Include Adafruit_NeoPixel.h and animations.h
   - Setup: initialise ring, set brightness
   - Loop: call state machine from animations.h

2. animations.h:
   - Define RING_PIN = 6, NUMPIXELS = 12
   - Adafruit_NeoPixel ring object
   - State enum: IDLE, ALERT, HAPPY, SCAN
   - Functions: animateIdle(), animateAlert(),
     animateHappy(), animateScan()
   - Timing via millis() — non-blocking

3. Wiring diagram:
   - Pin 6 → 470Ω → NeoPixel DIN
   - 5V → Cap+ and NeoPixel 5V
   - GND → Cap− and NeoPixel GND

Proceed with Agent mode to write the code?

```

*C-3PO reads the plan with visible relief.*

**C-3PO:** "A plan! Before the code! How wonderfully methodical. I approve of this approach entirely."

Click **Proceed** — Codey switches to Agent mode and writes.

### The Generated Code: `r2d2-dome.ino`

```cpp
// r2d2-dome.ino
// R2-D2 Dome Light System — Main File
// Board: Arduino UNO R3
// NeoPixel ring (WS2812B, 12 LEDs) on pin 6

#include <Adafruit_NeoPixel.h>
#include "animations.h"

void setup() {
  Serial.begin(9600);
  initAnimations();
  Serial.println("R2-D2 dome lights online!");
}

void loop() {
  updateAnimations();
}

```

### The Generated Header: `animations.h`

```cpp
// animations.h
// R2-D2 Dome Light Animations
// NeoPixel ring (WS2812B, 12 LEDs) on pin 6

#pragma once
#include <Adafruit_NeoPixel.h>

#define RING_PIN    6
#define NUMPIXELS   12
#define BRIGHTNESS  80   // 0-255 — keep under 100 for USB power

Adafruit_NeoPixel ring(NUMPIXELS, RING_PIN, NEO_GRB + NEO_KHZ800);

enum DomeState { IDLE, SCAN, HAPPY, ALERT };

DomeState currentState = IDLE;
unsigned long stateStartMs = 0;
unsigned long lastUpdateMs = 0;

// ── State durations (ms) ────────────────────────────────────────
const unsigned long IDLE_DURATION  = 5000;
const unsigned long SCAN_DURATION  = 4000;
const unsigned long HAPPY_DURATION = 3500;
const unsigned long ALERT_DURATION = 2500;

// ── Dome state machine order ────────────────────────────────────
DomeState stateOrder[] = {IDLE, SCAN, IDLE, HAPPY, IDLE, ALERT};
int stateIndex  = 0;
const int NUM_STATES = 6;

// ── Animation helpers ───────────────────────────────────────────
float breatheValue = 0.0f;
float breatheDir   = 0.02f;
int   scanPos      = 0;
int   alertSweep   = 0;
int   alertCount   = 0;
int   rainbowStep  = 0;

uint32_t blue(uint8_t brightness) {
  return ring.Color(0, 0, brightness);
}
uint32_t white(uint8_t brightness) {
  return ring.Color(brightness, brightness, brightness);
}
uint32_t blueWhite(int pos, uint8_t br) {
  return (pos % 3 == 0) ? white(br) : blue(br);
}

// ── IDLE: gentle blue-white breathing ───────────────────────────
void animateIdle() {
  unsigned long now = millis();
  if (now - lastUpdateMs < 20) return;
  lastUpdateMs = now;

  breatheValue += breatheDir;
  if (breatheValue >= 1.0f || breatheValue <= 0.1f) breatheDir = -breatheDir;

  uint8_t br = (uint8_t)(breatheValue * BRIGHTNESS);
  for (int i = 0; i < NUMPIXELS; i++) {
    ring.setPixelColor(i, blueWhite(i, br));
  }
  ring.show();
}

// ── SCAN: single blue LED orbiting slowly ───────────────────────
void animateScan() {
  unsigned long now = millis();
  if (now - lastUpdateMs < 80) return;
  lastUpdateMs = now;

  ring.clear();
  ring.setPixelColor(scanPos, ring.Color(0, 0, BRIGHTNESS));
  // Faint trail
  ring.setPixelColor((scanPos + NUMPIXELS - 1) % NUMPIXELS,
                     ring.Color(0, 0, BRIGHTNESS / 5));
  ring.show();
  scanPos = (scanPos + 1) % NUMPIXELS;
}

// ── HAPPY: rainbow then blue-white sparkle ───────────────────────
void animateHappy() {
  unsigned long now = millis();
  if (now - lastUpdateMs < 30) return;
  lastUpdateMs = now;

  for (int i = 0; i < NUMPIXELS; i++) {
    int hue = (rainbowStep * 256 + i * (65536L / NUMPIXELS)) & 0xFFFF;
    ring.setPixelColor(i, ring.gamma32(ring.ColorHSV(hue)));
  }
  ring.show();
  rainbowStep = (rainbowStep + 2) % 256;
}

// ── ALERT: fast red sweep, 3 times ──────────────────────────────
void animateAlert() {
  unsigned long now = millis();
  if (now - lastUpdateMs < 40) return;
  lastUpdateMs = now;

  ring.clear();
  ring.setPixelColor(alertSweep % NUMPIXELS, ring.Color(BRIGHTNESS, 0, 0));
  ring.show();
  alertSweep++;
  if (alertSweep >= NUMPIXELS) {
    alertSweep = 0;
    alertCount++;
  }
}

// ── State machine ────────────────────────────────────────────────
void initAnimations() {
  ring.begin();
  ring.setBrightness(BRIGHTNESS);
  ring.clear();
  ring.show();
  stateStartMs = millis();
}

void updateAnimations() {
  unsigned long now      = millis();
  unsigned long stateDur = 0;

  switch (currentState) {
    case IDLE:  animateIdle();  stateDur = IDLE_DURATION;  break;
    case SCAN:  animateScan();  stateDur = SCAN_DURATION;  break;
    case HAPPY: animateHappy(); stateDur = HAPPY_DURATION; break;
    case ALERT: animateAlert(); stateDur = ALERT_DURATION; break;
  }

  if (now - stateStartMs >= stateDur) {
    stateIndex   = (stateIndex + 1) % NUM_STATES;
    currentState = stateOrder[stateIndex];
    stateStartMs = now;
    alertSweep   = 0;
    alertCount   = 0;
    rainbowStep  = 0;
    scanPos      = 0;
    Serial.print("State → ");
    Serial.println(currentState);
  }
}

```

## The Voltage Safety Check — Codey Saves the Day ⚡

*Suddenly, a second prompt flashes on screen.*

**C-3PO:** "Oh! There it is! Codey's voltage safety check! I told everyone this moment would come!"

When you type the same prompt but specify **ESP32** instead of Arduino UNO, Codey adds a critical warning:

```
⚡ VOLTAGE SAFETY WARNING

Component: NeoPixel ring WS2812B
Logic level required: 5V data signal
Board selected: ESP32 DevKit V1 (3.3V logic)

ISSUE: The WS2812B data input requires a HIGH signal of at least
3.5V. ESP32 GPIO outputs only 3.3V, which may be unreliable or
cause flickering, colour errors, or complete failure.

RECOMMENDATION: Add a 74AHCT125 level shifter between ESP32
GPIO pin and the NeoPixel DIN pin.
OR: Use a 3.3V-compatible LED strip (SK6812 at 3.3V mode).
OR: Add a pullup via 10kΩ resistor to 5V on the data line.

The code below uses the level shifter approach.
Shall I update the wiring diagram?

```

**C-3PO:** "You see! THREE THOUSAND SEVEN HUNDRED AND TWENTY TO ONE were my odds and Codey — Codey caught it! Without the level shifter, R2-D2's dome lights would flicker erratically. Or not work at all. I have said it before: voltage compatibility is the cornerstone of reliable hardware."

*R2-D2 emits a long, approving whistle.*

**C-3PO:** "Yes. Quite."

## The Wiring Diagram — The Dome Blueprint 🧭

Click **Wiring Diagram**. Codey draws:

```
R2-D2 Dome Lights — Wiring Diagram (Arduino UNO R3)
═══════════════════════════════════════════════════════════

[Arduino UNO R3]
  5V   ──────────┬──── (100µF Cap +) ──── GND
                 └──── [NeoPixel Ring: 5V/PWR]
  GND  ──────────┬──── (100µF Cap −)
                 └──── [NeoPixel Ring: GND]
  Pin 6 ──── (470Ω) ── [NeoPixel Ring: DIN/DATA IN]

Color code:
  RED    = 5V power
  BLACK  = GND
  GREEN  = Data signal (Pin 6)
  GREY   = Through 470Ω resistor
  BROWN  = Capacitor leads

Connection Table:
┌─────────────────────┬──────────────────────────────────┐
│ From                │ To                               │
├─────────────────────┼──────────────────────────────────┤
│ Arduino 5V          │ NeoPixel Ring: 5V (PWR)          │
│ Arduino 5V          │ 100µF Capacitor: + (long leg)    │
│ Arduino GND         │ NeoPixel Ring: GND               │
│ Arduino GND         │ 100µF Capacitor: − (short leg)   │
│ Arduino Pin 6       │ Resistor leg 1 (470Ω)            │
│ Resistor leg 2      │ NeoPixel Ring: DIN               │
└─────────────────────┴──────────────────────────────────┘

⚡ Notes:
  - Arduino UNO is 5V logic — compatible with WS2812B
  - 100µF cap prevents power surge on LED startup
  - 470Ω resistor prevents signal overshoot
  - If using ESP32: add 74AHCT125 level shifter on data line

```

**LUKE:** "Print that. Actually — download the PDF and print it. I want this on the wall."

Click **Download PDF**. The wiring diagram is saved for your build log.

## Multi-File Projects: Real Code for Real Droids 📁

*Han Solo examines the two-tab project with a raised eyebrow.*

**HAN:** "Two files. A main and a header. That's how real firmware is structured. Not everything crammed into one endless sketch."

Codey's **Multi-file Projects** feature gave us:

- `r2d2-dome.ino` — clean, readable main file (12 lines!)
- `animations.h` — all animation logic in one focused place

Click between the tabs in Codey's editor. Both files have syntax highlighting and linting. When you compile, Codey knows they belong together and sends both to the cloud compiler.

**HAN:** "When we add the sensor system and the motor system in later episodes, each gets its own file. R2 stays clean. No 500-line monster sketch."

## Compile, Upload, and Watch the Dome Glow 🚀

Click **Compile**:

```
✓ Compilation successful
  Board:   Arduino UNO R3
  Sketch:  r2d2-dome.ino + animations.h
  Library: Adafruit NeoPixel (pre-installed)
  Size:    6,842 bytes (21% of flash)

```

Click **Upload**.

*The ring comes to life. Blue-white breathing. Slow. Like R2-D2 resting.*

*Then the scan — a single blue LED orbiting the ring.*

*Then the happiness sequence — rainbow wash, then back to blue-white.*

*Then the alert — red sweeping urgently.*

**LUKE:** *"It's... it's his dome. It looks exactly like his dome."*

*R2-D2 — the actual one — beeps from the corner. The sound is quiet, reverent. Even he seems moved.*

## Save Your Milestone 🚩

Name this milestone:

```
Milestone: "R2-D2 Dome Lights — Episode 3 Complete"

```

Codey saves the code, headers, and chat history.

## What's Next: The All-Seeing Eye 👁️

*Yoda sits quietly for a moment.*

**YODA:** "A droid that glows and beeps, you have built. But see, R2-D2 can. Obstacles he detects. Danger he senses. In Episode 4 — the sensor eye we add. HC-SR04, PIR sensor, reactive behavior. And the Auto Error Fixing feature... needed it will be."

*R2-D2 beeps something urgent.*

**YODA:** "Yes, Artoo. Ahead, Episode 4 is. Patient you must be."

**🔗 Resources**

- **Adafruit NeoPixel library**: [github.com/adafruit/Adafruit_NeoPixel](https://github.com/adafruit/Adafruit_NeoPixel)
- **WS2812B datasheet**: Search "WS2812B datasheet"
- **Codey Online**: [codey.online](http://codey.online)

*🤖 R2D2 Creation with Codey — building the galaxy's greatest droid, one episode at a time. May the Force — and the cloud compiler — be with you.*