import { Component, input, viewChild, ElementRef, AfterViewInit, effect } from '@angular/core';
import Highcharts from 'highcharts';

@Component({
  selector: 'app-live-chart',
  standalone: true,
  template: '<div #chartContainer class="chart-container"></div>',
  styles: [
    `
      :host {
        display: block;
        height: 100%;
      }
      .chart-container {
        width: 100%;
        height: 100%;
        min-height: 180px;
      }
    `,
  ],
})
export class LiveChart implements AfterViewInit {
  title = input<string>('');
  yLabel = input<string>('');
  data = input<Array<{ timestamp: number; value: number | null }>>([]);
  color = input<string>('#00d4ff');
  gradient = input<boolean>(true);

  private chartContainer = viewChild<ElementRef>('chartContainer');
  private chart: Highcharts.Chart | null = null;

  constructor() {
    effect(() => {
      const points = this.data();
      if (this.chart && points.length) {
        const series = this.chart.series[0];
        const mapped = points
          .filter((p) => p.value !== null)
          .map((p) => [p.timestamp * 1000, p.value!]);
        series.setData(mapped as Highcharts.PointOptionsObject[], true);
      }
    });
  }

  ngAfterViewInit(): void {
    this.initChart();
  }

  private initChart(): void {
    const el = this.chartContainer()?.nativeElement;
    if (!el) return;

    this.chart = Highcharts.chart(el, {
      chart: {
        type: 'areaspline',
        backgroundColor: 'transparent',
        animation: { duration: 300 },
        spacing: [4, 4, 4, 4],
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
          style: {
            color: '#5a6478',
            fontSize: '11px',
            fontFamily: 'JetBrains Mono',
          },
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
