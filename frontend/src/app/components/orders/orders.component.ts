import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subscription } from 'rxjs';
import { ApiService } from '../../services/api.service';
import { WebSocketService } from '../../services/websocket.service';
import { Order, OrderStatus } from '../../models/order.model';

@Component({
  selector: 'app-orders',
  templateUrl: './orders.component.html',
  styleUrls: ['./orders.component.scss']
})
export class OrdersComponent implements OnInit, OnDestroy {
  dataSource = new MatTableDataSource<Order>([]);
  displayedColumns = ['orderNumber', 'customer', 'status', 'paymentStatus', 'totalAmount', 'createdAt', 'actions'];
  loading = true;
  statusFilter = '';
  private sub!: Subscription;

  statuses: OrderStatus[] = ['PENDING','CONFIRMED','PROCESSING','SHIPPED','DELIVERED','CANCELLED','RETURNED'];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort)      sort!:      MatSort;

  constructor(
    private api: ApiService,
    private ws: WebSocketService,
    private snack: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.ws.connect();
    this.loadOrders();
    this.sub = this.ws.onOrderUpdate().subscribe(order => {
      const existing = this.dataSource.data.findIndex(o => o.id === order.id);
      if (existing >= 0) {
        const data = [...this.dataSource.data];
        data[existing] = order;
        this.dataSource.data = data;
      } else {
        this.dataSource.data = [order, ...this.dataSource.data];
      }
    });
  }

  loadOrders(): void {
    this.loading = true;
    this.api.getOrders(this.statusFilter || undefined).subscribe(orders => {
      this.dataSource.data = orders;
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
      this.loading = false;
    });
  }

  applyFilter(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.dataSource.filter = value.trim().toLowerCase();
  }

  updateStatus(order: Order, status: OrderStatus): void {
    this.api.updateOrderStatus(order.id, { status }).subscribe(() => {
      this.snack.open(`Order ${order.orderNumber} updated to ${status}`, 'OK', { duration: 3000 });
      this.loadOrders();
    });
  }

  deleteOrder(order: Order): void {
    if (!confirm(`Delete order ${order.orderNumber}?`)) return;
    this.api.deleteOrder(order.id).subscribe(() => {
      this.snack.open('Order deleted', 'OK', { duration: 2000 });
      this.loadOrders();
    });
  }

  ngOnDestroy(): void {
    this.sub?.unsubscribe();
  }
}
