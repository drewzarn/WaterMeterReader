import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { LiveDataViewerComponent } from './live-data-viewer/live-data-viewer.component';
import { TestCaseViewerComponent } from './test-case-viewer/test-case-viewer.component';
import { TestCaseListComponent } from './test-case-list/test-case-list.component';


const routes: Routes = [
  { path: 'live', component: LiveDataViewerComponent },
  { path: 'testcases', component: TestCaseListComponent },
  { path: 'testcase/:snapshot', component: TestCaseViewerComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
