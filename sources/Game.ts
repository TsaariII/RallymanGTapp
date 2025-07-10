
import { Dice, createDice } from "./Dice.ts";
import { Driver } from "./Driver.ts";
import { Team } from "./Team.ts";
import { Track } from "./Track.ts";
import readline from "readline";

export class Game {
  private track: Track;
  private teams: Team[] = [];
  private drivers: Driver[] = [];
  private weather: "Dry" | "Wet" = "Dry";

  constructor(trackName: string) {
    this.track = new Track(trackName);
    this.setWeather();
  }

  private setWeather(): void {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question("Select weather Dry or Wet: ", (input) => {
      this.weather = input === "Wet" ? "Wet" : "Dry";
      rl.close();
    });
  }

  private setupGame(): void {
    this.teams = [
      new Team("Evante", "Collins", "Cooper", "Normal", this.weather)
    ];
    this.drivers = this.teams.flatMap(t => [t.getDriver1(), t.getDriver2()]);
  }

  public start(): void {
    this.setupGame();
    this.printCountdown();
    this.raceLoop();
  }

  private printCountdown(): void {
    let dots = "";
    for (let i = 1; i <= 5; i++) {
      dots += "🔴 ";
      console.clear();
      console.log(dots);
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 1000);
    }
    console.log("\nRace begins!!");
  }

  private raceLoop(): void {
    const diceMap: Record<string, Dice> = {
      "1": createDice("1"),
      "2": createDice("2"),
      "3": createDice("3"),
      "4": createDice("4"),
      "5": createDice("5"),
      "6": createDice("6"),
      "C": createDice("C"),
      "B": createDice("B")
    };

    // Placeholder: insert real race logic
    console.log("Begin racing logic here...");
  }
}
