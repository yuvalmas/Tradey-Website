import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SharedModule } from '../../shared.module';
import { IonicModule } from '@ionic/angular';
import { HttpClientModule } from '@angular/common/http';
import { WatchListPageRoutingModule } from './watch-list-routing.module';

import { WatchListPage } from './watch-list.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    WatchListPageRoutingModule,
    SharedModule,
    HttpClientModule
  ],
  declarations: [WatchListPage]
})
export class WatchListPageModule {}
