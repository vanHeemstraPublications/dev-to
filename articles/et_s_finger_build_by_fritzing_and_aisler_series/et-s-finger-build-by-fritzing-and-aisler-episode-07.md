---
title: "E.T.‘s Finger build by Fritzing and Aisler 🔴 Ep.7"
published: false
description: "Episode 7: ‘We’re home.’ Elliot says it as E.T.’s heart light blazes and the flowers spring back to life. The boards have arrived from AISLER. The components are waiting. The soldering iron is at temperature. This episode assembles the E.T. Finger PCB from bare board to complete device: every component, every solder joint, every order of operations. We solder our way home."
tags: [soldering, electronics, assembly, makers]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-finger-episode-07.png"
series: "E.T.’s Finger build by Fritzing and Aisler"
canonical_url: ""
organization: "the-software-s-journey"
part: 7
---

## Episode 7: We’re Home — Soldering and Assembly

-----

## “We’re Home” 🏡

The plants stand upright again. E.T.’s chest glows warm red. The forest fills with light. Something that was lost — or seemed lost — comes flooding back.

The AISLER envelope arrives. You open it carefully. Three small PCBs, green-and-white (or black-and-white if you chose the dramatic option), slide out. The silkscreen reads: *E.T. FINGER v1.0*. The holes are perfectly drilled. The copper traces shine under the light. The touch pad gleams at the top.

You are home.

Now: solder everything onto it.

-----

## 🗂️ SIPOC — The Assembly Process

|**Suppliers**      |**Inputs**                                                    |**Process**                                                         |**Outputs**                                            |**Customers**                   |
|-------------------|--------------------------------------------------------------|--------------------------------------------------------------------|-------------------------------------------------------|--------------------------------|
|AISLER             |The bare 2-layer PCB                                          |Already done — just arrived!                                        |A bare PCB with correct holes, pads, traces, silkscreen|You — the assembler             |
|Your workbench     |Soldering iron, solder, flux, tweezers, component lead cutters|Through-hole soldering: insert component → solder → cut leads       |Completed PCB with all components soldered             |The programming step (Episode 8)|
|Component suppliers|ATtiny85, LED, resistors, capacitor, ISP header, CR2032 holder|Match each component to the correct pads on the PCB using silkscreen|A fully populated PCB                                  |A working E.T. Finger device    |

-----

## Tools You Will Need 🛠️

```
Essential:
  ✓ Soldering iron (25–40W, fine tip preferred)
  ✓ Solder (0.6–0.8 mm, 60/40 or lead-free rosin core)
  ✓ Lead cutters / flush cutters (to trim component leads)
  ✓ Tweezers (for holding components)
  ✓ Flux paste or flux pen (improves solder flow, especially for the CR2032 holder)

Helpful:
  ✓ PCB holder or helping hands (keeps the board steady)
  ✓ Magnifying glass or loupe (inspect solder joints)
  ✓ Desoldering braid or solder sucker (for mistakes)
  ✓ Isopropyl alcohol (IPA) + old toothbrush (clean flux residue after soldering)
  ✓ Multimeter (continuity testing before powering on)
```

-----

## Inspecting the Bare PCB 🔍

Before placing a single component, inspect the board:

```
Visual inspection checklist:
  ✓ Board dimensions: approximately 26 × 22 mm
  ✓ Board shape: rounded corners (if specified)
  ✓ Silkscreen: "E.T. FINGER v1.0", all reference designators visible
  ✓ Touch pad: copper exposed at top of board (no green solder mask)
  ✓ Holes: all component holes drilled (8 for ATtiny85, 2 for LED, 6 for ISP, 2 for R1–R3/C1)
  ✓ Surface finish: shiny solder on pads (HASL) or gold (ENIG)
  ✓ No shorts: no copper bridges between adjacent pads (use magnifier)
  ✓ Board edge: clean cut, no delamination or fraying

Electrical inspection (before any components):
  Set multimeter to continuity mode.
  Test: VCC pad → not connected to GND pad (open circuit)
  Test: GND pad → connected to all GND-labelled pads (continuity)
  This confirms the ground pour is correct and VCC is isolated.
```

-----

## Assembly Order: Smallest to Largest, Flattest First 📋

The golden rule of through-hole PCB assembly: **solder the shortest (lowest-profile) components first**, then progressively taller ones. This way, when you flip the board upside-down to solder, the taller components don’t fall out.

```
Assembly order for E.T. Finger PCB:

Order 1:  R1, R2, R3 (resistors) — flat, low profile
Order 2:  C1 (ceramic capacitor) — low profile
Order 3:  U1 (ATtiny85 DIP-8) — through-hole IC, medium height
Order 4:  ISP header (6-pin) — medium height
Order 5:  LED1 (5mm amber LED) — tallest component
Order 6:  (Back of board) CR2032 holder — SMD, needs different technique
```

-----

## Soldering the Resistors (R1, R2, R3) 🔧

**Resistors are non-polarised** — they can go in either direction. However, it is good practice to orient them consistently (e.g., the colour band reading left-to-right).

```
For each resistor:
  1. Bend the leads to match the hole spacing (typically 7.62 mm / 0.3" for axial)
  2. Insert the resistor from the top (component side)
  3. Bend the leads slightly outward (45°) on the back to hold it in place
  4. Flip the board upside down (or use a PCB holder)
  5. Touch the iron tip to the pad + lead junction for 2–3 seconds
  6. Feed solder into the joint (not the iron) until it flows around the lead
  7. Remove iron, let cool 3–5 seconds
  8. Trim the lead flush with flush cutters (or 0.5 mm above the solder)

Good solder joint characteristics:
  ✓ Shiny, smooth, volcano-shaped
  ✓ Solder wets both the lead and the pad (spreads out onto the pad)
  ✓ No cold joint (dull, grainy, bumpy surface)
  ✓ No excess solder bridging to adjacent pad
```

**Resistor placement — match to silkscreen:**

```
R1 (1 MΩ): Placed between PB0 and PB3 on the schematic
           On the PCB: look for "R1" silkscreen label
           Colour code: Brown–Black–Green (or Brown–Black–Black–Yellow)

R2 (10 kΩ): The pull-down resistor
            On the PCB: "R2" silkscreen label
            Colour code: Brown–Black–Orange (or Brown–Black–Black–Red)

R3 (47 Ω):  LED current limiter — nearest to the LED
            On the PCB: "R3" silkscreen label
            Colour code: Yellow–Violet–Black (or Yellow–Violet–Black–Gold)
```

-----

## Soldering the Bypass Capacitor (C1) 🔧

The 100 nF ceramic disc capacitor is also **non-polarised** — either direction is fine.

```
1. Insert C1 between VCC and GND holes (close to U1 as designed)
2. The lead spacing for disc capacitors is usually 2.54–5 mm
   Check which holes are correct by the "C1" silkscreen label
3. Solder using the same technique as resistors
4. Trim leads
```

-----

## Soldering the ATtiny85 (U1) — The Heart 🧠

The ATtiny85 is a DIP-8 integrated circuit. **It is polarised** — orientation matters. The chip has a notch (semicircle) on one end indicating Pin 1.

```
1. Look at the PCB silkscreen: the U1 footprint shows a notch/semicircle
   indicating which end has Pin 1 (typically facing left or top)
   
2. Orient the ATtiny85 so its notch matches the silkscreen notch
   
3. The pins may need slight bending inward to fit the holes:
   Lay the chip flat on a table, press gently on each row of pins
   to bend them slightly inward until they align with the holes

4. Insert all 8 pins into their holes
   Check from the side: all pins should protrude equally below the board
   
5. Hold the chip in place (it will try to lift)
   Solder one corner pin (Pin 1 or Pin 8) first to tack the chip in place
   
6. Check alignment from above: is the chip parallel to the board edge?
   Is the notch on the correct side?
   
7. Solder the remaining 7 pins

8. Inspect: each pin should have a clean solder joint with good wetting
   No bridges between adjacent pins (use magnifier to check)
```

**Alternative: Use a DIP-8 socket**

A DIP-8 socket is a plastic base that solders onto the PCB. The ATtiny85 plugs in and out of it. Advantages:

- Replace the MCU without desoldering
- Remove for reprogramming on a breadboard programmer
- Protects the IC from soldering heat

If using a socket:

- Solder the socket to the PCB (it is non-polarised, but match notch direction)
- Insert the ATtiny85 into the socket after all soldering is complete
- The notch on the IC and socket must align

**Recommended: Use a socket for prototyping.**

-----

## Soldering the ISP Header (6-pin) 🔌

The 6-pin 2×3 header is used for programming. It is non-polarised electrically, but there is a conventional orientation (Pin 1 = top-left with the marker dot).

```
1. Insert the header from the TOP of the board (pins go down through the board)
2. The header should sit flush against the board surface
3. Tack one corner pin first to check alignment
4. Solder all 6 pins
5. Trim any protruding pins below the board (they should be short already)

Pin 1 identification:
  Many ISP headers have a small triangle or dot on one end
  The silkscreen on the PCB should show which end is Pin 1
  Pin 1 = MISO
```

-----

## Soldering the Amber LED (LED1) 🟠

The LED **is polarised** — orientation is critical. If it goes in backwards, it will not light up (LEDs are diodes; current only flows one way).

```
LED polarity identification:
  Anode (+, positive):   Longer lead
  Cathode (−, negative): Shorter lead + flat side on the LED body

PCB marking:
  The LED footprint on the silkscreen shows a triangle symbol:
  Triangle points in the direction of current flow (from anode to cathode)
  The flat side of the triangle = cathode
  OR: the "+" and "−" may be marked directly

Procedure:
  1. Check the silkscreen for anode/cathode marking near the LED1 holes
  2. Insert LED with the longer lead (anode) into the "+" hole
  3. The LED will be the tallest component — it stands up from the board
  4. For a wearable device, the LED height matters:
     → For maximum forward glow: let it stand at full height (10 mm)
     → For a lower profile: bend the LED parallel to the board (horizontal)
  
  5. Solder both leads
  6. Trim leads close to the board

LED height recommendation:
  Stand the LED at about 5 mm above the board surface.
  This places the light source near the top edge of the PCB
  where it diffuses through any translucent fingertip cover material.
```

-----

## Soldering the CR2032 Holder (BT1) — SMD on the Back 🔋

The CR2032 SMD holder is soldered to the **back of the board**. This is the only surface-mount component in our design.

SMD soldering technique (simplified for one component):

```
1. Flip the board over (component side down)
2. The CR2032 holder pads are the two large pads on the back of the board
3. Apply a small amount of flux paste to each pad

4. Apply small amount of solder to BOTH pads first ("tinning")
   This makes the final soldering much easier

5. Place the CR2032 holder on the pads
   The spring contact goes on the GND pad
   The flat contact goes on the VCC pad
   (Most holders are labelled + and −)

6. Hold the holder in place with tweezers
   Press the holder down with the tweezers while heating each pad with the iron
   The pre-tinned solder should reflow and bond

7. Inspect: the holder should sit flat against the board
   Both pads should have solder wicking under the holder contacts

Common mistakes:
  ✗ Holder not flat (one side lifted) → reheat and press down
  ✗ Cold joint (grainy) → reheat until solder flows smoothly
  ✗ Excess solder bridging between + and − pads → use desoldering braid
```

-----

## Post-Assembly Cleaning 🧹

After all soldering is complete, clean the board:

```
1. Wet a soft brush (old toothbrush) with IPA (isopropyl alcohol, >90%)
2. Scrub the board gently, especially around solder joints
3. This removes flux residue (brown/yellowish buildup)
4. Pat dry with a lint-free cloth or let air dry for 5 minutes

Why clean?
  Flux residue is mildly corrosive over time
  It can interfere with capacitive touch readings (slightly)
  Clean boards look professional and allow better visual inspection
```

-----

## Final Assembly Inspection Checklist ✅

```
Visual:
  ✓ All components seated flush against the board (no lifted components)
  ✓ All solder joints shiny and volcano-shaped
  ✓ No solder bridges between adjacent pads (use 10× loupe)
  ✓ LED orientation correct (longer lead = anode = + hole)
  ✓ ATtiny85 orientation correct (notch = Pin 1, matches silkscreen)
  ✓ CR2032 holder flat against back of board
  ✓ All component leads trimmed

Electrical (before inserting battery):
  Set multimeter to continuity/beep mode
  ✓ VCC rail not shorted to GND (should be OPEN — no beep)
  ✓ VCC rail is continuous: CR2032 holder + → U1 pin 8 pad
  ✓ GND rail is continuous: all GND pads connected
  ✓ PB1 pad → R3 → LED anode (continuity through trace)
  ✓ PB0 pad → R1 → PB3 pad (continuity through R1)

Touch pad:
  ✓ Touch pad copper exposed (no solder mask)
  ✓ Touch pad connected to PB3/R1-R2 junction (continuity)
```

-----

## What’s Next: Upload and Wear It 🔴

*The board is assembled. The CR2032 is ready to insert. The ISP programmer is at hand.*

In **Episode 8**, we upload the firmware to the ATtiny85, test the touch sensing and LED breathing, tune the sensitivity threshold if needed, and finally — put it on a finger and experience the moment when digital design becomes a physical, wearable piece of magic.

*I love you, E.T. And so does this LED.*

-----

**🔗 Resources**

- **Through-hole soldering tutorial**: [learn.adafruit.com/adafruit-guide-excellent-soldering](https://learn.adafruit.com/adafruit-guide-excellent-soldering)
- **SMD soldering basics**: [learn.sparkfun.com/tutorials/how-to-solder-castellated-mounting-holes](https://learn.sparkfun.com/tutorials/how-to-solder-castellated-mounting-holes)
- **ATtiny85 socket**: search “DIP-8 IC socket” on any electronics supplier

-----

*🔴 E.T.’s Finger build by Fritzing and Aisler — from breadboard to fingertip, one glowing episode at a time.*
