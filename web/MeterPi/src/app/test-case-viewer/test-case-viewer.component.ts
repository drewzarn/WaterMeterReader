import { Component, OnInit } from '@angular/core';
import { TestCaseService } from '../_services/test-case.service';
import { Observable } from 'rxjs';
import { ActivatedRouteSnapshot, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-test-case-viewer',
  templateUrl: './test-case-viewer.component.html',
  styleUrls: ['./test-case-viewer.component.scss']
})
export class TestCaseViewerComponent implements OnInit {
  public Test$: Observable<any>;
  public snapshotName: string;

  constructor(public tcSvc: TestCaseService, public route: ActivatedRoute) { }

  ngOnInit(): void {
    this.snapshotName = this.route.snapshot.params['snapshot'];
    this.Test$ = this.tcSvc.GetData(this.route.snapshot.params['snapshot']);
  }

}
