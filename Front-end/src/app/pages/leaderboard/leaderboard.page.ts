import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserAuthService } from 'src/app/services/user-auth.service';
import { ActivatedRoute } from '@angular/router';
@Component({
  selector: 'app-leaderboard',
  templateUrl: './leaderboard.page.html',
  styleUrls: ['./leaderboard.page.scss'],
})
export class LeaderboardPage implements OnInit {
  user;
  url="";
  data;
  data1;
  topTen=false;
  constructor(private http: HttpClient, private userAuth: UserAuthService, route:ActivatedRoute) { 
    route.params.subscribe(val => {
      this.getLeaderboard();
    });
  }

  ngOnInit() {
  }
  currencyFormat(num) {
    return '$' + num.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
  }
  getLeaderboard(){
    this.userAuth.userObservable.subscribe((userData) =>{
      this.user = userData;
      if (this.user != null){
        this.url = "https://www.yuvalserver.com/getLeaderboard?userID="+this.user.email;
        console.log(this.url);
        this.http.get(this.url).subscribe(datas => {
          this.data = datas["topTen"];
          this.data1 = datas["user"];
          if (this.data1=="top10"){
            this.topTen=true;
          }
          else{
            this.topTen=false;
          }
          console.log(this.topTen);
        })
      }
      else{
        this.url = "https://www.yuvalserver.com/getLeaderboard";
        this.http.get(this.url).subscribe(datas => {
          this.data = datas["topTen"];
        })
      }
    })
  }
}