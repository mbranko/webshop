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

  getProductsInCategory(categoryID: number): Observable<Product[]> {
    return this.http.get<Product[]>(`/api/products/?category_id=${categoryID}`);
  }
}
