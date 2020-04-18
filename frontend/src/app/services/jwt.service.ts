import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { AuthUser, RegisterUser } from '../models';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class JwtService {

  constructor(private http: HttpClient) { }

  login(email: string, password: string): Observable<AuthUser> {
    return this.http.post<AuthUser>('/api/token-auth/', {username: email, password}).pipe(tap(res => {
      localStorage.setItem('token', res.token);
    }));
  }

  register(user: RegisterUser): Observable<any> {
    return this.http.post('/api/register/', user);
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('cart');
  }

  public get loggedIn(): boolean {
    return localStorage.getItem('token') !== null;
  }

}
