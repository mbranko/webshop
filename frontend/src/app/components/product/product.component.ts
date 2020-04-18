import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { Category, Product } from '../../models';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { CategoriesService } from '../../services/categories.service';
import { ProductService } from '../../services/product.service';
import { switchMap } from 'rxjs/operators';
import { JwtService } from '../../services/jwt.service';
import { CartService } from '../../services/cart.service';

@Component({
  selector: 'app-product',
  templateUrl: './product.component.html',
  styleUrls: ['./product.component.scss']
})
export class ProductComponent implements OnInit {

  product: Product;
  category: Category;
  prodID: number;

  constructor(
    private activatedRoute: ActivatedRoute,
    private categoriesService: CategoriesService,
    private productService: ProductService,
    private jwtService: JwtService,
    private cartService: CartService) { }

  ngOnInit(): void {
    this.activatedRoute.paramMap.pipe(
      switchMap((params: ParamMap, index: number) => {
        this.prodID = +params.get('id');
        return this.productService.getProduct(this.prodID);
      })
    ).subscribe((data) => this.product = data);
    this.activatedRoute.paramMap.pipe(
      switchMap((params: ParamMap, index: number) => {
        this.prodID = +params.get('id');
        return this.productService.getCategoryForProduct(this.prodID);
      })
    ).subscribe((data) => {
      this.category = data.length === 0 ? null : data[0];
    });
  }

  add(): void {
    if (this.jwtService.loggedIn) {
      this.cartService.add(this.product.id, this.product, 1);
    } else {

    }
  }
}
