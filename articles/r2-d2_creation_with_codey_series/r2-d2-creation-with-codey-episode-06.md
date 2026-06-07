---
title: "R2D2 Creation with Codey 🤖 Ep.6" 
published: false 
description: "Episode 6: A droid that cannot move is a very expensive ornament. We give R2-D2 motion — a servo-driven rotating dome and DC motor wheels via an L298N driver. The ESP32-S3's LEDC PWM system handles the servo. The wiring diagram grows to its most complex yet. Han Solo is characteristically dismissive until the dome starts spinning." 
tags: [esp32, servo, motors, makers] 
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/r2-d2_creation_with_codey_series/r2-d2-creation-with-codey-episode-06.png" 
series: "R2-D2 Creation With Codey" 
canonical_url: "" 
organization: "the-software-s-journey" 
part: 6
---
## Episode 6: Let the Wookiee Win — R2 Moves!

## "Would Somebody Get This Big Walking Carpet Out of My Way?" 🦾

*Han Solo enters the workshop with the energy of someone who has been waiting since Episode 1 for this moment.*

**HAN:** "Okay, look. I've put up with the blinking LED. The beeps were cute. The screen — fine, useful. But I need this droid to actually MOVE. Because right now he's sitting there like a very opinionated lamp and I am not impressed."

*R2-D2 beeps at high volume and at length.*

**HAN:** "Yeah yeah, I know, you're very capable. Prove it. Episode 6. Let's go."

*Somewhere, a Wookiee roars enthusiastically.*

**HAN:** "Chewie agrees. Let the droid move."

## 🗂️ SIPOC — The Motion System

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (the maker) | "Add servo for dome rotation on GPIO14, L298N motor driver for wheels on GPIO pins 25-27" | Codey writes ESP32-S3 LEDC servo code + L298N motor control, generates motion.h | Dome that sweeps left and right, wheels that drive forward/back/turn | R2-D2 — who finally lives up to his reputation |
| ESP32-S3 LEDC PWM | 50Hz PWM signal, 3.3V | Drives servo signal line (with level shifter) | Dome servo at 0°, 45°, 90°, 135°, 180° | SG90 servo — which rotates R2's dome |
| L298N Motor Driver | 5V–12V external power, direction + PWM signals from ESP32-S3 | H-bridge controls current direction to each DC motor | Forward / backward / left turn / right turn | Two DC motors — which drive R2's wheels |
| Codey Wiring Diagram | Full component list including motor power requirements | Draws color-coded diagram with separate power rail for motors | Two-rail wiring diagram: logic (3.3V) + motor power | You — who correctly separate the motor power from the logic power |

## The Components 🔧

*Yoda examines the motor driver with a long, thoughtful look.*

**YODA:** "Moving parts, added today we are. Careful, one must be. Motors, hungry for current they are. Directly from the ESP32-S3, power them you must not — destroyed, your microcontroller would be."

| Component | Quantity | Notes |
| --- | --- | --- |
| ESP32-S3 N16R8 | 1 | Our brain from Episode 5 |
| SG90 micro servo | 1 | For dome rotation — 5V, 3-wire |
| L298N dual H-bridge motor driver | 1 | Drives two DC motors, needs separate 5V–12V |
| DC gear motors with wheels | 2 | 3V–6V, ~200mA stall current each |
| 74AHCT125 level shifter | 1 | Servo signal: 3.3V → 5V |
| 9V battery or 2S LiPo | 1 | Motor power supply — separate from logic |
| Jumper wires | 12 | Several gauge sizes |
| USB cable | 1 |  |

**YODA:** "Two power rails, we shall have. Logic power: USB 5V → 3.3V for ESP32-S3. Motor power: separate battery for L298N and motors. Cross them, you must not."

## The ESP32-S3 and Servo Control: LEDC at 50Hz ⚙️

*C-3PO raises a cautionary finger.*

**C-3PO:** "I must explain the servo PWM situation. The Arduino Servo library used the Timer1 hardware. On the ESP32-S3, we use the LEDC peripheral — the same one we used for the buzzer tone in Episode 5, but configured at 50Hz for servo control. A standard hobby servo expects a pulse between 0.5ms and 2.5ms at a 50Hz frequency. Codey handles this calculation automatically."

**HAN:** "Three-PO. The servo. Just the servo."

**C-3PO:** "Yes. Moving on."

In **Agent mode**:

```
We're continuing R2-D2 on ESP32-S3 N16R8.

Add motion systems:

1. SG90 servo for dome rotation:
   - Signal on GPIO14 (through 74AHCT125 level shifter)
   - 5V power from VIN rail
   - Create these movements:
     a. idle_scan: slow sweep 60°→120° and back, 3 second period
     b. alert_snap: snap to face sensor direction
     c. full_sweep: 0° to 180° and back when "happy"

2. L298N motor driver for two DC wheels:
   - Motor A: IN1=GPIO25, IN2=GPIO26, ENA=GPIO27 (PWM)
   - Motor B: IN3=GPIO32, IN4=GPIO33, ENB=GPIO34 (PWM)
   - Create: forward(), backward(), turnLeft(), turnRight(), stop()
   - Speed: 0-255 mapped to LEDC duty cycle

3. Behavior: when distance < 30cm → stop + snap dome toward sensor
   When motion detected → sweep dome toward source

Create motion.h file for all motion code.
Keep existing animations.h, sensors.h, display.h, sounds.h unchanged.

```

### Generated `motion.h`

```cpp
// motion.h — R2-D2 Motion System
// Dome servo + DC wheel motors via L298N
// ESP32-S3 N16R8

#pragma once

// ── SERVO (dome rotation) ────────────────────────────────────────
#define SERVO_PIN     14     // GPIO14 — through 74AHCT125 to servo
#define SERVO_CHANNEL 1      // LEDC channel (channel 0 used by buzzer)

// Servo pulse widths in microseconds
#define SERVO_MIN_US  500    // 0°
#define SERVO_MID_US  1500   // 90° (centre)
#define SERVO_MAX_US  2500   // 180°

// LEDC config for servo: 50Hz, 16-bit resolution (allows fine pulse control)
#define SERVO_FREQ    50
#define SERVO_RES     16     // 16-bit → 0–65535

int currentDomeAngle = 90;     // Start centred
int targetDomeAngle  = 90;
int domeSweepDir     = 1;      // +1 or -1 for idle sweep
unsigned long lastServoMs = 0;

void initServo() {
  ledcSetup(SERVO_CHANNEL, SERVO_FREQ, SERVO_RES);
  ledcAttachPin(SERVO_PIN, SERVO_CHANNEL);
  // Centre the dome on startup
  int pulse   = map(90, 0, 180, SERVO_MIN_US, SERVO_MAX_US);
  int duty    = (int)((float)pulse / 20000.0f * 65535.0f);
  ledcWrite(SERVO_CHANNEL, duty);
  Serial.println("Dome servo centred.");
}

void setDomeAngle(int angle) {
  angle = constrain(angle, 0, 180);
  int pulse = map(angle, 0, 180, SERVO_MIN_US, SERVO_MAX_US);
  int duty  = (int)((float)pulse / 20000.0f * 65535.0f);
  ledcWrite(SERVO_CHANNEL, duty);
  currentDomeAngle = angle;
}

// Idle: slow sweep 60° ↔ 120°
void domeIdleSweep() {
  unsigned long now = millis();
  if (now - lastServoMs < 30) return;
  lastServoMs = now;

  currentDomeAngle += domeSweepDir;
  if (currentDomeAngle >= 120) domeSweepDir = -1;
  if (currentDomeAngle <= 60)  domeSweepDir =  1;
  setDomeAngle(currentDomeAngle);
}

// Snap to angle quickly (alert behaviour)
void domeSnap(int angle) {
  setDomeAngle(angle);
}

// Full sweep 0°→180°→0° (happy behaviour)
unsigned long fullSweepMs = 0;
int   fullSweepAngle = 0;
int   fullSweepDir   = 1;
bool  fullSweepDone  = false;

void domeSweepFull() {
  unsigned long now = millis();
  if (now - fullSweepMs < 12) return;
  fullSweepMs = now;

  fullSweepAngle += fullSweepDir * 2;
  if (fullSweepAngle >= 180) { fullSweepDir = -1; }
  if (fullSweepAngle <= 0)   { fullSweepDone = true; }
  setDomeAngle(fullSweepAngle);
}

// ── L298N MOTOR DRIVER ────────────────────────────────────────────
#define MOTOR_A_IN1  25
#define MOTOR_A_IN2  26
#define MOTOR_A_EN   27   // PWM channel 2

#define MOTOR_B_IN3  32
#define MOTOR_B_IN4  33
#define MOTOR_B_EN   34   // PWM channel 3

#define MOTOR_CHANNEL_A  2
#define MOTOR_CHANNEL_B  3
#define MOTOR_FREQ       5000   // 5kHz PWM for motors
#define MOTOR_RES        8      // 8-bit → 0–255

void initMotors() {
  // Direction pins
  pinMode(MOTOR_A_IN1, OUTPUT);
  pinMode(MOTOR_A_IN2, OUTPUT);
  pinMode(MOTOR_B_IN3, OUTPUT);
  pinMode(MOTOR_B_IN4, OUTPUT);

  // PWM channels for enable pins
  ledcSetup(MOTOR_CHANNEL_A, MOTOR_FREQ, MOTOR_RES);
  ledcSetup(MOTOR_CHANNEL_B, MOTOR_FREQ, MOTOR_RES);
  ledcAttachPin(MOTOR_A_EN, MOTOR_CHANNEL_A);
  ledcAttachPin(MOTOR_B_EN, MOTOR_CHANNEL_B);

  // Start stopped
  ledcWrite(MOTOR_CHANNEL_A, 0);
  ledcWrite(MOTOR_CHANNEL_B, 0);
  Serial.println("Motor driver online.");
}

void motorForward(uint8_t speed = 180) {
  digitalWrite(MOTOR_A_IN1, HIGH); digitalWrite(MOTOR_A_IN2, LOW);
  digitalWrite(MOTOR_B_IN3, HIGH); digitalWrite(MOTOR_B_IN4, LOW);
  ledcWrite(MOTOR_CHANNEL_A, speed);
  ledcWrite(MOTOR_CHANNEL_B, speed);
}

void motorBackward(uint8_t speed = 180) {
  digitalWrite(MOTOR_A_IN1, LOW);  digitalWrite(MOTOR_A_IN2, HIGH);
  digitalWrite(MOTOR_B_IN3, LOW);  digitalWrite(MOTOR_B_IN4, HIGH);
  ledcWrite(MOTOR_CHANNEL_A, speed);
  ledcWrite(MOTOR_CHANNEL_B, speed);
}

void motorTurnLeft(uint8_t speed = 150) {
  // Left motor backward, right motor forward = left turn
  digitalWrite(MOTOR_A_IN1, LOW);  digitalWrite(MOTOR_A_IN2, HIGH);
  digitalWrite(MOTOR_B_IN3, HIGH); digitalWrite(MOTOR_B_IN4, LOW);
  ledcWrite(MOTOR_CHANNEL_A, speed);
  ledcWrite(MOTOR_CHANNEL_B, speed);
}

void motorTurnRight(uint8_t speed = 150) {
  // Left motor forward, right motor backward = right turn
  digitalWrite(MOTOR_A_IN1, HIGH); digitalWrite(MOTOR_A_IN2, LOW);
  digitalWrite(MOTOR_B_IN3, LOW);  digitalWrite(MOTOR_B_IN4, HIGH);
  ledcWrite(MOTOR_CHANNEL_A, speed);
  ledcWrite(MOTOR_CHANNEL_B, speed);
}

void motorStop() {
  ledcWrite(MOTOR_CHANNEL_A, 0);
  ledcWrite(MOTOR_CHANNEL_B, 0);
  digitalWrite(MOTOR_A_IN1, LOW); digitalWrite(MOTOR_A_IN2, LOW);
  digitalWrite(MOTOR_B_IN3, LOW); digitalWrite(MOTOR_B_IN4, LOW);
}

void initMotion() {
  initServo();
  initMotors();
}

```

### Updated `r2d2-main.ino` loop

```cpp
// Loop addition — reactive motion

void loop() {
  if (!bootDone) { showBootScreen(); return; }

  float dist   = readDistance();
  bool  motion = checkMotion();

  // ── Dome behaviour ─────────────────────────────────────────
  if (dist < 30.0f) {
    domeSnap(90);       // face forward, something is ahead
    motorStop();        // stop wheels — obstacle!
  } else if (motion) {
    domeSnap(45);       // snap left — motion detected
  } else {
    domeIdleSweep();    // gentle idle scan
  }

  // ── Display ─────────────────────────────────────────────────
  if (dist < 15.0f)    showAlertScreen();
  else if (motion)     showMotionScreen();
  else                 showIdleScreen(dist);

  // ── Dome lights ─────────────────────────────────────────────
  updateAnimationsSensors(dist, motion);
}

```

## The Wiring Diagram — Two Power Rails 🧭

*C-3PO studies the diagram, then exhales slowly.*

**C-3PO:** "Codey has correctly separated the power rails. The logic rail — 3.3V from the ESP32-S3 regulator — powers only the microcontroller and the OLED. The motor rail — the external 9V battery through the L298N's onboard 5V regulator — powers the motors and the servo. This is exactly correct. Mixing them would cause voltage drops that would reset the ESP32-S3 every time a motor starts."

```
R2-D2 Motion System — Wiring Diagram (ESP32-S3 N16R8)
════════════════════════════════════════════════════════════════

POWER RAIL 1 — LOGIC (USB 5V → ESP32-S3 regulator):
  USB 5V  ──── ESP32-S3 VIN
  ESP32 3V3 ── OLED VCC
  ESP32 GND ── OLED GND, logic GND rail

POWER RAIL 2 — MOTOR POWER (9V battery):
  9V Bat (+) ── L298N: VS (motor supply)
  9V Bat (−) ── L298N: GND (common ground with ESP32 GND)
  L298N: 5V  ── Servo VCC (5V regulated output)
  L298N: 5V  ── 74AHCT125: VCC
  L298N: GND ── Servo GND, 74AHCT125 GND

  ⚠️  IMPORTANT: ESP32 GND and battery GND must be connected together!

SERVO (dome rotation):
  ESP32 GPIO14 ─── 74AHCT125 A1 input (3.3V signal in)
  74AHCT125 Y1 ─── Servo Signal wire (orange/yellow) — 5V signal out
  L298N 5V     ─── Servo VCC (red wire)
  L298N GND    ─── Servo GND (brown/black wire)

MOTORS via L298N:
  ESP32 GPIO25 ──── L298N IN1 (Motor A direction)
  ESP32 GPIO26 ──── L298N IN2 (Motor A direction)
  ESP32 GPIO27 ──── L298N ENA (Motor A PWM speed)
  ESP32 GPIO32 ──── L298N IN3 (Motor B direction)
  ESP32 GPIO33 ──── L298N IN4 (Motor B direction)
  ESP32 GPIO34 ──── L298N ENB (Motor B PWM speed)
  L298N OUT1   ──── DC Motor A: terminal 1
  L298N OUT2   ──── DC Motor A: terminal 2
  L298N OUT3   ──── DC Motor B: terminal 1
  L298N OUT4   ──── DC Motor B: terminal 2

NeoPixel (from Episode 5):
  ESP32 GPIO6 ── 74AHCT125 A2 ── NeoPixel DIN

Color code:
  RED    = 5V / VIN power
  ORANGE = 9V battery supply
  BLACK  = GND
  PURPLE = 3.3V logic
  GREEN  = NeoPixel data (level-shifted)
  BLUE   = Servo signal (level-shifted)
  YELLOW = Motor direction signals
  WHITE  = Motor PWM (speed) signals

Connection Table:
┌──────────────────────┬──────────────────────────────────────┐
│ From                 │ To                                   │
├──────────────────────┼──────────────────────────────────────┤
│ 9V Battery (+)       │ L298N: VS                            │
│ 9V Battery (−)       │ L298N: GND + ESP32 GND (common)      │
│ L298N: 5V out        │ Servo VCC (red), 74AHCT125 VCC       │
│ L298N: GND           │ Servo GND, 74AHCT125 GND             │
│ ESP32 GPIO14         │ 74AHCT125 A1 → servo signal (5V)     │
│ ESP32 GPIO6          │ 74AHCT125 A2 → NeoPixel DIN (5V)     │
│ ESP32 GPIO25         │ L298N IN1                            │
│ ESP32 GPIO26         │ L298N IN2                            │
│ ESP32 GPIO27 (PWM)   │ L298N ENA                            │
│ ESP32 GPIO32         │ L298N IN3                            │
│ ESP32 GPIO33         │ L298N IN4                            │
│ ESP32 GPIO34 (PWM)   │ L298N ENB                            │
│ L298N OUT1,OUT2      │ DC Motor A                           │
│ L298N OUT3,OUT4      │ DC Motor B                           │
└──────────────────────┴──────────────────────────────────────┘

```

**HAN:** "Two power rails. That's important. I've seen people blow a microcontroller trying to power motors directly off the GPIO pins. The L298N's internal regulator gives you the 5V for the servo and the level shifter. Clean."

*R2-D2 beeps approvingly.*

**HAN:** "Yeah, even I have to admit that's well done."

## Compile and Watch the Dome Spin 🚀

```
✓ Compilation successful
  Board:   ESP32-S3 N16R8
  Sketch:  r2d2-main.ino + 5 headers
  Binary:  498,244 bytes (7.2% of 16MB Flash)
  RAM:     Used 34,128 bytes (10.4% of 327KB)

```

The dome servo sweeps slowly between 60° and 120°. R2-D2 scans the room.

Wave your hand in front of the HC-SR04. The dome snaps to 90°. The wheels stop. The OLED shows "TOO CLOSE!"

*Han Solo watches the dome turn. A long pause.*

**HAN:** "...Okay. That's actually pretty good."

*R2-D2 beeps.*

**HAN:** "I said it was *pretty* good. Don't push it."

## Save Milestone 🚩

```
Milestone: "R2-D2 Motion Systems — Episode 6 Complete"

```

Five systems running. Dome rotating. Wheels ready. The droid is almost complete.

## What's Next: R2 Gets His Voice Back 🔊

*Obi-Wan speaks with warmth.*

**OBI-WAN:** "The dome spins. The lights glow. The screen projects. The wheels wait. But something is still missing — the true voice. Not just beeps from a buzzer, but the full audio character of the galaxy's most beloved droid. In Episode 7, we add the DFPlayer Mini and a speaker. R2-D2 will play actual audio files. And the Live Serial Monitor will show us exactly what is happening."

*R2-D2 emits a long, heartfelt whistle that says everything.*

**🔗 Resources**

- **ESP32 LEDC (servo)**: [randomnerdtutorials.com/esp32-servo-motor-web-server](https://randomnerdtutorials.com/esp32-servo-motor-web-server-arduino-ide/)
- **L298N motor driver**: Search "L298N Arduino ESP32 tutorial"
- **74AHCT125 level shifter**: Search "74AHCT125 3.3V 5V logic level converter"
- **Codey Online**: [codey.online](http://codey.online)

*🤖 R2D2 Creation with Codey — building the galaxy's greatest droid, one episode at a time. May the Force — and the cloud compiler — be with you.*