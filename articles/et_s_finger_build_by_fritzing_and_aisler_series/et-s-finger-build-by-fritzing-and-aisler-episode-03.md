---
title: "E.T.‘s Finger build by Fritzing and Aisler 🔴 Ep.3"
published: false
description: "Episode 3: ‘I’ll be right here,’ says E.T., pressing his glowing finger to Elliott’s forehead. The schematic is that promise. It is the document that persists through every physical revision, every component swap, every board respin. It tells the permanent truth about what the circuit does. This episode cleans up the Fritzing schematic view: proper symbols, net labels, power flags, and a complete circuit document."
tags: [fritzing, schematic, electronics, documentation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-finger-episode-03.png"
series: "E.T.’s Finger build by Fritzing and Aisler"
canonical_url: ""
organization: "the-software-s-journey"
part: 3
---

## Episode 3: I’ll Be Right Here — The Schematic

-----

## “I’ll Be Right Here” 📄

E.T. reaches up, presses his glowing fingertip to Elliott’s temple, and says: *“I’ll be right here.”*

The schematic is that promise. The breadboard view shows a snapshot of one physical moment — components on a mat, wires connecting them. But the **schematic** is the permanent record. It outlives the breadboard. It survives component substitutions, PCB revisions, and the passage of time. When someone finds this project ten years from now and asks “what does this circuit do?”, the schematic answers them completely.

We drew the circuit in the breadboard view. Now we clean it.

-----

## 🗂️ SIPOC — The Schematic View

|**Suppliers**                      |**Inputs**                               |**Process**                                                                                   |**Outputs**                                                 |**Customers**                                                                            |
|-----------------------------------|-----------------------------------------|----------------------------------------------------------------------------------------------|------------------------------------------------------------|-----------------------------------------------------------------------------------------|
|Fritzing (automatic extraction)    |Breadboard connections drawn in Episode 2|Fritzing auto-generates the schematic from breadboard — we then clean and annotate it         |A raw schematic with correct connections but messy layout   |The maker — who cleans the layout, adds labels, power symbols, and values                |
|The maker (you)                    |Raw auto-generated schematic             |Arrange components, add power symbols, add net labels, set reference designators, add values  |A publication-quality schematic                             |The PCB view — which uses the schematic netlist; anyone reading the project documentation|
|Electronics documentation standards|IEEE/IEC schematic conventions           |Apply: consistent net naming, power flags, decoupling caps near ICs, signal flow left-to-right|A schematic that communicates intent clearly to any engineer|Future maintainers, collaborators, the AISLER review process                             |

-----

## Switching to the Schematic View 🔄

Click the **Schematic** tab at the top of the Fritzing window (the second tab, between Breadboard and PCB).

Fritzing has automatically generated a schematic from your breadboard connections. The schematic will likely look like a chaotic web of crossing wires and poorly positioned symbols. This is normal — Fritzing places schematic symbols automatically at arbitrary positions. Our job is to clean it up.

```
What you will see initially:
  - All components from the breadboard are present as schematic symbols
  - Connections are preserved (the netlist is correct)
  - Component placement is random / auto-arranged
  - Wires may cross at right angles making it hard to follow

Our goal:
  - Arrange components in a logical signal flow (left to right)
  - Eliminate wire crossings where possible
  - Add power symbols (VCC, GND) to eliminate long power wires
  - Add net labels where wires cross unavoidably
  - Set proper reference designators (U1, LED1, R1–R3, C1, BT1)
  - Set component values clearly visible
```

-----

## Reference Designators: Naming the Cast 🏷️

Every component on a schematic needs a **reference designator** — a unique identifier. These carry through from schematic to PCB to BOM.

|Component              |Ref Des|Value / Type |
|-----------------------|-------|-------------|
|ATtiny85               |U1     |ATtiny85-20PU|
|Amber LED              |LED1   |590 nm, 20 mA|
|Touch send resistor    |R1     |1 MΩ, 1/4 W  |
|Touch receive pull-down|R2     |10 kΩ, 1/4 W |
|LED current limiter    |R3     |47 Ω, 1/4 W  |
|Bypass capacitor       |C1     |100 nF, 50 V |
|Battery holder         |BT1    |CR2032, 3 V  |

To set reference designators in Fritzing:

1. Select a component in the Schematic view
1. In the Properties panel (bottom right), find **Part label** or **Ref**
1. Type the reference designator (e.g., “U1”)
1. The label appears next to the component on the schematic

-----

## Adding Power Symbols: Clean Up the Power Rails ⚡

In a real schematic, you do not draw long wires from the battery to every component. Instead, you use **power symbols** — special symbols meaning “this net is connected to VCC” or “this net is connected to GND” everywhere they appear.

In Fritzing:

1. In the Parts panel, search for “power”
1. Drag a “Power Symbol — VCC” to the schematic
1. Connect it to the ATtiny85’s VCC pin (Pin 8)
1. Drag another “Power Symbol — GND” to the GND pin (Pin 4)
1. Repeat for the LED cathode, C1’s ground leg, and R2’s ground leg

This eliminates the long wires running to the battery holder, making the schematic much cleaner.

-----

## The Clean Schematic Layout 📐

Arrange the components in this logical order (left to right = signal flow):

```
Left side: Power sources
  BT1 (CR2032) → VCC symbol at top
                  GND symbol at bottom

Centre-left: MCU
  U1 (ATtiny85)
  Pin 8 (VCC) → VCC power symbol
  Pin 4 (GND) → GND power symbol
  Pin 5 (PB0) → R1 (touch send)
  Pin 2 (PB3) → R1 / R2 junction
  Pin 6 (PB1) → R3 (LED drive)

Centre-right: Touch network
  R1 (1 MΩ) — connects PB0 to PB3
  R2 (10 kΩ) — connects PB3 to GND

Right side: LED circuit
  R3 (47 Ω) — LED current limiter
  LED1 — amber LED, anode to R3, cathode to GND

Bottom: Decoupling capacitor
  C1 (100 nF) — across VCC and GND, near U1

Below all: Touch pad label
  Open net from PB3 / R1 junction → net label "TOUCH_PAD"
```

-----

## The Full Circuit in Schematic Notation 📋

Here is the complete circuit described as a schematic netlist — the underlying truth that Fritzing maintains:

```
Net: VCC (3V)
  BT1 pin + (positive)
  U1 pin 8 (VCC)
  C1 pin + (positive)

Net: GND
  BT1 pin − (negative)
  U1 pin 4 (GND)
  C1 pin − (negative)
  R2 pin 2 (pull-down to GND)
  LED1 cathode

Net: TOUCH_SEND
  U1 pin 5 (PB0)
  R1 pin 1

Net: TOUCH_RECEIVE / TOUCH_PAD
  U1 pin 2 (PB3)
  R1 pin 2
  R2 pin 1
  Open pad → exposed PCB touch pad

Net: LED_PWM
  U1 pin 6 (PB1)
  R3 pin 1

Net: LED_ANODE
  R3 pin 2
  LED1 anode
```

-----

## Adding Net Labels in Fritzing 🏷️

For the touch pad net and any net that crosses other wires, add a net label:

1. In Schematic view, go to Parts → search “net label” or “label”
1. Drag a net label onto the TOUCH_RECEIVE net
1. Name it: `TOUCH_PAD`
1. Add the same label name to the PCB’s exposed pad later
1. Fritzing will understand these two are the same electrical net

-----

## Annotating the Schematic: Component Values 📝

Fritzing shows component values next to each symbol. Make sure all are visible and correct:

|Symbol|Value to show|
|------|-------------|
|U1    |ATtiny85-20PU|
|LED1  |590nm Amber  |
|R1    |1MΩ          |
|R2    |10kΩ         |
|R3    |47Ω          |
|C1    |100nF        |
|BT1   |CR2032 3V    |

To edit a value in Fritzing:

1. Select the component
1. In Properties panel (bottom right) → **Value** field
1. Type the correct value

-----

## Adding a Notes Label: The Story Behind the Circuit 📝

In Fritzing’s schematic view, you can add text boxes:

1. Parts panel → search “note” or “text”
1. Drag a text box onto the schematic
1. Add the following description:

```
E.T.'s Finger PCB
─────────────────
Touch sensing: CapacitiveSensor library
  R1 (1MΩ): Send resistor PB0→PB3
  R2 (10kΩ): Pull-down on receive (PB3)

LED drive: PWM on PB1 (Timer0, OC0B)
  R3 (47Ω): At 3V, drives ~20 mA peak, ~10 mA avg at 50% PWM

Power: CR2032 (3V), no regulator needed
  ATtiny85 min Vcc: 1.8V — 3V CR2032 works perfectly
  C1 (100nF): VCC decoupling — essential for PWM stability

Touch pad: exposed PCB copper pad, 6×6 mm
  Located at top of board (fingertip area)
```

-----

## The Schematic Correctness Check ✅

Before exporting, mentally walk through the schematic:

```
Power path:
  CR2032 (+) → VCC → ATtiny85 pin 8, C1+
  CR2032 (−) → GND → ATtiny85 pin 4, C1−, R2 leg 2, LED1 cathode
  ✓ No missing power connections
  ✓ C1 is across VCC/GND close to U1

Touch path:
  PB0 → R1 (1MΩ) → PB3 (receive)
  PB3 → R2 (10kΩ) → GND
  PB3 → TOUCH_PAD (open net to PCB pad)
  ✓ Send and receive pins are on the same IC
  ✓ Pull-down resistor on receive
  ✓ Touch pad connected to the receive node

LED path:
  PB1 (PWM) → R3 (47Ω) → LED1 anode → LED1 cathode → GND
  ✓ Current limiting resistor present
  ✓ LED polarity correct (anode to resistor, cathode to GND)

No floating inputs: ✓ (PB4, PB2 not connected — acceptable)
Reset pin (PB5/Pin1): Not connected — acceptable for standalone operation
```

-----

## Exporting the Schematic as PDF 📤

```
File → Export → as PDF
Select: Schematic
Filename: et-finger-schematic.pdf
Print scale: 100%
```

This PDF is the permanent record of your design. Include it in any project documentation, GitHub repository, or shared project page.

-----

## What the ATtiny85 ISP Header Is (and Why We Added It) 🔌

Notice we have not added the ISP (In-System Programming) header yet. This is the 6-pin header that allows us to program the ATtiny85 without removing it from the circuit. We will add this in the PCB view (Episode 4), but here is why it matters:

```
ATtiny85 ISP Header (6-pin, 2.54 mm pitch):
  Pin 1: MISO  ← ATtiny85 Pin 6 (PB1)
  Pin 2: VCC   ← 3V
  Pin 3: SCK   ← ATtiny85 Pin 7 (PB2)
  Pin 4: MOSI  ← ATtiny85 Pin 5 (PB0)
  Pin 5: RESET ← ATtiny85 Pin 1 (PB5)
  Pin 6: GND   ← GND

⚠️ Note: PB0 (MOSI) is also our TOUCH_SEND pin.
   This means you cannot use touch sensing while the ISP programmer
   is connected. This is acceptable — programming and normal operation
   are mutually exclusive states.
```

We will add the ISP header to the PCB in Episode 4 and update the schematic accordingly.

-----

## What’s Next: The PCB View 🖥️

*The schematic tells us what the circuit does. The PCB view decides where it lives.*

In **Episode 4**, we switch to the PCB view — the most exciting step. We will shape the board like a rounded fingertip (22 mm × 18 mm), arrange the components for maximum ergonomics, route copper traces between them, pour a ground plane, and run the Design Rules Check. The board that AISLER will manufacture takes physical form.

*A finger takes shape. The glow grows closer.*

-----

**🔗 Resources**

- **Schematic design basics**: [fritzing.org/learning/tutorials/schematic-view](https://fritzing.org/learning/tutorials/schematic-view/)
- **Reference designators**: [en.wikipedia.org/wiki/Reference_designator](https://en.wikipedia.org/wiki/Reference_designator)

-----

*🔴 E.T.’s Finger build by Fritzing and Aisler — from breadboard to fingertip, one glowing episode at a time.*
