---
title: "E.T.‘s Finger build by Fritzing and Aisler 🔴 Ep.1"
published: false
description: "Episode 1: A long time ago, a small alien pressed his glowing fingertip against a child’s forehead and left a warmth that never faded. We are going to build that finger — a wearable PCB that glows warm amber-red at a touch, breathes like a heartbeat, and fits on your fingertip. This is how we plan it, install Fritzing, and begin the journey from the movie screen to your breadboard."
tags: [fritzing, aisler, electronics, makers]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-finger-episode-01.png"
series: "E.T.’s Finger build by Fritzing and Aisler"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 1: E.T. Phone Home

-----

## “I’ll Be Right Here” ✨

It is 1982. A film ends. The audience sits in silence for a moment longer than they normally would. An alien with a wrinkled neck and enormous eyes has just pressed one luminous fingertip to a child’s forehead, and something warm and irreversible has happened.

That glowing fingertip. The warm amber-red. The pulse that makes it feel alive rather than simply illuminated. It is one of cinema’s most recognisable practical effects — and forty years later, it is something a maker with a soldering iron and a weekend can recreate.

This series documents exactly that: building a wearable fingertip device that glows at a touch, breathes like a heartbeat, and fits on your index finger. We will design the circuit in **Fritzing**, lay out a custom PCB shaped like a rounded fingertip, export the Gerbers, and have the board manufactured by **AISLER**. Then we assemble, solder, upload the firmware, and wear the magic.

Eight episodes. One glowing finger. Let us begin.

-----

## 🗂️ SIPOC — The Project at a Glance

|**Suppliers**              |**Inputs**                                               |**Process**                                                                  |**Outputs**                                                      |**Customers**                                          |
|---------------------------|---------------------------------------------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------|-------------------------------------------------------|
|Fritzing (design tool)     |Electronic components, schematic intent, PCB layout rules|Design the circuit in Breadboard + Schematic + PCB views; export Gerber files|A complete `.fzz` project file + Gerber ZIP ready for manufacture|AISLER — which manufactures the physical PCB           |
|AISLER (manufacturer)      |The `.fzz` file or Gerber ZIP                            |Automated file check → queue → manufacture → ship                            |A beautiful 2-layer PCB delivered to your door                   |The maker — who assembles and programs the final device|
|The maker (you)            |Components, soldering iron, Arduino IDE                  |Solder components onto the PCB; upload firmware via ISP programmer           |A working wearable glowing finger                                |E.T. fans everywhere — who deserve this toy            |
|Firmware (Arduino/ATtiny85)|Capacitive touch readings, PWM output                    |Sense touch → ramp LED brightness → breathe → fade                           |A living, responsive warm glow                                   |The wearer — whose heart light recognises another      |

-----

## The E.T. Finger Effect: What We Are Rebuilding 🎬

In the film, E.T.’s fingertip glows from within — warm, orange-red, pulsing gently. It activates on contact: E.T. reaches out and the finger brightens. It fades when the contact is gone. The effect has a biological quality to it: it breathes.

We are going to replicate this with real electronics:

|Movie effect            |Our hardware implementation                         |
|------------------------|----------------------------------------------------|
|Warm amber-red glow     |Amber LED (590 nm) — the warmest glow available     |
|Activates on touch      |Capacitive touch pad on the PCB pad area            |
|Breathes / pulses       |Sinusoidal PWM fade on the LED                      |
|Self-contained, no wires|CR2032 coin cell on-board, ATtiny85 MCU             |
|Fits on a finger        |Custom PCB shaped as a rounded rectangle, 22 × 18 mm|

The PCB will be small enough to sit on a fingertip and be held in place with a thin rubber ring or medical tape — invisible at arm’s length, magical up close.

-----

## The Complete Bill of Materials Preview 🧾

We will build and justify every one of these choices over the coming episodes. For now, a preview of what will live on this tiny board:

|Component               |Part number / value     |Quantity|Role                                      |
|------------------------|------------------------|--------|------------------------------------------|
|MCU                     |ATtiny85-20PU (DIP-8)   |1       |Brain — runs touch and LED logic          |
|LED                     |5 mm amber LED, 590 nm  |1       |E.T.’s warm fingertip glow                |
|Touch resistor (send)   |1 MΩ resistor           |1       |High-value resistor for capacitive sensing|
|Touch resistor (receive)|10 kΩ resistor          |1       |Pull-down for touch receive pin           |
|LED resistor            |47 Ω resistor           |1       |Current limiter for LED at ~3 V           |
|Bypass capacitor        |100 nF (0.1 µF) ceramic |1       |MCU power decoupling                      |
|Battery holder          |CR2032 SMD holder       |1       |3 V power supply                          |
|Programming header      |6-pin 2.54 mm ISP header|1       |Burn bootloader + upload code             |

Total component cost: approximately €3–5. PCB from AISLER: approximately €13 for 3 boards.

-----

## The Toolchain: Two Tools, One Project 🛠️

### Fritzing — The Design Studio

Fritzing is an open-source hardware initiative that makes electronics accessible as a creative material for anyone. It offers a software tool, a community website and services in the spirit of Processing and Arduino, fostering a creative ecosystem that allows users to document their prototypes, share them with others, teach electronics in a classroom, and layout and manufacture professional PCBs.

For our purposes, Fritzing gives us:

- A **Breadboard view** to prototype the circuit visually
- A **Schematic view** to document it properly
- A **PCB view** to design the physical board
- A **Code view** to write and upload firmware
- A **Fabricate button** to send directly to AISLER

### AISLER — The Manufacturer

AISLER manufactures your electronic project within two business days and ships it to you worldwide at affordable prices.

AISLER accepts Fritzing `.fzz` files directly — either through the Fabricate button inside Fritzing, or by manually uploading the file on their website. They handle the Gerber conversion, design rule checking, and production. Their Beautiful Boards start at €12.20 for 3 copies of a 2-layer PCB.

-----

## Installing Fritzing 📥

Fritzing 1.0.7 (the current version as of April 2026) is available for Windows, macOS, and Linux:

```
1. Visit: https://fritzing.org/download/
2. Choose your platform
3. Windows: run the .exe installer
   macOS:   drag Fritzing.app to Applications
   Linux:   extract the .tar.bz2, run ./Fritzing
```

**First launch checklist:**

```
✓ Fritzing opens and shows the welcome screen
✓ The Parts panel is visible on the right side
✓ Create a new project: File → New
✓ You see three tabs: Breadboard | Schematic | PCB
✓ Save it as: et-finger.fzz (File → Save)
```

The project file is a `.fzz` file — a ZIP archive containing your breadboard layout, schematic, PCB design, and parts list all in one portable file.

-----

## What Fritzing’s Views Do: A Quick Orientation 🖥️

```
┌────────────────────────────────────────────────────────────┐
│                    FRITZING VIEWS                          │
│                                                            │
│  Breadboard View                                           │
│  ──────────────────────────────────────────────────        │
│  • Looks like a physical breadboard                        │
│  • Place components, draw wires in 3D-ish style            │
│  • Great for prototyping and documentation                 │
│  • NOT used for PCB manufacturing                          │
│                                                            │
│  Schematic View                                            │
│  ──────────────────────────────────────────────────        │
│  • Standard IEEE/IEC schematic symbols                     │
│  • Electrical correctness — nets and connections           │
│  • Export as PDF for documentation                         │
│                                                            │
│  PCB View                                                  │
│  ──────────────────────────────────────────────────        │
│  • The layout that becomes the physical board              │
│  • Set board shape, trace width, copper pours              │
│  • Export Gerber RS-274X files                             │
│  • AISLER uses this view                                   │
│                                                            │
│  Code View                                                 │
│  ──────────────────────────────────────────────────        │
│  • Write Arduino sketches                                  │
│  • Upload via serial (when connected)                      │
│  • ATtiny85 code lives here                                │
└────────────────────────────────────────────────────────────┘
```

-----

## The Project Architecture 📐

Before we place a single component, let us understand how all the pieces fit together:

```
et-finger.fzz
│
├── Breadboard View
│   └── ATtiny85 + LED + resistors + battery on virtual breadboard
│
├── Schematic View
│   └── Clean schematic with net labels and power symbols
│
├── PCB View
│   └── Custom 22×18 mm rounded PCB, all components placed and routed
│
└── Code View
    └── Arduino sketch for ATtiny85:
        - capacitive touch detection
        - PWM LED breathing
        - touch-triggered brightness burst
```

-----

## Understanding ATtiny85: The Small Brain 🧠

The ATtiny85 is the ideal MCU for this project:

```
ATtiny85 DIP-8 Pinout:
                ┌────────┐
  (RESET) PB5 ──┤1      8├── VCC
  (ADC3)  PB3 ──┤2      7├── PB2 (SCK/INT0)
  (ADC2)  PB4 ──┤3      6├── PB1 (MISO/OC0B/OC1A) ← LED PWM here
          GND ──┤4      5├── PB0 (MOSI/OC0A)
                └────────┘

Why ATtiny85?
  ✓ 8KB flash, 512B RAM, 512B EEPROM — plenty for our sketch
  ✓ Runs at 3.3V from a CR2032 (3V) — no regulator needed
  ✓ Hardware PWM on PB1 — smooth LED fading
  ✓ DIP-8 package — solders easily even for beginners
  ✓ Arduino-compatible with ATTinyCore or ATtiny85 board package
  ✓ Tiny footprint on the PCB
  ✓ Deep sleep modes — extends battery life dramatically
```

-----

## The Series Roadmap 🗺️

|#|Episode                     |Title           |What We Do                                          |
|-|----------------------------|----------------|----------------------------------------------------|
|1|*This one* — E.T. Phone Home|Introduction    |Plan, install Fritzing, understand the project      |
|2|Ouch                        |Breadboard View |Place components, draw wires in Fritzing Breadboard |
|3|I’ll Be Right Here          |Schematic View  |Clean schematic, net labels, power symbols          |
|4|He’s Alive!                 |PCB Layout      |Place, route, board outline, DRC, copper fill       |
|5|E.T. Phone Home             |Firmware        |Capacitive touch + LED breathing in Arduino/ATtiny85|
|6|The Flowers Are Dying       |Export + AISLER |Gerber export, AISLER upload, order review          |
|7|We’re Home                  |Assembly        |Receive PCB, solder components, build the device    |
|8|I Love You                  |Testing + Beyond|Upload code, test, wear it, what comes next         |

In **Episode 2**, we open Fritzing’s Breadboard view and begin placing components — the ATtiny85, the LED, the resistors, and the battery holder. Wires will be drawn. The circuit will take shape.

*E.T., the extra-terrestrial, pointed his finger at the sky. We point ours at a soldering iron.*

-----

**🔗 Resources**

- **Fritzing download**: [fritzing.org/download](https://fritzing.org/download/)
- **AISLER**: [aisler.net](https://aisler.net)
- **ATtiny85 datasheet**: [ww1.microchip.com/downloads/en/DeviceDoc/Atmel-2586-AVR-8-bit-Microcontroller-ATtiny25-ATtiny45-ATtiny85_Datasheet.pdf](https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-2586-AVR-8-bit-Microcontroller-ATtiny25-ATtiny45-ATtiny85_Datasheet.pdf)
- **ATTinyCore Arduino package**: [github.com/SpenceKonde/ATTinyCore](https://github.com/SpenceKonde/ATTinyCore)

-----

*🔴 E.T.’s Finger build by Fritzing and Aisler — from breadboard to fingertip, one glowing episode at a time.*
