import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Order, OrderStatus } from '../../models/order.model';

interface TrackingStep {
  status: OrderStatus;
  label: string;
  icon: string;
  description: string;
}

@Component({
  selector: 'app-order-tracking',
  templateUrl: './order-tracking.component.html',
  styleUrls: ['./order-tracking.component.scss']
})
export class OrderTrackingComponent implements OnInit {
  order: Order | null = null;
  loading = true;
  error = '';

  readonly steps: TrackingStep[] = [
    { status: 'PENDING',    label: 'Order Placed',  icon: 'receipt',         description: 'Your order has been received.' },
    { status: 'CONFIRMED',  label: 'Confirmed',     icon: 'verified',        description: 'Order confirmed by our team.' },
    { status: 'PROCESSING', label: 'Processing',    icon: 'inventory_2',     description: 'We are preparing your items.' },
    { status: 'SHIPPED',    label: 'Shipped',       icon: 'local_shipping',  description: 'Your order is on the way.' },
    { status: 'DELIVERED',  label: 'Delivered',     icon: 'check_circle',    description: 'Order delivered successfully.' },
  ];

  constructor(
    private route: ActivatedRoute,
    private api: ApiService
  ) {}

  ngOnInit(): void {
    const orderNumber = this.route.snapshot.paramMap.get('orderNumber')!;
    this.api.getOrderByNumber(orderNumber).subscribe({
      next: order => { this.order = order; this.loading = false; },
      error: () => { this.error = 'Order not found.'; this.loading = false; }
    });
  }

  getStepIndex(status: OrderStatus): number {
    return this.steps.findIndex(s => s.status === status);
  }

  isCompleted(step: TrackingStep): boolean {
    if (!this.order) return false;
    const current = this.getStepIndex(this.order.status);
    const stepIdx  = this.getStepIndex(step.status);
    return stepIdx < current;
  }

  isActive(step: TrackingStep): boolean {
    return this.order?.status === step.status;
  }
}
