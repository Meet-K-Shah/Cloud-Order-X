import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { ReportSummary } from '../../models/order.model';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.scss']
})
export class ReportsComponent implements OnInit {
  summary: ReportSummary | null = null;
  loading = true;

  revenueChartLabels: string[] = [];
  revenueData: any[] = [];
  statusLabels: string[] = [];
  statusData: any[] = [];

  readonly lineOptions = {
    responsive: true,
    plugins: { legend: { display: true } },
    scales: { y: { beginAtZero: true, ticks: { callback: (v: any) => '$' + v } } }
  };

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getReportSummary().subscribe(s => {
      this.summary = s;
      this.buildCharts(s);
      this.loading = false;
    });
  }

  buildCharts(s: ReportSummary): void {
    const months = Object.keys(s.revenueByMonth);
    this.revenueChartLabels = months;
    this.revenueData = [
      { data: months.map(m => s.revenueByMonth[m]), label: 'Revenue', fill: true,
        backgroundColor: 'rgba(99,102,241,0.1)', borderColor: '#6366f1', tension: 0.4 }
    ];
    const statuses = Object.keys(s.ordersByStatus);
    this.statusLabels = statuses;
    this.statusData = [{
      data: statuses.map(k => s.ordersByStatus[k]),
      backgroundColor: ['#fbbf24','#60a5fa','#a78bfa','#34d399','#10b981','#f87171','#9ca3af']
    }];
  }

  exportCsv(): void {
    if (!this.summary) return;
    const rows = [
      ['Metric', 'Value'],
      ['Total Orders', this.summary.totalOrders],
      ['Pending', this.summary.pendingOrders],
      ['Delivered', this.summary.deliveredOrders],
      ['Cancelled', this.summary.cancelledOrders],
      ['Total Revenue', this.summary.totalRevenue],
      ['Avg Order Value', this.summary.averageOrderValue],
    ];
    const csv = rows.map(r => r.join(',')).join('\n');
    const a = document.createElement('a');
    a.href = 'data:text/csv,' + encodeURIComponent(csv);
    a.download = 'cloudorderx-report.csv';
    a.click();
  }
}
