import { Component, OnInit, OnDestroy, inject, signal, computed } from '@angular/core';
import { NetworkService, Device } from '../../core/services/network.service';
import { LiveChart } from '../../shared/live-chart/live-chart';

type SortKey = 'hostname' | 'ip' | 'status' | 'vendor' | 'lastSeen' | 'firstSeen';
type SortDir = 'asc' | 'desc';

@Component({
  selector: 'app-devices',
  standalone: true,
  imports: [LiveChart],
  templateUrl: './devices.html',
  styleUrl: './devices.scss',
})
export class Devices implements OnInit, OnDestroy {
  protected network = inject(NetworkService);
  devices = this.network.devices;
  latencyHistory = this.network.latencyHistory;

  selectedDevice = signal<Device | null>(null);
  panelOpen = computed(() => this.selectedDevice() !== null);

  sortKey = signal<SortKey>('hostname');
  sortDir = signal<SortDir>('asc');

  private polling: ReturnType<typeof setInterval> | null = null;

  sortedDevices = computed(() => {
    const list = [...this.devices()];
    const key = this.sortKey();
    const dir = this.sortDir();
    list.sort((a, b) => {
      let aVal = (a as any)[key];
      let bVal = (b as any)[key];
      if (key === 'status') {
        aVal = aVal === 'online' ? 0 : 1;
        bVal = bVal === 'online' ? 0 : 1;
      }
      if (key === 'lastSeen' || key === 'firstSeen') {
        aVal = aVal ?? 0;
        bVal = bVal ?? 0;
      }
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      const cmp = typeof aVal === 'string' ? aVal.localeCompare(bVal) : aVal - bVal;
      return dir === 'asc' ? cmp : -cmp;
    });
    return list;
  });

  ngOnInit(): void {
    this.network.fetchDevices();
    this.polling = setInterval(() => this.network.fetchDevices(), 5000);
  }

  ngOnDestroy(): void {
    if (this.polling) clearInterval(this.polling);
  }

  setSort(key: SortKey): void {
    if (this.sortKey() === key) {
      this.sortDir.set(this.sortDir() === 'asc' ? 'desc' : 'asc');
    } else {
      this.sortKey.set(key);
      this.sortDir.set('asc');
    }
  }

  sortIndicator(key: SortKey): string {
    if (this.sortKey() !== key) return '';
    return this.sortDir() === 'asc' ? ' ▲' : ' ▼';
  }

  onDeviceClick(device: Device): void {
    this.selectedDevice.set(device);
    this.network.fetchLatencyHistory(60);
  }

  closePanel(): void {
    this.selectedDevice.set(null);
  }

  get detailLatencyData(): Array<{ timestamp: number; value: number | null }> {
    return this.latencyHistory().map((p) => ({
      timestamp: p.timestamp,
      value: p.pingRouter,
    }));
  }

  formatTime(ts: number | undefined | null): string {
    if (!ts) return '—';
    return new Date(ts * 1000).toLocaleString();
  }
}
