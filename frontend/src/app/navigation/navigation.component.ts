import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Observable } from 'rxjs';
import { map, shareReplay } from 'rxjs/operators';
import { CategoriesService } from '../services/categories.service';
import { Category } from '../models';
import { JwtService } from '../services/jwt.service';

@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.scss']
})
export class NavigationComponent implements OnInit {

  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );

  rootCategories: Category[];

  constructor(
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private breakpointObserver: BreakpointObserver,
    private categoriesService: CategoriesService,
    private jwtService: JwtService) {}

  showMenu() {
    this.categoriesService.getRootCategories().subscribe((data: Category[]) => this.rootCategories = data);
  }

  ngOnInit(): void {
    this.showMenu();
  }

  loggedIn(): boolean {
    return this.jwtService.loggedIn;
  }

  logout() {
    this.jwtService.logout();
    this.router.navigate(['/login']);
  }
}
