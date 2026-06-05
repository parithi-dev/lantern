import time
from collections import deque


class AlertManager:
    def __init__(self, max_alerts: int = 100):
        self._alerts: deque = deque(maxlen=max_alerts)
        self._known_devices: set[str] = set()
        self._latency_history: deque = deque(maxlen=30)
        self._latency_threshold: float = 200.0

    def set_latency_threshold(self, ms: float) -> None:
        self._latency_threshold = ms

    def check_new_devices(self, current_devices: list[dict]) -> list[dict]:
        alerts: list[dict] = []
        current_macs = {d['mac'] for d in current_devices if d.get('mac') and d['mac'] != 'Unknown'}

        for mac in current_macs:
            if mac not in self._known_devices:
                self._known_devices.add(mac)
                device = next((d for d in current_devices if d['mac'] == mac), None)
                if device:
                    alerts.append({
                        'type': 'device_joined',
                        'message': f"New device joined: {device.get('hostname') or device['ip']}",
                        'timestamp': time.time(),
                        'deviceIp': device['ip'],
                        'deviceMac': mac,
                    })

        return alerts

    def check_latency_spike(self, ping_router: float | None) -> list[dict]:
        alerts: list[dict] = []
        if ping_router is None:
            return alerts

        self._latency_history.append(ping_router)

        if ping_router > self._latency_threshold:
            avg = sum(self._latency_history) / len(self._latency_history) if self._latency_history else 0
            if avg > 0 and ping_router > avg * 2:
                alerts.append({
                    'type': 'latency_spike',
                    'message': f"Latency spike: {ping_router}ms (avg: {avg:.0f}ms)",
                    'timestamp': time.time(),
                    'deviceIp': '',
                    'value': ping_router,
                    'threshold': self._latency_threshold,
                })

        return alerts

    def add_alert(self, type_: str, message: str, device_ip: str = '') -> None:
        self._alerts.append({
            'type': type_,
            'message': message,
            'timestamp': time.time(),
            'deviceIp': device_ip,
        })

    def get_alerts(self, limit: int = 50) -> list[dict]:
        return list(self._alerts)[-limit:]

    def clear_alerts(self) -> None:
        self._alerts.clear()

    def seed_known_devices(self, devices: list[dict]) -> None:
        for d in devices:
            if d.get('mac') and d['mac'] != 'Unknown':
                self._known_devices.add(d['mac'])


alert_manager = AlertManager()
