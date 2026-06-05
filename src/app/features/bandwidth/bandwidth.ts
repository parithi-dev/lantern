import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
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
export class Bandwidth implements OnInit, OnDestroy {
  private network = inject(NetworkService);
  health = this.network.health;

  bandwidthHistory = signal<BandwidthPoint[]>([]);
  private history: BandwidthPoint[] = [];
  private maxPoints = 180;

  private polling: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.network.fetchHealth();
    this.polling = setInterval(() => {
      const h = this.health();
      if (h) {
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
      this.network.fetchHealth();
    }, 5000);
  }

  ngOnDestroy(): void {
    if (this.polling) clearInterval(this.polling);
  }

  get downloadData(): Array<{ timestamp: number; value: number | null }> {
    return this.bandwidthHistory().map((p) => ({
      timestamp: p.timestamp,
      value: p.downloadMbps,
    }));
  }

  get uploadData(): Array<{ timestamp: number; value: number | null }> {
    return this.bandwidthHistory().map((p) => ({
      timestamp: p.timestamp,
      value: p.uploadMbps,
    }));
  }

  get maxSpeed(): number {
    const all = this.bandwidthHistory();
    if (!all.length) return 1;
    const max = Math.max(...all.map((p) => Math.max(p.downloadMbps, p.uploadMbps)));
    return Math.max(max * 1.2, 1);
  }

  formatSpeed(mbps: number): string {
    if (mbps < 1) return (mbps * 1000).toFixed(0);
    return mbps.toFixed(mbps < 10 ? 1 : 0);
  }
}
