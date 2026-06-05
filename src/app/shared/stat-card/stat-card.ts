import { Component, input } from '@angular/core';

@Component({
  selector: 'app-stat-card',
  standalone: true,
  templateUrl: './stat-card.html',
  styleUrl: './stat-card.scss',
})
export class StatCard {
  label = input.required<string>();
  value = input.required<string>();
  unit = input<string>('');
  icon = input<string>('');
  trend = input<'up' | 'down' | 'neutral'>('neutral');
  color = input<'cyan' | 'purple' | 'green' | 'amber' | 'red'>('cyan');
  subtitle = input<string>('');
}
