import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { take } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { Category } from '../models';

@Injectable({
  providedIn: 'root'
})
export class CategoriesService {

  constructor(private http: HttpClient) { }

  getRootCategories(): Observable<Category[]> {
    return this.http.get<Category[]>('/api/categories/?noparent=True');
  }

  getChildren(parentID: number): Observable<Category[]> {
    return this.http.get<Category[]>(`/api/categories/?parent=${parentID}`);
  }

  getCategory(categoryID: number): Observable<Category> {
    return this.http.get<Category>(`/api/categories/${categoryID}`);
  }

  getParent(categoryID: number): Observable<Category[]> {
    return this.http.get<Category[]>(`/api/categories/?child=${categoryID}`);
  }
}
