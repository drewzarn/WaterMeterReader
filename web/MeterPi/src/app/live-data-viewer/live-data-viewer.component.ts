import { Component, OnInit } from '@angular/core';
import { LiveDataService } from '../_services/live-data.service';

@Component({
  selector: 'app-live-data-viewer',
  templateUrl: './live-data-viewer.component.html',
  styleUrls: ['./live-data-viewer.component.scss']
})
export class LiveDataViewerComponent implements OnInit {
  public datumCount: number = 0;

  constructor(public dataService: LiveDataService) {
    this.dataService.Data.subscribe(data => {
      this.datumCount = data[0].series.length;
    });
   }

  ngOnInit(): void {
  }

}
