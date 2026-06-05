import { Component, input, viewChild, ElementRef, AfterViewInit, signal } from '@angular/core';
import Highcharts from 'highcharts';

@Component({
  selector: 'app-live-chart',
  standalone: true,
  template: '<div #chartContainer class="chart-container"></div>',
  styles: [
    `
      :host {
        display: block;
      }
      .chart-container {
        width: 100%;
        height: 100%;
        min-height: 200px;
      }
    `,
  ],
})
export class LiveChart implements AfterViewInit {
  title = input<string>('');
  yLabel = input<string>('');
  data = input<Array<{ timestamp: number; value: number | null }>>([]);
  color = input<string>('#00d4ff');

  private chartContainer = viewChild<ElementRef>('chartContainer');
  private chart: Highcharts.Chart | null = null;
  private _ready = signal(false);

  ngAfterViewInit(): void {
    this.initChart();
    this._ready.set(true);
  }

  private initChart(): void {
    const el = this.chartContainer()?.nativeElement;
    if (!el) return;

    this.chart = Highcharts.chart(el, {
      chart: {
        type: 'areaspline',
        backgroundColor: 'transparent',
        animation: true,
        spacing: [8, 8, 8, 8],
        style: { fontFamily: 'DM Sans, sans-serif' },
      },
      title: { text: undefined },
      credits: { enabled: false },
      legend: { enabled: false },
      tooltip: {
        backgroundColor: 'rgba(22, 29, 46, 0.95)',
        borderColor: 'rgba(0, 212, 255, 0.2)',
        borderRadius: 8,
        style: { color: '#e8eaed', fontFamily: 'JetBrains Mono, monospace' },
        formatter: function () {
          const date = new Date(this.x!);
          const time = date.toLocaleTimeString();
          return `<b>${time}</b><br/>${this.y?.toFixed(1)} ms`;
        },
      },
      xAxis: {
        type: 'datetime',
        visible: false,
        labels: { style: { color: '#5a6478', fontSize: '11px' } },
        gridLineColor: 'rgba(0, 212, 255, 0.04)',
        tickLength: 0,
      },
      yAxis: {
        title: { text: undefined },
        labels: {
          style: { color: '#5a6478', fontSize: '11px', fontFamily: 'JetBrains Mono' },
        },
        gridLineColor: 'rgba(0, 212, 255, 0.04)',
        min: 0,
      },
      plotOptions: {
        areaspline: {
          fillOpacity: 0.3,
          marker: {
            enabled: false,
            states: { hover: { enabled: true, radius: 4 } },
          },
          states: { inactive: { opacity: 0.3 } },
        },
      },
      series: [
        {
          type: 'areaspline',
          name: this.yLabel(),
          data: [],
          color: this.color(),
          lineWidth: 2,
        },
      ],
    } as Highcharts.Options);
  }
}
