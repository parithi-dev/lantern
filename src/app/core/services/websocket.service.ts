import { Injectable, inject, signal } from '@angular/core';
import { NetworkService } from './network.service';

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private network = inject(NetworkService);
  private ws: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private destroyed = false;

  connected = signal(false);

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    try {
      this.ws = new WebSocket('ws://localhost:8000/ws/live');
    } catch {
      this.scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this.connected.set(true);
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (Array.isArray(data.devices) && data.devices.length > 0) {
          this.network.devices.set(data.devices);
        }
        if (data.health) this.network.health.set(data.health);
        if (Array.isArray(data.alerts)) this.network.alerts.set(data.alerts);
        if (Array.isArray(data.latencyHistory)) this.network.latencyHistory.set(data.latencyHistory);
      } catch {
        // ignore parse errors
      }
    };

    this.ws.onclose = () => {
      this.connected.set(false);
      this.ws = null;
      if (!this.destroyed) this.scheduleReconnect();
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  disconnect(): void {
    this.destroyed = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
    this.connected.set(false);
  }

  private scheduleReconnect(): void {
    if (this.destroyed) return;
    this.reconnectTimer = setTimeout(() => this.connect(), 5000);
  }
}
