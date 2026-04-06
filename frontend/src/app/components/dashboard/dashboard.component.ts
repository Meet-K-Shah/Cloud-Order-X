import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { ApiService } from '../../services/api.service';
import { WebSocketService } from '../../services/websocket.service';
import { ReportSummary, Order } from '../../models/order.model';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  summary: ReportSummary | null = null;
  recentOrders: Order[] = [];
  loading = true;
  private sub!: Subscription;

  revenueChartLabels: string[] = [];
  revenueChartData: any[] = [];
  statusChartLabels: string[] = [];
  statusChartData: any[] = [];

  readonly revenueChartOptions = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } }
  };

  constructor(
    private api: ApiService,
    private ws: WebSocketService
  ) {}

  ngOnInit(): void {
    this.ws.connect();
    this.loadData();
    this.sub = this.ws.onOrderUpdate().subscribe(() => this.loadData());
  }

  loadData(): void {
    this.api.getReportSummary().subscribe(s => {
      this.summary = s;
      this.buildCharts(s);
    });
    this.api.getOrders().subscribe(orders => {
      this.recentOrders = orders.slice(0, 10);
      this.loading = false;
    });
  }

  buildCharts(s: ReportSummary): void {
    const months = Object.keys(s.revenueByMonth);
    this.revenueChartLabels = months;
    this.revenueChartData = [{ data: months.map(m => s.revenueByMonth[m]), label: 'Revenue ($)', backgroundColor: '#818cf8', borderColor: '#6366f1', tension: 0.4 }];

    const statuses = Object.keys(s.ordersByStatus);
    this.statusChartLabels = statuses;
    this.statusChartData = [{ data: statuses.map(k => s.ordersByStatus[k]), backgroundColor: ['#fbbf24','#60a5fa','#a78bfa','#34d399','#10b981','#f87171','#9ca3af'] }];
  }

  ngOnDestroy(): void {
    this.sub?.unsubscribe();
    this.ws.disconnect();
  }
}
