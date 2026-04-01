import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';
import { environment } from '../../environments/environment';

declare var SockJS: any;
declare var Stomp: any;

export interface WsMessage<T> {
  type: string;
  payload: T;
}

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private stompClient: any = null;
  private orderUpdates$ = new Subject<any>();
  private connected = false;

  connect(): void {
    if (this.connected) return;
    const socket = new SockJS(environment.wsUrl);
    this.stompClient = Stomp.over(socket);
    this.stompClient.debug = () => {};   // suppress logs

    this.stompClient.connect({}, () => {
      this.connected = true;
      this.stompClient.subscribe('/topic/orders', (msg: any) => {
        try {
          const payload = JSON.parse(msg.body);
          this.orderUpdates$.next(payload);
        } catch {}
      });
    }, () => {
      this.connected = false;
      setTimeout(() => this.connect(), 5000); // auto-reconnect
    });
  }

  disconnect(): void {
    if (this.stompClient && this.connected) {
      this.stompClient.disconnect();
      this.connected = false;
    }
  }

  onOrderUpdate(): Observable<any> {
    return this.orderUpdates$.asObservable();
  }

  isConnected(): boolean {
    return this.connected;
  }
}
