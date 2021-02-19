import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, ReplaySubject } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { TestCase } from '../_classes/test-case';

@Injectable({
  providedIn: 'root'
})
export class TestCaseService {
  private _testCases: TestCase[] = [];

  constructor(private httpClient: HttpClient) {
    let pizza = 'pasta';
  }

  public List(): Observable<TestCase[]> {
    return this.httpClient.get<any[]>('http://172.24.84.10/api/TestCases.php?a=list').pipe(
      map(apiCases => {
        let workingCase: TestCase = null;
        apiCases.forEach(apiCase => {
          workingCase = this._testCases.find(c => c.SnapshotName == apiCase.snap_name && c.TestCaseID == apiCase.case_id);
          if(workingCase == null) {
            this._testCases.push(new TestCase(apiCase));
          } else {
            workingCase.AddWindow(apiCase.test_ac_time);
          }
        });

        return this._testCases;
      })
    )
  }

  public GetData(snapshot: string): Observable<any> {
    return this.List().pipe(
      switchMap(testCases => {
        let workingCase = testCases.find(c => c.SnapshotName == snapshot);
        return this.httpClient.post<any>('http://172.24.84.10/api/TestCases.php?a=data', {times: workingCase.WindowTimes});
      })
    );
  }
}
