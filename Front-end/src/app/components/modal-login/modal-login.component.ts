import { Component, OnInit } from '@angular/core';
import { ToastController } from '@ionic/angular';
import { UserAuthService } from 'src/app/services/user-auth.service';

@Component({
  selector: 'app-modal-login',
  templateUrl: './modal-login.component.html',
  styleUrls: ['./modal-login.component.scss'],
})
export class ModalLoginComponent implements OnInit {

  modal;
  state = "";
  headerText = "Sign Up";

  emailInput="";
  passwordInput="";
  nicknameInput="";

  constructor(public toastController: ToastController, public userAuthService: UserAuthService) { }

  ngOnInit() {
    this.changeState("login");
  }

  closeModal(){
    this.modal.dismiss();
  }

  changeState(state){
    this.state = state;

    if (this.state == "login"){
      this.headerText = "Login";
    }
    else if (this.state == "signup"){
      this.headerText = "Sign Up";
    }
    else if (this.state == "forgotPassword"){
      this.headerText = "Forgot Password";
    }
  }
  submit() {
    // Start of validation
    // Validate email
    if (this.validateEmail(this.emailInput) == false){
      this.presentToast("Please enter a valid email!", "danger");
      return;
    }
    // Validate password
    if(this.state != "forgotPassword" && this.passwordInput.length < 8){
      this.presentToast("Password must be at least 8 characters","danger");
      return;
    }
    if(this.state == "signup" && this.nicknameInput == ""){
      this.presentToast("Please enter a nickname", "danger");
      return;
    }
    // End of validation
    if(this.state == "login"){
      this.userAuthService.login(this.emailInput, this.passwordInput).then(()=>{
        this.modal.dismiss();
      })
    }
    else if(this.state == "signup"){
      
      this.userAuthService.createUser(this.emailInput, this.passwordInput, this.nicknameInput).then(userData=>{
      this.modal.dismiss();
      }).catch(errorMessage=>{
        // Catch means there was an error(Reject)
        this.presentToast(errorMessage, "danger");
      })
      this.presentToast("Thank you for signing up!", "success")
      this.modal.dismiss();
    }
    else if(this.state == "forgotPassword"){
      this.userAuthService.sendForgotPasswordEmail(this.emailInput).then(()=>{
        this.presentToast("Reset password email has been sent!", "success");
      })
      this.modal.dismiss();
    }

  }

  validateEmail(email){
 // Verify email
  const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(String(email).toLowerCase());
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
