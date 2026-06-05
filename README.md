# NetPulse — Home Network Monitor

Real-time network monitoring for your home. See every connected device, track bandwidth usage, monitor latency, and get alerts when something changes — all running locally on your machine with no cloud dependency.

---

## Features

- **Live Dashboard** — Public IP, ISP, router ping, internet latency, download/upload speeds at a glance
- **Device Discovery** — Every device on your network with IP, MAC address, hostname, vendor, and online status
- **Real-time Bandwidth** — Download and upload speed charts updated every 5 seconds
- **Latency Monitoring** — Router and internet ping with historical chart (up to 30 minutes)
- **Alert System** — Get notified when a new unknown device joins or when latency spikes
- **Device Labelling** — Name your devices so you can identify them easily
- **Configurable** — Adjust scan interval and alert thresholds to your needs
- **Zero Cloud** — Everything runs locally. No data ever leaves your machine.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Your Machine                       │
│                                                      │
│  ┌─────────────────────┐     ┌──────────────────┐   │
│  │   Python Agent       │     │  Angular 22 App   │   │
│  │   (FastAPI)          │     │  (Browser)        │   │
│  │                      │     │                   │   │
│  │  ┌───────────────┐   │     │  ┌─────────────┐  │   │
│  │  │  Network Scan  │──┼─────┼─▶│  Dashboard   │  │   │
│  │  │  (nmap/arp)    │   │     │  └─────────────┘  │   │
│  │  └───────────────┘   │     │  ┌─────────────┐  │   │
│  │  ┌───────────────┐   │     │  │  Devices     │  │   │
│  │  │  Health Checks │──┼─────┼─▶│  (AG Grid)   │  │   │
│  │  │  (ping/ISP)    │   │     │  └─────────────┘  │   │
│  │  └───────────────┘   │     │  ┌─────────────┐  │   │
│  │  ┌───────────────┐   │     │  │  Bandwidth  │  │   │
│  │  │  WebSocket    │◀─┼─────┼─▶│  (Charts)    │  │   │
│  │  │  Broadcaster  │   │     │  └─────────────┘  │   │
│  │  └───────────────┘   │     │  ┌─────────────┐  │   │
│  │  ┌───────────────┐   │     │  │  Settings    │  │   │
│  │  │  SQLite DB    │   │     │  └─────────────┘  │   │
│  │  └───────────────┘   │     │                   │   │
│  └─────────────────────┘     └──────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Agent** (`localhost:8000`) — Python FastAPI server that scans your network and exposes REST + WebSocket endpoints.

**Frontend** (`localhost:4200`) — Angular 22 app that fetches data from the agent and displays it in a modern dark-themed dashboard.

---

## Setup

### Prerequisites

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Agent runtime |
| Node.js | 22+ | Frontend build |
| npm | 10+ | Package manager |
| nmap _(optional)_ | Latest | Faster device scanning |

### macOS

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/netpulse
cd netpulse

# 2. Set up the Python agent
cd agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Start the agent
python -m agent.run

# 4. In another terminal — start the frontend
cd ..
npm install
npx ng serve
```

Open `http://localhost:4200` in your browser.

### Windows

```powershell
# 1. Clone the repo
git clone https://github.com/yourusername/netpulse
cd netpulse

# 2. Set up the Python agent
cd agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Start the agent
python -m agent.run

# 4. In another terminal — start the frontend
cd ..
npm install
npx ng serve
```

### Linux

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/netpulse
cd netpulse

# 2. Set up the Python agent
cd agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Start the agent (sudo may be needed for network scanning)
sudo .venv/bin/python -m agent.run

# 4. In another terminal — start the frontend
cd ..
npm install
npx ng serve
```

> **Note:** Network scanning requires root/admin privileges on most systems. Without them, the agent falls back to reading the ARP cache, which shows only devices that have recently communicated with your machine.

---

## Using the App

### Dashboard (`/dashboard`)
The overview page shows your network status at a glance:
- **Router** — gateway IP and local machine IP
- **Download/Upload** — current bandwidth usage in Mbps
- **Router Ping** — latency to your gateway
- **Internet Ping** — latency to Google DNS (8.8.8.8)
- **Devices** — how many devices are online / total
- **Latency Chart** — historical ping over time
- **Live Alerts** — notification feed for new devices and latency spikes

### Devices (`/devices`)
A full list of every device on your network with:
- Sortable and filterable columns
- Pagination for large networks
- Click any device to open a detail panel with latency history

### Bandwidth (`/bandwidth`)
Real-time download and upload speed charts that update every 5 seconds.

### Settings (`/settings`)
- **Scan Interval** — how often the agent rescans your network (15s / 30s / 1m / 5m)
- **Latency Threshold** — alert when ping exceeds this value (50–500ms)
- **Device Labeling** — view all detected devices by MAC address

---

## Project Structure

```
netpulse/
├── agent/                           # Python backend
│   ├── main.py                      # FastAPI app — all endpoints
│   ├── health.py                    # Ping, public IP, ISP, bandwidth
│   ├── scanner.py                   # nmap + arp device scanning
│   ├── alerts.py                    # New device + latency spike detection
│   ├── database.py                  # SQLite history and settings
│   ├── connection_manager.py        # WebSocket broadcast
│   ├── utils.py                     # Cross-platform OS utilities
│   ├── requirements.txt             # Python dependencies
│   ├── netpulse.spec                # PyInstaller build spec
│   ├── build.py                     # Build script for standalone exe
│   └── run.py / run_standalone.py   # Dev / prod entry points
│
├── src/app/                         # Angular frontend
│   ├── core/services/               # NetworkService + WebSocketService
│   ├── features/                    # Page components
│   │   ├── dashboard/               # Overview with stat cards + chart
│   │   ├── devices/                 # AG Grid table + detail panel
│   │   ├── bandwidth/              # Live speed charts
│   │   └── settings/               # Configuration
│   └── shared/                      # Reusable components
│       ├── stat-card/               # Glass-morphism metric card
│       ├── live-chart/              # Highcharts areaspline wrapper
│       └── alert-feed/              # Real-time alert list
│
├── .github/workflows/ci.yml         # CI pipeline
└── docs/
    ├── plan.md                      # Original project plan
    └── implementation-plan.md       # Commit-by-commit plan
```

---

## Tech Stack

### Backend (Python)
| Technology | Purpose |
|---|---|
| FastAPI | REST + WebSocket server |
| python-nmap | Network device discovery |
| psutil | Bandwidth and system stats |
| ping3 | Ping latency measurement |
| httpx | Public IP and ISP lookup |
| SQLite | Local history storage |
| PyInstaller | Standalone executable packaging |

### Frontend (Angular 22)
| Technology | Purpose |
|---|---|
| Angular 22 | Framework (standalone, signals) |
| Angular Material | UI primitives |
| AG Grid | Devices table |
| Highcharts | Latency and bandwidth charts |
| WebSocket API | Real-time data streaming |

### Design
- Dark "Mission Control" theme with glass-morphism cards
- Custom glow effects and pulse animations
- JetBrains Mono for data, DM Sans for UI
- Subtle dot-grid background
- Responsive layout for desktop and tablet

---

## Build a Standalone Executable

```bash
cd agent
pip install pyinstaller
python build.py
```

The executable will be in `agent/dist/netpulse` (or `netpulse.exe` on Windows). Run it directly without Python.

---

## Why I Built This

I wanted a **privacy-first** alternative to cloud-based network monitoring tools. Most home network apps either require a subscription, phone app with tracking, or upload your data to their servers.

NetPulse is:

- **Local-first** — everything runs on your machine, no cloud dependency
- **Free** — 100% open source, no paid tiers, no ads
- **Real** — actually scans your real network, not simulated data
- **Beautiful** — designed with care, not a generic admin panel

It's the kind of tool I wished existed: a network monitor that looks like a modern product, respects my privacy, and I can run on any machine in minutes.

---

## License

MIT
