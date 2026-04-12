-----

## title: “Stage Props! 🎬 Ep.6: Animating the Lamp”
published: false
description: “Episode 6: Lasseter built Luxo Jr. over months. ThingsBoard’s AI Solution Creator builds your entire IoT prototype — entity profiles, dashboards, alarm rules, user roles — in under 10 minutes from a plain-language description.”
tags: [iot, thingsboard, ai, homeautomation]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/stage-props-thingsboard-episode-06.png”
series: “Stage Props!”
canonical_url: “”
organization: “the-software-s-journey”

# Stage Props! 🎬

## Episode 6: Animating the Lamp

> *“Lasseter spent months modelling joints, testing motion curves, iterating on the character. Then he showed it at SIGGRAPH and the audience forgot it was a lamp in under two minutes.”*
> *“The AI Solution Creator spends 10 minutes understanding your IoT requirements and then produces the same result.”*

-----

## The Setup Tax 💸

Episodes 2 through 5 covered the honest reality of an IoT deployment: define entities, build the hierarchy, connect devices, design dashboards, wire alarm rules, configure notifications. Every piece has value. Every step is necessary.

But there is a problem. The problem has a name in the ThingsBoard blog post that prompted this episode: **the setup tax**.

Before you see a single data point, someone has to manually define equipment and assets, design user interfaces from scratch, and build the logic to handle alerts. For a developer, this is repetitive. For a business stakeholder, it is a barrier to entry. For a system integrator trying to win a bid, it is days lost before any demo is possible.

ThingsBoard’s **AI Solution Creator** eliminates the setup tax. It is not a template gallery or a wizard — it is an *intelligent agent* that reads your intent, asks clarifying questions, proposes a complete architecture, and then provisions the entire solution in one pass.

Lasseter gave Luxo Jr. personality over months. You describe what you want in plain language, and the AI Solution Creator gives it to you in ten minutes.

-----

## 🗂️ SIPOC — Animating the Lamp

|**Suppliers**                                            |**Inputs**                                       |**Process**                                                                                                       |**Outputs**                                                                                             |**Customers**                                                                    |
|---------------------------------------------------------|-------------------------------------------------|------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
|You (business stakeholder / system integrator / explorer)|A plain-language description of your IoT use case|AI Solution Creator Step 1: Architecture Design → AI proposes entity profiles, IAM, calculated fields, alarm rules|A visual entity hierarchy schema ready for review and adjustment                                        |You, reviewing and accepting or adjusting before anything is built               |
|You (approving the architecture)                         |Your feedback or approval                        |Step 2: Dashboard Design → AI proposes dashboard layouts, drill-down flows, user role visibility                  |Dashboard specifications showing what each persona sees                                                 |You, confirming the operator/customer/admin view meets requirements              |
|Your approval                                            |“Create Solution” click                          |Step 3: Solution Installation → AI provisions everything in one atomic pass                                       |Live entities, roles, permissions, dashboards, alarm rules, and demo data emulators — all wired together|You, able to log in as any user role and see the solution functioning immediately|

-----

## What the AI Solution Creator Actually Builds 🏗️

The blog post lists six outputs. Let us map each to the stage props metaphor:

|What it builds                 |Stage props equivalent                                              |Episodes covered manually      |
|-------------------------------|--------------------------------------------------------------------|-------------------------------|
|**Asset & Equipment Mapping**  |The set is designed — Building → Floor → Room → Device hierarchy    |Episode 2                      |
|**User Access (IAM)**          |The cast list — who sees which dressing room                        |Episode 2 (Customer assignment)|
|**Visual Dashboards**          |The prompt book — drill-down from overview to device detail         |Episode 4                      |
|**Real-Time Insights & Alarms**|The cue sheet — automated reactions to thresholds                   |Episode 5                      |
|**Calculated Metrics**         |Shadow maps — derived values from raw telemetry                     |Episode 5                      |
|**Live Simulation (Demo Data)**|Rehearsal with stand-ins — realistic data before real devices arrive|*(covered in this episode)*    |

In under 10 minutes. Without manual configuration of any of it.

-----

## The Three Steps 🎬

### Step 1 — Architecture Design: Tell the AI What You’re Building

Navigate to the AI Solution Creator (available on ThingsBoard Cloud — US or EU). You see a chat interface.

Describe your use case in plain language. The richer your description, the better the output:

**Minimal description (the AI will ask follow-up questions):**

```
I want to monitor temperature sensors in a building.
```

**Rich description (fewer follow-up questions, better results):**

```
I manage a 3-floor office building with 15 rooms per floor. Each room has a 
temperature sensor and a humidity sensor. Facilities managers need a building 
overview dashboard. Floor managers see their own floor. The system should alert 
facilities when temperature exceeds 28°C or humidity exceeds 75% for more than 
5 minutes. I also need to track average energy consumption per floor using 
smart meters.
```

The AI responds with a **proposed architecture** broken into four sections:

**Entity Profiles** — the set design:

```
Assets:
  - Building (1 instance: "Office Building")
  - Floor (3 instances: Floor 1, Floor 2, Floor 3)
  - Room (45 instances, 15 per floor)

Devices:
  - Temperature Humidity Sensor (90 instances, 2 per room)
  - Smart Energy Meter (3 instances, 1 per floor)

Device Profiles:
  - TH Sensor Profile (transport: MQTT, alarm rules configured)
  - Energy Meter Profile (transport: HTTP)
```

**IAM (Identity and Access Management)** — the cast list:

```
Roles:
  - Facilities Manager: sees all floors, all alarms, global dashboard
  - Floor Manager: sees only their assigned floor and its rooms/devices
  - Readonly User: view-only access to assigned dashboards
```

**Calculated Fields** — the shadow maps:

```
- avg_floor_temp: average temperature across all rooms on a floor
- total_floor_power: sum of smart meter readings per floor
- comfort_index: derived from temperature + humidity combination
```

**Alarm Rules** — the cue sheet:

```
- High Temperature: temperature > 28°C for 5 minutes → MAJOR alarm
- High Humidity: humidity > 75% for 5 minutes → MAJOR alarm  
- Combined Discomfort: temperature > 26°C AND humidity > 70% → WARNING
- Sensor Offline: no data received for 10 minutes → CRITICAL alarm
```

You can view the complete entity hierarchy in a **visual schema** — a diagram of the full set design. Review, adjust in plain language, and confirm.

### Step 2 — Dashboard Design: What the Prompt Book Looks Like

The AI immediately proposes the dashboards:

```
Dashboard 1: Building Overview (Facilities Manager role)
  - Entity table: all floors with avg_floor_temp, total_floor_power, alarm count
  - Time-series chart: building-wide temperature trend (last 24h)
  - Alarm table: all active alarms
  - Click a floor → navigate to Floor Detail dashboard

Dashboard 2: Floor Detail
  - Entity table: all rooms on this floor with latest temp/humidity
  - Calculated field cards: avg_floor_temp, total_floor_power
  - Click a room → navigate to Room Detail

Dashboard 3: Room Detail
  - Value cards: current temperature, current humidity, comfort index
  - Time-series charts: temperature and humidity last 24h
  - Alarm history for this room's devices
```

Review, adjust, confirm.

### Step 3 — Solution Installation: Click “Create Solution”

The AI provisions everything:

- Creates all assets (Building, 3 Floors, 45 Rooms)
- Creates all device profiles with alarm rules
- Creates all user roles
- Creates all calculated fields
- Creates all dashboards with drill-down navigation
- Creates device **emulators** — software agents that publish realistic demo data

When it completes, a summary window opens. Your solution is live, populated with realistic demo data, and fully navigable.

-----

## The Demo Data Emulators 🎭

The “rehearsal with stand-ins” feature is one of the most underappreciated capabilities. The AI creates software emulators that publish telemetry matching what real devices would send — correct ranges, realistic variation, occasional threshold breaches that trigger alarms.

This means:

- **Stakeholders can see a working demo immediately** — before a single physical device is deployed
- **Dashboard usability can be evaluated** before the installation phase
- **Alarm logic can be tested** with controlled data
- **Training can happen** on a live system before real devices are connected

When real devices arrive, connect them to the same device profiles. The emulators can be deleted. The dashboards, alarm rules, and entity hierarchy remain — the real devices drop in.

-----

## Pro Tips for Better Results 💡

The AI Solution Creator’s output quality scales directly with input quality. From the ThingsBoard blog:

**Describe your business goals, not just your devices:**

Instead of: *“I have 50 temperature sensors”*

Say: *“I need to ensure food storage temperature stays between 2°C and 8°C in 10 cold storage rooms. A facilities manager and a health inspector need different views. The system must create a CRITICAL alarm and notify the facilities manager within 30 seconds of any room exceeding 10°C.”*

**Specify who needs to see what:**

The AI generates IAM (user roles and permissions) from your description. If you name the personas — facilities manager, floor manager, health inspector, customer, admin — the AI creates distinct roles with appropriate access.

**Describe alarm severity and timing explicitly:**

*“Warning at 27°C for 2 minutes, Critical at 30°C immediately, clear when below 25°C”* produces a much more nuanced alarm rule than *“alert when hot”*.

**Name your calculated metrics:**

*“I need average room temperature per floor, total energy consumption per building per day, and a comfort score combining temperature and humidity”* tells the AI exactly which derived fields to create.

-----

## What the AI Solution Creator Is Not 🚧

The ThingsBoard blog is explicit: this is an **intelligent starting point**, not a finished product. The generated architecture is shaped around your business goals and reflects the team’s experience with large-scale IoT systems. But it is a **foundational architecture**, not a bespoke production deployment.

After the AI creates your solution:

- Connect real devices to the provisioned profiles
- Customise dashboards for your specific screen layouts and user preferences
- Refine alarm thresholds based on real operational data
- Add integration-specific rule chain nodes (Kafka, REST webhooks, external APIs)
- Configure backup, monitoring, and security hardening for production

The AI animates the lamp. You are the director who gives the performance its final shape.

-----

## Using AI Solution Creator for a Smart Home PoC 🏠

The AI Solution Creator is not only for industrial deployments. A smart home PoC for a Home Assistant integration (Episode 7):

```
I have a home with 6 rooms managed by Home Assistant. I want to mirror 
all HA sensor data into ThingsBoard for richer visualization and alerting. 
I need:
- A home overview dashboard showing all rooms
- Temperature and humidity history for each room  
- An alert when any room exceeds 25°C for 10 minutes
- A separate dashboard for energy monitoring (smart plugs via HA)
- A security section showing door/window sensors and alarm state
- Two user roles: admin (full access) and viewer (read-only, no alarm management)
```

The AI produces a complete home IoT architecture. Then in Episode 7, we connect the MQTT bridge from Home Assistant and real data starts flowing into the generated structure.

-----

In **Episode 7**, the bridge is built. Home Assistant publishes its entity states via MQTT to ThingsBoard. Luxo Jr. and the smart thermostat perform on the same stage.

-----

**🔗 Resources**

- **ThingsBoard AI Solution Creator blog post**: [thingsboard.io/blog/ai-solution-creator](https://thingsboard.io/blog/ai-solution-creator/)
- **ThingsBoard Cloud** (where AI Solution Creator lives): [thingsboard.cloud](https://thingsboard.cloud/signup)
- **EU Cloud**: [eu.thingsboard.cloud](https://eu.thingsboard.cloud/signup)

-----

*🎬 Stage Props! is a series about ThingsBoard — the IoT platform that gives your devices joints, personality, and behaviour.*
