# NetPulse — Implementation & Commit Plan

## Overview
Build a home network monitor with a cross-platform Python agent (FastAPI) and an Angular 22 frontend. This plan breaks the original 8-weekend schedule into 18 ordered commits across 8 phases.

---

## Commit Plan

### Phase 1 — Python Agent Foundation (Commits 1–3)
| # | Commit Message | What's Included |
|---|----------------|-----------------|
| 1 | `feat(agent): scaffold agent directory with cross-platform utils` | `agent/` structure, `requirements.txt`, `utils.py` (OS detection, gateway, ping, MAC vendor DB), `__init__.py` |
| 2 | `feat(agent): add health checks — ping, public IP, ISP, bandwidth` | `health.py` — cross-platform ping (Linux/Mac/Windows), public IP via ipify, ISP via ip-api.com + RDAP, bandwidth via psutil, speed measurement |
| 3 | `feat(agent): FastAPI entry point with /health endpoint and CORS` | `main.py` — lifespan events, CORS, `/health` endpoint, `run.py` for dev server |

### Phase 2 — Device Scanning (Commits 4–5)
| # | Commit Message | What's Included |
|---|----------------|-----------------|
| 4 | `feat(agent): cross-platform network scanner (nmap + arp fallback)` | `scanner.py` — nmap primary, `arp -a` fallback for Windows/Mac/Linux, MAC vendor lookup |
| 5 | `feat(agent): add /devices endpoint with structured device data` | Integrate scanner into FastAPI, return device list with IP/MAC/hostname/vendor/status |

### Phase 3 — Real-time Updates (Commits 6–7)
| # | Commit Message | What's Included |
|---|----------------|-----------------|
| 6 | `feat(agent): WebSocket connection manager + background scheduler` | `connection_manager.py` — broadcast to all WS clients, `_background_loop` in main.py |
| 7 | `feat(agent): WS /ws/live endpoint streaming devices, health, alerts` | WebSocket endpoint, periodic broadcast every 30s (configurable) |

### Phase 4 — History & Alerts (Commits 8–9)
| # | Commit Message | What's Included |
|---|----------------|-----------------|
| 8 | `feat(agent): SQLite database for latency, device, and alert history` | `database.py` — schema, CRUD for latency_history, device_history, alerts, settings |
| 9 | `feat(agent): alert logic — new device detection, latency spikes` | `alerts.py` — AlertManager class, new device/ latency spike detection, `/alerts` endpoint |

### Phase 5 — Angular Frontend Foundation (Commits 10–12)
| # | Commit Message | What's Included |
|---|----------------|-----------------|
| 10 | `feat(frontend): add Angular Material, AG Grid, Highcharts, routing` | Install deps, configure app.routes.ts for 4 pages, layout shell |
| 11 | `feat(frontend): core services — NetworkService, WebSocketService, HttpService` | Signal-based services, WS reconnection, httpResource polling |
| 12 | `feat(frontend): dashboard page with stat cards, latency chart, alerts` | Public IP/ISP cards, ping cards, Highcharts latency chart, alert feed |

### Phase 6 — Devices & Bandwidth (Commits 13–14)
| # | Commit Message | What's Included |
|---|----------------|-----------------|
| 13 | `feat(frontend): devices page with AG Grid table + detail panel` | Full-width grid, green/grey status dots, click-to-side-panel with ping history |
| 14 | `feat(frontend): bandwidth page with Highcharts area chart` | Total dl/ul over time, per-device breakdown |

### Phase 7 — Settings & Polish (Commits 15–16)
| # | Commit Message | What's Included |
|---|----------------|-----------------|
| 15 | `feat(frontend): settings page — scan interval, thresholds, device labels` | Form controls synced to agent POST /settings, known device labelling in SQLite |
| 16 | `feat(frontend): UI polish — navigation, theme, loading states, responsive` | Navigation rail/bar, dark/light theme toggle, skeleton loaders, responsive layout |

### Phase 8 — Packaging (Commits 17–18)
| # | Commit Message | What's Included |
|---|----------------|-----------------|
| 17 | `chore(agent): PyInstaller config for cross-platform executable` | `.spec` file, build script, single-exe packaging for Mac/Win/Linux |
| 18 | `docs: CI/CD workflow, README with architecture diagram and setup guide` | GitHub Actions CI, comprehensive README |

---

## Current Status

| Phase | Status |
|-------|--------|
| Phase 1 (Commits 1–3) | ✅ Committed |
| Phase 2 (Commits 4–5) | ✅ Committed (included in Phase 1) |
| Phase 3 (Commits 6–7) | ✅ Committed (included in Phase 1) |
| Phase 4 (Commits 8–9) | ✅ Committed (included in Phase 1) |
| Phase 5 (Commits 10–12) | ✅ Committed |
| Phase 6 (Commits 13–14) | ❌ Not started |
| Phase 7 (Commits 15–16) | ❌ Not started |
| Phase 8 (Commits 17–18) | ❌ Not started |

---

## Running the Agent

```bash
# From project root
cd agent
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m agent.run

# Or with uvicorn directly
uvicorn agent.main:app --reload --host 127.0.0.1 --port 8000
```

Agent runs at `http://localhost:8000`. Visit `http://localhost:8000/docs` for Swagger UI.
