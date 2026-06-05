import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { NetworkService, Device } from '../../core/services/network.service';

@Component({
  selector: 'app-devices',
  standalone: true,
  imports: [],
  templateUrl: './devices.html',
  styleUrl: './devices.scss',
})
export class Devices implements OnInit, OnDestroy {
  private network = inject(NetworkService);
  devices = this.network.devices;

  private polling: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.network.fetchDevices();
    this.polling = setInterval(() => this.network.fetchDevices(), 15000);
  }

  ngOnDestroy(): void {
    if (this.polling) clearInterval(this.polling);
  }

  formatTime(ts: number): string {
    return new Date(ts * 1000).toLocaleString();
  }

  statusIcon(status: string): string {
    return status === 'online' ? 'check_circle' : 'radio_button_unchecked';
  }

  statusClass(status: string): string {
    return status === 'online' ? 'status-online' : 'status-offline';
  }
}
