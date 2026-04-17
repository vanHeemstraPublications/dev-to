---
title: "Magic Lamp Ep.4"
published: false
description: "DMX lighting states, pygame projection scenes, and a BabylonJS digital twin — how PIXSTARS visualises the show before a single servo moves."
tags: ["python", "dmx", "babylonjs", "showcontrol"]
part: 4
series: "Magic Lamp Series"
organization: "the-software-s-journey"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/magic_lamp_series/magic-lamp-episode-04.png"
---

> *"Half the trick is where the audience looks."*

Paul Daniels was a master of misdirection — but misdirection only works if you control the full visual field. The light, the backdrop, the framing. Everything the audience sees is part of the trick, including what they don't notice they're seeing.

PIXSTARS operates the same way. The lamp is the focus, but three other visual layers are running simultaneously: stage lighting via DMX, a projected image on the back wall via pygame, and a real-time 3D digital twin in a browser. Each layer reinforces the lamp's emotional state. None of them work in isolation.

---

## 💡 DMX Lighting: 9 States

The stage lighting is driven through an **Enttec DMX USB Pro** controller and defined in `lighting/states.py` using the same state-machine pattern as the lamp.

```python
# lighting/states.py
from dataclasses import dataclass, field

@dataclass
class LightingState:
    name: str
    channels: dict[int, int]   # DMX channel (1-indexed) -> value 0–255
    description: str

LIGHTING_STATES: dict[str, LightingState] = {
    "BLACKOUT": LightingState(
        name="BLACKOUT",
        channels={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        description="All channels off"
    ),
    "LAMP_ONLY": LightingState(
        name="LAMP_ONLY",
        channels={1: 80, 2: 255, 3: 200, 4: 100, 5: 60},
        description="Warm spot on desk lamp only"
    ),
    "ROCKSTAR": LightingState(
        name="ROCKSTAR",
        channels={1: 255, 2: 255, 3: 50, 4: 0, 5: 0},
        description="Bold red/amber concert wash"
    ),
    "DISNEY_SOFT": LightingState(
        name="DISNEY_SOFT",
        channels={1: 120, 2: 0, 3: 80, 4: 255, 5: 160},
        description="Blue/purple fairy-tale wash"
    ),
    "AI_COLD": LightingState(
        name="AI_COLD",
        channels={1: 60, 2: 0, 3: 180, 4: 255, 5: 200},
        description="Cold blue/cyan technical light"
    ),
    "OVERHEAT": LightingState(
        name="OVERHEAT",
        channels={1: 255, 2: 255, 3: 80, 4: 0, 5: 180},
        description="Intense red with strobe"
    ),
    "DEATH": LightingState(
        name="DEATH",
        channels={1: 40, 2: 80, 3: 0, 4: 30, 5: 0},
        description="Dim fading red/purple"
    ),
    "REBIRTH": LightingState(
        name="REBIRTH",
        channels={1: 200, 2: 60, 3: 60, 4: 60, 5: 255},
        description="Warm white growing glow"
    ),
    "FINALE": LightingState(
        name="FINALE",
        channels={1: 255, 2: 255, 3: 220, 4: 180, 5: 255},
        description="Full bright warm celebration"
    ),
}
```

Channel assignments follow a standard RGBW + special fixture layout: channel 1 is intensity/dimmer, channels 2–4 are R/G/B, channel 5 is white or an effect channel (strobe in `OVERHEAT`, warm white in `REBIRTH`).

---

## 🔌 The DMX Controller

`lighting/controller.py` listens for OSC messages on port 9003 and applies the DMX values:

```python
# lighting/controller.py
from DMXEnttecPro import Controller
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from lighting.states import get_lighting_state

ENTTEC_PID = 24577   # FTDI product ID for auto-detection

class LightingController:
    def __init__(self, port: int = 9003, mock: bool = False):
        self.mock = mock
        if not mock:
            self.dmx = Controller(ENTTEC_PID)

        dispatcher = Dispatcher()
        dispatcher.map("/lighting/state", self._handle_state)
        self.server = BlockingOSCUDPServer(("127.0.0.1", port), dispatcher)

    def _handle_state(self, address: str, *args):
        state_name = str(args[0])
        state = get_lighting_state(state_name)

        if self.mock:
            print(f"[LIGHT MOCK] {state.name}: {state.channels}")
            return

        for ch, val in state.channels.items():
            self.dmx.set_channel(ch, max(0, min(255, val)))
        self.dmx.submit()

    def start(self):
        self.server.serve_forever()
```

The `mock=True` path is critical for rehearsals without the DMX hardware present. The entire show can be run, timed, and verified on a laptop with no physical lighting rig.

---

## 🎬 Projection: 10 Scenes in pygame

The projection subsystem runs a fullscreen pygame window on a second display. It receives `/projection/scene` OSC messages and transitions between 10 pre-defined scene images.

```python
# projection/scenes.py
from dataclasses import dataclass

@dataclass
class Scene:
    name: str
    image_file: str          # filename under assets/projection/
    background: tuple        # RGB fallback if image missing

SCENES: dict[str, Scene] = {
    "BLACKOUT":       Scene("BLACKOUT",       "",                    (0, 0, 0)),
    "GNR_LOGO":       Scene("GNR_LOGO",       "gnr_logo.png",        (0, 0, 0)),
    "DISNEY_CASTLE":  Scene("DISNEY_CASTLE",  "disney_castle.png",   (10, 10, 30)),
    "MICKEY_DRAWING": Scene("MICKEY_DRAWING", "mickey_drawing.png",  (255, 255, 255)),
    "LAMP_DRAWING":   Scene("LAMP_DRAWING",   "lamp_drawing.png",    (255, 255, 255)),
    "AI_ITERATIONS":  Scene("AI_ITERATIONS",  "ai_iterations.png",   (20, 20, 40)),
    "AI_SIGNATURE":   Scene("AI_SIGNATURE",   "ai_signature.png",    (0, 0, 0)),
    "WALT_SIGNATURE": Scene("WALT_SIGNATURE", "walt_signature.png",  (0, 0, 0)),
    "AXEL_SIGNATURE": Scene("AXEL_SIGNATURE", "axel_signature.png",  (0, 0, 0)),
    "TEAM_ROCKSTARS": Scene("TEAM_ROCKSTARS", "team_rockstars.png",  (0, 0, 0)),
}
```

The display loop in `projection/display.py` polls for a pending scene change and re-renders at 30fps:

```python
# projection/display.py (core loop)
def start(self):
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    while self.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        if self.pending_scene:
            self.current_scene = self.pending_scene
            self.pending_scene = None
            current_surface = self._load_image(self.current_scene)

        screen.fill(self.current_scene.background)
        if current_surface:
            screen.blit(current_surface, (0, 0))

        pygame.display.flip()
        clock.tick(30)

def _load_image(self, scene: Scene) -> pygame.Surface | None:
    if not scene.image_file:
        return None
    path = ASSETS_DIR / scene.image_file
    if not path.exists():
        # Graceful degradation: fall back to solid background colour
        return None
    img = pygame.image.load(str(path))
    return pygame.transform.scale(img, screen.get_size())
```

The graceful degradation on missing assets is intentional. During early development, projection assets often aren't ready — the show can run in full without them, falling back to the background colour.

---

## 🖥️ The Digital Twin

The digital twin is a 3D visualisation of the entire stage that runs in a browser and receives every OSC cue in real time. It serves two purposes: pre-visualisation before hardware is available, and a live monitor during technical rehearsals.

The architecture is a two-hop relay:

```
Conductor (Python)
    │
    │ OSC/UDP  port 9004
    ▼
Deno WebSocket bridge  (digital-twin/server/main.ts)
    │
    │ WebSocket  port 8765
    ▼
BabylonJS frontend  (digital-twin/frontend/)
```

**The Deno bridge** parses raw OSC UDP packets and broadcasts JSON events to all connected browser clients:

```typescript
// digital-twin/server/main.ts (simplified)
const OSC_PORT = 9004;
const WS_PORT  = 8765;

// Map OSC address -> JSON event type
function mapOSCToEvent(address: string, args: unknown[]): object {
    switch (address) {
        case "/lamp/state":
            return { type: "lamp",       value: args[0] };
        case "/projection/scene":
            return { type: "projection", value: args[0] };
        case "/lighting/state":
            return { type: "lighting",   value: args[0] };
        case "/transport/state":
            return { type: "transport",  value: args[0] };
        default:
            return { type: "unknown",    address, args };
    }
}

// UDP OSC listener
for await (const [data, _addr] of udpSocket) {
    const msg   = parseOSC(data);
    const event = mapOSCToEvent(msg.address, msg.args);
    broadcastJSON(event);   // send to all open WebSocket connections
}
```

**The BabylonJS frontend** receives these JSON events and updates the 3D scene accordingly — rotating the lamp mesh, swapping projected textures on the back wall, changing light colours. The performer can watch the digital twin on a second screen and see the full show as the conductor runs it, without needing a single piece of hardware.

---

## 🏛️ Architecture Decision: Why Mirror Everything to the Twin?

The mirror-to-twin pattern in `osc_sender.py` is unconditional: every cue sent to any subsystem is also forwarded to port 9004. No subsystem opts in or out.

The reason is operational safety. In a live show, the twin is the last fallback monitor — if a subsystem goes dark (DMX driver crash, pygame window closed), the twin still shows what *should* be happening, which makes diagnosis fast. If the twin only received messages when subsystems were healthy, it would go silent exactly when you needed it most.

This is the same logic that makes Paul Daniels' assistants watch *every* rehearsal, not just their own cues. The full picture is always in the room.

---

*Next: Episode 5 — Finding Its Voice: HiveMind satellite, Coqui XTTS synthesis, and the Raspberry Pi lamp head.*
