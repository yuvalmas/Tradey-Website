import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserAuthService } from 'src/app/services/user-auth.service';
import { ModalController, ToastController } from '@ionic/angular';
import { ModalBuyComponent } from 'src/app/components/modal-buy/modal-buy.component';
import { ActivatedRoute } from '@angular/router';


@Component({
  selector: 'app-watch-list',
  templateUrl: './watch-list.page.html',
  styleUrls: ['./watch-list.page.scss'],
})
export class WatchListPage{
  email: any;
  hasWatchlist = false;
  url;
  isOpen: boolean;
  constructor(private http: HttpClient, private userAuth: UserAuthService, public toastController: ToastController, public modalController: ModalController, route:ActivatedRoute) {
    route.params.subscribe(val => {
      this.userAuth.userObservable.subscribe((userData)=>{
        // this.email = userData.email;
        this.user = userData;
        this.initializeItems(this.user.email);
      });
      this.isMarketOpen();
    });
  }
  user;
  data;

  async initializeItems(email){
    this.url = "https://www.yuvalserver.com/getWatchlist?userID="+email;
    this.http.get(this.url).subscribe(datas => {
        this.data = datas["data"]
        if (this.data=="none"){
          this.hasWatchlist = false;
        }
        else{
          this.hasWatchlist = true;
        }
    });

    
  }
  removeFromWatchlist(symbol, i){
    this.userAuth.userObservable.subscribe((userData)=>{
      // this.email = userData.email;
      this.user = userData;
      let url = "https://www.yuvalserver.com/removeFromWatchlist?userID="+this.user.email+"&symbol="+symbol;
      this.http.get(url).subscribe(result => {
        this.presentToast(symbol+" has been removed from your watchlist.", "success");
        this.data.splice(i, 1);
        if (this.data.length==0){
          this.hasWatchlist = false;
        }
      });
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
