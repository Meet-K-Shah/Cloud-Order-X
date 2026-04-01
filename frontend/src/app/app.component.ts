import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

interface NavItem {
  label: string;
  icon: string;
  route: string;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'CloudOrderX';
  sidenavOpened = true;
  activeRoute = '';

  navItems: NavItem[] = [
    { label: 'Dashboard',  icon: 'dashboard',       route: '/dashboard' },
    { label: 'Orders',     icon: 'receipt_long',    route: '/orders' },
    { label: 'Reports',    icon: 'bar_chart',       route: '/reports' },
  ];

  constructor(private router: Router) {}

  ngOnInit(): void {
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd)
    ).subscribe((e: any) => {
      this.activeRoute = e.urlAfterRedirects;
    });
  }

  isActive(route: string): boolean {
    return this.activeRoute.startsWith(route);
  }
}
