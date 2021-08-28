import { Component, Input, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserAuthService } from 'src/app/services/user-auth.service';
import { ModalController, ToastController } from '@ionic/angular';

@Component({
  selector: 'app-modal-sell',
  templateUrl: './modal-sell.component.html',
  styleUrls: ['./modal-sell.component.scss'],
})
export class ModalSellComponent implements OnInit {

  @Input("symbol") symbol;
  @Input("max") max;
  date1;
  user;
  modal;
  date="";
  amount;
  price;
  
  constructor(private http: HttpClient, private userAuth: UserAuthService, public toastController: ToastController) { }


  ngOnInit() {
    this.date1 = new Date().toISOString().slice(0, 10);
    this.userAuth.userObservable.subscribe((userData)=>{
      // this.email = userData.email;
      this.user = userData;
    });
    
  }

  submit(){
    var diff = Math.abs(this.parseDate(this.date).getTime() - new Date().getTime());
    var limit = Math.ceil(diff / (1000 * 3600 * 24)); 
    let url = "https://www.yuvalserver.com/createOrder?orderType=sell&userID="+this.user.email+"&symbol="+this.symbol+"&price="+this.price+"&amount="+this.amount+"&limit="+limit;
    this.http.get(url).subscribe(result => {
      this.modal.dismiss();
      console.log(result["data"])
      if (result["data"]=="Created"){
        this.presentToast("Created a sell order for "+this.symbol+" at $"+this.price+" for "+this.amount+" shares expiring in "+limit+" days.", "success");
      }
      else{
        this.presentToast("You can only sell "+result["data"]+ " shares of "+this.symbol, "danger");
      }
    });
  }
  financial(x) {
    return Number.parseFloat(x).toFixed(2);
  }
  parseDate(input) {
    var parts = input.match(/(\d+)/g);
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
