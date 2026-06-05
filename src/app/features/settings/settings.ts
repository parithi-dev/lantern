import { Component, inject } from '@angular/core';
import { NetworkService } from '../../core/services/network.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [],
  templateUrl: './settings.html',
  styleUrl: './settings.scss',
})
export class Settings {
  private network = inject(NetworkService);
}
