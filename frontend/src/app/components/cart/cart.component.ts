import { Component, OnInit } from '@angular/core';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart.service';

interface CartTableItem {
  product: string;
  price: number;
  quantity: number;
  total: number;
}

@Component({
  selector: 'app-cart',
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.scss']
})
export class CartComponent implements OnInit {

  cartTable: CartTableItem[];
  totalCost: number;
  tableColumns: string[] = ['product', 'price', 'quantity', 'total'];

  constructor(
    private productService: ProductService,
    private cartService: CartService) { }

  ngOnInit(): void {
    this.initTableData();
  }

  initTableData(): void {
    this.cartTable = [];
    this.totalCost = 0;
    const items = this.cartService.cart.items;
    for (const item of items) {
      this.cartTable.push({
        product: item.product.vendor + ' ' + item.product.name,
        price: item.product.price,
        quantity: item.quantity,
        total: item.product.price * item.quantity,
      });
      this.totalCost += item.product.price * item.quantity;
    }
  }

  empty(): void {
    this.cartTable = [];
    this.totalCost = 0;
    this.cartService.empty();
  }
}

