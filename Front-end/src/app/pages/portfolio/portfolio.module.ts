import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SharedModule } from '../../shared.module';
import { IonicModule } from '@ionic/angular';
import { PortfolioPageRoutingModule } from './portfolio-routing.module';
import { HttpClientModule } from '@angular/common/http';
import { PortfolioPage } from './portfolio.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    PortfolioPageRoutingModule,
    SharedModule,
    HttpClientModule,
  ],
  declarations: [PortfolioPage]
})
export class PortfolioPageModule {}
