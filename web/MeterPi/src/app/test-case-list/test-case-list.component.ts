import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { TestCaseService } from '../_services/test-case.service';

@Component({
  selector: 'app-test-case-list',
  templateUrl: './test-case-list.component.html',
  styleUrls: ['./test-case-list.component.scss']
})
export class TestCaseListComponent implements OnInit {
  public Tests$: Observable<any>;

  constructor(public tcSvc: TestCaseService) { }

  ngOnInit(): void {
    this.Tests$ = this.tcSvc.List();
  }

  GetData(snapshotName: string) {
    this.tcSvc.GetData(snapshotName).subscribe();
  }

}
