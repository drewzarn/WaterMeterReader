import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ScriptStatusComponent } from './script-status/script-status.component';
import { FontAwesomeModule, FaIconLibrary } from '@fortawesome/angular-fontawesome';
import { faExclamationTriangle, faCheck, faHourglassEnd, faStop } from '@fortawesome/free-solid-svg-icons';
import { SnapshotControlComponent } from './snapshot-control/snapshot-control.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { TestCaseViewerComponent } from './test-case-viewer/test-case-viewer.component';
import { LiveDataViewerComponent } from './live-data-viewer/live-data-viewer.component';
import { ChartComponent } from './chart/chart.component';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HeaderComponent } from './header/header.component';
import { TestCaseListComponent } from './test-case-list/test-case-list.component';
import { IntervalDisplayComponent } from './interval-display/interval-display.component';
import { RoundPipe } from './_pipes/round.pipe';



@NgModule({
  declarations: [
    AppComponent,
    ScriptStatusComponent,
    SnapshotControlComponent,
    TestCaseViewerComponent,
    LiveDataViewerComponent,
    ChartComponent,
    HeaderComponent,
    TestCaseListComponent,
    IntervalDisplayComponent,
    RoundPipe
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    FontAwesomeModule,
    HttpClientModule,
    NgbModule,
    NgxChartsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {
  constructor(public library: FaIconLibrary) {
    library.addIcons(faExclamationTriangle, faCheck, faHourglassEnd, faStop);
  }
}
