import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent }      from './components/dashboard/dashboard.component';
import { OrdersComponent }         from './components/orders/orders.component';
import { OrderTrackingComponent }  from './components/order-tracking/order-tracking.component';
import { ReportsComponent }        from './components/reports/reports.component';

const routes: Routes = [
  { path: '',           redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard',  component: DashboardComponent },
  { path: 'orders',     component: OrdersComponent },
  { path: 'tracking/:orderNumber', component: OrderTrackingComponent },
  { path: 'reports',    component: ReportsComponent },
  { path: '**',         redirectTo: '/dashboard' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
