---
title: "R2D2 Creation with Codey 🤖 Ep.5" 
published: false 
description: "Episode 5: Help me, Codey Online — you're my only hope! R2-D2's holographic projector comes to life with an SSD1306 OLED display over I2C. But first — a major upgrade. We leave the Arduino UNO behind and migrate to the ESP32-S3 N16R8: dual-core, 16MB Flash, 8MB PSRAM, native USB. C-3PO has voltage concerns. Codey has a wiring diagram. Milestones save the day when a rollback becomes necessary." 
tags: [esp32, oled, ai, makers] 
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/r2-d2_creation_with_codey_series/r2-d2-creation-with-codey-episode-05.png" 
series: "R2-D2 Creation With Codey" 
canonical_url: "" 
organization: "the-software-s-journey" 
part: 5
---
## Episode 5: The Projector of Hope

## "Help Me, Codey Online — You're My Only Hope" 📽️

*The workshop is quiet. R2-D2 sits in the corner, dome LEDs softly breathing their blue-white rhythm. Then, suddenly — a holographic projection flickers from somewhere inside his chassis. Princess Leia. Eighteen centimetres tall. Looping silently.*

*Luke stares.*

**LUKE:** "That's what I want. That's exactly what I want. An OLED screen mounted in his dome, showing status messages, projecting text like a mission briefing. Something that makes him feel... alive."

*R2-D2 beeps with the energy of someone who has been waiting patiently for this episode.*

**LUKE:** "But Obi-Wan said something about upgrading the brain first. Moving to a bigger board."

*Obi-Wan's voice arrives like dawn.*

**OBI-WAN:** "The Arduino UNO served us well through four episodes, young one. But what lies ahead — the motion systems, the voice responses, the wireless capabilities — these require a more powerful foundation. It is time to meet the ESP32-S3 N16R8."

## 🗂️ SIPOC — The Great Upgrade

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (the maker) | "Migrate to ESP32-S3 N16R8 and add SSD1306 OLED via I2C" | Codey recognises the new board, updates pin mappings, rewrites I2C addresses, flags 3.3V implications | Correct ESP32-S3 firmware with Adafruit_SSD1306, new I2C pins | ESP32-S3 N16R8 — which drives the OLED and all previous systems |
| Codey Voltage Safety Check | NeoPixel (5V logic), OLED (3.3V or 5V), HC-SR04 (5V) vs ESP32-S3 (3.3V GPIO) | Cross-references component voltage requirements with ESP32-S3 GPIO levels | Specific warnings per component + recommended level shifter or workarounds | You — who avoid smoke on this far more expensive board |
| SSD1306 OLED (128×64) | 3.3V power, I2C (SDA/SCL) | Receives display commands over I2C protocol | A crisp 128×64 pixel display showing R2 status and messages | R2-D2's dome — the holographic projection system |
| Milestones & Rollback | Previous working code at Episode 4 milestone | One-click restore of code + chat history | Known-good state if the board migration causes issues | You — who can always go back |

## Meet the New Brain: ESP32-S3 N16R8 🧠

*C-3PO emerges carrying a padded case like it contains the Holy Grail.*

**C-3PO:** "The ESP32-S3 N16R8. I have computed its specifications forty-seven times. Allow me to translate from technical to comprehensible:"

| Feature | ESP32-S3 N16R8 | Arduino UNO R3 |
| --- | --- | --- |
| Processor | Dual-core Xtensa LX7 @ 240 MHz | Single-core ATmega328P @ 16 MHz |
| Flash storage | 16 MB | 32 KB |
| PSRAM | 8 MB | 0 |
| GPIO pins | 45 | 14 digital |
| Logic voltage | 3.3V | 5V |
| Wi-Fi | Yes (802.11b/g/n) | No |
| Bluetooth | Yes (BLE 5.0 + Classic) | No |
| USB | Native USB-CDC (two ports!) | USB via CH340/FTDI chip |
| PWM | LEDC — 8 channels, 14-bit resolution | 6 PWM pins, 8-bit |
| DAC | 2× 8-bit DAC outputs | None |

**C-3PO:** "Considerably more capable. However — and I cannot stress this strongly enough — the GPIO outputs are **3.3V**, not 5V. Several of our existing components expect a 5V signal. This is a matter of the gravest concern and I intend to address each one individually."

*R2-D2 beeps impatiently.*

**C-3PO:** "Artoo, voltage compatibility is NOT a detail. It is the difference between a functional droid and a very expensive doorstop."

## The 3.3V Migration: C-3PO's Component Review ⚡

*Darth Vader's voice rumbles through the ventilation system.*

**VADER:** "Your lack of a level shifter... disturbs me."

*C-3PO whirls around, then remembers where he is.*

**C-3PO:** "Quite. Let us review each component's voltage situation with the ESP32-S3:"

### Component Voltage Compatibility Table

| Component | VCC Needed | Signal Level Needed | ESP32-S3 GPIO (3.3V) | Action Required |
| --- | --- | --- | --- | --- |
| SSD1306 OLED | 3.3V or 5V | 3.3V I2C | ✅ Compatible | None — OLED runs perfectly on 3.3V |
| Piezo Buzzer | 3.3V–5V | 3.3V PWM | ✅ Compatible | None — works fine at 3.3V |
| NeoPixel WS2812B | 5V | 5V data signal | ⚠️ Marginal | Add 74AHCT125 level shifter OR use 470Ω + 3V3-to-5V shifter |
| HC-SR04 | 5V | 5V ECHO output | ⚠️ Risky | The ECHO pin outputs 5V — use voltage divider on ECHO |
| PIR HC-SR501 | 5V | 5V output | ⚠️ Risky | Use voltage divider (10k + 20k) on output pin |

**C-3PO:** "Codey will generate the level shifter and voltage divider circuits in the wiring diagram. This is precisely the scenario for which Codey's voltage safety checks were designed."

*Codey, upon seeing the ESP32-S3 selected, automatically adds voltage warnings for each incompatible component in the project.*

## Selecting the New Board in Codey 🔄

*Han Solo demonstrates with the casual confidence of someone who has hot-swapped ship components mid-jump.*

**HAN:** "Simple. In your Codey project, click the board selector at the top. Change it from Arduino UNO R3 to ESP32-S3 N16R8. Done. Codey figures out the rest."

1. Click the **board name** dropdown at the top of the Codey interface
2. Select **ESP32-S3 N16R8**
3. Codey immediately shows:

```
⚠️  Board changed: Arduino UNO R3 → ESP32-S3 N16R8

This board uses 3.3V GPIO logic.
I've detected components in your project that may be affected:

  • NeoPixel WS2812B (pin 6): Needs level shifter — see updated wiring diagram
  • HC-SR04 (pins 9/10): ECHO pin outputs 5V — needs voltage divider
  • PIR HC-SR501 (pin 2): Output is 5V — needs voltage divider

  Recommended: Add 74AHCT125 (quad level shifter) for WS2812B data line.
  Piezo buzzer (pin 8): ✓ Compatible — no change needed.

Shall I update the code and wiring diagram for the ESP32-S3?

```

*R2-D2 beeps enthusiastically: "YES."*

**HAN:** "See? It flags everything. No surprises."

## Before Moving On: Rolling Back If Needed 🚩

*Obi-Wan raises a steady hand.*

**OBI-WAN:** "Before this migration, let us invoke the wisdom of Milestones. Our Episode 4 code runs perfectly on the Arduino UNO. If the ESP32-S3 migration encounters difficulty, we must be able to return to that known-good state."

In Codey, click **Milestones** → find **"R2-D2 Sensor Eye — Episode 4 Complete"** → click **Restore**.

Both the code AND the chat history are restored to exactly how they were after Episode 4.

*Now* make a new milestone before starting the migration:

```
Milestone: "Pre-ESP32 Migration Checkpoint"

```

**OBI-WAN:** "The Force gives you wisdom to try. The Milestone gives you the courage to try boldly."

*R2-D2 beeps something along the lines of "can we please just look at the OLED already."*

## Prompting Codey for the ESP32-S3 Migration + OLED 💬

In **Plan mode** first:

```
We're upgrading R2-D2's brain from Arduino UNO R3 to ESP32-S3 N16R8.

Existing systems to migrate:
  - Piezo buzzer on pin 8 → keep same pin, use LEDC channel instead of tone()
  - NeoPixel ring (12 LEDs) on pin 6 → keep pin, add note about 74AHCT125
  - HC-SR04 on pins 9/10 → keep pins, add voltage divider on ECHO
  - PIR sensor on pin 2 → keep pin, add voltage divider on output

New addition:
  - SSD1306 OLED 128x64 display via I2C
  - ESP32-S3 I2C default: SDA=GPIO8, SCL=GPIO9
  - Show these screens:
    1. Startup: "R2-D2 ONLINE" with a spinning animation
    2. Idle: distance reading + "SAFE" or "ALERT"
    3. Motion: "MOTION DETECTED" with exclamation marks
    4. Very close: "TOO CLOSE" with a blinking border

Show me the plan before writing any code.

```

### Codey Plan Mode Response

```
R2-D2 ESP32-S3 Migration + Holographic Projector — Plan

FILES:
  r2d2-main.ino     — setup() and loop(), board init
  animations.h      — NeoPixel dome animations (migrated to ESP32)
  sensors.h         — HC-SR04 + PIR (voltage divider notes)
  display.h         — SSD1306 OLED functions (new)
  sounds.h          — LEDC-based tone functions (replaces tone() API)

KEY CHANGES:
  1. tone() → ledc functions (ESP32 uses LEDC peripheral for PWM)
     ledcSetup(0, 2637, 8) + ledcWrite(0, 128) replaces tone(pin, freq)

  2. I2C on ESP32-S3: Wire.begin(8, 9) for SDA=GPIO8, SCL=GPIO9
     (Adafruit_SSD1306 uses Wire automatically)

  3. NeoPixel: Same FastLED/NeoPixel API — ESP32-S3 natively supports
     RMT peripheral for WS2812B. Add 74AHCT125 recommendation in wiring.

  4. HC-SR04 ECHO: Add voltage divider (10kΩ + 20kΩ) to reduce 5V→3.3V
     TRIG output from ESP32-S3 (3.3V) is sufficient to trigger HC-SR04.

  5. PIR output: Add voltage divider (10kΩ + 20kΩ)

  DISPLAY STATES:
    • BOOT  — "R2-D2 ONLINE", spinner, 2 seconds
    • IDLE  — Distance + status, updates every 500ms
    • SCAN  — "MOTION DETECTED !!", large text
    • ALERT — "TOO CLOSE" with animated blinking border

Proceed?

```

Click **Proceed**. Codey writes all five files.

### Generated `display.h`

```cpp
// display.h — R2-D2 Holographic Projector
// SSD1306 OLED 128x64 via I2C
// ESP32-S3: SDA=GPIO8, SCL=GPIO9

#pragma once
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT  64
#define OLED_ADDR     0x3C   // Default I2C address for SSD1306

// OLED_RESET = -1 means share the Arduino reset pin (or no reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

bool displayReady = false;

// ── Boot animation ────────────────────────────────────────────────
const char* spinFrames[] = {"|", "/", "-", "\\"};
int spinIdx = 0;
unsigned long lastSpinMs = 0;
unsigned long bootStartMs = 0;
bool bootDone = false;

void initDisplay() {
  // ESP32-S3 I2C: SDA=GPIO8, SCL=GPIO9
  Wire.begin(8, 9);

  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("SSD1306 not found — check wiring!");
    return;
  }

  displayReady = true;
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  bootStartMs = millis();
  Serial.println("OLED projector online!");
}

void showBootScreen() {
  if (!displayReady || bootDone) return;

  unsigned long now = millis();

  if (now - lastSpinMs > 150) {
    lastSpinMs = now;
    spinIdx = (spinIdx + 1) % 4;

    display.clearDisplay();

    // Title — large text centred
    display.setTextSize(2);
    display.setCursor(4, 8);
    display.println("R2-D2");
    display.setCursor(4, 28);
    display.println("ONLINE");

    // Spinner bottom right
    display.setTextSize(2);
    display.setCursor(112, 48);
    display.print(spinFrames[spinIdx]);

    display.display();
  }

  if (now - bootStartMs > 2500) {
    bootDone = true;
  }
}

// ── Idle screen: distance + status ──────────────────────────────
unsigned long lastIdleRefreshMs = 0;

void showIdleScreen(float distance) {
  if (!displayReady) return;

  unsigned long now = millis();
  if (now - lastIdleRefreshMs < 500) return;
  lastIdleRefreshMs = now;

  display.clearDisplay();

  // Distance reading
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("DISTANCE:");

  display.setTextSize(2);
  display.setCursor(0, 12);
  if (distance < 500.0f) {
    display.print((int)distance);
    display.print(" cm");
  } else {
    display.print("--- cm");
  }

  // Status label
  display.setTextSize(1);
  display.setCursor(0, 48);
  if (distance < 15.0f) {
    display.print("!! TOO CLOSE !!");
  } else if (distance < 30.0f) {
    display.print("CAUTION");
  } else {
    display.print("SAFE");
  }

  display.display();
}

// ── Motion detected screen ───────────────────────────────────────
void showMotionScreen() {
  if (!displayReady) return;

  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(0, 8);
  display.println("MOTION");
  display.setCursor(0, 28);
  display.println("DETECTED");
  display.setTextSize(3);
  display.setCursor(96, 28);
  display.print("!!");
  display.display();
}

// ── Alert: blinking border + TOO CLOSE ──────────────────────────
bool borderVisible = true;
unsigned long lastBorderFlipMs = 0;

void showAlertScreen() {
  if (!displayReady) return;

  unsigned long now = millis();
  if (now - lastBorderFlipMs > 300) {
    lastBorderFlipMs = now;
    borderVisible = !borderVisible;
  }

  display.clearDisplay();

  if (borderVisible) {
    display.drawRect(0, 0, 128, 64, SSD1306_WHITE);
    display.drawRect(2, 2, 124, 60, SSD1306_WHITE);
  }

  display.setTextSize(2);
  display.setCursor(8, 16);
  display.println("TOO");
  display.setCursor(8, 36);
  display.println("CLOSE!");
  display.display();
}

```

### Generated `sounds.h` (ESP32 LEDC version)

```cpp
// sounds.h — R2-D2 Sound System (ESP32-S3 LEDC)
// Replaces Arduino tone() with ESP32 LEDC peripheral

#pragma once

#define BUZZER_PIN    8    // GPIO8 on ESP32-S3
#define LEDC_CHANNEL  0
#define LEDC_TIMER    8    // 8-bit resolution

bool ledcReady = false;

void initSounds() {
  // Configure LEDC channel for buzzer
  ledcSetup(LEDC_CHANNEL, 1000, LEDC_TIMER);
  ledcAttachPin(BUZZER_PIN, LEDC_CHANNEL);
  ledcWrite(LEDC_CHANNEL, 0); // silent
  ledcReady = true;
}

void playTone(int frequency) {
  if (!ledcReady || frequency <= 0) {
    ledcWrite(LEDC_CHANNEL, 0);
    return;
  }
  ledcWriteTone(LEDC_CHANNEL, frequency);
  ledcWrite(LEDC_CHANNEL, 128); // 50% duty cycle
}

void stopTone() {
  ledcWrite(LEDC_CHANNEL, 0);
}

```

### Generated `r2d2-main.ino` (ESP32-S3 version)

```cpp
// r2d2-main.ino — R2-D2 ESP32-S3 N16R8
// Unifying all systems: sounds, dome lights, sensors, display

#include <Adafruit_NeoPixel.h>
#include "sounds.h"
#include "animations.h"
#include "sensors.h"
#include "display.h"

void setup() {
  Serial.begin(115200);
  Serial.println("R2-D2 ESP32-S3 boot sequence...");

  initSounds();
  initAnimations();   // NeoPixel dome
  initSensors();      // HC-SR04 + PIR
  initDisplay();      // SSD1306 OLED

  Serial.println("All systems nominal. R2-D2 is ONLINE.");
}

void loop() {
  // Boot animation runs first
  if (!bootDone) {
    showBootScreen();
    return;
  }

  // Read sensors
  float dist    = readDistance();
  bool  motion  = checkMotion();

  // Update display based on state
  if (dist < 15.0f) {
    showAlertScreen();
  } else if (motion) {
    showMotionScreen();
  } else {
    showIdleScreen(dist);
  }

  // Update dome animations (non-blocking)
  updateAnimationsSensors(dist, motion);
}

```

## The Wiring Diagram — ESP32-S3 Edition 🧭

*C-3PO straightens to his full height, relieved.*

**C-3PO:** "Codey has drawn the wiring diagram. I have checked it. It includes the voltage dividers. It includes the level shifter recommendation. It is correct. I am, for the first time this episode, not worried."

```
R2-D2 Holographic System — ESP32-S3 N16R8 Wiring
════════════════════════════════════════════════════════════

[ESP32-S3 N16R8]

  POWER RAIL (3.3V):
    3V3  ───┬── OLED VCC (3.3V input)
            └── (100µF cap +)
    GND  ───┬── OLED GND
            └── (100µF cap −)

  POWER RAIL (5V via USB):
    VIN  ───┬── NeoPixel Ring: 5V
            ├── HC-SR04: VCC
            └── PIR HC-SR501: VCC
    GND  ───┬── NeoPixel Ring: GND
            ├── HC-SR04: GND
            └── PIR HC-SR501: GND

  I2C BUS (3.3V — OLED compatible):
    GPIO8 (SDA) ──── OLED SDA
    GPIO9 (SCL) ──── OLED SCL

  SIGNALS with PROTECTION:
    GPIO6  ──── [74AHCT125 level shifter] ──── NeoPixel DIN (5V)
    GPIO8  ──── (100Ω) ──────────────────────── Piezo Buzzer +
    GPIO9  ────────────────────────────────────── HC-SR04 TRIG
    GPIO10 ──── [10kΩ / 20kΩ divider] ─────────── HC-SR04 ECHO
    GPIO2  ──── [10kΩ / 20kΩ divider] ─────────── PIR OUT

Voltage Dividers for 5V → 3.3V:
  GPIO_pin ←── (junction) ─── 20kΩ ─── GND
                   └────────── 10kΩ ─── 5V signal in

Connection Table:
┌──────────────────────┬───────────────────────────────────┐
│ From                 │ To                                │
├──────────────────────┼───────────────────────────────────┤
│ ESP32-S3 3V3         │ OLED VCC                          │
│ ESP32-S3 GND         │ OLED GND                          │
│ ESP32-S3 GPIO8 (SDA) │ OLED SDA                          │
│ ESP32-S3 GPIO9 (SCL) │ OLED SCL                          │
│ ESP32-S3 VIN (5V)    │ NeoPixel 5V, HC-SR04 VCC, PIR VCC│
│ ESP32-S3 GPIO6       │ Level shifter → NeoPixel DIN      │
│ ESP32-S3 GPIO8       │ 100Ω → Piezo Buzzer +             │
│ ESP32-S3 GPIO9       │ HC-SR04 TRIG                      │
│ HC-SR04 ECHO (5V)    │ Voltage divider → ESP32 GPIO10    │
│ PIR OUT (5V)         │ Voltage divider → ESP32 GPIO2     │
└──────────────────────┴───────────────────────────────────┘

⚡ Critical Notes:
  - OLED: 3.3V compatible — no level shifting needed
  - NeoPixel: 5V logic required — 74AHCT125 MANDATORY
  - HC-SR04 ECHO: 5V output — voltage divider protects ESP32-S3
  - ESP32-S3 has two USB ports — Codey auto-detects the correct one

```

**LUKE:** "Download the PDF. Print two copies."

## Compile and Upload to ESP32-S3 🚀

The ESP32-S3 N16R8 has **two USB ports**. Codey knows which one to use:

```
⚙️  Board: ESP32-S3 N16R8

Note: This board has two USB connectors:
  • USB (UART) — for serial communication / upload via UART bridge
  • USB-OTG (native USB-CDC) — direct USB communication

Codey will attempt to detect the correct port automatically.
If upload fails, try the other USB connector.

```

Click **Compile**:

```
✓ Compilation successful
  Board:   ESP32-S3 N16R8
  Sketch:  r2d2-main.ino + 4 headers
  Binary:  412,288 bytes (5.9% of 16MB Flash)
  RAM:     Used 28,492 bytes (8.7% of 327KB)
  PSRAM:   8MB available for future expansion

```

Click **Upload** → Select the correct USB port → Flash completes.

*The OLED lights up: "R2-D2" and "ONLINE" with a spinning cursor.*

*R2-D2 beeps.*

*Then the idle screen appears: "DISTANCE: 87 cm — SAFE."*

*Luke waves his hand in front of the HC-SR04. The screen immediately switches to "TOO CLOSE!" with a blinking border.*

**LUKE:** "It works. He sees me. He's telling me I'm too close."

*R2-D2 beeps something that clearly means "yes, please back up."*

## Save the Milestone 🚩

```
Milestone: "R2-D2 Holographic Projector — Episode 5 Complete"

```

Four systems running. ESP32-S3 humming. The OLED projecting. The dome glowing. The sensors watching.

## What's Next: The Motion Systems Activate ⚙️

*Han Solo slaps the workbench.*

**HAN:** "Okay. He blinks, he beeps, he shows you a screen. But you know what R2-D2 actually does that nobody else can? He moves. He rolls. His dome spins. He navigates. Episode 6 — we give this droid wheels and a rotating dome. Servo for the dome, DC motors for the base. The wiring diagram is going to get interesting."

*R2-D2 beeps the equivalent of "I have been waiting for this my entire existence."*

**🔗 Resources**

- **ESP32-S3 datasheet**: [espressif.com/esp32-s3](https://www.espressif.com/en/products/socs/esp32-s3)
- **SSD1306 library**: [github.com/adafruit/Adafruit_SSD1306](https://github.com/adafruit/Adafruit_SSD1306)
- **74AHCT125 level shifter**: Search "74AHCT125 NeoPixel level shifter"
- **Codey Online**: [codey.online](http://codey.online)

*🤖 R2D2 Creation with Codey — building the galaxy's greatest droid, one episode at a time. May the Force — and the cloud compiler — be with you.*