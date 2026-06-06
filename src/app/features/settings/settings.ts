import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NetworkService, Device } from '../../core/services/network.service';

interface KnownDevice {
  mac: string;
  label: string;
}

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './settings.html',
  styleUrl: './settings.scss',
})
export class Settings implements OnInit {
  private network = inject(NetworkService);
  devices = this.network.devices;

  scanInterval = signal(5);
  latencyThreshold = signal(200);
  saved = signal(false);

  knownDevices = signal<KnownDevice[]>([]);
  editingLabel: string | null = null;
  editValue = '';

  ngOnInit(): void {
    this.loadSettings();
    this.network.fetchDevices();
  }

  async loadSettings(): Promise<void> {
    try {
      const res = await fetch('http://localhost:8000/settings');
      const data = await res.json();
      this.scanInterval.set(data.scanInterval ?? 30);
      this.latencyThreshold.set(data.latencyThreshold ?? 200);
    } catch {
      // use defaults
    }
  }

  async saveSettings(): Promise<void> {
    try {
      const params = new URLSearchParams();
      params.set('scan_interval', String(this.scanInterval()));
      params.set('latency_threshold', String(this.latencyThreshold()));
      await fetch('http://localhost:8000/settings', {
        method: 'POST',
        body: params,
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      this.saved.set(true);
      setTimeout(() => this.saved.set(false), 2000);
    } catch {
      // handle error
    }
  }

  getDeviceLabel(mac: string): string {
    const known = this.knownDevices().find((d) => d.mac === mac);
    return known?.label || '';
  }

  get unlabeledDevices(): Device[] {
    return this.devices().filter(
      (d) => d.mac && d.mac !== 'Unknown' && !this.getDeviceLabel(d.mac),
    );
  }

  get labeledDevices(): Device[] {
    return this.devices().filter((d) => d.mac && d.mac !== 'Unknown' && this.getDeviceLabel(d.mac));
  }
}
