import { Component, OnInit } from '@angular/core';
import { StatusService } from '../_services/status.service';

@Component({
  selector: 'app-script-status',
  templateUrl: './script-status.component.html',
  styleUrls: ['./script-status.component.scss']
})
export class ScriptStatusComponent implements OnInit {

  constructor(public statusSvc: StatusService) { }

  ngOnInit(): void {
  }

}
