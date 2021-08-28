import { Injectable } from '@angular/core';
import { AngularFireAuth } from '@angular/fire/auth';
import { AngularFirestore } from '@angular/fire/firestore';
import { BehaviorSubject } from 'rxjs';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class UserAuthService {


  public isLoggedIn = false;
  public userObservable: BehaviorSubject<any>;
  public user = {auth: null, data: null}
  constructor(public auth: AngularFireAuth, public db: AngularFirestore, private http: HttpClient) { 
    // auth.createUserWithEmailAndPassword("test@hotmail.com", "testtest");
    this.userObservable = new BehaviorSubject(null)
    this.updateUserState();
  }

  updateUserState(){
    this.auth.onAuthStateChanged(auth=>{
      // if user is signed in
      if (auth != null){
        this.user.auth = auth;
        this.isLoggedIn = true;
        this.getUserFromEmail(auth.email).then(userData=>{
          this.user.data = userData;
          // Alert the rest of the website that the user info changed
          this.userObservable.next(this.user.data);
        })
      }
      else{
        this.user.auth = null;
        this.user.data = null;
        this.isLoggedIn = false;
        this.userObservable.next(null);
      }
    })
  }

  public getUserFromEmail(email){
    return new Promise((resolve, reject)=>{
      this.db.collection("users", ref=> ref.where("email","==",email)).get().forEach(userList=>{
        userList.forEach(user=>{
          resolve(user.data());
        })
      })
    })
  }

public createUser(email,password,nickname){
  // Create a promise
  return new Promise((resolve, reject) => {
    // Check if the nickname was taken
    this.checkIfNicknameIsTaken(nickname).then(isTaken=>{
      if (isTaken == true){
        reject("This nickname has already been taken!");
      }
      else{
        let url = 'https://www.yuvalserver.com/createUser?userID='+email+"&nickname="+nickname;
        this.http.get(url).subscribe(result => {
        })
        this.auth.createUserWithEmailAndPassword(email, password).then(userAuthData=>{
          // Create user in our cloud firestore database
          let user = {id: userAuthData.user.uid, email: email, nickname: nickname};
          this.db.collection("users").doc(user.id).set(user).then(userData=>{
            resolve(userData);
          })
          .catch(error=>{
            reject(error)
          })
        }).catch(error=>{
          reject(error.message)
        })
      }
    })
  })
}

  public login(email, password){
    return new Promise<void>((resolve, reject)=>{
      this.auth.signInWithEmailAndPassword(email,password).then(()=>{
        resolve();
      }).catch(error=>{
        let errorMessage = error.message;
      })
    })
  }

    public sendForgotPasswordEmail(email){
      return new Promise((resolve, reject)=>{
        this.auth.sendPasswordResetEmail(email).then(()=>{
          resolve(true);
        })
      })
    }
  public logout(){
    this.auth.signOut();
  }

  public checkIfNicknameIsTaken(nickname){
    return new Promise((resolve, reject)=>{
      this.db.collection("users",ref=>ref.where("nickname", "==", nickname)).get().forEach(usersList=>{
        // If no users are returned nickname is not taken. Return false
        if (usersList.size==0){
          resolve(false)
        }
        // If users are returned nickname is taken. Return true
        else{
          resolve(true)
        }
      })
    })
  }
}
