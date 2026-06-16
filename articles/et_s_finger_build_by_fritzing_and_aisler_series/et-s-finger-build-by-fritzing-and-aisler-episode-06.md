---
title: "E.T.‘s Finger build by Fritzing and Aisler 🔴 Ep.6"
published: false
description: "Episode 6: ‘The flowers are dying.’ Elliott’s plants wilt as E.T. sickens — the connection between them is severing. But not yet. We have one more critical step before anything physical can be born: getting the design off the screen and into the hands of a manufacturer. This episode exports the Gerbers from Fritzing, uploads them to AISLER, reviews the order, and clicks ‘manufacture’."
tags: [fritzing, aisler, pcb, manufacturing]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-finger-episode-06.png"
series: "E.T.’s Finger build by Fritzing and Aisler"
canonical_url: ""
organization: "the-software-s-journey"
part: 6
---

## Episode 6: The Flowers Are Dying — Exporting and Ordering

-----

## “The Flowers Are Dying” 🌿

In the film, Elliott’s houseplants begin to wilt at the same time E.T. does. The connection between them — that strange, tender psychic link — means that when E.T. suffers, the flowers feel it too. The threshold between one state and another.

Our project is at a similar threshold. The design exists only on a screen. The board exists only as a `.fzz` file and Gerber layers. Nothing physical has been made yet. This episode crosses that threshold: we export the design data, hand it to AISLER, and begin the irreversible process of turning electrons into copper.

After this episode, a real PCB will be on its way to your door.

-----

## 🗂️ SIPOC — The Manufacturing Pipeline

|**Suppliers**         |**Inputs**                      |**Process**                                                             |**Outputs**                                                       |**Customers**                                    |
|----------------------|--------------------------------|------------------------------------------------------------------------|------------------------------------------------------------------|-------------------------------------------------|
|Fritzing PCB view     |Completed, DRC-clean `.fzz` file|Export Extended Gerber RS-274X and drill file                           |A ZIP containing 7 Gerber layers + 1 drill file                   |AISLER — which accepts the ZIP or `.fzz` directly|
|AISLER (upload step)  |Gerber ZIP or `.fzz` file       |Automated Gerber processing → design rule check → preview generation    |An order page showing board preview, pricing, and delivery options|You — who review and confirm the order           |
|AISLER (manufacturing)|Confirmed order                 |PCB fabrication: imaging → etching → drilling → surface finish → routing|3 physical PCBs (AISLER minimum order)                            |You — delivered within 1–2 business days         |

-----

## Two Ways to Get Your Design to AISLER 🔀

AISLER accepts Fritzing files in two ways:

### Method 1: The Fabricate Button (Recommended for Beginners)

Inside Fritzing, there is a direct **Fabricate** button that sends your `.fzz` file directly to AISLER:

```
Fritzing PCB view → bottom bar → "Fabricate" button
  (or: File → Export → for Production → Fabricate at AISLER)

What this does:
  1. Opens your browser to fab.fritzing.org (or aisler.net)
  2. Automatically uploads your current .fzz file
  3. AISLER's servers convert it to Gerbers automatically
  4. You review and order
  
Advantages:
  ✓ Simplest workflow — one click
  ✓ No manual Gerber export needed
  ✓ AISLER's conversion is tested against Fritzing's output format
  
Disadvantages:
  ✗ You cannot review Gerbers before uploading
  ✗ Any conversion quirks are handled by AISLER, not by you
```

### Method 2: Manual Gerber Export (Recommended for Production)

Export Gerbers yourself, review them, then upload to AISLER:

```
Fritzing PCB view → File → Export → for Production → Extended Gerber (RS-274X)

Alternatively:
  File → Export → for Production → Extended Gerber (RS-274X)...

A file dialog opens: choose a folder (e.g., et-finger-gerbers/)
Fritzing saves these files:
  et-finger_copperTop.ger           ← Top copper layer
  et-finger_copperBottom.ger        ← Bottom copper (ground pour)
  et-finger_maskTop.ger             ← Top solder mask
  et-finger_maskBottom.ger          ← Bottom solder mask
  et-finger_silkTop.ger             ← Top silkscreen (labels, outlines)
  et-finger_etchingLayerTop.ger     ← Board outline (for routing)
  et-finger_drill.txt               ← Drill file (Excellon format)

ZIP the folder: et-finger-gerbers.zip
Upload this to AISLER at: aisler.net/p/new
```

-----

## Understanding Each Gerber Layer 📚

Before uploading, let us understand what each file represents:

```
et-finger_copperTop.ger
  What it is: All copper on the top side of the board
  Contains:   Traces, pads, through-hole pad rings
  Appearance: On the green PCB, this is what you see through the solder mask
  Critical:   This is your circuit — must be correct!

et-finger_copperBottom.ger
  What it is: All copper on the bottom side
  Contains:   Ground pour, any bottom-side traces
  Appearance: The back of the board

et-finger_maskTop.ger
  What it is: The solder mask on the top
  Contains:   Everything the green lacquer COVERS
  Important:  The touch pad should NOT be in this layer
              (we want the touch pad copper EXPOSED, not masked)
  Inversion:  Solder mask files show the COVERED areas, not the openings

et-finger_maskBottom.ger
  What it is: Solder mask on the bottom
  Contains:   Mask over the ground pour
  Contains:   Openings for the CR2032 holder pads

et-finger_silkTop.ger
  What it is: The white silkscreen print on top
  Contains:   Component outlines, reference designators, text labels
  Note:       Verify "TOUCH" label and "E.T. FINGER" text appear here

et-finger_etchingLayerTop.ger (or _contour.ger)
  What it is: The board outline — the shape the router cuts
  Contains:   The 26 × 22 mm rounded rectangle outline
  Critical:   Must be a closed, single-line shape — no gaps

et-finger_drill.txt
  What it is: Drill file in Excellon format
  Contains:   X/Y coordinates and diameter for every hole
  Critical:   ATtiny85 DIP-8 holes, LED hole, ISP header holes
```

-----

## Reviewing Gerbers Before Uploading: Free Gerber Viewers 🔍

Always review your Gerbers before uploading. Two good free options:

**Option 1: AISLER’s online preview (during upload)**

When you upload to AISLER, they show you a rendered preview before you confirm the order. Look for:

- Board outline is the right shape
- All pads are visible and correctly positioned
- Silkscreen text is readable
- Touch pad appears as an exposed copper area (no mask)

**Option 2: Tracespace.io (free online Gerber viewer)**

```
1. Go to tracespace.io/view
2. Drag all Gerber files from et-finger-gerbers/ onto the viewer
3. The viewer renders each layer in colour
4. Toggle layers on/off to verify:
   - Copper traces connect correctly
   - No missing traces (zoom in on each connection)
   - Board outline is correct shape
   - Drill holes are in the right positions
```

**What to look for in the preview:**

```
✓ ATtiny85 DIP-8 footprint: 8 holes in two rows of 4, spacing 2.54mm
✓ LED 5mm: two holes for anode and cathode, 2.54mm spacing
✓ ISP header: 6 holes in 2×3 grid, 2.54mm pitch
✓ CR2032 holder: SMD pads on bottom layer, correct size
✓ Touch pad: an 8×8mm area of exposed copper at board top
✓ Silkscreen: "E.T. FINGER v1.0" text on top layer
✓ Board outline: correct 26×22mm shape with rounded corners
✓ No traces disappearing or connecting to wrong pads
```

-----

## Uploading to AISLER: The Order Process 🛒

### Step 1: Start a New Project

```
Go to: aisler.net
Click: "Start Project"
  (or: aisler.net/p/new for the direct upload page)
```

### Step 2: Upload the File

AISLER accepts:

- `.fzz` files directly (Fritzing format)
- Gerber ZIP files
- Other EDA formats (KiCad, Eagle, etc.)

```
Upload options:
  → Drag and drop et-finger-gerbers.zip onto the upload area
  OR → Click "Upload" and select et-finger-gerbers.zip
  OR → Upload et-finger.fzz directly (AISLER converts for you)
```

### Step 3: Review the Preview

AISLER shows a 3D-rendered preview of your board. Check:

- Board shape matches your design (26×22mm)
- Top layer shows component pads and traces
- Silkscreen shows your labels
- No obvious errors (missing layers, wrong scale)

### Step 4: Configure the Order

```
Board specifications:
  Layers:            2 (minimum — our design uses both layers)
  Surface finish:    HASL (Hot Air Solder Level) — standard, affordable
                     → Choose HASL for through-hole-heavy boards
                     → Choose ENIG (gold) if you want better touch pad quality
                     
  Copper weight:     35 µm (standard)
  Board thickness:   1.6 mm (standard)
  Colour:            Green (standard) — or black for dramatic look!
  Silkscreen:        White
  
Quantity:
  AISLER minimum order: 3 boards
  Price for 3 boards:   Starting at €12.20 for up to ~100 cm²
  Our board area:        26 × 22 mm = 5.72 cm² — well within 100 cm² per set
```

**For E.T.’s Finger — board colour recommendation:**

```
Green: Standard, familiar, easy to solder
Black: Very dramatic — the amber LED pops against dark green/black
Blue:  Looks futuristic, also beautiful with amber LED

Recommendation: Black soldermask with white silkscreen.
  The amber LED glow against the dark board is closest to
  E.T.'s original aesthetic — warm light in darkness.
```

### Step 5: Check the Price

At time of writing (2025/2026):

```
AISLER Beautiful Boards pricing:
  3 boards, ≤100 cm², 2-layer, 1.6mm, HASL, standard colours:
  Starting at: €12.20 + shipping
  
  Shipping to Netherlands/Germany: often free or included
  Shipping worldwide: available at additional cost
  
  Delivery time:
    Manufacturing:  1 business day
    Shipping:       1–3 days within Europe
    Total:          2–4 days from order to your door
```

### Step 6: Add to Cart and Check Out

```
Click "Add to Cart"
Create an account if you don't have one
    (email + password — GDPR compliant, hosted in Germany)
Fill in shipping address
Select shipping method
Enter payment (credit card, PayPal, etc.)
Complete order → Confirmation email sent
```

-----

## What Happens After You Click Order 🏭

Behind the scenes, AISLER’s manufacturing process:

```
Day 1 - Manufacturing:
  1. Gerber files → CNC imaging machine → UV-expose copper-clad board
  2. Chemical etching → removes unwanted copper, leaves traces
  3. Drilling → CNC drill through all hole positions
  4. Surface finish → HASL: tin-lead or lead-free solder applied
  5. Solder mask → UV-cure green/black lacquer over copper
  6. Silkscreen → inkjet white labels and outlines
  7. Board separation → router cuts out individual boards from panel
  8. Visual inspection + electrical test → beep test

Day 1–2 - Shipping:
  9. Boards packed and shipped
  10. Tracking email sent

Day 2–4 - Delivery:
  11. Your boards arrive
  12. Open the package very carefully (boards can be sharp!)
```

-----

## While You Wait: Prepare the Components 🛍️

While AISLER manufactures the PCB, order the components. The complete BOM with recommended suppliers:

```
Component       Value         Supplier (example)       Approx cost
──────────────  ───────────   ──────────────────────   ──────────────
ATtiny85-20PU   DIP-8 MCU     Mouser / Digikey / TME   €1.20 each
Amber LED 5mm   590 nm, 20mA  Any LED supplier          €0.10 each
R1              1 MΩ 1/4W     Any resistor set          €0.02
R2              10 kΩ 1/4W    Any resistor set          €0.02
R3              47 Ω 1/4W     Any resistor set          €0.02
C1              100 nF 50V    Any capacitor set         €0.05
CR2032 holder   SMD, Keystone Any electronics supplier  €0.50 each
ISP header      6-pin 2.54mm  Any header strip          €0.20
CR2032 battery  3V            Supermarket / online      €0.50 each

Total components per unit: ~€2.60
Total for 3 units (matching 3 PCBs): ~€8
PCB (3 boards): ~€12.20
TOTAL PROJECT COST: ~€20–25
```

**Where to buy in the Netherlands (AISLER ships from Europe):**

- **TinkerParts.nl** — Dutch maker supplier
- **Mouser.nl** — Professional component distributor
- **Conrad.nl** — Electronics retail
- **AISLER Simple Supply** — AISLER also sells components!

-----

## A Note on the Touch Pad Surface Finish 🖐️

The touch pad is exposed copper on the PCB. Over time, copper oxidises and the sensitivity may decrease.

**Options to improve long-term touch pad quality:**

```
1. ENIG surface finish on the board
   → Gold-plated pads never oxidise
   → Add ~€5 to the board cost from AISLER
   → Best choice if you plan to use the device regularly

2. HASL (standard)
   → Tin-plated pads — oxidises slowly over months
   → Fine for prototyping and occasional use
   → Cheaper

3. After assembly: thin layer of clear nail varnish over touch pad
   → Protects copper from oxidation
   → Slightly reduces sensitivity (test with firmware threshold)
   → Free fix for HASL boards
```

-----

## What’s Next: Assembly! 🔧

*The boards are in the post. The components are on the workbench. The soldering iron is heating up.*

In **Episode 7**, the PCBs arrive and we assemble them: the ATtiny85 into its DIP-8 socket, the LED, the resistors, the capacitor, the ISP header, and the CR2032 holder on the back. We will walk through each solder joint, discuss through-hole soldering technique for small boards, and end with a board ready for programming.

*We’re coming home, E.T. We’re almost home.*

-----

**🔗 Resources**

- **AISLER new project**: [aisler.net/p/new](https://aisler.net/p/new)
- **AISLER design rules**: [community.aisler.net/t/pcb-design-rules/41](https://community.aisler.net/t/pcb-design-rules/41)
- **AISLER Fritzing integration**: [community.aisler.net/t/fritzing/89](https://community.aisler.net/t/fritzing/89)
- **Gerber viewer**: [tracespace.io/view](https://tracespace.io/view)

-----

*🔴 E.T.’s Finger build by Fritzing and Aisler — from breadboard to fingertip, one glowing episode at a time.*
