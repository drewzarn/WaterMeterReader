import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-interval-display',
  templateUrl: './interval-display.component.html',
  styleUrls: ['./interval-display.component.scss']
})
export class IntervalDisplayComponent implements OnInit {
  @Input() series: {name: string, value: number}[];
  public peakCount: number = 0;
  public avgInterval: number = 0;
  public flow: number = 0

  constructor() { }

  ngOnInit(): void {
    console.log(this.series);
    let peaks = this.series.filter(p => p.value > 0);
    this.peakCount = peaks.length;
    let intervals = [];
    for(let i=1; i<peaks.length; i++) {
      intervals.push(new Date("1/1/2000 " + peaks[i].name).getTime() - new Date("1/1/2000 " + peaks[i-1].name).getTime());
    }
    this.avgInterval = intervals.reduce((a, b) => a + b) / intervals.length;

    this.flow = 60 * (1000 / this.avgInterval) * (1/120);
  }

}
