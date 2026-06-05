# NetPulse — Home Network Monitor
### Full Project Plan (Option B: Local Agent + Angular Web UI)

---

## What It Does

When you open `localhost:4200` in your browser you see:

- Your router's IP, ISP name, public IP, upload/download speed
- Every device connected to your WiFi — phone, laptop, TV, smart bulbs — with their IP, MAC address, hostname, and whether they're online
- Bandwidth usage per device in real time
- Ping/latency to your router and to google.com updated live
- Alerts when a new unknown device joins your network, or when latency spikes

---

## Architecture

```
Your Machine
├── Python Agent (runs in background)
│   ├── Scans local network (nmap / scapy)
│   ├── Pings router + internet
│   ├── Reads bandwidth stats
│   └── Exposes FastAPI at localhost:8000
│       ├── GET  /devices        → all connected devices
│       ├── GET  /health         → router ping, internet ping, speeds
│       ├── GET  /alerts         → spike/new device events
│       └── WS   /ws/live        → real-time stream to Angular
│
└── Angular 21 Frontend (localhost:4200)
    ├── Reads from localhost:8000
    ├── Shows dashboard, devices table, charts
    └── WebSocket receives live updates
```

---

## Tech Stack — 100% Free

### Python Agent
| Package | Purpose |
|---|---|
| `FastAPI` | REST + WebSocket server |
| `python-nmap` | Network scanning — find connected devices |
| `psutil` | Bandwidth, CPU, memory stats |
| `ping3` | Ping router and internet |
| `schedule` | Run scans every 30 seconds |
| `sqlite3` (built-in) | Store history locally |
| `pyinstaller` | Bundle as a single executable for distribution |

### Angular 21 Frontend
| Package | Purpose |
|---|---|
| Angular 21 (Zoneless + Signals) | Core framework |
| AG Grid Community | Devices table |
| Highcharts | Bandwidth and latency charts |
| Angular Material | UI components |
| Native WebSocket API | Live updates from Python agent |

---

## Pages

### 1. `/dashboard` — Overview
- Public IP, ISP name, router IP
- Current download / upload speed (Mbps)
- Ping to router (ms) + ping to google.com (ms)
- Live Highcharts line chart — latency last 30 minutes
- Alert feed — new devices joined, latency spikes

### 2. `/devices` — Connected Devices
- AG Grid table with every device on your network
- Columns: Hostname, IP, MAC Address, Vendor, Status, Last Seen
- Green dot = online, grey = offline
- Click a device → side panel with ping history chart

### 3. `/bandwidth` — Bandwidth Usage
- Highcharts area chart — total download/upload over time
- Per-device breakdown

### 4. `/settings` — Configuration
- Scan interval (30s / 60s / 5 min)
- Alert thresholds (latency above X ms = alert)
- Known devices — label your devices ("Parithi's Phone", "Smart TV")

---

## API Endpoints (Python Agent)

```
GET  /health
     → { routerIp, publicIp, isp, pingRouter, pingInternet, downloadMbps, uploadMbps }

GET  /devices
     → [{ ip, mac, hostname, vendor, status, lastSeen }]

GET  /alerts
     → [{ type, message, timestamp, deviceIp }]

GET  /history/latency?minutes=30
     → [{ timestamp, pingRouter, pingInternet }]

WS   /ws/live
     → streams { devices, health, alerts } every 10 seconds
```

---

## Folder Structure

```
netpulse/
├── agent/                        # Python backend
│   ├── main.py                   # FastAPI app entry point
│   ├── scanner.py                # nmap device scanning
│   ├── health.py                 # ping + speed checks
│   ├── alerts.py                 # alert logic
│   ├── database.py               # SQLite history
│   ├── websocket.py              # WS broadcast
│   └── requirements.txt
│
├── frontend/                     # Angular 21 app
│   ├── src/app/
│   │   ├── core/
│   │   │   └── services/
│   │   │       ├── network.service.ts    # signals + polling
│   │   │       └── websocket.service.ts  # WS connection
│   │   ├── features/
│   │   │   ├── dashboard/
│   │   │   ├── devices/
│   │   │   ├── bandwidth/
│   │   │   └── settings/
│   │   └── shared/
│   │       ├── stat-card/
│   │       ├── live-chart/
│   │       └── alert-feed/
│   └── angular.json
│
├── .github/
│   └── workflows/
│       └── ci.yml                # lint → test → build
│
└── README.md
```

---

## Build Order (8 Weekends)

| Weekend | What You Build |
|---|---|
| 1 | Python agent — FastAPI running, `/health` endpoint returning router ping and public IP |
| 2 | `/devices` endpoint — nmap scan returning all connected devices with MAC and hostname |
| 3 | WebSocket — agent pushes live updates every 10s |
| 4 | Angular dashboard — stat cards + live latency chart working end to end |
| 5 | Angular devices page — AG Grid with real device data from the agent |
| 6 | Bandwidth charts + alert logic in the agent |
| 7 | Settings page + device labelling + SQLite history |
| 8 | PyInstaller packaging + README + demo screen recording |

---

## Angular 21 Key Patterns Used

```typescript
// NetworkService — signals replace BehaviorSubject entirely
@Injectable({ providedIn: 'root' })
export class NetworkService {
  devices     = signal<Device[]>([]);
  health      = signal<HealthData | null>(null);
  alerts      = signal<Alert[]>([]);

  // computed — auto-derived, no manual subscriptions
  onlineCount = computed(() => this.devices().filter(d => d.status === 'online').length);
  avgLatency  = computed(() => this.health()?.pingRouter ?? 0);
  slowDevices = computed(() => this.devices().filter(d => d.latency > 200).length);
}
```

```typescript
// WebSocket service — native browser WebSocket
@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private svc = inject(NetworkService);

  connect() {
    const ws = new WebSocket('ws://localhost:8000/ws/live');
    ws.onmessage = ({ data }) => {
      const payload = JSON.parse(data);
      this.svc.devices.set(payload.devices);
      this.svc.health.set(payload.health);
      this.svc.alerts.set(payload.alerts);
    };
  }
}
```

---

## Python Agent Key Code

```python
# main.py
from fastapi import FastAPI, WebSocket
from scanner import scan_devices
from health import get_health
import asyncio, json

app = FastAPI()

@app.get("/devices")
def devices():
    return scan_devices()

@app.get("/health")
def health():
    return get_health()

@app.websocket("/ws/live")
async def live(ws: WebSocket):
    await ws.accept()
    while True:
        payload = {
            "devices": scan_devices(),
            "health":  get_health(),
            "alerts":  get_alerts(),
        }
        await ws.send_text(json.dumps(payload))
        await asyncio.sleep(10)
```

```python
# scanner.py
import nmap

def scan_devices():
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.0/24', arguments='-sn')
    devices = []
    for host in nm.all_hosts():
        devices.append({
            "ip":       host,
            "hostname": nm[host].hostname(),
            "mac":      nm[host]['addresses'].get('mac', 'Unknown'),
            "status":   nm[host].state(),
        })
    return devices
```

---

## CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run test -- --watch=false --browsers=ChromeHeadless
      - run: npm run build -- --configuration production

  agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r agent/requirements.txt
      - run: python -m pytest agent/tests/
```

---

## What Makes This Portfolio-Worthy

- **Real product** you actually use at home every day
- **Full-stack thinking** — system-level Python + modern Angular 21
- **WebSocket integration** is rare in frontend portfolios
- **Local-first** — no cloud, no subscription, privacy-respecting
- **Angular 21 modern APIs** — Zoneless, Signals, Standalone, OnPush everywhere
- **Looks professional** — comparable to Fing app or Pi-hole UI, but you built it

---

## Setup Commands

```bash
# Clone and set up
git clone https://github.com/yourusername/netpulse
cd netpulse

# Python agent
cd agent
pip install -r requirements.txt
python main.py
# Agent runs at http://localhost:8000

# Angular frontend (new terminal)
cd ../frontend
npm install
ng serve
# App runs at http://localhost:4200
```

---

## README Must-Haves

- Screenshot or GIF of the dashboard with real device data
- Architecture diagram (boxes showing Angular ↔ FastAPI ↔ Network)
- Setup instructions for Mac, Windows, Linux
- "Why I built this" section — shows product thinking, not just coding

---

*Built with Angular 21 · FastAPI · python-nmap · AG Grid · Highcharts*