import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserAuthService } from 'src/app/services/user-auth.service';
import { ModalController, ToastController } from '@ionic/angular';

@Component({
  selector: 'app-modal-buy',
  templateUrl: './modal-buy.component.html',
  styleUrls: ['./modal-buy.component.scss'],
})
export class ModalBuyComponent implements OnInit {

  @Input("value") value;
  date;
  modal;
  date1;
  user;
  price;
  amount;
  cashBalance;
  buyingPower;
  constructor(private http: HttpClient, private userAuth: UserAuthService, public toastController: ToastController) { }

  ngOnInit() {
    this.date1 = new Date().toISOString().slice(0, 10);
    this.userAuth.userObservable.subscribe((userData)=>{
      // this.email = userData.email;
      this.user = userData;
    });
    let url  = "https://www.yuvalserver.com/getBalance?userID="+this.user.email;
    this.http.get(url).subscribe(result => {
      this.cashBalance = this.currencyFormat(result['data'][0]['currentBalance']);
      const num = (result['data'][0]['currentBalance']-result['data'][1]['holdingBalance']);
      this.buyingPower = this.currencyFormat(num);
      
    });
  }
  currencyFormat(num) {
    return '$' + num.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
  }
  submit(){
    // Find the day difference between limit and todays date
    var diff = Math.abs(this.parseDate(this.date).getTime() - new Date().getTime());
    var limit = Math.ceil(diff / (1000 * 3600 * 24)); 
    let url = "https://www.yuvalserver.com/createOrder?orderType=buy&userID="+this.user.email+"&symbol="+this.value+"&price="+this.price+"&amount="+this.amount+"&limit="+limit;
    this.http.get(url).subscribe(result => {
      this.modal.dismiss();
      if (result['data']=="insufficientFunds"){
        this.presentToast("insufficient Funds.", "danger");
      }
      else{
        this.presentToast("Created a buy order for "+this.value+" at $"+this.price+" for "+this.amount+" shares expiring in "+limit+" days.", "success");
      }
    });
  }
  parseDate(input) {
    var parts = input.match(/(\d+)/g);
    // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
    return new Date(parts[0], parts[1]-1, parts[2]); // months are 0-based
  }
  async presentToast(myMessage, myColor){
    const toast = await this.toastController.create({
      message: myMessage,
      duration: 5000,
      color: myColor

    })
    toast.present();
  }
}
