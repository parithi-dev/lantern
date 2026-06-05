import sqlite3
import time
import json
import os
from pathlib import Path


DB_PATH = Path(__file__).parent / 'netpulse.db'


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS latency_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            ping_router REAL,
            ping_internet REAL
        );

        CREATE TABLE IF NOT EXISTS device_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            ip TEXT NOT NULL,
            mac TEXT,
            hostname TEXT,
            status TEXT,
            vendor TEXT
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp REAL NOT NULL,
            device_ip TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_latency_timestamp ON latency_history(timestamp);
        CREATE INDEX IF NOT EXISTS idx_device_mac ON device_history(mac);
        CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
    ''')
    conn.commit()
    conn.close()


def save_latency(ping_router: float | None, ping_internet: float | None) -> None:
    conn = get_connection()
    conn.execute(
        'INSERT INTO latency_history (timestamp, ping_router, ping_internet) VALUES (?, ?, ?)',
        (time.time(), ping_router, ping_internet),
    )
    conn.commit()
    conn.close()


def get_latency_history(minutes: int = 30) -> list[dict]:
    conn = get_connection()
    cutoff = time.time() - (minutes * 60)
    rows = conn.execute(
        'SELECT timestamp, ping_router, ping_internet FROM latency_history WHERE timestamp > ? ORDER BY timestamp',
        (cutoff,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_devices(devices: list[dict]) -> None:
    conn = get_connection()
    now = time.time()
    for d in devices:
        conn.execute(
            'INSERT INTO device_history (timestamp, ip, mac, hostname, status, vendor) VALUES (?, ?, ?, ?, ?, ?)',
            (now, d['ip'], d.get('mac', ''), d.get('hostname', ''), d.get('status', ''), d.get('vendor', '')),
        )
    conn.commit()
    conn.close()


def save_alert(alert: dict) -> None:
    conn = get_connection()
    conn.execute(
        'INSERT INTO alerts (type, message, timestamp, device_ip) VALUES (?, ?, ?, ?)',
        (alert['type'], alert['message'], alert['timestamp'], alert.get('deviceIp', '')),
    )
    conn.commit()
    conn.close()


def get_alerts_from_db(limit: int = 50) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        'SELECT type, message, timestamp, device_ip FROM alerts ORDER BY timestamp DESC LIMIT ?',
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_setting(key: str, default: str = '') -> str:
    conn = get_connection()
    row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key: str, value: str) -> None:
    conn = get_connection()
    conn.execute(
        'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
        (key, value),
    )
    conn.commit()
    conn.close()
