export class TestCase {
    public SnapshotName: string;
    private _windowTimes: Set<number>;
    public TestCaseID: number;

    constructor(apiSource: any) {
        this.SnapshotName = apiSource.snap_name;
        this.TestCaseID = apiSource.case_id;
        this._windowTimes = new Set<number>();
    }

    public AddWindow(time: number) {
        this._windowTimes.add(time);
    }

    public get Duration(): number {
        let startTime = Math.min(...this._windowTimes.values());
        let endTime = Math.max(...this._windowTimes.values());
        return Math.floor((endTime - startTime) / 1000);
    }

    public get StartTime(): number {
        return Math.min(...this._windowTimes.values());
    }

    public get WindowTimes(): number[] {
        return [...this._windowTimes.values()];
    }
}
