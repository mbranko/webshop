import { Injectable } from '@angular/core';
import { Cart, CartItem, Product } from '../models';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CartService {

  cart: Cart;

  constructor(private http: HttpClient) {
    const storedCart = localStorage.getItem('cart');
    if (storedCart === null) {
      this.cart = { creationDate: new Date(), items: [] };
      localStorage.setItem('cart', JSON.stringify(this.cart));
    } else {
      this.cart = JSON.parse(storedCart);
    }
  }

  public get cartSize(): number {
    let size = 0;
    for (const item of this.cart.items) {
      size += item.quantity;
    }
    return size;
  }

  add(productID: number, product: Product, quantity: number) {
    let updated = false;
    for (const item of this.cart.items) {
      if (item.productID === productID) {
        item.quantity += quantity;
        updated = true;
        break;
      }
    }
    if (!updated) {
      const item: CartItem = { productID, product, quantity };
      this.cart.items.push(item);
    }
    localStorage.setItem('cart', JSON.stringify(this.cart));
  }

  empty(): void {
    this.cart.items = [];
    localStorage.setItem('cart', JSON.stringify(this.cart));
  }

  isEmpty(): boolean {
    return this.cart.items.length === 0;
  }

  purchase(): Observable<any> {
    return this.http.post<Cart>('/api/purchase/', this.cart);
  }
}
