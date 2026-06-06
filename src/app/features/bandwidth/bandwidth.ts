import { Component, OnInit, OnDestroy, inject, signal, computed, effect } from '@angular/core';
import { NetworkService } from '../../core/services/network.service';
import { LiveChart } from '../../shared/live-chart/live-chart';

interface BandwidthPoint {
  timestamp: number;
  downloadMbps: number;
  uploadMbps: number;
}

@Component({
  selector: 'app-bandwidth',
  standalone: true,
  imports: [LiveChart],
  templateUrl: './bandwidth.html',
  styleUrl: './bandwidth.scss',
})
export class Bandwidth implements OnInit {
  private network = inject(NetworkService);
  health = this.network.health;
  loading = this.network.loading;

  bandwidthHistory = signal<BandwidthPoint[]>([]);
  private history: BandwidthPoint[] = [];
  private maxPoints = 180;
  private lastTimestamp = 0;

  maxSpeed = computed(() => {
    const h = this.bandwidthHistory();
    if (!h.length) return 0;
    return Math.max(...h.map((p) => p.downloadMbps));
  });

  downloadData = computed(() =>
    this.bandwidthHistory().map((p) => ({
      timestamp: p.timestamp,
      value: p.downloadMbps,
    })),
  );

  uploadData = computed(() =>
    this.bandwidthHistory().map((p) => ({
      timestamp: p.timestamp,
      value: p.uploadMbps,
    })),
  );

  constructor() {
    effect(() => {
      const h = this.health();
      if (h && h.timestamp !== this.lastTimestamp) {
        this.lastTimestamp = h.timestamp;
        this.history.push({
          timestamp: h.timestamp,
          downloadMbps: h.downloadMbps,
          uploadMbps: h.uploadMbps,
        });
        if (this.history.length > this.maxPoints) {
          this.history = this.history.slice(-this.maxPoints);
        }
        this.bandwidthHistory.set([...this.history]);
      }
    });
  }

  ngOnInit(): void {
    this.network.fetchHealth();
  }

  formatSpeed(mbps: number): string {
    if (mbps < 1) return (mbps * 1000).toFixed(0);
    return mbps.toFixed(mbps < 10 ? 1 : 0);
  }
}
