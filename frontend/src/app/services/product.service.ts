import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import {Category, Product} from '../models';

@Injectable({
  providedIn: 'root'
})
export class ProductService {

  constructor(private http: HttpClient) { }

  getProduct(productID: number): Observable<Product> {
    return this.http.get<Product>(`/api/products/${productID}`);
  }

  getCategoryForProduct(productID: number): Observable<Category[]> {
    return this.http.get<Category[]>(`/api/categories/?product=${productID}`);
  }

  getProductsInCategory(categoryID: number): Observable<Product[]> {
    return this.http.get<Product[]>(`/api/products/?category_id=${categoryID}`);
  }

  getMostPopularProducts(): Observable<Product[]> {
    return this.http.get<Product[]>('/api/most-popular-products/');
  }
}
