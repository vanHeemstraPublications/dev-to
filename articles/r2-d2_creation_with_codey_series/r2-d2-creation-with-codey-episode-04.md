---
title: "R2D2 Creation with Codey 🤖 Ep.4" 
published: false 
description: "Episode 4: R2-D2 doesn't just glow and beep — he watches, senses, and reacts. We add the HC-SR04 ultrasonic sensor eye and a PIR motion detector. When R2 detects something close, his dome reacts. Codey's Auto Error Fixing rescues a compilation failure in real time. And the Vision feature reads a breadboard photo to check our wiring." 
tags: [arduino, sensors, ai, makers] 
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/r2-d2_creation_with_codey_series/r2-d2-creation-with-codey-episode-04.png" 
series: "R2-D2 Creation With Codey" 
canonical_url: "" 
organization: "the-software-s-journey" 
part: 4
---
## Episode 4: The All-Seeing Eye

## "Impressive. Most Impressive." 👁️

*Darth Vader enters — wait, no. Wrong side.*

*Luke Skywalker stands at the workbench, holding an HC-SR04 ultrasonic sensor up to the light.*

**LUKE:** "I've always wondered how he knew. How R2 always knew when something was coming. When an obstacle was in the way. When the Death Star trench was approaching. He sees things. Feels them. Before anyone else does."

*R2-D2 beeps softly, as if this is a deeply personal topic.*

**LUKE:** "Today we give him that. The sensor eye. And this time—" *he gestures at the screen* "—Codey's going to show us something called Auto Error Fixing. Because I have a feeling we're going to need it."

*From somewhere unseen, a voice floats through the Force.*

**VADER:** *"Your lack of a level-shifted data pin... disturbs me."*

**LUKE:** "We're on 5V. We'll be fine."

## 🗂️ SIPOC — The Sensor Eye System

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (the maker) | "Add HC-SR04 on pins 9/10 and PIR on pin 2, react with beeps and dome color changes" | Codey writes sensor code, integrates with sound and dome systems from previous episodes | Unified firmware: sense → respond with light + sound | R2-D2 — who now reacts to the world around him |
| HC-SR04 Sensor | 5V power, TRIG pulse from Arduino | Emits ultrasonic pulse, measures return echo time | Distance in centimetres | The code — which decides how close is "too close" |
| PIR Motion Sensor | 5V power, GPIO input to Arduino | Digital HIGH when motion detected | A HIGH signal on the interrupt pin | The code — which triggers the alert sequence |
| Auto Error Fixing | A compilation error from incorrect code | Codey reads the error log, rewrites the offending lines, recompiles | Fixed code that compiles successfully | You — who get working firmware without decoding C++ error messages |
| Vision Feature | A photo of your breadboard | Codey reads the image and identifies component placement | A verification report: "Wiring looks correct" or specific mismatches | You — who confirm wiring before upload |

## The Components 🔧

*C-3PO enters with a tray of precisely arranged components.*

**C-3PO:** "Today we add perception to R2-D2's capabilities. The HC-SR04 ultrasonic sensor — which I should note operates at 5V and is therefore perfectly compatible with the Arduino UNO without any level shifting, which is a relief — and the HC-SR501 PIR motion sensor, also 5V compatible. I have pre-sorted them by height to prevent any confusion."

*R2-D2 beeps something that sounds like "nobody asked you to sort them."*

| Component | Quantity | Notes |
| --- | --- | --- |
| Arduino UNO R3 | 1 | Our trusted base |
| HC-SR04 ultrasonic sensor | 1 | 5V, TRIG + ECHO pins |
| HC-SR501 PIR sensor | 1 | 5V, single digital output |
| 10kΩ resistor | 1 | PIR output pull-down (some modules need it) |
| Jumper wires | 6 |  |
| USB cable | 1 |  |

Plus the buzzer from Episode 2 and NeoPixel ring from Episode 3 — we are building on the complete system.

## The Codey Prompt — Building on What We Have 💬

*Han Solo points at the screen.*

**HAN:** "Here's the thing about AI coding tools — you don't start from scratch every time. You tell it what already exists and what you want to add. Context is everything. Same in the smuggling business."

**LUKE:** "You're comparing Codey to smuggling?"

**HAN:** "I'm saying context matters. Do you want the lecture or the sensor?"

Open your Codey project (from Episode 3 milestone). In **Agent mode**:

```
We're continuing the R2-D2 build from the previous episodes.
Existing systems:
  - Piezo buzzer on pin 8 (tone-based sounds)
  - NeoPixel ring (12 LEDs) on pin 6 (dome animations)

Add these sensor systems:
  1. HC-SR04 ultrasonic sensor
     - TRIG on pin 9, ECHO on pin 10
     - Measure distance every 150ms (non-blocking)
     - If distance < 30cm: trigger alert animation + alert sound
     - If distance < 15cm: trigger full RED dome + rapid alert beeps

  2. PIR motion sensor on pin 2 (interrupt-capable)
     - On motion detected: trigger scan animation for 3 seconds
     - Then return to idle

Extend animations.h with these reactive behaviors.
Keep the state machine approach.
Use millis() everywhere — no delay().

```

### Generated Code Addition to `animations.h`

```cpp
// ── Sensor additions (append to animations.h) ───────────────────

// ── HC-SR04 ─────────────────────────────────────────────────────
#define TRIG_PIN   9
#define ECHO_PIN   10

unsigned long lastSonarMs  = 0;
float         lastDistance = 999.0f;

float readDistance() {
  // Non-blocking: only trigger if enough time has passed
  unsigned long now = millis();
  if (now - lastSonarMs < 150) return lastDistance;
  lastSonarMs = now;

  // Send 10µs TRIG pulse
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Read echo duration (timeout 30ms = ~5m max range)
  long duration = pulseIn(ECHO_PIN, HIGH, 30000UL);
  if (duration == 0) return 999.0f;

  // Convert to centimetres
  lastDistance = (duration * 0.0343f) / 2.0f;
  return lastDistance;
}

// ── PIR Motion Sensor ────────────────────────────────────────────
#define PIR_PIN   2

volatile bool motionDetected = false;

void IRAM_ATTR onMotion() {
  motionDetected = true;
}

// ── Reactive behaviour in updateAnimations() ─────────────────────
// (replaces/extends the existing updateAnimations function)

void updateAnimationsSensors() {
  unsigned long now = millis();

  // ── Check PIR first (interrupt-driven, higher priority) ─────
  if (motionDetected) {
    motionDetected = false;
    currentState   = SCAN;
    stateStartMs   = now;
    Serial.println("Motion detected — scan mode!");
  }

  // ── Check HC-SR04 distance ─────────────────────────────────
  float dist = readDistance();

  if (dist < 15.0f) {
    // Very close — full red alert
    if (currentState != ALERT) {
      currentState = ALERT;
      stateStartMs = now;
      tone(BUZZER_PIN, 2637); // C6 — high alert tone
    }
    // Override: set all LEDs red while this close
    for (int i = 0; i < NUMPIXELS; i++) {
      ring.setPixelColor(i, ring.Color(BRIGHTNESS, 0, 0));
    }
    ring.show();
    return;
  } else if (dist < 30.0f) {
    // Approaching — amber warning
    if (currentState == IDLE) {
      currentState = ALERT;
      stateStartMs = now;
    }
  } else {
    noTone(BUZZER_PIN); // Silence if moved away
  }

  // ── Normal state machine ────────────────────────────────────
  updateAnimations(); // existing function handles the rest
}

```

### Updated `r2d2-dome.ino`

```cpp
// r2d2-dome.ino — updated for sensor eye
#include <Adafruit_NeoPixel.h>
#include "animations.h"

void setup() {
  Serial.begin(9600);
  initAnimations();

  // Sensor pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(PIR_PIN,  INPUT);

  // PIR interrupt — fires on rising edge (motion start)
  attachInterrupt(digitalPinToInterrupt(PIR_PIN), onMotion, RISING);

  Serial.println("R2-D2 sensor eye online!");
}

void loop() {
  updateAnimationsSensors(); // new unified call
}

```

## Auto Error Fixing in Action 🛠️

*And then it happens.*

**LUKE:** "I tried to compile and—"

```
Compilation Error:
  animations.h:47: error: 'IRAM_ATTR' was not declared in this scope
  animations.h:47: note: 'IRAM_ATTR' is an ESP32 attribute, not available on AVR

```

**LUKE:** "What does that mean? I just—"

*Before Luke can panic, the screen updates automatically.*

**CODEY AUTO ERROR FIX:**

```
I see the error! IRAM_ATTR is an ESP32-specific macro for placing
interrupt handlers in IRAM (fast memory). The Arduino UNO uses
an ATmega328P — it doesn't have IRAM at all.

For Arduino UNO, the interrupt handler just needs the ISR() attribute,
which I used in the function signature. I'll remove IRAM_ATTR.

Fixed:
  Before: void IRAM_ATTR onMotion() {
  After:  void onMotion() {

Recompiling...

```

```
✓ Compilation successful (after auto-fix)
  Board:   Arduino UNO R3
  Sketch:  r2d2-dome.ino + animations.h
  Size:    9,104 bytes (28% of flash)

```

**LUKE:** "It... fixed it. By itself."

**HAN:** *"Never tell me the odds."*

**LUKE:** "That's not the same—"

**HAN:** "The AI fixed its own mistake without you having to understand why. That's what matters."

## The Wiring Diagram — Three Systems Now 🧭

Click **Wiring Diagram**. The diagram now shows all three systems:

```
R2-D2 Sensor Eye + Dome + Sound — Wiring Diagram
════════════════════════════════════════════════════════════

[Arduino UNO R3]

  POWER RAIL:
    5V  ─────────┬── NeoPixel 5V
                 ├── HC-SR04 VCC
                 ├── PIR Sensor VCC
                 └── (100µF cap +)
    GND ─────────┬── NeoPixel GND
                 ├── HC-SR04 GND
                 ├── PIR Sensor GND
                 └── (100µF cap −)

  SIGNALS:
    Pin 6  ──── (470Ω) ──── NeoPixel DIN
    Pin 8  ──── (100Ω) ──── Piezo Buzzer +
    Pin 9  ─────────────── HC-SR04 TRIG
    Pin 10 ─────────────── HC-SR04 ECHO
    Pin 2  ─────────────── PIR Sensor OUT

Color code:
  RED    = 5V / power rail
  BLACK  = GND rail
  GREEN  = NeoPixel data (pin 6)
  ORANGE = Buzzer signal (pin 8)
  BLUE   = HC-SR04 TRIG (pin 9)
  PURPLE = HC-SR04 ECHO (pin 10)
  YELLOW = PIR output (pin 2)
  GREY   = Through resistors

Connection Table:
┌────────────────────┬──────────────────────────────────┐
│ From               │ To                               │
├────────────────────┼──────────────────────────────────┤
│ Arduino 5V         │ NeoPixel Ring: 5V                │
│ Arduino 5V         │ HC-SR04: VCC                     │
│ Arduino 5V         │ PIR HC-SR501: VCC                │
│ Arduino 5V         │ 100µF Cap: + (long leg)          │
│ Arduino GND        │ NeoPixel Ring: GND               │
│ Arduino GND        │ HC-SR04: GND                     │
│ Arduino GND        │ PIR HC-SR501: GND                │
│ Arduino GND        │ 100µF Cap: − (short leg)         │
│ Arduino Pin 6      │ Resistor 470Ω → NeoPixel DIN     │
│ Arduino Pin 8      │ Resistor 100Ω → Piezo (+)        │
│ Arduino Pin 9      │ HC-SR04: TRIG                    │
│ Arduino Pin 10     │ HC-SR04: ECHO                    │
│ Arduino Pin 2      │ PIR HC-SR501: OUT                │
└────────────────────┴──────────────────────────────────┘

```

**C-3PO:** "Seven signals on eight wires plus the power rail. The color-coded system makes it genuinely manageable. Download the PDF immediately — this is the most complex wiring diagram we have produced so far and I do not trust organic memory."

## Vision Feature: "Is My Breadboard Wired Correctly?" 👁️

*Luke takes a photo of his assembled breadboard.*

**LUKE:** "Before I upload — can I check this with Codey? Just to be sure?"

Click the **Vision** icon in Codey (Pro feature). Upload the breadboard photo.

Codey responds:

```
I can see your breadboard. Here's what I observe:

✓ HC-SR04 ultrasonic sensor connected:
  - VCC to 5V rail — correct
  - GND to GND rail — correct
  - TRIG appears connected to the digital pin area (looks like pin 9) — correct
  - ECHO appears connected to pin 10 — correct

✓ PIR sensor:
  - VCC and GND connections look correct
  - Signal wire appears to go to pin 2 — correct

⚠️ One potential issue:
  I notice what looks like the NeoPixel data wire may not have the
  470Ω resistor in line — it appears to connect directly. Check that
  the resistor is seated in the breadboard between pin 6 and the DIN
  input. A direct connection may cause LED flickering or data errors.

Everything else looks correctly laid out!

```

*Luke examines the breadboard.*

**LUKE:** "The resistor... it's in the wrong row. It's not actually connected to anything."

*R2-D2 beeps in the tone of "I could have told you that."*

**LUKE:** "Vision just saved R2's dome lights."

## What's Next: The Holographic Projector 📽️

*Obi-Wan's presence fills the workshop like warm light.*

**OBI-WAN:** "You have given R2-D2 his lights. His sounds. His sense of the world around him. But the moment that first made the galaxy fall in love with this droid — do you remember it, Luke?"

**LUKE:** *"Help me, Obi-Wan Kenobi. You're my only hope."*

**OBI-WAN:** "In Episode 5, we give Artoo his projector. The SSD1306 OLED display — small, crisp, I2C wired — will show R2's status, messages, and a recreation of that famous message. Milestones and Rollback will save us if anything goes wrong."

*R2-D2 beeps the opening notes of the Princess Leia theme.*

**🔗 Resources**

- **HC-SR04 with Arduino**: Search "HC-SR04 Arduino tutorial"
- **PIR HC-SR501**: Search "HC-SR501 Arduino interrupt"
- **Codey Online Vision**: [codey.online](http://codey.online) — Pro feature
- **Auto Error Fixing**: built into all Codey plans

*🤖 R2D2 Creation with Codey — building the galaxy's greatest droid, one episode at a time. May the Force — and the cloud compiler — be with you.*