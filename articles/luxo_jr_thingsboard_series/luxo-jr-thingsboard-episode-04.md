---
title: "Luxo Jr. ThingsBoard 🎬 Ep.4"
part: 4
published: false
description: "Episode 4: The director needs to see every prop’s state at a glance. ThingsBoard Dashboards are the prompt book — time-series charts, value gauges, alarm tables, maps, and control widgets, all wired to your device telemetry."
tags: [iot, thingsboard, dashboard, homeautomation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/stage-props-thingsboard-episode-04.png"
series: "Luxo Jr. ThingsBoard Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 4: The Prompt Book

> *“The director always has the script, the cue sheet, and the prop list in front of them. Without those, the production is chaos.”*

-----

## The Director’s View 🎬

In a stage production, the director and stage manager work from a **prompt book** — the master reference document that maps what happens where, when, and why. Every lighting cue, every prop entrance, every sound effect is listed. At a glance, you can see the entire state of the production.

ThingsBoard **Dashboards** are the prompt book. They give the director — the operator, the building manager, the homeowner — a single view of everything happening on the stage: current temperatures, brightness levels, active alarms, device status, historical charts. Real-time and live-updating.

In Episode 3, Luxo Jr. started speaking. Now we build the panel where the director hears the conversation.

-----

## 🗂️ SIPOC — The Prompt Book

|**Suppliers**                          |**Inputs**                                      |**Process**                                                               |**Outputs**                                                        |**Customers**                                                              |
|---------------------------------------|------------------------------------------------|--------------------------------------------------------------------------|-------------------------------------------------------------------|---------------------------------------------------------------------------|
|ThingsBoard telemetry storage          |Time-series data from all devices               |Dashboard → add widgets → configure datasources → wire to device telemetry|Live-updating visual dashboard: gauges, charts, maps, tables       |Operators who monitor; managers who review; customers who get shared view  |
|Device attributes                      |Static properties (location, thresholds, labels)|Attribute widgets show fixed context alongside dynamic telemetry          |Cards showing device details, location maps, configuration panels  |Support teams needing full device context                                  |
|Alarm engine (Episode 5)               |Active alarms from all entities                 |Alarm table widget — shows, acknowledges, clears alarms                   |Unified alarm management panel for all devices                     |On-call teams; building managers; the director calling for immediate action|
|Shared dashboards (customer assignment)|Device data, access controls                    |Assign dashboard to customer → customer views only their data             |A customer-facing portal — clean, scoped, no admin controls visible|Your clients, tenants, end-users                                           |

-----

## The Dashboard Anatomy 🎨

A ThingsBoard Dashboard is a canvas divided into a grid. On that canvas you place **Widgets** — the individual display elements. Each widget:

- Has a **type** (chart, gauge, table, map, card, button, etc.)
- Has one or more **datasources** (which entities’ telemetry or attributes to display)
- Has **settings** (time window, thresholds, colours, labels)

The canvas supports multiple **States** (like scenes in a play) — clicking a device in an entity table can navigate to a detailed view of that device, creating drill-down navigation through your entity hierarchy.

-----

## Creating Your First Dashboard 📋

1. Navigate to **Dashboards** in the left menu
1. Click **+** → **Create new dashboard**
1. Name: `Luxo Jr. Stage Monitor`
1. Click **Open dashboard** → click the **pencil/edit** icon to enter edit mode
1. You are now on the canvas. Click **Add widget**

-----

## The Widget Library: Stage Lighting Effects 🎭

ThingsBoard ships a rich widget library. Here are the most useful categories for a stage monitor:

### Cards — The “State at a Glance” Board

**Simple card** / **Value card** — shows the current value of one telemetry key. Perfect for “Current Temperature: 24.5°C” or “Brightness: 800 lux”.

Add a Value Card:

1. **Add widget** → **Cards** → **Simple Card** (or **Value Card**)
1. Datasource: **Device** → select `Luxo Jr. Lamp`
1. Data key: `ambientTemp`
1. Label: `Ambient Temperature`
1. Unit: `°C`
1. Advanced: set alarm thresholds for colour change (green → orange → red)

### Time-Series Charts — The Performance History

Shows telemetry over time. Multiple keys on one chart. Essential for understanding trends.

Add a Time-Series Chart:

1. **Add widget** → **Charts** → **Line chart** (or **Time-series chart**)
1. Datasource: Device → `Luxo Jr. Lamp`
1. Data keys: `ambientTemp`, `powerWatts` (add multiple)
1. Set time window: Last 24 hours (adjustable by user)
1. Y-axis labels, legend, colour customisation available

### Gauges — The Dial on the Lamp

An analog or digital gauge widget shows a value within a defined min/max range. Perfect for brightness (0–1000 lux), temperature (0–40°C), or power consumption.

Add an Analog Gauge:

1. **Add widget** → **Gauges** → **Analogue Gauge** or **Radial Gauge**
1. Datasource: `brightness`
1. Min: 0, Max: 1000
1. Set arc colours for zones (green/amber/red)

### Entity Table — The Cast List

Shows a table of multiple devices with their latest telemetry values. The stage director’s at-a-glance cast list.

Add an Entity Table:

1. **Add widget** → **Entity widgets** → **Entities table**
1. Datasource type: **Entity list** or **Entity group** or **Asset entity** (all devices in a room)
1. Columns: Name, `ambientTemp`, `brightness`, `lampOn`, `powerWatts`

When configured to an Asset datasource (e.g., Floor 4), the table automatically shows every device in that floor’s hierarchy — no manual device selection.

### Alarm Table — The Stage Manager’s Crisis List

Shows active alarms across all your entities. Supports acknowledge and clear actions directly from the dashboard.

Add an Alarms Table:

1. **Add widget** → **Alarm widgets** → **Alarms table**
1. Configure: show all alarms for the current time window
1. Columns: Device, Alarm Type, Severity, Status, Time
1. Enable acknowledge and clear actions

### Map — Where the Props Are 📍

For geographically distributed deployments (or a multi-room home), a map widget shows device locations as pins, colour-coded by alarm status.

Add a Map widget:

1. **Add widget** → **Maps** → **OpenStreetMap** or **Image map**
1. For geographic: set device server-side attributes `latitude` and `longitude`
1. For floor plan: use an Image Map widget with a floor plan image — devices appear as pins

### Control Widgets — The Director Calls Action 🎬

Control widgets send RPC commands to devices from the dashboard. A button, slider, or toggle.

Add a Control Button:

1. **Add widget** → **Control widgets** → **Round button** or **Switch control**
1. Select device: `Luxo Jr. Lamp`
1. RPC method: `setBrightness`
1. Default value / parameters: `{"brightness": 100}`
1. Confirm dialogs, success/fail handling available

Now the dashboard has a button. Click it → RPC fires → device receives `setBrightness({brightness: 100})` → lamp adjusts → telemetry confirms new value.

-----

## Dashboard States — Scene Changes 🎭

A dashboard with many devices benefits from drill-down navigation. ThingsBoard **Dashboard States** implement this as named “scenes” the user navigates between.

**State 1 — Overview**: Entity table showing all devices. Click a row → navigate to device detail.

**State 2 — Device Detail**: Detailed charts and gauges for the selected device. A back button returns to Overview.

### Creating States

1. In edit mode: click the state icon (top right of dashboard editor)
1. Click **+** to add a state
1. Name it (e.g., `device_detail`)
1. Add widgets to this state (detailed charts for one device)

### Navigation between states

On the Overview entity table, add an **Action** to rows:

1. Edit the Entity Table widget → **Actions** tab
1. **Row click** → Action type: **Navigate to new dashboard state**
1. Target state: `device_detail`
1. Pass entity ID as a state parameter — the detail view uses this to show the clicked device’s data

The prompt book now has chapters, and the director navigates between them by clicking on the cast list.

-----

## Time Window Control ⏱️

Every dashboard has a **time window selector** — the period of history the time-series widgets display. Default: last hour. Users can change it to last 24 hours, last 7 days, or a custom range.

In edit mode, you can set a **default time window** per dashboard, and configure whether users can change it (useful for customer-facing dashboards where you want a fixed view).

-----

## Sharing the Dashboard with Customers 👥

A dashboard can be assigned to a Customer. The customer’s users see only the dashboard and its data — no admin interface, no other tenants’ devices.

1. Dashboard → click the share icon
1. Select customer
1. The customer receives a login and sees only their assigned dashboards

For a smart home bridged from HA: a customer user (e.g., Rianne) could get a read-only dashboard showing the home’s device states and alarm history — the “what is happening in the house right now” view, without ThingsBoard admin access.

-----

## A Sample Home Dashboard Layout 🏠

For the Home Assistant integration (Episode 7), here is a suggested dashboard layout:

**State 1 — Home Overview:**

- Entity table: all rooms, showing latest temperature, humidity, alarm status
- Card row: current alarms (count), active devices, home mode (armed/away/home)
- Map widget: floor plan with device pins, colour by alarm status

**State 2 — Room Detail** (navigated to by clicking a room):

- Value cards: temperature, humidity, occupancy
- Time-series chart: temperature last 24 hours
- Device list: all HA entities in this room
- Alarm table: alarms for this room’s devices

**State 3 — Device Detail** (navigated to by clicking a device):

- All telemetry as charts (full history)
- All attributes as a card
- Alarm history table
- Control widgets (if the device accepts RPC)

-----

In **Episode 5**, we give the prompt book reactive intelligence — the Rule Engine. When the temperature crosses a threshold, the book does not just display a red value. It sends an email. It triggers a sound cue. It logs the event. The director does not need to watch continuously — the stage manages itself.

-----

**🔗 Resources**

- **Dashboards overview**: [thingsboard.io/docs/user-guide/dashboards](https://thingsboard.io/docs/user-guide/dashboards/)
- **Widget library**: [thingsboard.io/docs/user-guide/ui/widget-library](https://thingsboard.io/docs/user-guide/ui/widget-library/)
- **Dashboard states**: [thingsboard.io/docs/user-guide/ui/advanced-data-key-configuration](https://thingsboard.io/docs/user-guide/ui/advanced-data-key-configuration/)

-----

*🎬 Stage Props! is a series about ThingsBoard — the IoT platform that gives your devices joints, personality, and behaviour.*
