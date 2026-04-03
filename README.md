# Roller Blind Automation

Thesis project by Kevin Shocosh and John Beskow.

Automates roller blinds using a Raspberry Pi and an nRF52832 microcontroller connected over BLE. The system runs on a daily schedule, pulls weather forecasts from SMHI, sends morning notifications via Discord, and starts a Spotify playlist at wake-up. The Discord bot accepts natural language commands in Swedish, English, and Spanish — interpreted by GPT-3.5 — and relays them as BLE messages to the microcontroller.

---

## Architecture

```
Raspberry Pi
├── main.py              scheduler, threading
├── central.py           BLE central (Bleak, async)
├── smhi_api.py          weather forecast (SMHI open API)
├── discord_bot.py       outbound weather DM
├── discord_listener.py  inbound commands via GPT-3.5
├── spotify_api.py       playback control (Spotipy)
├── display.py           16x2 LCD output
└── motor_control.py     GPIO motor control (L293D)
        |
        | Bluetooth Low Energy (GATT / NUS)
        |
nRF52832
├── main.c               BLE UART peripheral
├── motor.c              DC motor driver
└── lcd.c                LCD driver
```

---

## Features

- Blinds open on a weekday/weekend schedule and close every night at 22:00
- Weather forecast fetched from SMHI each morning; rain/snow alerts and temperature sent as a Discord DM
- Spotify playlist starts on a configured device a few minutes after the blinds open
- Discord bot accepts commands in natural language; GPT-3.5 maps them to BLE commands sent to the nRF52832
- 16x2 LCD displays weather status and temperature
- BLE auto-reconnect handled by a background shell script

---

## Stack

| Component | Technology |
|---|---|
| Host | Raspberry Pi, Python 3 |
| Microcontroller | Nordic nRF52832, nRF5 SDK (C) |
| BLE | Bleak (async GATT central) |
| Motor driver | L293D H-bridge, 2× DC motors |
| Weather | SMHI Open Data — pmp3g v2 |
| Music | Spotify Web API, Spotipy |
| Notifications | Discord Bot API |
| NLP | OpenAI GPT-3.5-turbo |
| Display | RPLCD, 16×2 GPIO LCD |
| Scheduler | schedule |

---

## Project Structure

```
.
├── main.py
├── central.py
├── smhi_api.py
├── discord_bot.py
├── discord_listener.py
├── spotify_api.py
├── motor_control.py
├── display.py
├── requirements.txt
├── scripts/
│   ├── ble_reconnect.sh
│   └── raspotify_boot.sh
└── Nrf52832/
    ├── main.c
    ├── motor.c / motor.h
    ├── lcd.c / lcd.h
    └── sdk_config.h
```

---

## Setup

**Requirements**

- Raspberry Pi with GPIO and BLE support
- nRF52832 dev kit flashed with the firmware in `Nrf52832/`
- Python 3.9+
- Discord bot token and a server channel
- Spotify Developer app (Client ID + Secret)
- OpenAI API key

**Install**

```bash
git clone https://github.com/your-username/examenarbete.git
cd examenarbete
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Environment variables**

Create a `.env` file in the project root:

```
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
SPOTIFY_DEVICE_NAME=

DISCORD_TOKEN=
DISCORD_CHANNEL_ID=
USER_ID=

OPENAI_API_KEY=
```

**Flash firmware**

Open `Nrf52832/` in SEGGER Embedded Studio or build with the nRF5 SDK and flash to the board.

**Run**

```bash
python main.py
```

---

## Discord Commands

The bot accepts commands in Swedish, English, and Spanish.

| Action | Examples |
|---|---|
| Open / close blinds | `öppna`, `stäng`, `open`, `close`, `abre`, `cierra` |
| Toggle LED | `sätt på`, `sätt av`, `turn on`, `turn off`, `apagar` |
| Create LED | `skapa`, `create`, `crear` |
| Delete LED | `ta bort`, `delete`, `borrar` |
| Select LED | `led 1`, `välj led 2`, `led3` |

---

## Authors

Kevin Shocosh and John Beskow —  IoT-/Systemutvecklare - Stockholm Tekniska Institut, 2025
