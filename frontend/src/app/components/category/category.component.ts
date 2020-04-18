import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { switchMap } from 'rxjs/operators';
import { Category, Product } from '../../models';
import { CategoriesService } from '../../services/categories.service';
import { Observable } from 'rxjs';
import { ProductService } from '../../services/product.service';

@Component({
  selector: 'app-category',
  templateUrl: './category.component.html',
  styleUrls: ['./category.component.scss']
})
export class CategoryComponent implements OnInit {

  category: Observable<Category>;
  children: Observable<Category[]>;
  products: Observable<Product[]>;
  parent: Category;
  catID: number;

  constructor(
    private activatedRoute: ActivatedRoute,
    private categoriesService: CategoriesService,
    private productService: ProductService
  ) { }

  ngOnInit(): void {
    this.category = this.activatedRoute.paramMap.pipe(
      switchMap((params: ParamMap, index: number) => {
        this.catID = +params.get('id');
        return this.categoriesService.getCategory(this.catID);
      })
    );
    this.children = this.activatedRoute.paramMap.pipe(
      switchMap((params: ParamMap, index: number) => {
        this.catID = +params.get('id');
        return this.categoriesService.getChildren(this.catID);
      })
    );
    this.products = this.activatedRoute.paramMap.pipe(
      switchMap((params: ParamMap, index: number) => {
        this.catID = +params.get('id');
        return this.productService.getProductsInCategory(this.catID);
      })
    );
    this.activatedRoute.paramMap.pipe(
      switchMap((params: ParamMap, index: number) => {
        this.catID = +params.get('id');
        return this.categoriesService.getParent(this.catID);
      })
    ).subscribe((data) => {
      this.parent = data.length === 0 ? null : data[0];
    });
  }

}
