import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { NetworkService } from '../../core/services/network.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { StatCard } from '../../shared/stat-card/stat-card';
import { LiveChart } from '../../shared/live-chart/live-chart';
import { AlertFeed } from '../../shared/alert-feed/alert-feed';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [StatCard, LiveChart, AlertFeed],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit, OnDestroy {
  private network = inject(NetworkService);
  private ws = inject(WebSocketService);

  health = this.network.health;
  devices = this.network.devices;
  alerts = this.network.alerts;
  onlineCount = this.network.onlineCount;
  totalDevices = this.network.totalDevices;
  latencyHistory = this.network.latencyHistory;
  wsConnected = this.ws.connected;

  private fallbackTimer: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.network.fetchAll();
    this.ws.connect();
    this.fallbackTimer = setInterval(() => {
      if (!this.ws.connected()) {
        this.network.fetchAll();
      }
    }, 30000);
  }

  ngOnDestroy(): void {
    this.ws.disconnect();
    if (this.fallbackTimer) clearInterval(this.fallbackTimer);
  }

  get latencyChartData(): Array<{ timestamp: number; value: number | null }> {
    return this.latencyHistory().map((p) => ({
      timestamp: p.timestamp,
      value: p.pingRouter,
    }));
  }

  get internetLatencyData(): Array<{ timestamp: number; value: number | null }> {
    return this.latencyHistory().map((p) => ({
      timestamp: p.timestamp,
      value: p.pingInternet,
    }));
  }

  formatSpeed(mbps: number): string {
    if (mbps < 1) return (mbps * 1000).toFixed(0);
    return mbps.toFixed(mbps < 10 ? 1 : 0);
  }

  speedUnit(mbps: number): string {
    return mbps < 1 ? 'Kbps' : 'Mbps';
  }

  pingValue(ping: number | null): string {
    if (ping === null) return '—';
    return ping.toFixed(1);
  }

  pingStatus(ping: number | null): 'green' | 'amber' | 'red' {
    if (ping === null) return 'green';
    if (ping < 30) return 'green';
    if (ping < 100) return 'amber';
    return 'red';
  }
}
