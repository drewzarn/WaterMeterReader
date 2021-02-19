import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ReplaySubject, interval } from 'rxjs';
import { ScriptStatus } from '../_classes/script-status';

@Injectable({
  providedIn: 'root'
})
export class StatusService {
  public Scripts$: ReplaySubject<Set<ScriptStatus>> = new ReplaySubject<Set<ScriptStatus>>();
  private tick = interval(1000);

  constructor(private httpClient: HttpClient) {
    this.tick.subscribe(() => {
      this.httpClient.get('http://172.24.84.10/api/Scripts.php').subscribe((status: any[]) => {
        let scripts = new Set<ScriptStatus>();
        status.forEach(script => {
          scripts.add(new ScriptStatus(script.name, script.run, script.running));
        })
        this.Scripts$.next(scripts);
      })
    });
  }
}
