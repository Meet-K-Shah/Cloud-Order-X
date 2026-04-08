import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// Angular Material
import { MatToolbarModule }    from '@angular/material/toolbar';
import { MatSidenavModule }    from '@angular/material/sidenav';
import { MatListModule }       from '@angular/material/list';
import { MatIconModule }       from '@angular/material/icon';
import { MatButtonModule }     from '@angular/material/button';
import { MatTableModule }      from '@angular/material/table';
import { MatPaginatorModule }  from '@angular/material/paginator';
import { MatSortModule }       from '@angular/material/sort';
import { MatInputModule }      from '@angular/material/input';
import { MatFormFieldModule }  from '@angular/material/form-field';
import { MatSelectModule }     from '@angular/material/select';
import { MatSnackBarModule }   from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule }       from '@angular/material/card';
import { MatDialogModule }     from '@angular/material/dialog';
import { MatTooltipModule }    from '@angular/material/tooltip';
import { MatChipsModule }      from '@angular/material/chips';
import { MatBadgeModule }      from '@angular/material/badge';

// Charts
import { NgChartsModule } from 'ng2-charts';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent }     from './app.component';
import { DashboardComponent }     from './components/dashboard/dashboard.component';
import { OrdersComponent }        from './components/orders/orders.component';
import { OrderTrackingComponent } from './components/order-tracking/order-tracking.component';
import { ReportsComponent }       from './components/reports/reports.component';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    OrdersComponent,
    OrderTrackingComponent,
    ReportsComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    AppRoutingModule,
    NgChartsModule,
    // Material
    MatToolbarModule, MatSidenavModule, MatListModule, MatIconModule,
    MatButtonModule, MatTableModule, MatPaginatorModule, MatSortModule,
    MatInputModule, MatFormFieldModule, MatSelectModule, MatSnackBarModule,
    MatProgressSpinnerModule, MatCardModule, MatDialogModule, MatTooltipModule,
    MatChipsModule, MatBadgeModule,
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
