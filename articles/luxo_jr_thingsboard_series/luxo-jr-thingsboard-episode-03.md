---
title: "Luxo Jr. ThingsBoard 🎬 Ep.3"
part: 3
published: false
description: "Episode 3: The lamp tilts its head — the first telemetry arrives. Connecting devices via MQTT and HTTP, telemetry vs attributes, access tokens, and the difference between a prop that just sits there and one that reports its state."
tags: [iot, thingsboard, mqtt, homeautomation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/stage-props-thingsboard-episode-03.png"
series: "Luxo Jr. ThingsBoard Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 3: The Prop Speaks

> *“As soon as the lamp moved, people started going crazy.”*
> — Craig Good, Pixar, on the moment Luxo Jr. first animated at SIGGRAPH

-----

## The First Movement 💡

In the Pixar auditorium in 1986, six thousand people were watching a rendering demo. They had seen technical demos before — waves, a beach chair. Fine. Then the lamp on screen turned its head.

Pandemonium.

Not because the rendering was the best they had seen. Because the lamp *moved* in a way that implied awareness. The head swivel said: “I know something is here.” The subsequent lean and bounce said: “And I care about it.”

Your ThingsBoard device does the same thing the moment its first telemetry packet arrives. The status changes from `Inactive` to `Active`. Data appears in the Latest Telemetry tab. The dashboard widget updates. The prop is no longer just a registered name in a list. It is speaking.

This episode makes the prop speak.

-----

## 🗂️ SIPOC — The First Transmission

|**Suppliers**                                          |**Inputs**                 |**Process**                                                     |**Outputs**                                                             |**Customers**                                                   |
|-------------------------------------------------------|---------------------------|----------------------------------------------------------------|------------------------------------------------------------------------|----------------------------------------------------------------|
|A physical device (sensor, actuator) or Home Assistant |Raw sensor readings in JSON|MQTT publish to `v1/devices/me/telemetry` with Access Token auth|Timestamped key-value pairs stored in ThingsBoard’s time-series database|Dashboard widgets, Rule Engine, Alarm evaluation                |
|A device’s fixed properties (location, model, firmware)|Key-value metadata         |MQTT publish to `v1/devices/me/attributes`                      |Stored as client-side attributes — permanent properties, not time-series|Attribute widgets, entity filters, RPC parameter lookup         |
|ThingsBoard platform                                   |RPC command (e.g., turn on)|MQTT subscribe to `v1/devices/me/rpc/request/+`                 |Device receives command, acts on it, publishes response                 |Dashboards with control widgets; rule chains that issue commands|

-----

## The Two Kinds of Data: Telemetry vs Attributes 📊

Before connecting anything, one distinction is essential. ThingsBoard stores device data in two fundamentally different ways, with different semantics and different storage backends.

### Telemetry — The Prop’s Observable State

**Telemetry** is time-series data: measurements the device reports over time. Every reading is stored with its timestamp. You can query history, aggregate over windows, draw charts.

```json
{ "temperature": 24.5, "humidity": 62 }
```

- Stored with a timestamp (server-assigned or device-provided)
- Multiple readings accumulate — full history preserved
- Used for: charts, trend analysis, alarm thresholds, real-time displays
- Example: every 30 seconds, the lamp reports its ambient temperature

### Attributes — The Prop’s Fixed Characteristics

**Attributes** are static properties — metadata about the device, not time-series readings. ThingsBoard stores only the *current* value. There is no history.

Three scopes:

- **Client-side attributes**: the device sets and owns these (firmware version, calibration date)
- **Server-side attributes**: ThingsBoard sets these; the device can read them (threshold config, location)
- **Shared attributes**: ThingsBoard sets them; the device subscribes to changes (configuration the device should apply)

```json
{ "location": "Room 401", "firmwareVersion": "2.1.4", "maxTempThreshold": 30 }
```

Think of it this way: Luxo Jr.’s **telemetry** is the angle of each joint at each moment in the animation. His **attributes** are the fixed facts about his model — the length of his arm segments, his base colour, which scene he belongs to.

-----

## Authentication: The Access Token 🔑

ThingsBoard authenticates device connections using **Access Tokens** — unique credentials generated per device. No username/password; the token *is* the identity.

To find your device’s token:

1. **Entities → Devices** → click your device
1. Click the key icon (**Manage credentials**)
1. The **Access Token** is shown — copy it

```bash
# The token is passed as the MQTT username
# Password: leave blank
# Topic: uses a fixed path structure

mosquitto_pub \
  -h "thingsboard.cloud" \
  -p 1883 \
  -u "YOUR_ACCESS_TOKEN" \
  -t "v1/devices/me/telemetry" \
  -m '{"temperature": 24.5, "humidity": 62}'
```

ThingsBoard Cloud supports MQTT on port 1883 (plain) or 8883 (TLS). For production, always use TLS.

-----

## Publishing Telemetry via MQTT 📡

The MQTT topic structure for ThingsBoard devices is fixed:

|What                                 |MQTT Topic                             |Direction           |
|-------------------------------------|---------------------------------------|--------------------|
|Publish telemetry                    |`v1/devices/me/telemetry`              |Device → ThingsBoard|
|Publish attributes                   |`v1/devices/me/attributes`             |Device → ThingsBoard|
|Subscribe to shared attribute updates|`v1/devices/me/attributes/response/+`  |ThingsBoard → Device|
|Subscribe to RPC requests            |`v1/devices/me/rpc/request/+`          |ThingsBoard → Device|
|Publish RPC response                 |`v1/devices/me/rpc/response/$requestId`|Device → ThingsBoard|

### Telemetry payload formats

**Simple JSON (server-side timestamp):**

```json
{"temperature": 24.5, "humidity": 62, "brightness": 800}
```

**With device-side timestamp** (milliseconds since epoch):

```json
{"ts": 1744400000000, "values": {"temperature": 24.5, "humidity": 62}}
```

**Multiple readings in one message:**

```json
[
  {"ts": 1744400000000, "values": {"temperature": 24.5}},
  {"ts": 1744400010000, "values": {"temperature": 24.7}}
]
```

### Mosquitto test command

```bash
# Install mosquitto clients (macOS)
brew install mosquitto

# Ubuntu / Debian
sudo apt install mosquitto-clients

# Test telemetry publish
mosquitto_pub \
  -h "YOUR_THINGSBOARD_HOST" \
  -p 1883 \
  -u "YOUR_ACCESS_TOKEN" \
  -t "v1/devices/me/telemetry" \
  -m '{"temperature": 24.5, "humidity": 62}'
```

After running this command, open your device in ThingsBoard → **Latest Telemetry** tab. You should see `temperature: 24.5` and `humidity: 62`. The lamp has tilted its head. The data is there.

-----

## Publishing via HTTP (REST) 🌐

For devices that cannot use MQTT (or for quick testing), ThingsBoard accepts telemetry via HTTP POST:

```bash
# POST telemetry
curl -v -X POST \
  -H "Content-Type: application/json" \
  -d '{"temperature": 24.5, "humidity": 62}' \
  "https://YOUR_THINGSBOARD_HOST/api/v1/YOUR_ACCESS_TOKEN/telemetry"

# POST attributes
curl -v -X POST \
  -H "Content-Type: application/json" \
  -d '{"location": "Room 401", "firmwareVersion": "2.1.4"}' \
  "https://YOUR_THINGSBOARD_HOST/api/v1/YOUR_ACCESS_TOKEN/attributes"
```

The token appears in the URL path, not in headers. This is simpler for constrained devices but less efficient than MQTT for high-frequency telemetry.

-----

## Verifying the Connection 🔍

After publishing telemetry:

1. **Entities → Devices** → click your device
1. **Latest Telemetry** tab — you see all keys and their current values
1. **Events** tab → **DEBUG** events (if debug mode is on in the Rule Chain) — shows the raw message
1. Device status changes from **Inactive** to **Active**

The device’s status badge turning green is your SIGGRAPH moment. The prop is active. It is part of the production.

### Using ThingsBoard’s built-in connectivity check

ThingsBoard Cloud and recent CE versions include a **Check Connectivity** wizard:

1. Open device → click **Check Connectivity**
1. Select protocol (MQTT, HTTP, CoAP) and OS
1. ThingsBoard generates the exact command to run — copy and paste
1. Watch the status change from Inactive to Active in real time

-----

## Sending Attributes: The Prop’s Fixed Properties 🏷️

Attributes do not replace telemetry — they complement it. Send attributes once at startup and when they change, not on every telemetry cycle.

```bash
# Publish client-side attributes via MQTT
mosquitto_pub \
  -h "YOUR_THINGSBOARD_HOST" \
  -p 1883 \
  -u "YOUR_ACCESS_TOKEN" \
  -t "v1/devices/me/attributes" \
  -m '{"location": "Room 401", "firmwareVersion": "2.1.4", "macAddress": "AA:BB:CC:DD:EE:FF"}'
```

Server-side attributes (assigned by ThingsBoard, not the device) are set in the UI:

1. Open device → **Attributes** tab
1. Select **Server attributes** scope
1. Click **+** → add key, type, value
1. Save

Example server-side attributes for a lamp:

```json
{
  "maxBrightness": 1000,
  "location": "Stage Left",
  "scene": "Act 2 Scene 3",
  "temperatureAlarmThreshold": 35
}
```

These attributes can be read by the Rule Engine and referenced in dashboard widgets — the lamp knows its own threshold, the dashboard reads it, the alarm uses it.

-----

## Receiving RPC Commands: The Director Calls “Action!” 📢

Telemetry flows device → ThingsBoard. RPC flows ThingsBoard → device. This is how you send commands: turn on the lamp, set brightness to 50%, reset the sensor.

The device subscribes to the RPC topic:

```python
# Python example (using paho-mqtt)
import paho.mqtt.client as mqtt
import json

ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
THINGSBOARD_HOST = "YOUR_HOST"

def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.subscribe("v1/devices/me/rpc/request/+")

def on_message(client, userdata, msg):
    print(f"RPC received: {msg.payload.decode()}")
    # Parse the request
    data = json.loads(msg.payload)
    method = data.get("method")
    params = data.get("params", {})
    
    # Handle the command
    if method == "setBrightness":
        brightness = params.get("brightness", 0)
        # ... set hardware brightness here ...
        print(f"Setting brightness to {brightness}")
    
    # Send response back
    request_id = msg.topic.split("/")[-1]
    response_topic = f"v1/devices/me/rpc/response/{request_id}"
    response = json.dumps({"status": "ok", "brightness": brightness})
    client.publish(response_topic, response)

client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.on_connect = on_connect
client.on_message = on_message
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_forever()
```

From the ThingsBoard dashboard or Rule Engine, an RPC call can trigger this handler. In Episode 4, we add a control widget that sends an RPC from the dashboard. In Episode 5, a Rule Engine node sends RPC based on alarm conditions.

-----

## A Complete MQTT Sketch: The Luxo Jr. Lamp 💡

Here is a minimal Python script that simulates the Luxo Jr. lamp — publishing telemetry every 10 seconds and accepting RPC brightness commands:

```python
import paho.mqtt.client as mqtt
import json
import time
import random

ACCESS_TOKEN = "YOUR_DEVICE_ACCESS_TOKEN"
THINGSBOARD_HOST = "thingsboard.cloud"

def on_connect(client, userdata, flags, rc):
    print(f"Connected: rc={rc}")
    # Subscribe to RPC requests
    client.subscribe("v1/devices/me/rpc/request/+")
    # Subscribe to shared attribute updates
    client.subscribe("v1/devices/me/attributes/response/+")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    if "rpc/request" in msg.topic:
        method = data.get("method")
        params = data.get("params", {})
        request_id = msg.topic.split("/")[-1]
        print(f"RPC: {method}({params})")
        # Respond
        resp_topic = f"v1/devices/me/rpc/response/{request_id}"
        client.publish(resp_topic, json.dumps({"status": "ok"}))

client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.on_connect = on_connect
client.on_message = on_message
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

# Publish initial attributes
attributes = {
    "location": "Stage Left",
    "firmwareVersion": "1.0.0",
    "lampModel": "Luxo Jr."
}
client.publish("v1/devices/me/attributes", json.dumps(attributes))

# Publish telemetry every 10 seconds
brightness = 800  # initial brightness
while True:
    # Simulate ambient sensor readings
    telemetry = {
        "ambientTemp": round(random.uniform(20.0, 28.0), 1),
        "brightness": brightness,
        "powerWatts": round(brightness * 0.012, 2),  # derived
        "lampOn": brightness > 0
    }
    client.publish("v1/devices/me/telemetry", json.dumps(telemetry))
    print(f"Published: {telemetry}")
    time.sleep(10)
```

Run this script while watching ThingsBoard. Within 10 seconds, your device turns Active and you see the first telemetry values appearing. The lamp is performing.

-----

## Checking the Latest Telemetry Tab 📋

After publishing, open your device. The **Latest Telemetry** tab shows:

|Key        |Value|Last updated |
|-----------|-----|-------------|
|ambientTemp|24.5 |2 seconds ago|
|brightness |800  |2 seconds ago|
|powerWatts |9.6  |2 seconds ago|
|lampOn     |true |2 seconds ago|

Each key is a separate time series. ThingsBoard stores all historical values. You can visualise any key on a chart going back to the first data point.

-----

In **Episode 4**, we build the prompt book — the Dashboard. Widgets appear on stage: a brightness gauge, a temperature chart, an alarm table. The prop’s story becomes visible to the director.

-----

**🔗 Resources**

- **MQTT Device API Reference**: [thingsboard.io/docs/reference/mqtt-api](https://thingsboard.io/docs/reference/mqtt-api/)
- **Getting Started (hello world)**: [thingsboard.io/docs/getting-started-guides/helloworld](https://thingsboard.io/docs/getting-started-guides/helloworld/)
- **paho-mqtt Python library**: [pypi.org/project/paho-mqtt](https://pypi.org/project/paho-mqtt/)

-----

*🎬 Stage Props! is a series about ThingsBoard — the IoT platform that gives your devices joints, personality, and behaviour.*
