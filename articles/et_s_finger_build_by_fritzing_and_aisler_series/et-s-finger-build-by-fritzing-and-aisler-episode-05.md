---
title: "E.T.’s Finger by Fritzing and Aisler 🔴 Ep.5"
published: false
description: "Episode 5: E.T. leans over the radio, soldered from spare parts, and speaks into it: ‘E.T. phone home.’ The radio works. The call gets through. Our firmware is that radio — the piece of code that makes the hardware speak, that transforms an amber LED from a static light into something alive, responsive, breathing. This episode writes the complete ATtiny85 sketch: capacitive touch, sinusoidal LED breathing, and the touch-triggered glow."
tags: [arduino, attiny85, firmware, electronics]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-finger-episode-05.png"
series: “E.T.’s Finger by Fritzing and Aisler”
canonical_url: ""
organization: "the-software-s-journey"
part: 5
---

## Episode 5: E.T. Phone Home — The Firmware

-----

## “E.T. Phone Home” 📡

E.T. builds a communicator from toy parts and a coffee can. He does not know the technical specifications of the components he salvages. He does not understand the physics of radio transmission. He simply knows what he needs — *to reach his people* — and he builds the thing that does it.

Our firmware is built with the same spirit. We need the amber LED to glow warm at a touch, to breathe like something alive, to say without words: *I am here.* The code is the communicator. The ATtiny85 is the coffee can.

This episode writes that code completely.

-----

## 🗂️ SIPOC — The Firmware

|**Suppliers**            |**Inputs**                                                    |**Process**                                                             |**Outputs**                                                           |**Customers**                                                             |
|-------------------------|--------------------------------------------------------------|------------------------------------------------------------------------|----------------------------------------------------------------------|--------------------------------------------------------------------------|
|ATtiny85 MCU             |GPIO pins PB0 (send), PB3 (receive), PB1 (LED); 3V from CR2032|Sketch: capacitive sensing → decide touch/no-touch → modulate PWM on PB1|PWM signal driving LED brightness — breathing at rest, bright at touch|The LED — which converts the PWM duty cycle into perceived light intensity|
|CapacitiveSensor library |Two GPIO pins (send/receive) and a resistor                   |Measures charge time as an indicator of nearby capacitance              |A reading (number) that goes up when a finger is near the pad         |The sketch logic — which compares to a threshold                          |
|Arduino PWM (analogWrite)|PB1 (Pin 6 on ATtiny85, OC0B PWM-capable)                     |analogWrite(0–255) controls LED duty cycle                              |LED brightness from fully off (0) to full brightness (255)            |The amber LED (through R3)                                                |

-----

## Setting Up the Arduino IDE for ATtiny85 🛠️

Before writing the code, configure Arduino IDE to compile for ATtiny85:

**Step 1: Install ATTinyCore board package**

1. Arduino IDE → File → Preferences
1. Additional Boards Manager URLs, add:
   
   ```
   http://drazzy.com/package_drazzy.com_index.json
   ```
1. Tools → Board → Boards Manager → search “ATTinyCore” → Install

**Step 2: Configure the board**

```
Tools → Board → ATTinyCore → ATtiny85 (Optiboot, No millis, No micros)

Settings:
  Chip:               ATtiny85
  Clock:              8 MHz (internal)
  B.O.D.:             2.7V (brownout detect at 2.7V for CR2032 safety)
  Timer 1 Clock:      CPU (64 MHz)
  LTO (1.6+ only):    Enabled
  millis()/micros():  Enabled (we need timing)
  Save EEPROM:        EEPROM retained
  Programmer:         USBtinyISP (or your programmer of choice)
```

**Step 3: Burn the bootloader (set fuses)**

Before uploading any code, you must set the ATtiny85 fuses to use the 8 MHz internal oscillator. Connect your ISP programmer and:

```
Tools → Burn Bootloader

This sets:
  LFUSE = 0xE2  (8 MHz internal clock)
  HFUSE = 0xDF  (SPIEN enabled, BOD 2.7V)
  EFUSE = 0xFF  (default)
```

-----

## The CapacitiveSensor Library 📚

The Arduino CapacitiveSensor library by Paul Stoffregen works by timing how long it takes to charge a receive pin through a large resistor. When a finger is near the touch pad, the added capacitance slows the charging time — and the library reports a higher value.

**Install the library:**

```
Arduino IDE → Tools → Manage Libraries
Search: "CapacitiveSensor"
Install: "CapacitiveSensor by Paul Stoffregen"
```

**How it works with our circuit:**

```
Without finger:
  PB0 (send, HIGH) → R1 (1MΩ) → PB3 (receive)
  Charge time: ~50 µs (fast — just PCB trace capacitance)
  Reading: ~50 (baseline)

With finger on touch pad:
  Finger adds ~20-100 pF of capacitance to the PB3 node
  Charge time: ~500 µs (much slower — more capacitance to charge)
  Reading: ~500–2000 (significantly above baseline)
  
Touch threshold: ~200 (safe margin above baseline of ~50)
```

-----

## The Complete ATtiny85 Firmware 💻

```cpp
// ============================================================
// E.T.'s Finger — ATtiny85 Firmware
// ============================================================
// Hardware:
//   ATtiny85 running at 8 MHz internal oscillator, 3V (CR2032)
//   PB0 (Pin 5): CapacitiveSensor SEND
//   PB3 (Pin 2): CapacitiveSensor RECEIVE + TOUCH_PAD node
//   PB1 (Pin 6): LED (PWM via analogWrite)
//   R1: 1 MΩ between PB0 and PB3
//   R2: 10 kΩ pull-down from PB3 to GND
//   R3: 47 Ω in series with LED from PB1
//
// Behaviour:
//   IDLE:    LED breathes slowly (sinusoidal 0→200→0 at 2.5 sec period)
//   TOUCHED: LED ramps quickly to 255, holds briefly, then resumes breathing
//   SLEEP:   After 30 seconds of no touch, ATtiny85 enters deep sleep
//             and wakes on any touch (pin-change interrupt)
// ============================================================

#include <CapacitiveSensor.h>
#include <avr/sleep.h>
#include <avr/interrupt.h>
#include <avr/power.h>
#include <math.h>

// ── Pin definitions ──────────────────────────────────────────
#define LED_PIN       1   // PB1 — PWM-capable (OC0B)
#define TOUCH_SEND    0   // PB0 — CapSense send
#define TOUCH_RECEIVE 3   // PB3 — CapSense receive

// ── Capacitive touch configuration ───────────────────────────
// CapacitiveSensor(sendPin, receivePin)
CapacitiveSensor touchSensor = CapacitiveSensor(TOUCH_SEND, TOUCH_RECEIVE);

const long TOUCH_THRESHOLD     = 200;   // Baseline ~50, finger ~500+
const int  TOUCH_SAMPLES        = 30;   // Readings averaged per check
const unsigned long SLEEP_AFTER = 30000; // Sleep after 30s of no touch

// ── Breathing effect parameters ──────────────────────────────
const uint8_t BREATHE_MIN       = 0;    // Minimum LED brightness (off)
const uint8_t BREATHE_MAX       = 200;  // Maximum brightness in idle
const uint8_t TOUCH_BRIGHTNESS  = 255;  // Full brightness on touch
const float   BREATHE_PERIOD_MS = 2500.0f; // One breath cycle: 2.5 seconds

// ── State machine ─────────────────────────────────────────────
enum State {
  STATE_BREATHING,    // Normal idle — gentle sinusoidal pulse
  STATE_TOUCHED,      // Touch detected — brightness burst
  STATE_FADING_OUT,   // Touch released — fading back to breathe
  STATE_SLEEPING      // Deep sleep mode
};

State currentState = STATE_BREATHING;

// ── Timing ───────────────────────────────────────────────────
unsigned long lastTouchTime     = 0;
unsigned long touchStartTime    = 0;
unsigned long stateEnteredAt    = 0;
const unsigned long TOUCH_HOLD  = 800;   // Hold full brightness for 800ms
const unsigned long FADE_TIME   = 1200;  // Fade from full to breathe in 1.2s

// ── Breathing position ────────────────────────────────────────
float breathePhase = 0.0f;

// ── Interrupt flag (wakes from sleep) ─────────────────────────
volatile bool wakeFlag = false;

// ── Pin-change interrupt for wake from sleep ──────────────────
// PB3 is PCINT3 — fires when the touch receive pin changes state
// (The CapacitiveSensor library will detect the actual touch after wake)
ISR(PCINT0_vect) {
  wakeFlag = true;
}

// ─────────────────────────────────────────────────────────────
void setup() {
  // Configure LED pin
  pinMode(LED_PIN, OUTPUT);
  analogWrite(LED_PIN, 0);   // Start with LED off

  // CapacitiveSensor: disable auto-calibrate for better consistency
  touchSensor.set_CS_AutocaL_Millis(0xFFFFFFFF);

  // Disable unused peripherals to save power
  power_usi_disable();       // USI not used
  power_adc_disable();       // ADC not used (we use digital CapSense)

  stateEnteredAt = millis();
}

// ─────────────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();

  // ── Capacitive touch reading ──────────────────────────────
  long touchReading = touchSensor.capacitiveSensor(TOUCH_SAMPLES);
  bool isTouched    = (touchReading > TOUCH_THRESHOLD);

  if (isTouched) {
    lastTouchTime = now;
  }

  // ── State transitions ─────────────────────────────────────
  switch (currentState) {

    case STATE_BREATHING:
      // Transition → TOUCHED when finger detected
      if (isTouched) {
        currentState   = STATE_TOUCHED;
        stateEnteredAt = now;
        touchStartTime = now;
      }
      // Transition → SLEEPING after 30 seconds of no touch
      else if (now - lastTouchTime > SLEEP_AFTER) {
        enterSleep();
        // Execution continues here after wake
        currentState   = STATE_BREATHING;
        stateEnteredAt = now;
        lastTouchTime  = now;
      }
      break;

    case STATE_TOUCHED:
      // Hold at maximum brightness for TOUCH_HOLD duration
      if (now - stateEnteredAt > TOUCH_HOLD && !isTouched) {
        currentState   = STATE_FADING_OUT;
        stateEnteredAt = now;
      }
      // If still touching, reset timer (keep at max brightness)
      else if (isTouched) {
        stateEnteredAt = now;
      }
      break;

    case STATE_FADING_OUT:
      // If touched again during fade, go back to TOUCHED
      if (isTouched) {
        currentState   = STATE_TOUCHED;
        stateEnteredAt = now;
      }
      // After fade complete, return to breathing
      else if (now - stateEnteredAt > FADE_TIME) {
        currentState   = STATE_BREATHING;
        stateEnteredAt = now;
      }
      break;

    case STATE_SLEEPING:
      // Should not reach here — handled by enterSleep()
      currentState = STATE_BREATHING;
      break;
  }

  // ── LED output ────────────────────────────────────────────
  uint8_t ledValue = computeLedBrightness(now);
  analogWrite(LED_PIN, ledValue);

  // Small delay to reduce power consumption and cap sense noise
  delay(20);  // 50 Hz update rate
}

// ─────────────────────────────────────────────────────────────
// computeLedBrightness: returns 0–255 based on current state
// ─────────────────────────────────────────────────────────────
uint8_t computeLedBrightness(unsigned long now) {
  switch (currentState) {

    case STATE_BREATHING: {
      // Sinusoidal breathing: smooth, organic, alive
      // Phase advances at rate: 2*PI / period (in ms)
      float t     = (float)now;
      float phase = (2.0f * M_PI * t) / BREATHE_PERIOD_MS;
      // sin(phase) goes −1 to +1; map to 0→1
      float sinVal = (sinf(phase) + 1.0f) / 2.0f;
      // Gamma-correct: sinVal^2 feels more natural to the eye
      float gammaVal = sinVal * sinVal;
      return (uint8_t)(BREATHE_MIN + gammaVal * (BREATHE_MAX - BREATHE_MIN));
    }

    case STATE_TOUCHED:
      // Quick ramp to full brightness
      {
        unsigned long elapsed = now - stateEnteredAt;
        if (elapsed < 150) {
          // Ramp up in first 150 ms
          return (uint8_t)((float)elapsed / 150.0f * TOUCH_BRIGHTNESS);
        }
        return TOUCH_BRIGHTNESS;
      }

    case STATE_FADING_OUT: {
      // Fade from TOUCH_BRIGHTNESS to current breathe value
      unsigned long elapsed = now - stateEnteredAt;
      float progress = (float)elapsed / (float)FADE_TIME;
      progress = constrain(progress, 0.0f, 1.0f);

      // Current breathe target
      float phase    = (2.0f * M_PI * (float)now) / BREATHE_PERIOD_MS;
      float sinVal   = (sinf(phase) + 1.0f) / 2.0f;
      float gammaVal = sinVal * sinVal;
      uint8_t breatheTarget = (uint8_t)(BREATHE_MIN + gammaVal * (BREATHE_MAX - BREATHE_MIN));

      // Linear interpolate from TOUCH_BRIGHTNESS to breatheTarget
      uint8_t result = (uint8_t)(TOUCH_BRIGHTNESS * (1.0f - progress) +
                                  breatheTarget * progress);
      return result;
    }

    default:
      return 0;
  }
}

// ─────────────────────────────────────────────────────────────
// enterSleep: put ATtiny85 into deep sleep mode
//             wakes on pin-change interrupt from TOUCH_RECEIVE
// ─────────────────────────────────────────────────────────────
void enterSleep() {
  // Fade LED down gracefully before sleeping
  for (int b = analogRead(LED_PIN); b >= 0; b -= 4) {
    analogWrite(LED_PIN, max(b, 0));
    delay(10);
  }
  analogWrite(LED_PIN, 0);
  delay(50);

  // Enable pin-change interrupt on PB3 (PCINT3)
  GIMSK |= (1 << PCIE);     // Enable pin-change interrupt group
  PCMSK |= (1 << PCINT3);   // Enable interrupt on PB3 specifically
  sei();                      // Global interrupt enable

  wakeFlag = false;

  // Set sleep mode to POWER_DOWN — the deepest sleep
  // Current consumption: ~0.1 µA (CR2032 can last years in sleep!)
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  sleep_enable();
  sleep_cpu();  // ←── MCU sleeps here until pin-change interrupt fires

  // ── Execution resumes here after wake ──────────────────────
  sleep_disable();
  PCMSK &= ~(1 << PCINT3);  // Disable pin-change interrupt
  GIMSK &= ~(1 << PCIE);

  // Allow CapSense to re-stabilise after wake
  delay(200);
}
```

-----

## Understanding the Breathing Algorithm 🌊

The breathing effect is the heart of the firmware — the thing that makes the LED feel alive rather than just “on” or “off.” It uses a sinusoidal wave:

```cpp
float phase  = (2.0f * M_PI * t) / BREATHE_PERIOD_MS;
float sinVal = (sinf(phase) + 1.0f) / 2.0f;   // Range: 0.0 to 1.0
float gammaVal = sinVal * sinVal;               // Gamma correction

// Gamma correction: why square it?
// Human eye perceives LED brightness logarithmically.
// Without correction, the LED appears to snap between on/off.
// Squaring the sine value creates more time near the extremes
// and less time in the middle — exactly what our eyes expect
// from something breathing.
```

The period is 2500 ms — one full breath cycle in 2.5 seconds. This matches the slow, restful breathing of a living creature at rest.

-----

## Power Consumption Analysis 🔋

With a CR2032 (typical capacity: 225 mAh):

```
State           Current draw      Battery life
──────────────  ───────────────  ──────────────────────
Active (LED on) ~22 mA            ~10 hours
LED breathing   ~5 mA average     ~45 hours
Deep sleep      ~0.1 µA           ~25,000 hours (>2 years)

Real-world scenario: touch for 30 seconds, sleep for hours
  → Effective average current: ~0.5 mA
  → Battery life: ~450 hours (~19 days of occasional use)
```

The sleep mode is critical for a coin-cell powered device.

-----

## Uploading via ISP 📤

Connect your USBtinyISP (or Arduino-as-ISP) to the 6-pin ISP header on the PCB:

```
ISP Header Pinout (standard AVR ISP):
  ┌───────────────────┐
  │ 1 (MISO) │ 2 (VCC)│
  │ 3 (SCK)  │ 4 (MOSI)│
  │ 5 (RESET)│ 6 (GND)│
  └───────────────────┘

USBtinyISP → PCB header:
  MISO  → Pin 1
  VCC   → Pin 2
  SCK   → Pin 3
  MOSI  → Pin 4
  RESET → Pin 5
  GND   → Pin 6
```

**Do not connect the CR2032 battery while the ISP programmer is connected.** The programmer provides 5V power; the CR2032 provides 3V. Mixing the two power sources will damage the MCU.

```
Arduino IDE → Tools → Board → ATtiny85
              Tools → Programmer → USBtinyISP
              Sketch → Upload Using Programmer (Ctrl+Shift+U)
```

-----

## Testing on a Breadboard First 🧪

Before soldering everything to the finished PCB, test the circuit on a physical breadboard:

```
Minimum test circuit:
  ATtiny85 DIP-8 in a breadboard
  VCC pin (8) → 3V from 2x AA batteries in series (or bench supply set to 3V)
  GND pin (4) → GND
  PB0 (5) → 1MΩ → PB3 (2)
  PB3 (2) → 10kΩ → GND
  PB1 (6) → 47Ω → amber LED anode → LED cathode → GND

  "Touch pad" for testing: a 15 cm wire connected to PB3/R1 junction
  Touching the wire end with your finger should trigger the LED
```

If the LED breathes smoothly without a finger near the wire, touch detection is working at the firmware level. Adjust `TOUCH_THRESHOLD` in the code if the LED triggers from circuit noise:

```cpp
// If false triggers: raise threshold
const long TOUCH_THRESHOLD = 400;

// If no trigger when touched: lower threshold
const long TOUCH_THRESHOLD = 100;
```

-----

## What’s Next: Exporting for AISLER 📦

*The firmware is written. The circuit is tested on a breadboard. The PCB is designed.*

In **Episode 6**, we bring together the PCB design from Fritzing and send it to AISLER. We will export the Gerber files, review them in AISLER’s online preview, fill in the order form, and watch the manufacturing queue spin up. The flowers are dying — but the board is being born.

-----

**🔗 Resources**

- **CapacitiveSensor library**: [github.com/PaulStoffregen/CapacitiveSensor](https://github.com/PaulStoffregen/CapacitiveSensor)
- **ATTinyCore**: [github.com/SpenceKonde/ATTinyCore](https://github.com/SpenceKonde/ATTinyCore)
- **ATtiny85 sleep modes**: [ww1.microchip.com/downloads/en/DeviceDoc/Atmel-2586-AVR-8-bit-Microcontroller-ATtiny25-ATtiny45-ATtiny85_Datasheet.pdf](https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-2586-AVR-8-bit-Microcontroller-ATtiny25-ATtiny45-ATtiny85_Datasheet.pdf)

-----

*🔴 E.T.’s Finger build by Fritzing and Aisler — from breadboard to fingertip, one glowing episode at a time.*
