import os
import subprocess
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .utils import (
    IS_WINDOWS,
    IS_MAC,
    IS_LINUX,
    get_mac_vendor,
    get_local_ip,
    get_default_gateway,
    get_network_interfaces,
)


def _ping_host(ip: str) -> str | None:
    try:
        if IS_WINDOWS:
            subprocess.run(
                ['ping', '-n', '1', '-w', '1000', ip],
                capture_output=True,
                timeout=2,
            )
        else:
            subprocess.run(
                ['ping', '-c', '1', '-W', '1', ip],
                capture_output=True,
                timeout=2,
            )
        return ip
    except Exception:
        return None


def _ping_sweep(subnet_prefix: str):
    ips = [f'{subnet_prefix}.{i}' for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=50) as pool:
        list(pool.map(_ping_host, ips))


def _arp_scan() -> list[dict]:
    devices: list[dict] = []
    seen_macs: set[str] = set()

    if IS_LINUX:
        try:
            result = subprocess.run(
                ['arp', '-n'], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4 and '(' in line:
                    ip = parts[1].strip('()')
                    mac = parts[3] if len(parts) > 3 else 'Unknown'
                    if mac not in seen_macs and mac != 'Unknown' and '(incomplete)' not in line:
                        seen_macs.add(mac)
                        devices.append({
                            'ip': ip,
                            'mac': mac,
                            'hostname': _resolve_hostname(ip),
                            'vendor': get_mac_vendor(mac),
                            'status': 'online' if '(incomplete)' not in line else 'offline',
                            'lastSeen': time.time(),
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        try:
            with open('/proc/net/arp') as f:
                for line in f.readlines()[1:]:
                    parts = line.split()
                    if len(parts) >= 4 and parts[3] != '00:00:00:00:00:00':
                        ip = parts[0]
                        mac = parts[3]
                        if mac not in seen_macs:
                            seen_macs.add(mac)
                            devices.append({
                                'ip': ip,
                                'mac': mac,
                                'hostname': _resolve_hostname(ip),
                                'vendor': get_mac_vendor(mac),
                                'status': 'online' if parts[2] == '0x2' else 'offline',
                                'lastSeen': time.time(),
                            })
        except (FileNotFoundError, IndexError):
            pass

    elif IS_MAC:
        try:
            result = subprocess.run(
                ['arp', '-a'], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                match = re.match(r'\? \(([\d.]+)\) at ([a-fA-F0-9:]+)', line)
                if match:
                    ip = match.group(1)
                    mac = match.group(2)
                    if mac not in seen_macs:
                        seen_macs.add(mac)
                        devices.append({
                            'ip': ip,
                            'mac': mac,
                            'hostname': _resolve_hostname(ip),
                            'vendor': get_mac_vendor(mac),
                            'status': 'online',
                            'lastSeen': time.time(),
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    elif IS_WINDOWS:
        try:
            result = subprocess.run(
                ['arp', '-a'], capture_output=True, text=True, timeout=5, shell=True
            )
            for line in result.stdout.splitlines():
                match = re.match(r'^\s*([\d.]+)\s+([a-fA-F0-9-]+)', line)
                if match:
                    ip = match.group(1)
                    mac = match.group(2).replace('-', ':')
                    if mac not in seen_macs and mac != 'ff:ff:ff:ff:ff:ff':
                        seen_macs.add(mac)
                        devices.append({
                            'ip': ip,
                            'mac': mac,
                            'hostname': _resolve_hostname(ip),
                            'vendor': get_mac_vendor(mac),
                            'status': 'online',
                            'lastSeen': time.time(),
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return devices


def _resolve_hostname(ip: str) -> str:
    try:
        import socket
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except Exception:
        return ''


_last_devices: list[dict] | None = None
_last_scan_time: float = 0


def scan_devices(
    use_nmap: bool = True,
    alert_manager: object | None = None,
    fast: bool = False,
) -> list[dict]:
    global _last_devices, _last_scan_time

    local_ip = get_local_ip()
    subnet_prefix = '.'.join(local_ip.split('.')[:3]) if local_ip else None
    is_root = not IS_WINDOWS and os.geteuid() == 0

    if use_nmap and is_root:
        try:
            import nmap
            nm = nmap.PortScanner()
            if not subnet_prefix:
                return _arp_scan()
            subnet = subnet_prefix + '.0/24'
            nm.scan(hosts=subnet, arguments='-sn')
            devices = []
            for host in nm.all_hosts():
                mac = nm[host]['addresses'].get('mac', 'Unknown')
                devices.append({
                    'ip': host,
                    'hostname': nm[host].hostname() or '',
                    'mac': mac,
                    'vendor': get_mac_vendor(mac),
                    'status': nm[host].state(),
                    'lastSeen': time.time(),
                })
            if alert_manager:
                devices = alert_manager.enrich_devices(devices)
            _last_devices = devices
            _last_scan_time = time.time()
            return devices
        except (ImportError, Exception):
            pass

    if not fast and subnet_prefix and IS_LINUX:
        _ping_sweep(subnet_prefix)

    devices = _arp_scan()
    if alert_manager:
        devices = alert_manager.enrich_devices(devices)

    if _last_devices and not fast:
        existing = {d['mac'] for d in devices if d.get('mac') and d['mac'] != 'Unknown'}
        for d in _last_devices:
            mac = d.get('mac', '')
            if mac and mac not in existing:
                devices.append(d)

    _last_devices = devices
    _last_scan_time = time.time()
    return devices


def get_cached_devices() -> list[dict] | None:
    return _last_devices
