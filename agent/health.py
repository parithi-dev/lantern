import time
import httpx
import psutil

from .utils import ping_host, get_default_gateway, get_local_ip


_last_health: dict | None = None
_last_health_time: float = 0


async def get_public_ip_info() -> dict:
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
            resp = await client.get('https://api.ipify.org?format=json')
            ip_data = resp.json()
            public_ip = ip_data['ip']

            isp = 'Unknown'
            try:
                ipinfo = await client.get(f'http://ip-api.com/json/{public_ip}')
                if ipinfo.status_code == 200:
                    data = ipinfo.json()
                    if data.get('status') == 'success' and data.get('isp'):
                        isp = data['isp']
            except Exception:
                pass

            if isp == 'Unknown':
                try:
                    isp_resp = await client.get(
                        f'https://rdap.arin.net/registry/ip/{public_ip}',
                        headers={'Accept': 'application/json'},
                    )
                    if isp_resp.status_code == 200:
                        data = isp_resp.json()
                        for key in ('org', 'name'):
                            if key in data:
                                isp = data[key]
                                break
                except Exception:
                    pass

            return {'publicIp': public_ip, 'isp': isp}
    except Exception:
        return {'publicIp': 'Unknown', 'isp': 'Unknown'}


def get_bandwidth() -> dict:
    counters = psutil.net_io_counters()
    return {
        'bytesSent': counters.bytes_sent,
        'bytesRecv': counters.bytes_recv,
        'packetsSent': counters.packets_sent,
        'packetsRecv': counters.packets_recv,
    }


def measure_speed(duration: float = 1.0) -> dict:
    counters_before = psutil.net_io_counters()
    time.sleep(duration)
    counters_after = psutil.net_io_counters()

    download_bps = (counters_after.bytes_recv - counters_before.bytes_recv) * 8 / duration
    upload_bps = (counters_after.bytes_sent - counters_before.bytes_sent) * 8 / duration

    return {
        'downloadMbps': round(download_bps / 1_000_000, 2),
        'uploadMbps': round(upload_bps / 1_000_000, 2),
    }


async def get_health(force_refresh: bool = False) -> dict:
    global _last_health, _last_health_time

    now = time.time()
    if not force_refresh and _last_health and (now - _last_health_time) < 5:
        return _last_health

    router_ip = get_default_gateway()
    local_ip = get_local_ip()

    ping_router = ping_host(router_ip) if router_ip else None
    ping_internet = ping_host('8.8.8.8')

    ip_info = await get_public_ip_info()
    speed = measure_speed(1.0)

    health_data = {
        'routerIp': router_ip or 'Unknown',
        'localIp': local_ip or 'Unknown',
        'publicIp': ip_info['publicIp'],
        'isp': ip_info['isp'],
        'pingRouter': ping_router,
        'pingInternet': ping_internet,
        'downloadMbps': speed['downloadMbps'],
        'uploadMbps': speed['uploadMbps'],
        'timestamp': now,
    }

    _last_health = health_data
    _last_health_time = now
    return health_data


def get_cached_health() -> dict | None:
    return _last_health
