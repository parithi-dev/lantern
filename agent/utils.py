import platform
import subprocess
import re
import socket
from pathlib import Path


SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'
IS_MAC = SYSTEM == 'darwin'
IS_LINUX = SYSTEM == 'linux'


def get_default_gateway() -> str | None:
    if IS_LINUX:
        try:
            result = subprocess.run(
                ['ip', 'route'], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if line.startswith('default'):
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            try:
                with open('/proc/net/route') as f:
                    for line in f.readlines()[1:]:
                        fields = line.strip().split()
                        if len(fields) >= 3 and fields[1] == '00000000':
                            ip_hex = fields[2]
                            ip = '.'.join(
                                str(int(ip_hex[i : i + 2], 16))
                                for i in range(6, -1, -2)
                            )
                            return ip
            except (FileNotFoundError, IndexError, ValueError):
                pass

    elif IS_MAC:
        try:
            result = subprocess.run(
                ['netstat', '-rn'], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if line.startswith('default'):
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    elif IS_WINDOWS:
        try:
            result = subprocess.run(
                ['ipconfig'], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if 'Default Gateway' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        gw = parts[1].strip()
                        if gw and gw != ':' and not gw.startswith('fe80'):
                            return gw
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return None


def get_local_ip() -> str | None:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None


def ping_host(host: str, count: int = 2, timeout: int = 3) -> float | None:
    if IS_WINDOWS:
        cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), host]
        flag = 'time='
        pattern = r'time[=< ](\d+\.?\d*)'
    elif IS_MAC:
        cmd = ['ping', '-c', str(count), '-t', str(timeout), host]
        pattern = r'time=(\d+\.?\d*)'
    else:
        cmd = ['ping', '-c', str(count), '-W', str(timeout), host]
        pattern = r'time=(\d+\.?\d*)'

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
        if result.returncode != 0:
            return None
        times = re.findall(pattern, result.stdout, re.IGNORECASE)
        if times:
            return round(sum(float(t) for t in times) / len(times), 1)
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass
    return None


def get_network_interfaces() -> list[dict]:
    try:
        import psutil
        interfaces = []
        for name, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                    interfaces.append({
                        'name': name,
                        'ip': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast,
                    })
        return interfaces
    except ImportError:
        return []


def get_mac_vendor(mac: str) -> str:
    if not mac or mac == 'Unknown':
        return 'Unknown'
    oui = mac.upper().replace(':', '').replace('-', '')[:6]
    OUI_DB: dict[str, str] = {
        '00037F': 'Cisco',
        '0015E9': 'Apple',
        '001CBF': 'Apple',
        '0025BC': 'Apple',
        '0050F2': 'Microsoft',
        '08002B': 'DEC',
        '0C9D92': 'Samsung',
        '102CBA': 'Google',
        '182666': 'Xiaomi',
        '1C5C55': 'Xiaomi',
        '1CE62B': 'Xiaomi',
        '100D7F': 'Huawei',
        '1C6F65': 'Google',
        '24A42B': 'LG',
        '28C2DD': 'Intel',
        '2C542D': 'Apple',
        '304F75': 'TP-Link',
        '34F64B': 'Google',
        '38229D': 'Xiaomi',
        '3C5AB4': 'Google',
        '3CD92B': 'Hewlett Packard',
        '40B395': 'Amazon',
        '44D9E7': 'Roku',
        '4C6600': 'Amazon',
        '5453ED': 'Asustek',
        '585076': 'Amazon',
        '5C5181': 'TP-Link',
        '5CF9DD': 'Raspberry Pi',
        '64DBA0': 'Dell',
        '74D435': 'Sonos',
        '78D6F0': 'Amazon',
        '806C1B': 'Samsung',
        '8C7B9D': 'Roku',
        '8C8E76': 'D-Link',
        '9097D5': 'TP-Link',
        'A0369F': 'Apple',
        'A40CC3': 'Apple',
        'ACBC32': 'Netgear',
        'B0C554': 'Google',
        'B4749F': 'Netgear',
        'BCAEC5': 'Asustek',
        'C03F0E': 'Intel',
        'C8D3A3': 'Amazon',
        'CC2D8C': 'Xiaomi',
        'D4F63E': 'Xiaomi',
        'DC892C': 'Cisco',
        'E0143D': 'Apple',
        'E8ABFA': 'Amazon',
        'F04DA2': 'Google',
        'F05F5A': 'Amazon',
        'F44D17': 'Samsung',
        'F8CFC5': 'Intel',
        'FCB4E7': 'Sony',
    }
    return OUI_DB.get(oui, 'Unknown')
