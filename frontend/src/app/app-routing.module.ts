import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { LoginComponent } from './components/login/login.component';
import { CategoryComponent } from './components/category/category.component';
import { ProductComponent } from './components/product/product.component';
import { CartComponent } from './components/cart/cart.component';
import { PaymentComponent } from './components/payment/payment.component';
import { RegisterComponent } from './components/register/register.component';

const routes: Routes = [{
    path: '',
    component: HomeComponent,
  }, {
    path: 'category/:id',
    component: CategoryComponent,
  }, {
    path: 'product/:id',
    component: ProductComponent,
  }, {
    path: 'cart',
    component: CartComponent,
  }, {
    path: 'payment',
    component: PaymentComponent,
  }, {
    path: 'register',
    component: RegisterComponent,
  }, {
    path: 'login',
    component: LoginComponent,
}];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
