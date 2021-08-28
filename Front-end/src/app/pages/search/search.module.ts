import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SharedModule } from '../../shared.module';
import { IonicModule } from '@ionic/angular';
import { Ng2SearchPipeModule } from 'ng2-search-filter';
import { SearchPageRoutingModule } from './search-routing.module';
import { HttpClientModule } from '@angular/common/http';
import { SearchPage } from './search.page';
import { ScrollingModule} from '@angular/cdk/scrolling';
@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    SearchPageRoutingModule,
    SharedModule,
    HttpClientModule,
    Ng2SearchPipeModule,
    ScrollingModule
  ],
  declarations: [SearchPage]
})
export class SearchPageModule {}
