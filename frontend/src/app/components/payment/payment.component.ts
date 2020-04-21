import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CartService } from '../../services/cart.service';
import { UiService } from '../../services/ui.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';

@Component({
  selector: 'app-payment',
  templateUrl: './payment.component.html',
  styleUrls: ['./payment.component.scss']
})
export class PaymentComponent implements OnInit {

  formGroup: FormGroup;
  formSubmitted: boolean;

  constructor(
    private fb: FormBuilder,
    private cartService: CartService,
    private uiService: UiService,
    private snackBar: MatSnackBar,
    private router: Router) { }

  ngOnInit(): void {
    this.formGroup = this.fb.group({
      name: ['John Doe', Validators.compose([Validators.required, Validators.maxLength(80)])],
      cardNumber: ['4111111111111111', Validators.compose([Validators.required, Validators.minLength(16), Validators.maxLength(16)])],
      expiryMonth: ['12', Validators.compose([Validators.required, Validators.maxLength(2)])],
      expiryYear: ['2020', Validators.compose([Validators.required, Validators.maxLength(4)])],
    });
    this.formSubmitted = false;
  }

  isDisabled(): boolean {
    return this.cartService.isEmpty() && !this.formSubmitted;
  }

  onSubmit(): void {
    if (this.formGroup.valid) {
      this.formSubmitted = false;
      this.uiService.spin.next(true);
      this.cartService.purchase().subscribe((data) => {
        this.uiService.spin.next(false);
        this.formSubmitted = false;
        this.cartService.empty();
        const snackBarRef = this.snackBar.open('Purchase successful!', 'OK');
        snackBarRef.afterDismissed().subscribe(() => {
          this.router.navigate(['/']);
        });
      }, (errors) => {
        this.uiService.spin.next(false);
        this.formSubmitted = false;
        const snackBarRef = this.snackBar.open('Purchase unsuccessful!', 'OK');
        snackBarRef.afterDismissed().subscribe(() => {
          this.router.navigate(['/cart']);
        });
        console.log(errors);
      });
    } else {
      console.log(this.formGroup.errors);
    }
  }
}
