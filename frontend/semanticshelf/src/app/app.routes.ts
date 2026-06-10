import { Routes } from '@angular/router';

export const routes: Routes = [
  {path:"" , redirectTo: "catalog", pathMatch: "full", },
  {path:"catalog" , loadComponent: () => import('../features/catalog/catalog').then(m => m.Catalog),} ,
  {path:"book/:id" , loadComponent: () => import('../features/book/book').then(m => m.BookComponent),},
  {path:"**" ,redirectTo: "catalog"}
];
