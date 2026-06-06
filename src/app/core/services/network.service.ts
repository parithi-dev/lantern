import { Injectable, signal, computed } from '@angular/core';

export interface Device {
  ip: string;
  mac: string;
  hostname: string;
  vendor: string;
  status: 'online' | 'offline';
  lastSeen: number;
  firstSeen?: number;
}

export interface HealthData {
  routerIp: string;
  localIp: string;
  publicIp: string;
  isp: string;
  pingRouter: number | null;
  pingInternet: number | null;
  downloadMbps: number;
  uploadMbps: number;
  timestamp: number;
}

export interface Alert {
  type: 'device_joined' | 'latency_spike';
  message: string;
  timestamp: number;
  deviceIp: string;
}

export interface LatencyPoint {
  timestamp: number;
  pingRouter: number | null;
  pingInternet: number | null;
}

@Injectable({ providedIn: 'root' })
export class NetworkService {
  devices = signal<Device[]>([]);
  health = signal<HealthData | null>(null);
  alerts = signal<Alert[]>([]);
  latencyHistory = signal<LatencyPoint[]>([]);
  loading = signal(true);

  onlineCount = computed(() => this.devices().filter((d) => d.status === 'online').length);
  offlineCount = computed(() => this.devices().filter((d) => d.status === 'offline').length);
  totalDevices = computed(() => this.devices().length);
  avgPing = computed(() => this.health()?.pingRouter ?? 0);

  async fetchHealth(): Promise<HealthData | null> {
    try {
      const res = await fetch('http://localhost:8000/health');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      this.health.set(data);
      return data;
    } catch (e) {
      console.error('fetchHealth failed:', e);
      return null;
    }
  }

  async fetchDevices(): Promise<Device[]> {
    try {
      const res = await fetch('http://localhost:8000/devices');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (Array.isArray(data)) this.devices.set(data);
      return this.devices();
    } catch (e) {
      console.error('fetchDevices failed:', e);
      return this.devices();
    }
  }

  async fetchAlerts(): Promise<Alert[]> {
    try {
      const res = await fetch('http://localhost:8000/alerts');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (Array.isArray(data)) this.alerts.set(data);
      return this.alerts();
    } catch (e) {
      console.error('fetchAlerts failed:', e);
      return this.alerts();
    }
  }

  async fetchLatencyHistory(minutes = 30): Promise<LatencyPoint[]> {
    try {
      const res = await fetch(`http://localhost:8000/history/latency?minutes=${minutes}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (Array.isArray(data)) this.latencyHistory.set(data);
      return this.latencyHistory();
    } catch (e) {
      console.error('fetchLatencyHistory failed:', e);
      return this.latencyHistory();
    }
  }

  async fetchAll(): Promise<void> {
    const start = Date.now();
    await Promise.all([
      this.fetchHealth(),
      this.fetchDevices(),
      this.fetchAlerts(),
      this.fetchLatencyHistory(),
    ]);
    const elapsed = Date.now() - start;
    const remaining = Math.max(0, 600 - elapsed);
    if (remaining > 0) await new Promise((r) => setTimeout(r, remaining));
    this.loading.set(false);
  }
}
