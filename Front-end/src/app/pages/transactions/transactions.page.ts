import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserAuthService } from 'src/app/services/user-auth.service';
import { ModalController, ToastController } from '@ionic/angular';
import { ModalSellComponent } from 'src/app/components/modal-sell/modal-sell.component';
import { ActivatedRoute, Router } from '@angular/router';
@Component({
  selector: 'app-transactions',
  templateUrl: './transactions.page.html',
  styleUrls: ['./transactions.page.scss'],
})
export class TransactionsPage{

  constructor(private router: Router, private http: HttpClient, private userAuth: UserAuthService, public toastController: ToastController, public modalController: ModalController, route:ActivatedRoute) {
    route.params.subscribe(val => {
      this.getTransactions();
    });
  }

  url;
  user;
  active;
  completed;
  cancelled;
  hasActive = false;
  hasCompleted = false;
  hasCancelled = false;
  getTransactions() {
    this.userAuth.userObservable.subscribe((userData) => {
      // this.email = userData.email;
      this.user = userData;
      this.url = "https://www.yuvalserver.com/getTransactions?userID=" + this.user.email;
    console.log(this.url);
    this.http.get(this.url).subscribe(datas => {
      console.log(datas);
      this.active = datas["active"];
      this.completed = datas["completed"];
      this.cancelled = datas["cancelled"];
      if (this.active == "none") {
        this.hasActive = false;
      }
      else {
        this.hasActive = true;
      }
      if (this.completed == "none") {
        this.hasCompleted = false;
      }
      else {
        this.hasCompleted = true;
      }
      if (this.cancelled == "none") {
        this.hasCancelled = false;
      }
      else {
        this.hasCancelled = true;
      }
    });
    });
    
  }
  cancelOrder(id, orderType, symbol, wantedPrice, amount, index) {
    this.userAuth.userObservable.subscribe((userData) => {
      // this.email = userData.email;
      this.user = userData;
      this.url = "https://www.yuvalserver.com/cancelTransaction?orderType=" + orderType + "&userID=" + this.user.email + "&symbol=" + symbol + "&wantedPrice=" + wantedPrice + "&amount=" + amount + "&ID=" + id;
      this.http.get(this.url).subscribe(datas => { });
      this.cancelled.push(this.active[index]);
      this.active.splice(index, 1);
      if (this.active.length == 0){
        this.hasActive = false;
      }
    });

  }
  financial(x) {
    return '$' + x.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
  }
}