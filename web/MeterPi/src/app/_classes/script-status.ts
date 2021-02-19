export class ScriptStatus {
    public Name: string;
    public Run: boolean = false;
    public Running: boolean = false;

    constructor(name: string, run: boolean, running: boolean) {
        this.Name = name;
        this.Run = run;
        this.Running = running;
    }
}