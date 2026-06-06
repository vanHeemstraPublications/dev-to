---
title: "R2D2 Creation with Codey 🤖 Ep.1"
published: false
description: "Episode 1: A long time ago in a browser tab far, far away — a builder decided to make the galaxy’s most beloved droid with Codey Online. Meet the tools: AI vibe coding, wiring diagrams, cloud compiler, and Web Serial upload. The R2-D2 build plan is laid out. The first LED blinks. The Force awakens."
tags: [arduino, esp32, ai, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/r2-d2_creation_with_codey_series/r2d2-creation-with-codey-episode-01.png"
series: "R2D2 Creation with Codey"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 1: The Rebellion Begins

*A long time ago in a browser tab far, far away…*

-----

## “Help Me, Codey Online — You’re My Only Hope” 📡

*The hologram flickers. Obi-Wan Kenobi steps forward, robes sweeping the workshop floor.*

**OBI-WAN:** “For a thousand generations, makers have built remarkable things with their hands. But now there is a new path — one where you describe what you wish to create, and an intelligence writes the code, draws the wires, and compiles the future for you. That path is called Codey Online. And the project before us… is the most beloved droid in the galaxy.”

*R2-D2 lets out a long, excited series of beeps and whistles from somewhere across the workshop.*

**OBI-WAN:** “Yes, Artoo. We are going to build you.”

*More frantic beeping.*

**OBI-WAN:** “From scratch. Yes, all of it. In a browser tab. Come — the Force will guide our USB cable.”

-----

## 🗂️ SIPOC — The Mission Briefing

|**Suppliers**           |**Inputs**                           |**Process**                                                           |**Outputs**                                                 |**Customers**                                                 |
|------------------------|-------------------------------------|----------------------------------------------------------------------|------------------------------------------------------------|--------------------------------------------------------------|
|You (the maker)         |A description of what R2-D2 should do|Codey writes the code, draws the wiring diagram, compiles in the cloud|Compiled firmware uploaded directly to your Arduino or ESP32|The completed R2-D2 droid — dome lights blazing, beeps echoing|
|Codey AI                |Natural language instructions        |AI generates complete Arduino sketches, libraries, and helper files   |Working `.ino` code with correct `#include` statements      |Your microcontroller — which finally knows what to do         |
|The Cloud Compiler      |Your `.ino` source files             |Compiles without any local IDE, toolchain, or SDK                     |A compiled `.hex` or `.bin` firmware file                   |Web Serial uploader — which flashes it to your board          |
|Wiring Diagram Generator|Your component list                  |Draws color-coded diagrams with connection table                      |PDF-exportable wiring guide                                 |You — so you know which jumper wire goes where                |

-----

## What Is Codey Online? The Holonet Briefing 🌐

*C-3PO rushes in, datapad clutched to his golden chest.*

**C-3PO:** “Oh my! Allow me to translate the technical specifications, as I am fluent in over six million forms of programming environments. Codey Online, built by OTRONIC of the Netherlands, is what the organic beings call a ‘browser-based vibe coding IDE’ for Arduino and ESP32 microcontrollers. It requires no installation, no driver configuration, no local toolchain whatsoever. I calculate the probability of a beginner successfully installing the traditional Arduino IDE without frustration is approximately three thousand, seven hundred and twenty-to-one!”

*R2-D2 beeps dismissively.*

**C-3PO:** “Yes, yes, Artoo — with Codey the odds are considerably better. The complete feature set, as I have catalogued it, is as follows:”

|Feature                       |What it does                                                  |
|------------------------------|--------------------------------------------------------------|
|🤖 **AI Vibe Coding**          |Describe your idea — Codey writes the complete sketch         |
|🧭 **Wiring Diagram Generator**|Color-coded diagrams, pin labels, connection table, PDF export|
|☁️ **Cloud Compiler**          |No local IDE needed — compilation runs on Codey’s servers     |
|🔌 **Direct USB Upload**       |Flash via Web Serial in Chrome or Edge — no drivers           |
|📟 **Live Serial Monitor**     |Debug in real time without leaving the browser                |
|🛠️ **Auto Error Fixing**       |Codey reads errors and fixes them automatically               |
|📚 **Smart Library Picker**    |Correct library chosen automatically for each sensor          |
|📁 **Multi-file Projects**     |`.ino`, `.h`, `.cpp` files in a tabbed editor                 |
|🚩 **Milestones & Rollback**   |Save snapshots, restore code AND chat history                 |
|⚡ **Voltage Safety Checks**   |Warns when 3.3V boards meet 5V sensors                        |
|🧠 **Agent / Plan / Ask Modes**|Three reasoning modes for different needs                     |
|👁️ **Vision: Upload Images**   |Photo of your breadboard — Codey reads it                     |

**C-3PO:** “And the supported boards include Arduino UNO R3, Arduino Nano V3, Arduino Mega 2560, ESP32 DevKit V1, ESP32-S3, and ESP32-C3. Most satisfactory.”

-----

## The R2-D2 Build Plan: A Galaxy of Systems 🤖

*Luke Skywalker spreads a holographic blueprint across the table.*

**LUKE:** “I had no idea how many systems R2 actually has. Every time he does something amazing, I just thought— well, it was just R2 being R2. But look at this.”

The complete R2-D2 we are going to build across this series:

|Episode|R2-D2 System          |Components             |Codey Feature Spotlight                          |
|-------|----------------------|-----------------------|-------------------------------------------------|
|1      |First Power — Dome LED|Arduino UNO + LED      |Account setup, first sketch, first wiring diagram|
|2      |Voice and Beeps       |Piezo buzzer           |Smart Library Picker, tone() code                |
|3      |Dome Light Array      |NeoPixel ring          |FastLED/NeoPixel, voltage safety check           |
|4      |Sensor Eye            |HC-SR04 + PIR          |Auto Error Fixing, Vision photo upload           |
|5      |Holographic Projector |SSD1306 OLED           |Milestones & Rollback, I2C wiring                |
|6      |Motion Systems        |Servo + DC motors      |Multi-file projects, complex wiring diagrams     |
|7      |Audio Voice System    |DFPlayer Mini + speaker|Library Picker, Live Serial Monitor              |
|8      |The Complete Droid    |All systems together   |ESP32 integration, Deep Think mode, final PDF    |

-----

## Step 1: Creating Your Codey Account 🎟️

*Han Solo leans against the Millennium Falcon’s landing strut.*

**HAN:** “Look, kid, I’ve made a lot of accounts in my day. Mos Eisley cantina membership, Outer Rim trader registry, questionable Imperial databases… This one’s the easiest. Just go to codey.online, hit Sign Up, and you’re in. Free account gets you five AI messages a day to start. That’s enough to get Artoo blinking.”

Go to **[codey.online](https://codey.online)** and create your free account. The Starter plan includes:

- 5 AI messages per day
- Cloud compilation
- Direct USB uploading
- Wiring diagram generator
- Live serial monitor

*R2-D2 beeps urgently.*

**HAN:** “Yeah yeah, the Pro plan is nine ninety-nine a month and gives you unlimited messages, Deep Think mode, photo uploads, and priority compilation. But start free — we’re still on Tatooine here.”

-----

## Step 2: Your First Project — The Dome Light Test 💡

*Obi-Wan gestures toward the workbench.*

**OBI-WAN:** “Every journey begins with a single step. For R2-D2, that step is a single blinking LED — a proof that power flows through the circuit, that the code runs, that the connection between maker and machine is alive. In the Jedi tradition, we call this ‘Hello World.’ R2 calls it something rather more enthusiastic.”

*R2-D2 beeps with what can only be described as pride.*

### Opening Codey and Creating a Project

1. Log in at **codey.online**
1. Click **New Project**
1. Choose your board: **Arduino UNO R3** (perfect for our first test)
1. In the AI chat panel, type exactly this:

```
Build me an R2-D2 dome LED test.
Connect a blue LED to pin 13 with a 220 ohm resistor.
Make the LED blink in an R2-D2 style pattern:
two quick blinks, a pause, then three slower blinks.
Repeat forever.
```

*Within seconds, Codey responds:*

### The Code Codey Writes

```cpp
// R2-D2 Dome LED Test
// Generated by Codey Online
// Board: Arduino UNO R3

const int LED_PIN = 13;

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  // R2-D2 style: two quick blinks
  quickBlink();
  quickBlink();

  delay(600); // pause between groups

  // Three slower blinks
  slowBlink();
  slowBlink();
  slowBlink();

  delay(1500); // pause before repeating
}

void quickBlink() {
  digitalWrite(LED_PIN, HIGH);
  delay(80);
  digitalWrite(LED_PIN, LOW);
  delay(120);
}

void slowBlink() {
  digitalWrite(LED_PIN, HIGH);
  delay(350);
  digitalWrite(LED_PIN, LOW);
  delay(250);
}
```

*R2-D2 beeps approvingly.*

**OBI-WAN:** “You see? Codey understood the intent — not just ‘blink an LED,’ but blink it *as R2-D2 would.* This is the difference between code and character.”

-----

## Step 3: The First Wiring Diagram 🧭

*C-3PO peers at the screen with great concern.*

**C-3PO:** “Oh, I do hope we connect this correctly. I once computed the odds of a short circuit at—”

**HAN:** “Threepio. The diagram. Look at the diagram.”

After Codey generates the code, click the **Wiring Diagram** tab. Codey instantly draws:

```
Arduino UNO R3 Wiring Diagram
══════════════════════════════

[Arduino UNO R3]
  Pin 13 ──────── (220Ω Resistor) ──── [LED Anode (+)]
  GND    ──────────────────────────── [LED Cathode (−)]

Color code:
  RED   = 5V / VCC
  BLACK = GND
  BLUE  = Signal (Pin 13)
  GREY  = Through resistor

Connection Table:
┌─────────────────┬──────────────────────────┐
│ From            │ To                       │
├─────────────────┼──────────────────────────┤
│ Arduino Pin 13  │ Resistor leg 1 (220Ω)    │
│ Resistor leg 2  │ LED Anode (+, long leg)   │
│ LED Cathode (−) │ Arduino GND              │
└─────────────────┴──────────────────────────┘
```

**C-3PO:** “Color-coded wires! Red for power, black for ground, distinct colors for each signal. I must say, this is considerably more reassuring than the hand-drawn schematics Master Luke produces.”

Click **Download PDF** to save the wiring diagram. Print it and pin it above your workbench — R2-D2’s blueprints have begun.

-----

## Step 4: Compile and Upload 🚀

*Luke bounces on his heels with excitement.*

**LUKE:** “This is the part where— wait, it actually compiled? Already? Without me installing anything?”

### Cloud Compile

Click the **Compile** button. Codey’s cloud servers compile your code. No toolchain. No library downloads. No error-prone local setup. You see:

```
✓ Compilation successful
  Board:  Arduino UNO R3
  Sketch: r2d2-dome-led-test.ino
  Size:   1,024 bytes (3% of flash)
```

### Web Serial Upload

1. Plug your Arduino UNO into your computer via USB
1. Click **Upload**
1. Chrome asks permission to access the serial port — click Allow
1. Codey auto-detects the board, resets it, and flashes the firmware

```
✓ Upload complete
  Port:   COM3 (or /dev/ttyACM0 on Linux)
  Board:  Arduino UNO R3
  Speed:  115200 baud
```

*R2-D2’s LED equivalent blinks: two quick, pause, three slow. Again. Again.*

**LUKE:** “He’s… he’s alive. I mean — the LED is— this is amazing.”

*R2-D2 beeps smugly, as if to say “I told you it would work.”*

-----

## The Three AI Modes: Choose Your Approach 🧠

*Yoda settles into his hover-chair, ears raised.*

**YODA:** “Three paths in Codey there are. Which to walk, choose wisely you must.”

|Mode     |What it does                                       |When to use it                                 |
|---------|---------------------------------------------------|-----------------------------------------------|
|**Agent**|Writes and edits your code files directly          |Most building tasks — “add a new sensor”       |
|**Plan** |Drafts a step-by-step plan before touching any code|Complex integrations — review before committing|
|**Ask**  |Answers questions without touching files at all    |Learning — “how does tone() work?”             |

**YODA:** “For today, Agent mode sufficient it is. When complex R2’s circuits become, Plan mode you shall choose. Ask mode — when to Yoda you speak, that is.”

-----

## What’s Next: The Sound of the Force 🔊

*R2-D2 lets out a cascade of excited beeps — something between a fanfare and an impatient demand.*

**OBI-WAN:** “Artoo is right, of course. A droid that only blinks is not yet truly R2-D2. In Episode 2, we give him his voice — those remarkable whistles and beeps that have carried messages across the galaxy. We will connect a piezo buzzer, explore Codey’s Smart Library Picker, and hear R2 speak for the first time.”

*The LED blinks: two quick, three slow.*

*Somewhere in the Force, a rebellion stirs.*

-----

**🔗 Resources**

- **Codey Online**: [codey.online](https://codey.online)
- **Create free account**: [codey.online/register](https://codey.online/register)
- **OTRONIC**: [otronic.nl](https://www.otronic.nl)

-----

*🤖 R2D2 Creation with Codey — building the galaxy’s greatest droid, one episode at a time. May the Force — and the cloud compiler — be with you.*
