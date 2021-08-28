import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserAuthService } from 'src/app/services/user-auth.service';
import { ModalController, ToastController } from '@ionic/angular';
import { ModalBuyComponent } from 'src/app/components/modal-buy/modal-buy.component';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-search',
  templateUrl: './search.page.html',
  styleUrls: ['./search.page.scss'],
})
export class SearchPage{

  filterTerm: string;
  data = [];
  page_number = 1;
  page_limit = 5;
  isFirstLoad;
  isOpen: boolean;
  gotBack: string;
  constructor(private http: HttpClient, private userAuth: UserAuthService, public toastController: ToastController, public modalController: ModalController, route:ActivatedRoute) {
    route.params.subscribe(val => {
      this.initializeItems(false, "");
      this.userAuth.userObservable.subscribe((userData)=>{
        // this.email = userData.email;
        this.user = userData;
      });
      this.isMarketOpen();
      
      
    });
  }


  user;
  offset = 0;
  searchInput="";
  url;


  async initializeItems(isFirstLoad, event){
    
    this.url = "https://www.yuvalserver.com/getStocks?offset="+this.offset+"&searchValue="+this.searchInput;
    this.http.get(this.url).subscribe(datas => {
      this.data = this.data.concat(datas["data"]);
      console.log(this.data);
      if (isFirstLoad){
        event.target.complete();
        
      }
      this.page_number++;
      this.offset = this.offset + 20;
  });
    
  }
  isMarketOpen(){
    this.url = "https://www.yuvalserver.com/isOpen";
    this.http.get(this.url).subscribe(datas =>{
      if (datas["data"]=='open'){
        this.isOpen = true;
      }
      else{
        this.isOpen = false;
      }
      console.log(this.isOpen);
    })
  }

  doInfinite(event) {
    this.initializeItems(true, event);
  }

  addToWatchlist(symbol){
    this.userAuth.userObservable.subscribe((userData)=>{
      this.user = userData;
      let url = "https://www.yuvalserver.com/addToWatchlist?userID="+this.user.email+"&symbol="+symbol;
      this.http.get(url).subscribe(result => {
        if (result['data']=="notAdded"){
          this.presentToast(symbol+" is already in your watchlist.", "danger");
        }
        else{
          this.presentToast("Added "+symbol+" to your watchlist.", "success");
        }
      });
    });
    
    
    
  }
  async presentToast(myMessage, myColor){
    const toast = await this.toastController.create({
      message: myMessage,
      duration: 5000,
      color: myColor

    })
    toast.present();
  }
  async presentModal(symbol){
    const modal = await this.modalController.create({
      component: ModalBuyComponent,
      cssClass: 'buy-modal',
    })
    modal.componentProps = {
      modal: modal,
      value: symbol,
      
    }
    return await modal.present();
  }
}