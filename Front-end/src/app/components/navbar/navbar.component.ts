import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ModalController } from '@ionic/angular';
import { ModalLoginComponent } from '../modal-login/modal-login.component';
import { UserAuthService } from 'src/app/services/user-auth.service';


@Component({
  selector: 'navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
})
export class NavbarComponent implements OnInit {

  user;
  isLoggedIn = false;
  constructor(private router: Router, public modalController: ModalController, public userAuthService: UserAuthService) { }

  sendToPortfolio(){
    this.router.navigate(['/portfolio']);
  }
  sendToLeaderboard(){
    this.router.navigate(['/leaderboard']);
  }
  sendToWatchlist(){
    this.router.navigate(['/watch-list']);
  }
  sendToSearch(){
    this.router.navigate(['/search']);
  }
  sendToHome(){
    this.router.navigate(['/']);
  }
  ngOnInit() {
    this.userAuthService.userObservable.subscribe((userData)=>{
      this.user = userData;
      if (this.user==null){
        this.isLoggedIn = false;
      }
      else{
        this.isLoggedIn = true;
      }
    })
  }
  getLoginButtonText(){
    if (this.isLoggedIn==false){
      // If user is NOT signed in
      return "Login";
    }
    else{
      // If user is signed in
      return "Logout";
    }

  }

  submit(){
    if (this.user == null){
      // If not logged in
      this.presentModal();
    }
    // If logged in
    else{
      this.userAuthService.logout();
    }
  }

  async presentModal(){
    const modal = await this.modalController.create({
      component: ModalLoginComponent,
      cssClass: 'login-modal'
    })
    modal.componentProps = {
      modal: modal
    }
    return await modal.present();
  }
  async checkLoginAction(){
    if (this.user == null){
      this.presentModal();
    }
    else{
      this.userAuthService.logout();
      this.router.navigate(['/']);
    }
  }
}
