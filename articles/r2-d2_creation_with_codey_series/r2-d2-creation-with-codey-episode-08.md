---
title: "R2D2 Creation with Codey 🤖 Ep.8" 
published: false 
description: "Episode 8: The finale. Every system comes together — dome lights, sensor eye, holographic display, motion, audio voice — all orchestrated by the ESP32-S3 N16R8. Codey's Deep Think mode handles the most complex prompt in the series. Wi-Fi adds a remote command interface. The final complete wiring diagram is drawn, downloaded as PDF, and pinned to the wall. The droid is complete. May the Force be with you." 
tags: [esp32, arduino, ai, makers] 
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/r2-d2_creation_with_codey_series/r2-d2-creation-with-codey-episode-08.png" 
series: "R2-D2 Creation With Codey" 
canonical_url: "" 
organization: "the-software-s-journey" 
part: 8
---
## Episode 8: The Complete Droid

## "The Force Will Be With You. Always." 🌟

*The entire crew stands in the workshop. Han Solo, arms folded. Luke, grinning. C-3PO, hands clasped with barely-contained anxiety. Princess Leia's message loops on the OLED — a recreation, text only, but the words are right: "Help me, Obi-Wan Kenobi."*

*And in the centre, dome slowly rotating, blue-white LEDs breathing, speaker playing a quiet ambient whistle — R2-D2.*

**OBI-WAN:** *quietly* "Seven episodes. Seven systems. And now, the droid is nearly complete. There is one thing left — the final integration. The moment when all systems stop running in parallel and begin running as one coherent whole. When R2-D2 stops being a collection of components and becomes the galaxy's greatest droid."

*R2-D2 beeps once. Confident. Ready.*

**OBI-WAN:** "And then — the Force. The Wi-Fi."

*Han Solo snorts.*

**HAN:** "The Wi-Fi. Very mystical."

## 🗂️ SIPOC — The Complete Droid

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (the maker) | "Integrate all systems + add Wi-Fi remote command interface" | Codey Deep Think mode plans the full architecture before writing | A unified state machine with all systems communicating, Wi-Fi endpoint for remote commands | The complete R2-D2 — one firmware, all systems orchestrated |
| ESP32-S3 N16R8 | 16MB Flash, 8MB PSRAM, dual-core, Wi-Fi | Dual-core operation: Core 0 for Wi-Fi/networking, Core 1 for real-time sensor/motor/audio loop | Smooth operation without Wi-Fi blocking the real-time control loop | All R2-D2 systems — none starved of processor time |
| Codey Deep Think mode | Complex multi-file integration prompt | Takes longer to respond — reasons about the whole architecture first | The cleanest, most architecturally coherent code in the series | Your long-term maintainability |
| Final Wiring Diagram | All 7 systems' component lists | Codey draws the complete master diagram with all connections, protection circuits, and power rails | A single PDF showing the complete R2-D2 build | Your workshop wall — the crown jewel of your build log |

## The Final Component Inventory — Every Piece of R2-D2 🔧

*C-3PO produces a datapad with the air of someone who has been waiting seven episodes to read this list.*

**C-3PO:** "The complete inventory, as accumulated across eight glorious — and at times terrifying — episodes:"

| Component | Episode Added | Purpose |
| --- | --- | --- |
| ESP32-S3 N16R8 | 5 | The brain — all systems connect here |
| SSD1306 OLED 128×64 | 5 | Holographic display — I2C via GPIO8/9 |
| NeoPixel ring 12 LED | 3 | Dome lights — GPIO6 via level shifter |
| HC-SR04 ultrasonic | 4 | Distance sensing eye — GPIO9/10 |
| PIR HC-SR501 | 4 | Motion sensing — GPIO2 (interrupt) |
| SG90 servo | 6 | Dome rotation — GPIO14 via level shifter |
| DC gear motors × 2 | 6 | Wheel drive — via L298N |
| L298N motor driver | 6 | Motor control, also provides 5V rail |
| DFPlayer Mini | 7 | Audio playback — UART2 GPIO16/17 |
| Speaker 4Ω/8Ω | 7 | Voice output |
| microSD card (FAT32) | 7 | Audio files 0001–0007.mp3 |
| 74AHCT125 level shifter | 3/6 | NeoPixel + servo: 3.3V → 5V |
| 470Ω resistor | 3 | NeoPixel data protection |
| 1kΩ resistor | 7 | DFPlayer RX protection |
| 100Ω resistor | — | (buzzer, now removed) |
| 100µF capacitor | 3 | NeoPixel power decoupling |
| 10µF capacitor | 7 | DFPlayer power filtering |
| Voltage dividers (10k+20k) | 5 | HC-SR04 ECHO + PIR output: 5V → 3.3V |
| 9V battery or 2S LiPo | 6 | Motor power rail |
| USB cable | All | Programming + logic power |

**C-3PO:** "R2-D2. In components. On a breadboard. I find this both impressive and somewhat unsettling."

*R2-D2 beeps with what sounds like pride.*

## Deep Think Mode: The Wisest Path 🧠

*Yoda settles into his chair.*

**YODA:** "Complex this prompt is. Many files to touch. Many systems to unify. For this — Deep Think mode you shall use. Longer it takes. Wiser the result."

**LUKE:** "What's Deep Think mode?"

**YODA:** "Plan mode's elder sibling. Not just a plan — a deep analysis of the architecture first. Consider edge cases it will. Identify conflicts between systems it shall. Only then write, it does."

In Codey, click the mode dropdown and select **Deep Think** (Pro feature). Then type the final integration prompt:

```
FINAL R2-D2 INTEGRATION — Deep Think mode

We have these existing header files for the ESP32-S3 N16R8:
  - animations.h  (NeoPixel dome: GPIO6 via 74AHCT125)
  - sensors.h     (HC-SR04: GPIO9 TRIG / GPIO10 ECHO; PIR: GPIO2)
  - display.h     (SSD1306 OLED: I2C SDA=GPIO8 / SCL=GPIO9 — NOTE: conflict!)
  - motion.h      (Servo: GPIO14; L298N: GPIO25-27, GPIO32-34)
  - voice.h       (DFPlayer Mini: UART2 TX=GPIO17 / RX=GPIO16)
  - sounds.h      (LEDC buzzer: now removed, GPIO freed)

CONFLICT TO RESOLVE:
  HC-SR04 TRIG uses GPIO9. OLED I2C SCL also uses GPIO9.
  These cannot share! Remap one of them.
  Suggestion: Move HC-SR04 TRIG to GPIO11, ECHO to GPIO12.
  Update sensors.h and the wiring diagram accordingly.

NEW FEATURE — Wi-Fi remote control:
  Use ESP32-S3 Wi-Fi to create a simple HTTP server.
  Endpoints:
    GET /status    → JSON with distance, motion, dome angle, current sound
    GET /command/forward   → drive forward for 2 seconds
    GET /command/backward  → drive backward for 2 seconds
    GET /command/left      → turn left for 1 second
    GET /command/right     → turn right for 1 second
    GET /command/stop      → stop motors immediately
    GET /command/sound/N   → play sound N (1-7)
    GET /command/dome/N    → move dome to angle N degrees

  Use WiFiAP mode (R2-D2 creates its own access point):
    SSID: "R2-D2"
    Password: "beepboop"
  
  Run HTTP server on Core 0. Real-time systems on Core 1.
  
FINAL r2d2-main.ino:
  - Resolve the GPIO conflict
  - Add wifi.h header for Wi-Fi + HTTP server
  - Clean unified loop with clear comments
  - All systems operational
  - Serial output at 115200 showing all state transitions

Please think through the architecture fully before writing.

```

### Deep Think Mode Analysis (Codey Responds)

```
[Deep Think analysis in progress...]

Architecture review:

1. GPIO CONFLICT IDENTIFIED:
   GPIO9 cannot serve both HC-SR04 TRIG and I2C SCL.
   Resolution: Remap I2C to SDA=GPIO4, SCL=GPIO5 (available on ESP32-S3).
   This avoids touching sensors.h; only display.h changes:
     Wire.begin(4, 5) instead of Wire.begin(8, 9).

2. DUAL-CORE STRATEGY:
   Core 0 (Arduino default): Wi-Fi, HTTP server, WebServer library
   Core 1 (pinned task): sensor reading, NeoPixel, servo, display, audio
   Separation prevents Wi-Fi TCP/IP stack from blocking 50Hz servo updates.
   Implementation: xTaskCreatePinnedToCore() for real-time loop.

3. STATE MACHINE:
   Unified DomeState enum: IDLE, SCAN, ALERT, DANGER, REMOTE_CONTROL
   REMOTE_CONTROL state: Wi-Fi command overrides sensor-driven behavior.
   Auto-return to IDLE after 5 seconds of no remote command.

4. MEMORY:
   16MB Flash — no concern.
   8MB PSRAM — HTTP response buffers can use ps_malloc() if needed.
   RAM: estimated ~68KB used (20.8% of 327KB) — safe.

5. POWER:
   Wi-Fi radio: ~240mA peak. USB 500mA should be sufficient for ESP32-S3.
   Motors: separate 9V rail — no impact on ESP32 power.

Generating files now...

```

### Generated `wifi.h`

```cpp
// wifi.h — R2-D2 Wi-Fi Remote Control
// ESP32-S3 Access Point: SSID "R2-D2", password "beepboop"
// HTTP server on port 80 — runs on Core 0

#pragma once
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

const char* AP_SSID     = "R2-D2";
const char* AP_PASSWORD = "beepboop";
const int   HTTP_PORT   = 80;

WebServer server(HTTP_PORT);

// Shared state (volatile — accessed from both cores)
volatile float  sharedDistance    = 999.0f;
volatile bool   sharedMotion      = false;
volatile int    sharedDomeAngle   = 90;
volatile bool   remoteCommandPending = false;
volatile String remoteCommand     = "";

// ── Status endpoint ──────────────────────────────────────────────
void handleStatus() {
  StaticJsonDocument<256> doc;
  doc["distance_cm"] = sharedDistance;
  doc["motion"]      = sharedMotion;
  doc["dome_angle"]  = sharedDomeAngle;
  doc["state"]       = "online";
  doc["uptime_s"]    = millis() / 1000;

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
  Serial.println("[WiFi] GET /status");
}

// ── Command endpoints ────────────────────────────────────────────
void handleCommand() {
  String path    = server.uri();      // e.g. "/command/forward"
  String command = path.substring(9); // strip "/command/"
  remoteCommand        = command;
  remoteCommandPending = true;
  server.send(200, "text/plain", "ACK: " + command);
  Serial.print("[WiFi] Command: ");
  Serial.println(command);
}

// ── Root page (simple UI) ─────────────────────────────────────────
void handleRoot() {
  String html = R"rawhtml(
<!DOCTYPE html>
<html>
<head><title>R2-D2 Control</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body { font-family:sans-serif; background:#111; color:#4af;
         display:flex; flex-direction:column; align-items:center; }
  h1 { color:#4af; }
  button { background:#1a3a5a; color:#4af; border:2px solid #4af;
           padding:14px 28px; font-size:1.1em; margin:6px;
           border-radius:6px; cursor:pointer; }
  button:active { background:#4af; color:#111; }
  #status { margin-top:16px; font-size:0.9em; color:#aaa; }
</style></head>
<body>
<h1>R2-D2</h1>
<div>
  <button onclick="cmd('sound/5')">🔊 Startup</button>
  <button onclick="cmd('sound/1')">😄 Happy</button>
  <button onclick="cmd('sound/3')">😢 Sad</button>
</div>
<div>
  <button onclick="cmd('forward')">▲ Forward</button>
</div>
<div>
  <button onclick="cmd('left')">◄ Left</button>
  <button onclick="cmd('stop')">■ Stop</button>
  <button onclick="cmd('right')">► Right</button>
</div>
<div>
  <button onclick="cmd('backward')">▼ Backward</button>
</div>
<div>
  <button onclick="cmd('dome/0')">Dome ◄</button>
  <button onclick="cmd('dome/90')">Dome ●</button>
  <button onclick="cmd('dome/180')">Dome ►</button>
</div>
<div id="status">Connecting...</div>
<script>
function cmd(c) {
  fetch('/command/'+c).then(r=>r.text()).then(t=>{
    document.getElementById('status').textContent = 'Last: '+c;
  });
}
setInterval(()=>{
  fetch('/status').then(r=>r.json()).then(d=>{
    document.getElementById('status').textContent =
      'Dist: '+d.distance_cm.toFixed(0)+'cm | Motion: '+d.motion+
      ' | Uptime: '+d.uptime_s+'s';
  });
}, 2000);
</script>
</body></html>
)rawhtml";
  server.send(200, "text/html", html);
}

// ── Init Wi-Fi + HTTP server (call from Core 0 task) ─────────────
void initWifi() {
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  Serial.print("[WiFi] AP started: ");
  Serial.println(AP_SSID);
  Serial.print("[WiFi] IP: ");
  Serial.println(WiFi.softAPIP());

  server.on("/",          handleRoot);
  server.on("/status",    handleStatus);
  server.onNotFound([]() {
    // Any /command/* path
    if (server.uri().startsWith("/command/")) handleCommand();
    else server.send(404, "text/plain", "Not found");
  });

  server.begin();
  Serial.println("[WiFi] HTTP server started — connect to R2-D2 network");
}

// ── Core 0 task: runs Wi-Fi server continuously ──────────────────
void wifiTask(void* param) {
  initWifi();
  for (;;) {
    server.handleClient();
    vTaskDelay(1); // yield to RTOS — must not block Core 0
  }
}

```

### Final `r2d2-main.ino`

```cpp
// r2d2-main.ino — R2-D2 COMPLETE
// ESP32-S3 N16R8 | All systems operational
// Core 0: Wi-Fi + HTTP server
// Core 1: Sensors, display, NeoPixel, servo, motors, audio

#include <Adafruit_NeoPixel.h>
#include "animations.h"   // NeoPixel dome: GPIO6
#include "sensors.h"      // HC-SR04: GPIO9(TRIG) GPIO10(ECHO); PIR: GPIO2
#include "display.h"      // OLED I2C: SDA=GPIO4 SCL=GPIO5 (CONFLICT RESOLVED)
#include "motion.h"       // Servo: GPIO14; L298N: GPIO25-27, GPIO32-34
#include "voice.h"        // DFPlayer: UART2 GPIO16/17
#include "wifi.h"         // Wi-Fi AP + HTTP server

TaskHandle_t realtimeTask;   // Core 1 handle

// ── Remote command processor ─────────────────────────────────────
void processRemoteCommand(const String& cmd) {
  if      (cmd == "forward")   motorForward();
  else if (cmd == "backward")  motorBackward();
  else if (cmd == "left")      motorTurnLeft();
  else if (cmd == "right")     motorTurnRight();
  else if (cmd == "stop")      motorStop();
  else if (cmd.startsWith("sound/")) {
    int n = cmd.substring(6).toInt();
    if (n >= 1 && n <= 7) playSound((R2Sound)n);
  }
  else if (cmd.startsWith("dome/")) {
    int angle = cmd.substring(5).toInt();
    domeSnap(constrain(angle, 0, 180));
  }
}

unsigned long lastRemoteCmdMs     = 0;
const unsigned long REMOTE_TIMEOUT = 5000; // return to autonomous after 5s

// ── Core 1: real-time loop ───────────────────────────────────────
void realtimeLoop(void* param) {
  // Init all real-time systems on Core 1
  initAnimations();
  initSensors();
  initDisplay();
  initMotion();
  initVoiceSystem();

  for (;;) {
    if (!bootDone) { showBootScreen(); vTaskDelay(10); continue; }

    float dist   = readDistance();
    bool  motion = checkMotion();

    // Share state with Wi-Fi (Core 0 reads these)
    sharedDistance  = dist;
    sharedMotion    = motion;
    sharedDomeAngle = currentDomeAngle;

    // ── Remote command takes priority ──────────────────────────
    bool remoteActive = (millis() - lastRemoteCmdMs < REMOTE_TIMEOUT);

    if (remoteCommandPending) {
      String cmd = remoteCommand;
      remoteCommandPending = false;
      processRemoteCommand(cmd);
      lastRemoteCmdMs = millis();
      remoteActive    = true;
    }

    // ── Autonomous behaviour (when no remote command) ─────────
    if (!remoteActive) {
      if (dist < 30.0f) {
        domeSnap(90);
        motorStop();
      } else if (motion) {
        domeSnap(45);
      } else {
        domeIdleSweep();
      }
    }

    // ── Display + lights + voice (always) ─────────────────────
    if (dist < 15.0f)    showAlertScreen();
    else if (motion)     showMotionScreen();
    else                 showIdleScreen(dist);

    updateAnimationsSensors(dist, motion);
    updateVoice(dist, motion, currentState);

    vTaskDelay(10); // 10ms tick — 100Hz loop
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("╔═══════════════════════════════╗");
  Serial.println("║   R2-D2 — COMPLETE BUILD      ║");
  Serial.println("║   ESP32-S3 N16R8              ║");
  Serial.println("╚═══════════════════════════════╝");

  // Start Wi-Fi server on Core 0
  xTaskCreatePinnedToCore(
    wifiTask,       // function
    "WiFiTask",     // name
    8192,           // stack size (bytes)
    NULL,           // parameter
    1,              // priority
    NULL,           // task handle
    0               // core: 0
  );

  // Start real-time loop on Core 1
  xTaskCreatePinnedToCore(
    realtimeLoop,   // function
    "RTLoop",       // name
    8192,           // stack size
    NULL,           // parameter
    2,              // priority (higher than Wi-Fi)
    &realtimeTask,  // task handle
    1               // core: 1
  );

  // Arduino loop() runs on Core 1 by default — we've moved everything
  // to FreeRTOS tasks, so loop() is intentionally empty.
}

void loop() {
  vTaskDelay(portMAX_DELAY); // yield forever — all work done in tasks
}

```

## The Final Master Wiring Diagram 🧭

*C-3PO takes a deep breath and presents the complete diagram with a formality appropriate to the occasion.*

**C-3PO:** "The final wiring diagram. Every component. Every wire. Every protection circuit. Every power rail. Downloadable as PDF. Printable. Frameable. I am... genuinely proud of this."

```
R2-D2 COMPLETE BUILD — Master Wiring Diagram
ESP32-S3 N16R8 | All Systems
════════════════════════════════════════════════════════════════════

POWER RAIL 1 — LOGIC (USB 5V regulated to 3.3V by ESP32-S3):
  USB 5V → ESP32-S3 VIN
  ESP32 3V3 output → (nothing external — 3.3V stays internal)
  ESP32 GND → Common GND rail

POWER RAIL 2 — 5V PERIPHERALS (L298N internal regulator from 9V):
  9V Battery (+) → L298N: VS
  9V Battery (−) → GND (common with ESP32 GND!)
  L298N 5V out → Servo VCC (red), 74AHCT125 VCC, DFPlayer VCC
  L298N GND → Servo GND, 74AHCT125 GND, DFPlayer GND

I2C BUS (conflict-resolved: SDA=GPIO4, SCL=GPIO5):
  ESP32 GPIO4 (SDA) ──── OLED SDA
  ESP32 GPIO5 (SCL) ──── OLED SCL
  ESP32 3V3         ──── OLED VCC (via 100µF cap to GND)

NEOPIXEL DOME (5V logic via level shifter):
  ESP32 GPIO6 ──── 74AHCT125 A1 ──── NeoPixel DIN
  L298N 5V    ──── NeoPixel 5V + 100µF cap+
  GND         ──── NeoPixel GND + 100µF cap−
  (470Ω resistor between 74AHCT125 Y1 output and NeoPixel DIN)

HC-SR04 ULTRASONIC (5V sensor, voltage divider on ECHO):
  ESP32 GPIO9  (TRIG) ──────────────── HC-SR04 TRIG
  HC-SR04 ECHO (5V)   ── 10kΩ ──┬──── ESP32 GPIO10
                                 └──── 20kΩ ──── GND

PIR MOTION SENSOR (5V output, voltage divider):
  L298N 5V    ──── PIR HC-SR501 VCC
  GND         ──── PIR HC-SR501 GND
  PIR OUT (5V) ── 10kΩ ──┬──── ESP32 GPIO2
                          └──── 20kΩ ──── GND

SERVO — DOME ROTATION (5V signal via level shifter):
  ESP32 GPIO14 ──── 74AHCT125 A2 ──── Servo signal (orange)
  L298N 5V     ──── Servo VCC (red)
  GND          ──── Servo GND (brown)

L298N MOTOR DRIVER:
  ESP32 GPIO25 ──── L298N IN1
  ESP32 GPIO26 ──── L298N IN2
  ESP32 GPIO27 ──── L298N ENA (PWM)
  ESP32 GPIO32 ──── L298N IN3
  ESP32 GPIO33 ──── L298N IN4
  ESP32 GPIO34 ──── L298N ENB (PWM)
  L298N OUT1,2 ──── DC Motor Left
  L298N OUT3,4 ──── DC Motor Right

DFPLAYER MINI AUDIO:
  L298N 5V    ──── DFPlayer VCC + 10µF cap+
  GND         ──── DFPlayer GND + 10µF cap−
  ESP32 GPIO17 ── (1kΩ) ─── DFPlayer RX
  DFPlayer TX ──── ESP32 GPIO16
  DFPlayer SPK1 ── Speaker +
  DFPlayer SPK2 ── Speaker −

Color code (master):
  RED    = 5V / VIN
  ORANGE = 9V battery rail
  PURPLE = 3.3V logic
  BLACK  = GND (common rail)
  GREEN  = NeoPixel data (level-shifted 5V)
  BLUE   = Servo signal (level-shifted 5V)
  YELLOW = Motor direction pins (IN1-IN4)
  WHITE  = Motor PWM enable pins (ENA, ENB)
  CYAN   = I2C SDA (GPIO4)
  PINK   = I2C SCL (GPIO5)
  BROWN  = HC-SR04 TRIG (GPIO9)
  VIOLET = HC-SR04 ECHO with divider (GPIO10)
  GREY   = PIR output with divider (GPIO2)
  MAROON = DFPlayer UART (TX=GPIO17, RX=GPIO16)

COMPLETE Connection Table:
┌──────────────────────┬──────────────────────────────────────────┐
│ From                 │ To                                       │
├──────────────────────┼──────────────────────────────────────────┤
│ USB 5V               │ ESP32-S3 VIN                             │
│ 9V Battery (+)       │ L298N VS                                 │
│ 9V Battery (−)       │ L298N GND + ESP32 GND (common)           │
│ L298N 5V             │ Servo VCC, 74AHCT125 VCC, DFPlayer VCC   │
│ ESP32 GPIO4 (SDA)    │ OLED SDA                                 │
│ ESP32 GPIO5 (SCL)    │ OLED SCL                                 │
│ ESP32 3V3            │ OLED VCC (+ 100µF cap to GND)            │
│ ESP32 GPIO6          │ 74AHCT125 A1 → (470Ω) → NeoPixel DIN     │
│ ESP32 GPIO9 (TRIG)   │ HC-SR04 TRIG                             │
│ HC-SR04 ECHO (5V)    │ 10k+20k divider → ESP32 GPIO10           │
│ L298N 5V             │ PIR VCC                                  │
│ PIR OUT (5V)         │ 10k+20k divider → ESP32 GPIO2            │
│ ESP32 GPIO14         │ 74AHCT125 A2 → Servo signal (orange)     │
│ ESP32 GPIO25         │ L298N IN1                                │
│ ESP32 GPIO26         │ L298N IN2                                │
│ ESP32 GPIO27 (PWM)   │ L298N ENA                                │
│ ESP32 GPIO32         │ L298N IN3                                │
│ ESP32 GPIO33         │ L298N IN4                                │
│ ESP32 GPIO34 (PWM)   │ L298N ENB                                │
│ L298N OUT1,2         │ DC Motor A                               │
│ L298N OUT3,4         │ DC Motor B                               │
│ L298N 5V             │ DFPlayer VCC + 10µF cap+                 │
│ ESP32 GPIO17 (TX2)   │ 1kΩ → DFPlayer RX                        │
│ DFPlayer TX          │ ESP32 GPIO16 (RX2)                       │
│ DFPlayer SPK1        │ Speaker terminal 1                       │
│ DFPlayer SPK2        │ Speaker terminal 2                       │
└──────────────────────┴──────────────────────────────────────────┘

⚡ Critical Notes:
  - 9V battery GND MUST connect to ESP32 GND (common ground)
  - 74AHCT125 handles BOTH NeoPixel AND servo level-shift
  - HC-SR04 ECHO and PIR output: voltage dividers MANDATORY on ESP32-S3
  - DFPlayer RX 1kΩ resistor is mandatory
  - OLED I2C now on GPIO4(SDA)/GPIO5(SCL) — conflict with GPIO9 resolved

```

**C-3PO:** "Download the PDF. All twenty-three connection rows. Printed. Laminated if possible. This is the complete blueprint of R2-D2."

## Final Compile 🚀

```
✓ Compilation successful
  Board:        ESP32-S3 N16R8
  Files:        r2d2-main.ino + 6 headers
  Binary:       634,512 bytes (9.1% of 16MB Flash)
  RAM:          Used 52,416 bytes (16.0% of 327KB)
  PSRAM:        8.0 MB free
  Wi-Fi:        Access Point mode — SSID: "R2-D2"
  Dual-core:    Core 0: Wi-Fi/HTTP | Core 1: Real-time control

```

Click **Upload**.

*The ESP32-S3 boots. The OLED shows "R2-D2 ONLINE." The startup fanfare plays from the speaker. The dome LEDs breathe. The servo sweeps. The Serial Monitor shows:*

```
╔═══════════════════════════════╗
║   R2-D2 — COMPLETE BUILD      ║
║   ESP32-S3 N16R8              ║
╚═══════════════════════════════╝
OLED projector online!
Dome servo centred.
Motor driver online.
DFPlayer Mini online!
R2-D2 says: [sound 5]
[WiFi] AP started: R2-D2
[WiFi] IP: 192.168.4.1
[WiFi] HTTP server started — connect to R2-D2 network
All systems ONLINE. R2-D2 is ready.
Distance: 95 cm — SAFE

```

*Pick up your phone. Connect to the "R2-D2" Wi-Fi network. Password: beepboop. Open a browser. Navigate to 192.168.4.1.*

*A simple control page appears. Blue on black. R2-D2's face.*

*Tap "Forward."*

*The wheels turn.*

*Tap "Happy."*

*R2's happy whistle plays.*

*Tap "Dome ◄."*

*The dome snaps left.*

## The Final Milestone 🚩

```
Milestone: "R2-D2 COMPLETE — Episode 8 Final Build"

```

*Every episode. Every system. Every milestone. All saved. All restorable.*

## The Complete Droid 🤖

*The workshop is quiet. The crew stands in a circle around R2-D2 — the completed droid. Dome rotating. Lights breathing. OLED projecting. Speaker quiet for now, waiting.*

**OBI-WAN:** "You see what has been built. Not just a robot. Not just a collection of components. The process itself is the lesson — the way Codey lowered every barrier between the idea and the creation. You described. It wrote. You compiled. It fixed. You drew. It diagrammed. Each episode, a little more complex. Each episode, possible."

**LUKE:** "Eight episodes. I went from blinking an LED to a Wi-Fi controlled droid with dome lights, sensors, a display, motors, and audio. And I'm not a programmer."

**HAN:** "Kid, I've seen the Millennium Falcon held together with less intentionality than this thing. And the Falcon can make the Kessel Run."

*R2-D2 beeps. Loudly. Repeatedly. Proudly.*

**C-3PO:** "He says — and I am translating precisely — 'I told you all it would work.'"

*A long pause.*

**C-3PO:** "He also says thank you. Which, from Artoo, is quite remarkable."

*Obi-Wan smiles.*

**OBI-WAN:** "The Force will be with you. Always."

*R2-D2 plays his startup fanfare one more time. The dome lights sweep blue-white. The OLED displays: "MISSION COMPLETE."*

## The Series Map — What We Built 🗺️

| Episode | System | Board | Codey Feature Spotlight |
| --- | --- | --- | --- |
| 1 | First LED blink | Arduino UNO R3 | Account setup, first sketch, first wiring diagram |
| 2 | Piezo sound | Arduino UNO R3 | Smart Library Picker, tone(), Serial Monitor |
| 3 | NeoPixel dome | Arduino UNO R3 | Voltage safety check, FastLED, multi-file project |
| 4 | Sensor eye | Arduino UNO R3 | Auto Error Fixing, Vision photo upload |
| 5 | OLED projector | ESP32-S3 N16R8 | Board upgrade, Milestones & Rollback, I2C |
| 6 | Motion systems | ESP32-S3 N16R8 | LEDC servo, L298N motors, two-rail wiring |
| 7 | Audio voice | ESP32-S3 N16R8 | DFPlayer Mini, UART, Live Serial Monitor |
| 8 | Complete droid | ESP32-S3 N16R8 | Deep Think mode, Wi-Fi, dual-core, final diagram |

**🔗 Resources**

- **Codey Online**: [codey.online](http://codey.online)
- **ESP32-S3 technical reference**: [docs.espressif.com/esp32-s3](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/)
- **ArduinoJson library**: [arduinojson.org](http://arduinojson.org)
- **ESP32 FreeRTOS tasks**: [freertos.org/documentation](https://www.freertos.org/Documentation/)
- **OTRONIC / Codey**: [otronic.nl](http://otronic.nl) | [codey.online](http://codey.online)

*🤖 R2D2 Creation with Codey — eight episodes, one complete droid, infinite possibilities. The Force — and the cloud compiler — were with us. Always.*