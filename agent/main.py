import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import FileResponse

from .health import get_health
from .scanner import scan_devices
from .alerts import alert_manager
from .database import init_db, save_latency, save_devices, save_alert
from .connection_manager import manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(name)s  %(levelname)s  %(message)s',
)
log = logging.getLogger('netpulse')

STATIC_DIR = Path(__file__).parent.parent / 'dist' / 'lantern' / 'browser'


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as e:
            if e.status_code == 404:
                return await super().get_response('index.html', scope)
            raise


_scan_interval: float = 30.0
_background_task: asyncio.Task | None = None


async def _background_loop():
    log.info('Background scan loop started (interval=%ss)', _scan_interval)
    while True:
        try:
            health = await get_health()
            devices = scan_devices(alert_manager=alert_manager)
            new_alerts = alert_manager.check_new_devices(devices)
            latency_alerts = alert_manager.check_latency_spike(health.get('pingRouter'))
            all_alerts = new_alerts + latency_alerts

            save_latency(health.get('pingRouter'), health.get('pingInternet'))
            save_devices(devices)
            for alert in all_alerts:
                save_alert(alert)

            payload = {
                'devices': devices,
                'health': health,
                'alerts': alert_manager.get_alerts(limit=20),
            }
            await manager.broadcast(payload)
        except Exception as e:
            log.error('Background loop error: %s', e)
        await asyncio.sleep(_scan_interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    log.info('Database initialized')
    global _background_task
    _background_task = asyncio.create_task(_background_loop())
    yield
    if _background_task:
        _background_task.cancel()


app = FastAPI(
    title='NetPulse Agent',
    version='1.0.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
async def health_endpoint():
    return await get_health(force_refresh=True)


@app.get('/devices')
def devices_endpoint():
    return scan_devices(alert_manager=alert_manager)


@app.get('/alerts')
def alerts_endpoint(limit: int = 50):
    return alert_manager.get_alerts(limit=limit)


@app.get('/history/latency')
def latency_history(minutes: int = 30):
    from .database import get_latency_history
    return get_latency_history(minutes=minutes)


@app.get('/settings')
def get_settings():
    from .database import get_setting
    return {
        'scanInterval': float(get_setting('scan_interval', '30')),
        'latencyThreshold': float(get_setting('latency_threshold', '200')),
    }


@app.post('/settings')
def update_settings(scan_interval: float | None = None, latency_threshold: float | None = None):
    from .database import set_setting
    global _scan_interval
    if scan_interval is not None:
        set_setting('scan_interval', str(scan_interval))
        _scan_interval = scan_interval
    if latency_threshold is not None:
        set_setting('latency_threshold', str(latency_threshold))
        alert_manager.set_latency_threshold(latency_threshold)
    return {'status': 'ok'}


@app.websocket('/ws/live')
async def live_websocket(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(ws)


@app.get('/')
async def root():
    return FileResponse(STATIC_DIR / 'index.html')


if STATIC_DIR.is_dir():
    app.mount('/', SPAStaticFiles(directory=str(STATIC_DIR), html=True), name='app')
