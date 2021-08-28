import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserAuthService } from 'src/app/services/user-auth.service';
import { ModalController, ToastController } from '@ionic/angular';
import { ModalSellComponent } from 'src/app/components/modal-sell/modal-sell.component';
import { ActivatedRoute, Router } from '@angular/router';
@Component({
  selector: 'app-portfolio',
  templateUrl: './portfolio.page.html',
  styleUrls: ['./portfolio.page.scss'],
})
export class PortfolioPage{

  data;
  balances;
  user;
  url = "";
  onHold;
  onHoldText;
  currentBalance;
  currentBalanceText;
  totalBalance;
  totalBalanceText;
  hasPortfolio = false;
  isOpen: boolean;
  constructor(private router: Router, private http: HttpClient, private userAuth: UserAuthService, public toastController: ToastController, public modalController: ModalController, route:ActivatedRoute) { 
    route.params.subscribe(val => {
      this.initializeItems();
      this.isMarketOpen();
    });
  }

  currencyFormat(num) {
    return '$' + num.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
  }
  initializeItems() {
    this.userAuth.userObservable.subscribe((userData)=>{
      // this.email = userData.email;
      this.user = userData;
      if (this.user != null){
        this.url = "https://www.yuvalserver.com/getPortfolio?userID="+this.user.email;
        this.http.get(this.url).subscribe(datas => {
          this.data = datas["data"];
          if (this.data == "none"){
            this.hasPortfolio = false;
          }
          else{
            this.hasPortfolio = true;
          }
          console.log(datas["balances"]);
          this.balances = datas["balances"];
          this.currentBalance = this.balances[0]["currentBalance"];
          this.currentBalanceText = this.currencyFormat(this.currentBalance);
          this.onHold = this.balances[1]["holdingBalance"];
          this.onHoldText = this.currencyFormat(this.onHold);
          this.totalBalance = this.balances[2]["totalBalance"];
          this.totalBalanceText = this.currencyFormat(this.totalBalance);
        });
      }
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
  async presentModal(symbol, amount, onHold){
    const modal = await this.modalController.create({
      component: ModalSellComponent,
      cssClass: 'sell-modal',
    })
    modal.componentProps = {
      modal: modal,
      symbol: symbol,
      max: amount-onHold,
      
    }
    return await modal.present();
  }
  switchToTransactions(){
    this.router.navigate(['/transactions']);
  }

  

}
