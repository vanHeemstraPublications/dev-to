---
title: "E.T.’s Finger build by Fritzing and Aisler 🔴 Ep.8"
published: false
description: "Episode 8: The finale. ‘I love you,’ says Elliott. E.T. glows warm, points his finger at the sky, and leaves. We upload the firmware, watch the LED breathe its first breath, press a finger to the touch pad and see the amber glow respond. Then we put it on a finger and point at the stars. This is the episode where everything we built comes alive. And then we talk about what comes next."
tags: [arduino, electronics, makers, wearable]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-finger-episode-08.png"
series: "E.T.’s Finger build by Fritzing and Aisler"
canonical_url: ""
organization: "the-software-s-journey"
part: 8
---

## Episode 8: I Love You — Testing and Beyond

-----

## “I Love You” ❤️

Elliott kneels on the hillside. E.T. lifts his glowing finger and presses it gently to Elliott’s forehead. *“I’ll be right here.”*

Elliott says: *“I love you.”*

The ship rises. The trail of light follows it into the sky, leaving a rainbow behind over the trees.

Eight episodes. A design, a schematic, a layout, a firmware, an order, a soldering session. And now — the moment. The firmware uploads. The LED breathes. The amber glow responds to your touch with the warmth of something remembered.

Let us do it.

-----

## 🗂️ SIPOC — The Final System

|**Suppliers**            |**Inputs**                                    |**Process**                                                   |**Outputs**                                                   |**Customers**                                          |
|-------------------------|----------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------|-------------------------------------------------------|
|Assembled PCB (Episode 7)|Soldered board, CR2032 battery, ISP programmer|Upload firmware → test touch sensing → tune threshold → wear  |A working wearable device                                     |You — wearing a piece of movie magic on your fingertip |
|Firmware (Episode 5)     |Completed `.ino` sketch                       |Arduino IDE → Upload Using Programmer → ATtiny85 flash written|ATtiny85 with breathing LED firmware                          |The assembled hardware — which now has a soul          |
|Your finger              |The capacitive touch pad on the PCB           |Touch pad detects the added capacitance of a human finger     |A triggered brightness burst → LED blazes → fades to breathing|The person wearing it — who experiences the E.T. effect|

-----

## Part 1: Uploading the Firmware 📤

### Connect the ISP Programmer

```
ISP Header on PCB (6-pin):
  Connect to: USBtinyISP, Arduino-as-ISP, USBASP, or any AVR ISP programmer
  
  Do NOT insert the CR2032 battery while programmer is connected!
  The programmer provides its own VCC.
  
Programmer → PCB:
  MISO  → ISP Pin 1
  VCC   → ISP Pin 2  (programmer provides 5V or 3.3V)
  SCK   → ISP Pin 3
  MOSI  → ISP Pin 4
  RESET → ISP Pin 5
  GND   → ISP Pin 6
  
For USBtinyISP: connect the 10-pin IDC cable with the adapter board
For Arduino-as-ISP: use the standard ArduinoISP wiring
```

### Upload Sequence

```
Step 1: Verify board settings in Arduino IDE
  Tools → Board: ATtiny85 (ATTinyCore)
  Tools → Clock: 8 MHz (internal)
  Tools → B.O.D.: 2.7V
  Tools → Programmer: USBtinyISP (or your programmer)

Step 2: Burn bootloader FIRST (sets ATtiny85 fuses for 8 MHz)
  Tools → Burn Bootloader
  Expected output: "Burning bootloader... Done."
  This must succeed before any sketch upload will work.

Step 3: Upload the sketch
  Open the et-finger.ino sketch from Episode 5
  Click: Sketch → Upload Using Programmer (NOT regular Upload!)
  Or: Ctrl+Shift+U

Expected serial output during upload:
  avrdude: Device signature = 0x1e930b (ATtiny85)
  avrdude: reading input file "et-finger.ino.hex"
  avrdude: writing flash (4,xxx bytes)
  avrdude: verifying flash
  avrdude: 4,xxx bytes of flash verified
  avrdude done. Thank you.
```

-----

## Part 2: First Power-On Test 🔴

After uploading firmware:

```
1. Disconnect the ISP programmer
2. Insert the CR2032 battery into the holder (+ side up, facing the back of PCB)
3. Observe the LED

Expected behaviour on first power-on:
  ✓ LED begins a slow sinusoidal breathing (2.5 second period)
  ✓ The amber glow fades in and out smoothly
  ✓ No flickering (indicates stable power supply and correct fuses)
  ✓ No constant-on behaviour (indicates firmware is running, not stuck)
```

**If the LED does NOT light up:**

```
Diagnosis 1: Dead battery
  Try a fresh CR2032. If the battery holder voltage is below 2V, try fresh.

Diagnosis 2: Fuses not set
  Retry "Burn Bootloader" step — the ATtiny85 may still be configured for 1 MHz
  (factory default) which makes the sketch timing wrong.

Diagnosis 3: Incorrect orientation
  Verify LED anode (+) is in the + hole, cathode in the − hole
  Verify ATtiny85 notch aligns with the silkscreen

Diagnosis 4: Cold solder joint on LED or U1
  Use multimeter continuity mode: test PB1 → R3 → LED anode
  If open circuit: resolder the suspect joint

Diagnosis 5: Sketch not uploaded correctly
  Verify: Tools → Board is ATtiny85 (not Arduino Uno!)
  Verify: Upload Using Programmer (not regular Upload)
  Verify: The programmer is recognised (device signature shown in output)
```

-----

## Part 3: Touch Testing 🖐️

After confirming the LED breathes:

```
Touch test procedure:
  1. Place PCB on a non-conductive surface (wooden table, foam, etc.)
  2. Slowly bring ONE FINGER toward the copper touch pad at the top
  3. Do not touch any other part of the board

Expected result:
  ✓ LED ramps up quickly to full brightness when finger is ~1–2 mm from pad
  ✓ LED holds at full brightness while finger touches the pad
  ✓ LED fades back to breathing when finger is removed
  ✓ The transition feels responsive, not sluggish
```

**If the LED triggers when nothing touches it (false triggering):**

```
Cause: Baseline capacitance too high, or threshold too low
Fix: Increase TOUCH_THRESHOLD in firmware

Current: const long TOUCH_THRESHOLD = 200;
Try:     const long TOUCH_THRESHOLD = 350;

Re-upload and test. Repeat in increments of 50 until false triggers stop.
```

**If the LED does NOT respond to touch:**

```
Cause: Threshold too high, or sensing not working
Diagnosis:
  1. Connect Serial (requires extra setup for ATtiny85 — use SoftwareSerial)
     OR: add Serial output in firmware to debug readings
  
  2. Simpler test: temporarily set threshold very low
     const long TOUCH_THRESHOLD = 50;
     If it now triggers, your baseline is above 50. Increase threshold.
  
  3. Check R1 (1 MΩ): continuity from PB0 to PB3 (should be 1 MΩ)
     If open: R1 not soldered or wrong value

  4. Check touch pad connection: continuity from touch pad copper to PB3 net
     If open: trace from touch pad to R1/R2 junction broken

  5. Try: touch the pad with multiple fingers for larger capacitance effect
```

-----

## Part 4: Calibrating the Touch Sensitivity 🎛️

Add a serial debug option to calibrate:

```cpp
// Temporary debug mode — add to setup() for calibration
// NOTE: ATtiny85 does not have hardware Serial
// Use ATtinyCore's Serial which routes to PB4 at 9600 baud
// Or connect an FTDI adapter and use SoftwareSerial

#include <SoftwareSerial.h>
SoftwareSerial debugSerial(4, 3);  // RX=PB4, TX=PB3 (temporary!)

void setup() {
  debugSerial.begin(9600);
  // ... rest of setup
}

void loop() {
  long reading = touchSensor.capacitiveSensor(30);
  debugSerial.print("Touch reading: ");
  debugSerial.println(reading);
  delay(100);
}
```

Run this, open the serial monitor, and observe readings:

- Without finger: your baseline (should be 20–100)
- With finger: your triggered reading (should be 300–2000)
- Set `TOUCH_THRESHOLD` to halfway between baseline and triggered

Remove the debug code before the final upload.

-----

## Part 5: Wearing It 🫵

The assembled PCB is ready to wear. Here are a few attachment methods:

### Method 1: Elastic Loop

```
Materials: 2 cm of thin elastic band (~8mm wide)
Method:
  1. Thread elastic through the ISP header pins from below
     (the header acts as a retention point)
  2. Form a loop sized to fit over your finger
  3. Secure with a small knot
  
Result: The PCB sits on the back of the middle phalanx of the index finger
        Touch pad faces upward, LED faces forward
```

### Method 2: Medical Tape

```
Materials: A 10cm strip of medical/micropore tape
Method:
  1. Lay the PCB on your fingertip (LED facing forward)
  2. Wrap tape once around the board and your finger
  3. Ensures the PCB doesn't rotate
  
Result: Solid hold, comfortable, easily removed
```

### Method 3: 3D-Printed Fingertip Shell

```
Design (optional, for advanced makers):
  A small shell that wraps around the fingertip and snaps shut
  The PCB slides into a slot in the shell
  A diffuser window at the front (frosted translucent filament)
  
  This is the movie-accurate approach: E.T.'s finger had a soft-looking
  rounded tip with warm light diffusing through the skin texture.
  
  For the DIY version: a cone of translucent hot-melt glue or
  white shrink tube over the LED acts as a diffuser and gives
  the glow a softer, more organic quality.
```

### The Amber Glow with a Diffuser

The most visually striking way to wear the E.T. Finger:

```
Simple diffuser:
  1. Cut a 15mm section of wide white heat-shrink tubing
  2. Slide it over the LED and shrink with hot air (or lighter at distance)
  3. The LED now glows through the diffuser — softer, more organic

Advanced diffuser:
  1. Mix a small amount of white silicone (RTV) 
  2. Apply as a dome over the LED
  3. Let cure for 12 hours
  4. The silicone dome diffuses beautifully and looks skin-like
  
Both options dramatically improve the visual quality of the glow.
```

-----

## Part 6: The Complete Series — What We Built Together 🗺️

|Episode|Title                  |What We Accomplished                                                    |
|-------|-----------------------|------------------------------------------------------------------------|
|1      |E.T. Phone Home        |Understood the project, installed Fritzing, met the ATtiny85            |
|2      |Ouch                   |Placed all components in Fritzing’s Breadboard view, wired the circuit  |
|3      |I’ll Be Right Here     |Created the clean schematic, set reference designators and values       |
|4      |He’s Alive!            |Designed the PCB layout: finger shape, component placement, routing, DRC|
|5      |E.T. Phone Home        |Wrote the complete ATtiny85 firmware: touch sensing + LED breathing     |
|6      |The Flowers Are Dying  |Exported Gerbers, uploaded to AISLER, placed the order                  |
|7      |We’re Home             |Received the PCBs, soldered every component                             |
|8      |*This one* — I Love You|Uploaded firmware, tested, calibrated, and wore it                      |

-----

## Part 7: What Comes Next — Extensions and Variations 🚀

The E.T. Finger is a complete project. But complete projects are also starting points.

### Variation 1: The Full E.T. Heart Light

```
The movie E.T. also had a glowing chest — the "heart light."
Extend the project:
  • Larger PCB: 40 × 30 mm, chest-shaped
  • Multiple WS2812B addressable LEDs (NeoPixels) for colour control
  • ATtiny85 drives the NeoPixels via a single GPIO
  • Heartbeat detection? Add MAX30102 sensor — glow pulses with real heartbeat
  • OR: simulate heartbeat with 60 BPM pulse modulation in firmware
```

### Variation 2: Two Fingers, One Magic

```
Build two E.T. Finger devices.
Add a second touch pad connected via a wire between the two boards.
When one board touches the other's pad → both LEDs brighten.
Like touching fingertips in the film.

This requires:
  • Two assembled E.T. Finger PCBs
  • A thin conductive thread or wire connecting the two touch pads
  • Modified firmware: second touch input triggers both LEDs simultaneously
```

### Variation 3: NFC-Triggered Glow

```
Advanced variant:
  • Replace ATtiny85 with ATtiny2313 or ATmega328P (more pins)
  • Add PN532 NFC reader module
  • Glow brightens when an NFC tag is detected (e.g., a card in someone's hand)
  • The finger glows when it "recognises" someone
  • Ultimate expression of E.T.'s ability to feel the identity of another
```

### Variation 4: A Better Firmware — Heartbeat-Accurate Breathing

```cpp
// Real heartbeat simulation: 72 BPM average
// Heartbeat is NOT a simple sine wave
// It has a sharp systolic peak then a slower diastolic curve

float heartbeatBrightness(unsigned long now) {
  // One beat period: 60000ms / 72 BPM = 833ms
  const float BEAT_PERIOD = 833.0f;
  float t = fmodf((float)now, BEAT_PERIOD) / BEAT_PERIOD;  // 0.0 to 1.0

  // Simulate the characteristic double-peak cardiac waveform:
  // First peak (systole) at t=0.1, second smaller peak (diastole) at t=0.25
  float peak1 = expf(-80.0f * powf(t - 0.10f, 2.0f)) * 1.0f;   // Systolic peak
  float peak2 = expf(-80.0f * powf(t - 0.25f, 2.0f)) * 0.5f;   // Diastolic peak
  float wave  = peak1 + peak2;

  // Map 0→1 to BREATHE_MIN→BREATHE_MAX
  return BREATHE_MIN + wave * (BREATHE_MAX - BREATHE_MIN);
}
```

This produces a biologically accurate heartbeat light pulse — more convincing than the simple sine wave, and even closer to the original E.T. effect.

-----

## The Final Moment: Point at the Sky 🌌

The PCB is on your fingertip. The CR2032 is in its holder. The amber LED breathes slowly — two and a half seconds per breath.

You touch the pad with your other hand.

The LED blazes warm.

Somewhere in the mid-eighties, a child in a darkened cinema looked up at a screen and saw something touch the sky.

You lift your finger.

*I’ll be right here.*

-----

**The Project Files**

All files for this series:

- `et-finger.fzz` — Complete Fritzing project (Breadboard + Schematic + PCB)
- `et-finger-gerbers.zip` — Gerber files ready for AISLER upload
- `et-finger-firmware.ino` — Complete ATtiny85 Arduino sketch
- `et-finger-bom.csv` — Bill of Materials

Share your build! Tag it `#ETfingerFritzing` — the maker community loves a well-lit fingertip.

-----

**🔗 Resources**

- **Fritzing**: [fritzing.org](https://fritzing.org)
- **AISLER**: [aisler.net](https://aisler.net)
- **ATTinyCore**: [github.com/SpenceKonde/ATTinyCore](https://github.com/SpenceKonde/ATTinyCore)
- **CapacitiveSensor library**: [github.com/PaulStoffregen/CapacitiveSensor](https://github.com/PaulStoffregen/CapacitiveSensor)
- **AISLER Fritzing guide**: [community.aisler.net/t/fritzing/89](https://community.aisler.net/t/fritzing/89)

-----

*🔴 E.T.’s Finger build by Fritzing and Aisler — from breadboard to fingertip. Thank you for building with us.*

*🌌 E.T. phone home.*
