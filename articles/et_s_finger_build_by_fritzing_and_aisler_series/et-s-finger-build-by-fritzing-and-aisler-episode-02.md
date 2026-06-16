---
title: "E.T.’s Finger build by Fritzing and Aisler 🔴 Ep.2"
published: false
description: "Episode 2: ‘Ouch,’ says E.T., pointing to his heart. That single word carries more meaning than most speeches — it is the acknowledgement of connection, of feeling, of something shared. In our Fritzing breadboard, we now place the components that will create that feeling: the ATtiny85, the amber LED, the resistors, the coin cell battery. We wire them together and watch the circuit take its first visible shape."
tags: [fritzing, breadboard, electronics, circuit]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-finger-episode-02.png"
series: "E.T.’s Finger build by Fritzing and Aisler"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

## Episode 2: Ouch — The Breadboard View

-----

## “Ouch” 💛

E.T. points to his chest, to his heart light, and says: *“Ouch.”*

Not because it hurts. Because connection does something irreversible to you. He is about to leave, and his chest hurts — not from injury but from the weight of feeling that binds him to Elliott.

In our project, the breadboard view is the moment of first contact. Components placed on a virtual mat. Wires drawn between them. The circuit takes shape not as an abstract schematic but as a physical, tangible thing you can see and understand. This is why Fritzing’s breadboard view exists — to make electronics accessible as a creative material, not as a discipline reserved for the formally trained.

Let us make it ouch.

-----

## 🗂️ SIPOC — The Breadboard View

|**Suppliers**         |**Inputs**                                                                               |**Process**                                                                |**Outputs**                                                |**Customers**                                                                   |
|----------------------|-----------------------------------------------------------------------------------------|---------------------------------------------------------------------------|-----------------------------------------------------------|--------------------------------------------------------------------------------|
|Fritzing parts library|Component footprints + symbols for ATtiny85, LED, resistors, CR2032 holder               |Drag, drop, wire components in the Breadboard view                         |A visual breadboard layout documenting the physical circuit|The maker — who can prototype on a real breadboard exactly following this layout|
|The circuit design    |Bill of materials: ATtiny85, amber LED, three resistors, one capacitor, one CR2032 holder|Map each component to a Fritzing part; connect with coloured wires         |A complete, wired breadboard diagram                       |The Schematic view — which extracts electrical connections from this layout     |
|ATtiny85 DIP-8        |The microcontroller physically placed on the breadboard                                  |Pin assignments: PB0 (touch send), PB3 (touch receive), PB1 (LED), VCC, GND|Wired connections to LED and touch pad                     |The Schematic view and PCB view — which inherit all connections                 |

-----

## Opening the Breadboard View 🖥️

1. Open Fritzing
1. Open your `et-finger.fzz` project (or create a new one: File → New)
1. The active tab should show **Breadboard** (the first tab)
1. You will see a virtual breadboard in the centre

The breadboard view represents the real, physical prototype. Every component placed here corresponds to something you could put on an actual solderless breadboard — useful for testing before committing to a PCB.

-----

## Finding Components in the Parts Panel 🔍

The Parts panel on the right side of Fritzing contains thousands of components. Search for each of ours:

```
Parts Panel → Search:

1. "ATtiny85"
   → Find: IC — ATtiny85 (DIP-8)
   → If not found: use "ATtiny85-20PU" or search "ATtiny" and pick DIP-8

2. "LED"
   → Find: LED (standard 5mm) — amber or yellow colour preferred

3. "resistor"
   → Find: Resistor (generic)
   → We need three — drag three instances out

4. "capacitor ceramic"
   → Find: Ceramic Capacitor (disc type)

5. "coin cell"
   → Find: CR2032 Battery Holder (3V)
   → Alternatively: "coin cell battery holder"
```

**Tip:** If you cannot find the exact ATtiny85 in the standard library, the Generic IC (DIP-8) can be used in breadboard view with manual pin labelling. The correct footprint matters most in PCB view.

-----

## Placing the ATtiny85 🧠

In Fritzing’s breadboard view:

1. Drag the ATtiny85 (DIP-8) from the Parts panel onto the breadboard
1. Position it straddling the central gap of the breadboard (pins facing down)
1. The chip should sit with pins 1–4 on the left row and pins 5–8 on the right row

```
ATtiny85 breadboard placement:
                    Central gap
                         │
Row ←  ●  ●  ●  ●  ●  ●│●  ●  ●  ●  ●  ●  → Row
                    [ATtiny85]
         Pin 1 (PB5/Reset)│  │Pin 8 (VCC)
         Pin 2 (PB3/ADC3) │  │Pin 7 (PB2/SCK)
         Pin 3 (PB4/ADC2) │  │Pin 6 (PB1/OC0B) ← LED PWM
         Pin 4 (GND)      │  │Pin 5 (PB0/MOSI) ← Touch
```

-----

## Placing the Remaining Components 📦

**The amber LED:**

1. Drag a standard LED to the breadboard
1. Place it 3–4 rows to the right of the ATtiny85
1. The LED has two legs: Anode (+, longer leg) and Cathode (−, shorter leg)
1. In Fritzing, the anode is marked with a small triangle on the symbol

**Change the LED colour to amber:**

1. With the LED selected, look at the Properties panel (bottom right)
1. Change Color to “orange” or “amber” if available
1. This does not affect the circuit — it is purely visual — but it makes the drawing meaningful

**The three resistors:**

1. Place **R1** (1 MΩ) — this is the capacitive touch send resistor
1. Place **R2** (10 kΩ) — this is the capacitive touch receive pull-down
1. Place **R3** (47 Ω) — this is the LED current-limiting resistor

**Setting resistor values in Properties:**

1. Select R1 → Properties panel → Resistance → type “1MΩ” or “1000000”
1. Select R2 → Properties → Resistance → “10kΩ” or “10000”
1. Select R3 → Properties → Resistance → “47Ω” or “47”

**The bypass capacitor:**

1. Drag a ceramic capacitor to the breadboard near the ATtiny85’s VCC pin
1. Properties → Capacitance → “100nF” or “0.1µF”

**The CR2032 battery holder:**

1. Drag the coin cell holder to the breadboard
1. The + terminal connects to VCC. The − terminal connects to GND

-----

## Wiring the Circuit 🔌

In Fritzing, you draw wires by hovering over a component pin until a green dot appears, then clicking and dragging to the target pin.

### The Touch Sensing Circuit

We use the classic Arduino CapacitiveSensor library technique: two resistor-connected pins, one sending a charge, one receiving it. The large resistor (1 MΩ) connects Send to Receive.

```
Wire 1: ATtiny85 Pin 5 (PB0) → R1 leg 1 (1 MΩ)
Wire 2: R1 leg 2 → ATtiny85 Pin 2 (PB3)
Wire 3: ATtiny85 Pin 2 (PB3) → R2 leg 1 (10 kΩ)
Wire 4: R2 leg 2 → GND rail

Purpose:
  PB0 = Touch SEND pin (drives signal)
  PB3 = Touch RECEIVE pin (reads charge time)
  R1 (1MΩ) = connects send to receive
  R2 (10kΩ) = pulls receive pin low when not touched
  
  An exposed copper pad on the PCB will be wired to the PB3/PB0
  junction — when you touch it, your finger acts as the capacitor
  that slows charge accumulation, extending the measured time.
```

### The LED Circuit

```
Wire 5: ATtiny85 Pin 6 (PB1) → R3 leg 1 (47 Ω)
Wire 6: R3 leg 2 → LED Anode (+)
Wire 7: LED Cathode (−) → GND rail

Why 47 Ω at 3V?
  CR2032 provides 3V
  LED forward voltage (amber): ~2.0 V
  Current = (3.0 - 2.0) / 47 = 21 mA
  (Max ATtiny85 pin current: 40 mA — safely within limits)
  At PWM = 128 (50% duty cycle): ~10 mA average — bright enough
```

### Power and Bypass Capacitor

```
Wire 8:  CR2032 + terminal → VCC rail (red rail on breadboard)
Wire 9:  CR2032 − terminal → GND rail (blue rail on breadboard)
Wire 10: ATtiny85 Pin 8 (VCC) → VCC rail
Wire 11: ATtiny85 Pin 4 (GND) → GND rail
Wire 12: Capacitor C1 leg 1 (+) → VCC rail (as close to ATtiny85 as possible)
Wire 13: Capacitor C1 leg 2 (−) → GND rail

The 100 nF bypass capacitor absorbs voltage spikes when the ATtiny85
switches GPIO outputs rapidly. Without it, the LED PWM switching can
cause brief voltage drops that reset the MCU.
```

-----

## Setting Wire Colours for Clarity 🎨

In Fritzing, you can right-click any wire and change its colour. Use a convention:

```
Red wires:    VCC / 3V power
Black wires:  GND
Blue wires:   Touch send (PB0)
Yellow wires: Touch receive (PB3)
Green wires:  LED signal (PB1)
```

This colour convention will carry through to the schematic and make debugging infinitely easier.

-----

## Adding the Touch Pad Annotation 🖐️

The touch pad itself is not a component — it is a copper pad on the PCB that you touch with your finger. In the breadboard view, we represent it as an open wire end.

Draw a short wire from the PB3 node (the junction between R1 and R2) going to empty space to the right. Add a **label** to this wire endpoint:

1. Right-click the wire end → Add Label
1. Label text: “TOUCH PAD”
1. This endpoint represents the exposed copper pad we will add in the PCB view

-----

## The Complete Breadboard Circuit: Verification ✅

After all wires are placed, verify:

```
Component connections — verify these before moving to schematic:

ATtiny85 Pin 1 (PB5/Reset): unconnected (or connect to VCC via 10kΩ for reset protection)
ATtiny85 Pin 2 (PB3):        → R1 leg 2, R2 leg 1 [TOUCH RECEIVE]
ATtiny85 Pin 3 (PB4):        unconnected
ATtiny85 Pin 4 (GND):        → GND rail
ATtiny85 Pin 5 (PB0):        → R1 leg 1 [TOUCH SEND]
ATtiny85 Pin 6 (PB1):        → R3 leg 1 [LED PWM]
ATtiny85 Pin 7 (PB2):        unconnected (or ISP SCK — add later)
ATtiny85 Pin 8 (VCC):        → VCC rail

R1 leg 1: → PB0 (send)
R1 leg 2: → PB3 (receive), R2 leg 1

R2 leg 1: → PB3, R1 leg 2
R2 leg 2: → GND rail

R3 leg 1: → PB1
R3 leg 2: → LED anode

LED anode:   → R3 leg 2
LED cathode: → GND rail

C1 (+): → VCC rail
C1 (−): → GND rail

CR2032 (+): → VCC rail
CR2032 (−): → GND rail

TOUCH PAD (open wire): → junction of R1/R2
```

-----

## Saving and Exporting the Breadboard View as PDF 💾

Before moving on:

```
File → Save (or Ctrl+S)
```

To share or document the breadboard:

```
File → Export → as PDF
Select: Breadboard
Save as: et-finger-breadboard.pdf
```

This PDF is useful for sharing with others, printing as an assembly guide, or attaching to a project log.

-----

## What’s Next: The Schematic View 📋

*The breadboard view shows us the physical circuit. The schematic view tells us what it means electrically.*

In **Episode 3**, we switch to the Schematic view in Fritzing and clean up the connections into proper IEEE/IEC schematic symbols — voltage sources, ground symbols, net labels, component reference designators. The schematic is the document that lives forever with the project: it survives changes, it survives different PCB revisions, it is the DNA of the design.

*“I’ll be right here,” says E.T. — and so will this schematic.*

-----

**🔗 Resources**

- **Fritzing breadboard tutorial**: [fritzing.org/learning/tutorials/building-circuit](https://fritzing.org/learning/tutorials/building-circuit/)
- **CapacitiveSensor library**: [github.com/PaulStoffregen/CapacitiveSensor](https://github.com/PaulStoffregen/CapacitiveSensor)
- **ATtiny85 pinout**: [pinout.xyz/pinout/attiny85](https://pinout.xyz/pinout/attiny85)

-----

*🔴 E.T.’s Finger build by Fritzing and Aisler — from breadboard to fingertip, one glowing episode at a time.*
