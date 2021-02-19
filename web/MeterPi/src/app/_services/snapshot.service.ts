import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SnapshotService {

  constructor(private httpClient: HttpClient) { }

  public List(): Observable<any[]> {
    return this.httpClient.get<any[]>('http://172.24.84.10/api/Snapshots.php?a=list');
  }

  public Start(name): Observable<any> {
    return this.httpClient.get<any>('http://172.24.84.10/api/Snapshots.php?a=start&name=' + name);
  }

  public Stop(startTime): Observable<any> {
    return this.httpClient.get<any>('http://172.24.84.10/api/Snapshots.php?a=stop&start=' + startTime);
  }
}
