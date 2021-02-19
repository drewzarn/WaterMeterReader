import { Component, OnInit } from '@angular/core';
import { SnapshotService } from '../_services/snapshot.service';

@Component({
  selector: 'app-snapshot-control',
  templateUrl: './snapshot-control.component.html',
  styleUrls: ['./snapshot-control.component.scss']
})
export class SnapshotControlComponent implements OnInit {
  Snapshots: any[];

  constructor(public snapshotSvc: SnapshotService) { }

  ngOnInit(): void {
    this.snapshotSvc.List().subscribe(snaps => {
      this.Snapshots = snaps;
    })
  }

  StartSnapshot(name) {
    this.snapshotSvc.Start(name).subscribe(snaps => {
      this.Snapshots = snaps;
    });
  }

  StopSnapshot(startTime) {
    this.snapshotSvc.Stop(startTime).subscribe(snaps => {
      this.Snapshots = snaps;
    });
  }

}
