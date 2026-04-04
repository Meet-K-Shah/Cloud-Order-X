import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import {
  ApiResponse, Order, Product, Customer,
  CreateOrderRequest, UpdateOrderStatusRequest, ReportSummary
} from '../models/order.model';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Orders
  getOrders(status?: string): Observable<Order[]> {
    let params = new HttpParams();
    if (status) params = params.set('status', status);
    return this.http.get<ApiResponse<Order[]>>(`${this.base}/orders`, { params })
      .pipe(map(r => r.data));
  }

  getOrder(id: number): Observable<Order> {
    return this.http.get<ApiResponse<Order>>(`${this.base}/orders/${id}`)
      .pipe(map(r => r.data));
  }

  getOrderByNumber(orderNumber: string): Observable<Order> {
    return this.http.get<ApiResponse<Order>>(`${this.base}/orders/number/${orderNumber}`)
      .pipe(map(r => r.data));
  }

  createOrder(req: CreateOrderRequest): Observable<Order> {
    return this.http.post<ApiResponse<Order>>(`${this.base}/orders`, req)
      .pipe(map(r => r.data));
  }

  updateOrderStatus(id: number, req: UpdateOrderStatusRequest): Observable<Order> {
    return this.http.patch<ApiResponse<Order>>(`${this.base}/orders/${id}/status`, req)
      .pipe(map(r => r.data));
  }

  deleteOrder(id: number): Observable<void> {
    return this.http.delete<ApiResponse<void>>(`${this.base}/orders/${id}`)
      .pipe(map(() => undefined));
  }

  getReportSummary(): Observable<ReportSummary> {
    return this.http.get<ApiResponse<ReportSummary>>(`${this.base}/orders/reports/summary`)
      .pipe(map(r => r.data));
  }

  // Products
  getProducts(search?: string): Observable<Product[]> {
    let params = new HttpParams();
    if (search) params = params.set('search', search);
    return this.http.get<ApiResponse<Product[]>>(`${this.base}/products`, { params })
      .pipe(map(r => r.data));
  }

  createProduct(product: Partial<Product>): Observable<Product> {
    return this.http.post<ApiResponse<Product>>(`${this.base}/products`, product)
      .pipe(map(r => r.data));
  }

  updateProduct(id: number, product: Partial<Product>): Observable<Product> {
    return this.http.put<ApiResponse<Product>>(`${this.base}/products/${id}`, product)
      .pipe(map(r => r.data));
  }

  deleteProduct(id: number): Observable<void> {
    return this.http.delete<ApiResponse<void>>(`${this.base}/products/${id}`)
      .pipe(map(() => undefined));
  }

  // Customers
  getCustomers(): Observable<Customer[]> {
    return this.http.get<ApiResponse<Customer[]>>(`${this.base}/customers`)
      .pipe(map(r => r.data));
  }

  createCustomer(customer: Partial<Customer>): Observable<Customer> {
    return this.http.post<ApiResponse<Customer>>(`${this.base}/customers`, customer)
      .pipe(map(r => r.data));
  }
}
