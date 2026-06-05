import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { NetworkService } from '../../core/services/network.service';

@Component({
  selector: 'app-bandwidth',
  standalone: true,
  imports: [],
  templateUrl: './bandwidth.html',
  styleUrl: './bandwidth.scss',
})
export class Bandwidth implements OnInit, OnDestroy {
  private network = inject(NetworkService);
  health = this.network.health;

  private polling: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.network.fetchHealth();
    this.polling = setInterval(() => this.network.fetchHealth(), 10000);
  }

  ngOnDestroy(): void {
    if (this.polling) clearInterval(this.polling);
  }
}
