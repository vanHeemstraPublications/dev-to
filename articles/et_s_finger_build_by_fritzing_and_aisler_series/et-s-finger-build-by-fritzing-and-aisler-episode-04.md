---
title: "E.T.‘s Finger build by Fritzing and Aisler 🔴 Ep.4"
published: false
description: "Episode 4: The moment E.T. opened his eyes in the ice chest and his heart light blazed, everyone in the cinema felt it — the sudden blazing return of something that should not exist but does. In our project, this is the PCB view: the moment the circuit stops being an abstraction and becomes a physical object. We shape the board like a fingertip, route the traces, pour the ground plane, and run the DRC."
tags: [fritzing, pcb, layout, electronics]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-finger-episode-04.png"
series: "E.T.’s Finger build by Fritzing and Aisler"
canonical_url: ""
organization: "the-software-s-journey"
part: 4
--- 

## Episode 4: He’s Alive! — The PCB Layout

-----

## “He’s Alive!” ⚡

Elliott leans over the ice chest. E.T. lies still. And then — suddenly, impossibly — the heart light blazes red-warm through the alien’s wrinkled chest. *“He’s alive!”*

The PCB view is that moment. Until now, everything has been abstract: wire connections, net names, component symbols. The PCB view is where the circuit becomes a physical, tangible thing — copper on FR4, shapes that a machine can cut and etch. The moment you see your circuit laid out as a real board, something shifts. It is suddenly real.

Let us make it real.

-----

## 🗂️ SIPOC — The PCB Layout

|**Suppliers**               |**Inputs**                                                        |**Process**                                                            |**Outputs**                                                     |**Customers**                                                                  |
|----------------------------|------------------------------------------------------------------|-----------------------------------------------------------------------|----------------------------------------------------------------|-------------------------------------------------------------------------------|
|Fritzing (schematic netlist)|The component list and connections from the Schematic view        |Import components into PCB view; arrange, route traces, add copper fill|A complete PCB layout file in `.fzz` format                     |The Export step (Episode 6) — which generates Gerber files for AISLER          |
|AISLER design rules         |Min trace: 200 µm, min clearance: 150 µm, min drill: 0.3 mm (HASL)|Apply DRC in Fritzing; verify all traces meet AISLER’s minimum rules   |A DRC-clean layout that AISLER can manufacture without errors   |AISLER manufacturing — which accepts or rejects based on design rule compliance|
|Board shape (finger design) |A 22 × 18 mm rounded rectangle board outline                      |Draw on the Board layer in Fritzing; the outline defines what gets cut |A precisely shaped PCB with rounded corners matching a fingertip|The assembled device — which will sit on a finger comfortably                  |

-----

## Switching to the PCB View 🖥️

Click the **PCB** tab (third tab in Fritzing).

You will see:

- A grey rectangle — the default board outline
- All your components floating outside the board as “ratsnest” symbols (components not yet placed)
- Yellow lines (ratsnest) showing which pins need to be connected
- The board itself shown with layers visible

**First: Resize and reshape the board.**

-----

## Shaping the Board: The Fingertip 🫵

Our board needs to fit on a fingertip:

- **Size**: 22 mm wide × 18 mm tall
- **Shape**: Rounded rectangle (radius 4 mm corners)
- **Touch pad**: 8 × 8 mm exposed copper square at the top

**Step 1: Set the board size**

1. Click on the board outline (grey rectangle)
1. In Properties panel (bottom right), set:
- Width: 22 mm
- Height: 18 mm
1. The board outline updates

**Step 2: Add rounded corners**

Fritzing’s board shape is drawn on the **Board** layer. To make it rounded:

1. In the PCB view, use the board outline editing tools
1. Select the board rectangle → right-click → “Edit Board Outline”
1. Add an arc at each corner with radius 4 mm
1. Alternatively: draw the outline manually using the Polygon tool on the Board layer

```
Board outline coordinates (origin at bottom-left):
  Bottom edge: (0,0) to (22,0)
  Right edge:  (22,0) to (22,18)  
  Top edge:    (22,18) to (0,18)
  Left edge:   (0,18) to (0,0)
  
  Corner arcs: 4 mm radius at each corner
  Total board area: 22 × 18 mm = 396 mm²
  
  Enough space for:
    - ATtiny85 DIP-8 (10.16 × 6.5 mm footprint)
    - LED (5mm diameter)
    - 5× resistors/capacitor (axial through-hole)
    - CR2032 holder (23.5 mm diameter — wait, this is too wide!)
```

**CR2032 holder problem!** A standard CR2032 holder (coin cell battery holder) is 23.5 mm in diameter — larger than our entire board. We have two solutions:

**Option A**: Use a SMD CR2032 holder with horizontal profile (Keystone 3034 or similar, 26 mm wide). The battery would extend beyond the PCB edge slightly — this is fine for a prototype.

**Option B**: Connect the board via short wires to an external battery. Simpler for first iteration.

**Recommended**: Use an SMD CR2032 holder soldered to the back of the board. The holder is wider than the board, but the battery sits behind the finger and is held by the same rubber ring. We will design for Option A.

**Revised board size: 26 mm wide × 22 mm tall** — to accommodate the CR2032 holder.

-----

## Component Placement Strategy 🗺️

Placement is about three things: function, manufacturability, and the user experience of assembling it.

```
Board layout (top view):

  ┌─────────────────────────────┐  ← 26 mm wide
  │  ╔═══════════╗              │  ← 22 mm tall
  │  ║           ║              │
  │  ║  TOUCH    ║  ← 8×8mm    │
  │  ║   PAD     ║   exposed    │
  │  ╚═══════════╝   copper     │
  │                              │
  │  ┌────────────┐              │
  │  │  LED1      │  R3─────┐   │
  │  │ (amber 5mm)│         │   │
  │  └────────────┘  ┌──────┘   │
  │                  │           │
  │  ┌──────────────────────┐   │
  │  │      U1 (ATtiny85)   │   │
  │  │      DIP-8           │   │
  │  └──────────────────────┘   │
  │                              │
  │  R1───  R2───  C1───         │
  │                              │
  │  ┌──────────────────────────┐│
  │  │   ISP HEADER (6-pin)     ││  ← bottom edge
  │  └──────────────────────────┘│
  └─────────────────────────────┘
         (back of board)
         [CR2032 HOLDER - SMD]
```

**Placement principles:**

```
1. Touch pad at top  — closest to the fingertip area
2. LED near top     — visible glow from above
3. ATtiny85 centre  — shortest average trace length
4. Passive components (R1, R2, R3, C1) between MCU and their connections
5. ISP header at bottom edge — accessible for programming without removing device
6. CR2032 on back side  — keeps front clean; battery weight balances on the finger
```

-----

## Placing Components in PCB View 📦

**Step 1: Drag components from the “ratsnest” area onto the board**

1. Click a component in the grey area outside the board
1. Drag it onto the board
1. Use the mouse to rotate (press ‘R’ while dragging, or right-click → Rotate)
1. Place according to the layout diagram above

**Step 2: Set component orientations**

For the ATtiny85 (DIP-8):

- Rotate so that Pin 1 is at top-left (notch facing left)
- Align with the long axis along the board

For LED1:

- Anode (positive) to face right, toward R3
- Cathode (negative) faces left, toward GND trace

For the ISP header:

- 6-pin, 2 × 3 configuration (standard AVR ISP)
- Place at bottom edge of board with pins accessible from outside

-----

## Setting Trace Widths for AISLER Compliance 📏

Before routing, set the trace widths in Fritzing’s routing settings:

```
Routing → DRC and Autorouter Settings

Minimum trace width:    0.4 mm (400 µm)
  → AISLER minimum is 200 µm. We use 400 µm for safety and easy soldering.
  
Minimum clearance:      0.3 mm (300 µm)
  → AISLER minimum is 150 µm. We use 300 µm for safety.
  
Minimum via diameter:   0.8 mm outer, 0.4 mm drill
  → AISLER minimum drill: 0.3 mm. We use 0.4 mm for strength.

Power traces (VCC, GND): 0.8 mm minimum
  → Slightly thicker for power distribution
```

In Fritzing:

1. Menu → Routing → Design Rule Settings (DRC/Autorouter Settings)
1. Set the values above
1. These apply to all future traces and the DRC check

-----

## Routing the Traces ✏️

Fritzing supports both auto-routing and manual routing. For a board this small, **manual routing** gives better results.

**How to route in Fritzing:**

1. Select the Routing tool (the pen icon)
1. Click on a pin pad — this starts a trace
1. Click at routing waypoints to bend the trace
1. Click on the destination pin — this completes the connection
1. The yellow ratsnest line disappears when a connection is complete

**Routing order (minimise crossings):**

```
Route 1: GND net (black)
  Rationale: GND connects the most things — route it first
  → LED1 cathode → GND via → ATtiny85 pin 4 → R2 pin 2 → C1 −
  → Connect all GND nodes with short, direct traces

Route 2: VCC net (red)
  → BT1 + → C1 + → ATtiny85 pin 8
  → Keep short — 0.8 mm trace width

Route 3: LED_PWM (green)
  → ATtiny85 pin 6 (PB1) → R3 pin 1
  → R3 pin 2 → LED1 anode
  → Short, direct — no crossing needed

Route 4: TOUCH_SEND (blue)
  → ATtiny85 pin 5 (PB0) → R1 pin 1

Route 5: TOUCH_RECEIVE (yellow)
  → R1 pin 2 → ATtiny85 pin 2 (PB3)
  → R2 pin 1 → same node as above (the touch pad junction)
  → Copper pad at top of board → same net via trace

Route 6: ISP connections
  → ATtiny85 pin 6 (PB1/MISO) → ISP header pin 1
  → ATtiny85 pin 7 (PB2/SCK)  → ISP header pin 3
  → ATtiny85 pin 5 (PB0/MOSI) → ISP header pin 4
  → ATtiny85 pin 1 (PB5/RESET)→ ISP header pin 5
  → VCC → ISP header pin 2
  → GND → ISP header pin 6
```

-----

## Adding the Touch Pad: Exposed Copper Area 🖐️

The touch pad is the most critical feature of this PCB — it is what makes E.T.’s finger respond to touch.

1. In PCB view, select the **Copper layer** (top layer)
1. Draw a rectangle pad: 8 × 8 mm at the top of the board
1. Connect it to the TOUCH_RECEIVE net via a short trace
1. This pad will be **not covered by solder mask** — we want the bare copper exposed

To remove solder mask from the touch pad:

1. Select the pad area
1. In Properties: **Solder Mask** → **No** (exposed)
1. The copper will be bare — your finger bridges the gap between this pad and the rest of the circuit capacitance

**Touch pad annotation on silkscreen:**

Add a silkscreen label above the touch pad:

1. Select the Silkscreen layer
1. Add text: “TOUCH” with an upward arrow icon
1. Font size: 1.5 mm (readable on a small board)

-----

## Adding a Ground Pour (Copper Fill) 🟫

A ground plane fills all unused PCB area with copper connected to GND. It reduces noise, improves signal integrity, and can simplify routing.

In Fritzing:

1. Menu → Routing → Fill Ground (or press Ctrl+G)
1. Select the layer: Bottom Copper
1. Select the net: GND
1. Fritzing fills all unoccupied space on the bottom layer with GND copper

**Why ground pour on bottom?**

The top layer has our components and traces. The bottom layer is mostly empty — adding GND copper there gives us the ground plane without interfering with top-layer routing.

After adding the ground pour, check that:

- The ground pour connects to all GND pads (a small trace should bridge each GND pad to the pour)
- No trace is accidentally short-circuited by the pour
- The clearance between traces and the pour is at least 0.3 mm (our minimum)

-----

## Running the Design Rules Check (DRC) ✅

```
Menu → Routing → Design Rules Check (DRC)

Or: Menu → Routing → DRC Settings → Run DRC
```

The DRC checks:

- Minimum trace width (we set 0.4 mm — AISLER minimum is 0.2 mm)
- Minimum clearance between traces and pads (we set 0.3 mm)
- Unconnected nets (any remaining yellow ratsnest lines)
- Overlapping pads

**Common DRC errors and fixes:**

|Error                           |Cause                                   |Fix                                                      |
|--------------------------------|----------------------------------------|---------------------------------------------------------|
|`unconnected net: TOUCH_PAD`    |Touch pad not connected to TOUCH_RECEIVE|Route a short trace from the copper pad to R1/R2 junction|
|`trace too narrow`              |A trace is thinner than the minimum     |Select the trace → Properties → Width → set to 0.4 mm    |
|`clearance violation`           |Two copper features too close           |Move trace, add a jog, or use the other layer            |
|`missing ground fill connection`|Ground pour island not connected        |Add a via or short trace to bridge it                    |

**The DRC should show zero errors before you export.** This is not optional — if AISLER receives a file with DRC violations, the board may be manufactured with errors that you cannot fix without a new order.

-----

## Board Layers: What Each Layer Means 📚

Fritzing works with these board layers, all of which become Gerber files:

```
Layer                  Gerber file     Purpose
────────────────────  ─────────────  ──────────────────────────────────────
Copper (top)           .gtl           Top copper traces, pads, SMD features
Copper (bottom)        .gbl           Bottom copper, ground pour
Solder Mask (top)      .gts           Everywhere covered by green solder mask
Solder Mask (bottom)   .gbs           Where solder mask is on the bottom
Silkscreen (top)       .gto           White component outlines, text, labels
Drill file             .drl           All hole positions and diameters
Board outline          .gko           The board edge for the router/milling
```

AISLER needs all of these to manufacture the board. Fritzing exports them all in one ZIP when you choose “Extended Gerber (RS-274X)”.

-----

## Board Checklist Before Export ✅

```
Physical:
  ✓ Board size set: 26 × 22 mm
  ✓ Corners are rounded (4 mm radius)
  ✓ All components are within the board outline
  ✓ No component overhangs the board edge

Electrical:
  ✓ Zero unconnected nets (no yellow ratsnest lines remain)
  ✓ DRC passes with zero errors
  ✓ Ground pour fills bottom layer
  ✓ All GND pads connected to ground pour or ground trace

Manufacturability:
  ✓ Minimum trace width: 0.4 mm (>AISLER 0.2 mm minimum)
  ✓ Minimum clearance: 0.3 mm (>AISLER 0.15 mm minimum)
  ✓ Minimum drill: 0.4 mm (>AISLER 0.3 mm minimum)
  ✓ Touch pad has solder mask removed (exposed copper)
  ✓ Silkscreen text does not overlap pads

Usability:
  ✓ ISP header accessible at board edge
  ✓ LED positioned to shine forward (away from finger)
  ✓ Touch pad at fingertip position
  ✓ Component ref designators visible on silkscreen
```

-----

## What’s Next: Writing the Firmware 💻

*The board is laid out. The circuit is routed. The shape is a finger.*

In **Episode 5**, we switch to Fritzing’s Code view and write the ATtiny85 firmware: capacitive touch detection using the CapacitiveSensor technique, PWM LED breathing using a sinusoidal ramp, and the touch-triggered brightness burst. The code that makes the finger *feel alive*.

*He’s alive! And soon, so is our firmware.*

-----

**🔗 Resources**

- **Fritzing PCB design**: [fritzing.org/learning/tutorials/making-pcb](https://fritzing.org/learning/tutorials/making-pcb/)
- **AISLER design rules**: [community.aisler.net/t/pcb-design-rules/41](https://community.aisler.net/t/pcb-design-rules/41)
- **AISLER trace width**: HASL: 200 µm minimum, ENIG: 125 µm minimum

-----

*🔴 E.T.’s Finger build by Fritzing and Aisler — from breadboard to fingertip, one glowing episode at a time.*
