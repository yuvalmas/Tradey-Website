import { NavbarComponent } from '../app/components/navbar/navbar.component'
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ModalLoginComponent } from './components/modal-login/modal-login.component'
import { ModalBuyComponent } from './components/modal-buy/modal-buy.component'
import { ModalSellComponent } from './components/modal-sell/modal-sell.component'

@NgModule({
  declarations: [NavbarComponent, ModalLoginComponent, ModalBuyComponent, ModalSellComponent],
  entryComponents: [],
  exports: [NavbarComponent, ModalLoginComponent, ModalBuyComponent,  ModalSellComponent],
  imports: [FormsModule, ReactiveFormsModule, CommonModule],
  providers: [],
  bootstrap: [],
})
export class SharedModule {}
