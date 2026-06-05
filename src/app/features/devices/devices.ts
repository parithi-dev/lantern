import { Component, OnInit, OnDestroy, inject, signal, computed } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import type { ColDef, GridReadyEvent, ICellRendererParams } from 'ag-grid-community';
import { ModuleRegistry, ClientSideRowModelModule } from 'ag-grid-community';
import { NetworkService, Device } from '../../core/services/network.service';
import { LiveChart } from '../../shared/live-chart/live-chart';

ModuleRegistry.register(ClientSideRowModelModule);

@Component({
  selector: 'app-devices',
  standalone: true,
  imports: [AgGridAngular, LiveChart],
  templateUrl: './devices.html',
  styleUrl: './devices.scss',
})
export class Devices implements OnInit, OnDestroy {
  protected network = inject(NetworkService);
  devices = this.network.devices;
  latencyHistory = this.network.latencyHistory;

  selectedDevice = signal<Device | null>(null);
  panelOpen = computed(() => this.selectedDevice() !== null);

  private polling: ReturnType<typeof setInterval> | null = null;

  colDefs: ColDef[] = [
    {
      field: 'status',
      headerName: '',
      width: 56,
      cellRenderer: (params: ICellRendererParams) => {
        const online = params.value === 'online';
        return `<span class="status-indicator ${online ? 'online' : 'offline'}"></span>`;
      },
      sortable: false,
      filter: false,
    },
    {
      field: 'hostname',
      headerName: 'Hostname',
      flex: 2,
      cellRenderer: (params: ICellRendererParams) => {
        return params.value || params.data.ip;
      },
    },
    { field: 'ip', headerName: 'IP Address', flex: 1, filter: 'agTextColumnFilter' },
    { field: 'mac', headerName: 'MAC Address', flex: 1 },
    {
      field: 'vendor',
      headerName: 'Vendor',
      flex: 1,
      cellRenderer: (params: ICellRendererParams) => {
        if (!params.value || params.value === 'Unknown') return '';
        return `<span class="vendor-badge">${params.value}</span>`;
      },
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 96,
      cellRenderer: (params: ICellRendererParams) => {
        const online = params.value === 'online';
        return `<span class="status-label ${online ? 'online' : 'offline'}">${
          online ? 'Online' : 'Offline'
        }</span>`;
      },
    },
    {
      field: 'lastSeen',
      headerName: 'Last Seen',
      width: 160,
      valueFormatter: (params) => {
        if (!params.value) return '—';
        return new Date(params.value * 1000).toLocaleString();
      },
    },
  ];

  defaultColDef: ColDef = {
    resizable: true,
    sortable: true,
    filter: false,
  };

  ngOnInit(): void {
    this.network.fetchDevices();
    this.polling = setInterval(() => this.network.fetchDevices(), 15000);
  }

  ngOnDestroy(): void {
    if (this.polling) clearInterval(this.polling);
  }

  onGridReady(params: GridReadyEvent): void {
    params.api.sizeColumnsToFit();
  }

  onRowClicked(device: Device): void {
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

  formatTime(ts: number): string {
    return new Date(ts * 1000).toLocaleString();
  }
}
