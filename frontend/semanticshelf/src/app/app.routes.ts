import { Routes } from '@angular/router';

export const routes: Routes = [
  {path:"" , loadComponent: () => import('../features/catalog/catalog').then(m => m.Catalog),},
  {path:"search" , loadComponent: () => import('../features/catalog/catalog').then(m => m.Catalog),} ,
  {path:"book/:id" , loadComponent: () => import("../features/book-site/book-site").then(m => m.BookSite),},
  {path:"search/:q" , loadComponent: () => import('../features/catalog/catalog').then(m => m.Catalog),},
  {path:"**" ,redirectTo: ""}
];
