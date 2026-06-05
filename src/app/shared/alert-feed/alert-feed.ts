import { Component, input } from '@angular/core';

interface AlertItem {
  type: 'device_joined' | 'latency_spike';
  message: string;
  timestamp: number;
  deviceIp: string;
}

@Component({
  selector: 'app-alert-feed',
  standalone: true,
  templateUrl: './alert-feed.html',
  styleUrl: './alert-feed.scss',
})
export class AlertFeed {
  alerts = input<AlertItem[]>([]);
  maxAlerts = input(20);

  get sorted(): AlertItem[] {
    return [...this.alerts()].reverse().slice(0, this.maxAlerts());
  }

  formatTime(ts: number): string {
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString();
  }

  alertIcon(type: string): string {
    switch (type) {
      case 'device_joined':
        return 'sensors';
      case 'latency_spike':
        return 'bolt';
      default:
        return 'info';
    }
  }

  alertClass(type: string): string {
    switch (type) {
      case 'device_joined':
        return 'alert-device';
      case 'latency_spike':
        return 'alert-latency';
      default:
        return 'alert-info';
    }
  }
}
