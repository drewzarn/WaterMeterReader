import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subject, interval } from 'rxjs';
import { startWith } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class LiveDataService {
  private _data: any;
  public Data: Subject<any> = new Subject<any>();

  constructor(private httpClient: HttpClient) {
    interval(10000).pipe(startWith(0)).subscribe(() => {
      this.httpClient.get('http://172.24.84.10/api/LiveData.php?a=data&window=30').subscribe(data => {
        this.Data.next(data);
      });
    });
  }
}
