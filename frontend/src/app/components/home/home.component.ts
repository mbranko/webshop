import { Component, Input, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { Product } from '../../models';
import { ProductService } from '../../services/product.service';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { map, shareReplay } from 'rxjs/operators';
import { NavigationComponent } from '../../navigation/navigation.component';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  products: Observable<Product[]>;
  columnCount: number;

  constructor(
      private productService: ProductService,
      private breakpointObserver: BreakpointObserver) {
    this.breakpointObserver.observe(Breakpoints.Handset)
      .pipe(map(r => r.matches), shareReplay()).subscribe(() => this.columnCount = 1);
    this.breakpointObserver.observe(Breakpoints.Tablet)
      .pipe(map(r => r.matches), shareReplay()).subscribe(() => this.columnCount = 2);
    this.breakpointObserver.observe(Breakpoints.Web)
      .pipe(map(r => r.matches), shareReplay()).subscribe(() => this.columnCount = 3);
  }

  ngOnInit(): void {
    this.loadMostPopularProducts();
  }

  loadMostPopularProducts() {
    this.products = this.productService.getMostPopularProducts();
  }

}
