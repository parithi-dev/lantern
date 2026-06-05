import subprocess
import re
import time
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


def scan_devices(use_nmap: bool = True) -> list[dict]:
    if use_nmap:
        try:
            import nmap
            nm = nmap.PortScanner()
            local_ip = get_local_ip()
            if not local_ip:
                return _arp_scan()
            subnet = '.'.join(local_ip.split('.')[:3]) + '.0/24'
            nm.scan(hosts=subnet, arguments='-sn --unprivileged')
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
            return devices
        except ImportError:
            pass
        except Exception:
            pass

    return _arp_scan()
