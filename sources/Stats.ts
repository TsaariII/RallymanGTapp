
export class Stats {
  private turns = 0;
  private focusTokens = 0;
  private usedFocusTokens = 0;
  private lostGear = 0;
  private lostBrake = 0;
  private lostCoast = 0;
  private weatherToken = 0;
  private yellowFlag = 0;
  private greenFlag = 0;
  private normalTire = 0;
  private wetTire = 0;
  private softTire = 0;
  private diceRolls: string[] = [];
  private totalTime = 0;
  private lapTime: number[] = [];

  addTurn(): void { this.turns++; }
  addFocusToken(): void { this.focusTokens++; }
  useFocusToken(): void {
    if (this.focusTokens > 0) {
      this.focusTokens--;
      this.usedFocusTokens++;
    }
  }
  loseGear(): void { this.lostGear++; }
  loseBrake(): void { this.lostBrake++; }
  loseCoast(): void { this.lostCoast++; }
  addWeatherToken(): void { this.weatherToken++; }
  addYellowFlag(): void { this.yellowFlag++; }
  addGreenFlag(): void { this.greenFlag++; }
  addNormalTire(): void { this.normalTire++; }
  addWetTire(): void { this.wetTire++; }
  addSoftTire(): void { this.softTire++; }
  addDiceRoll(roll: string): void { this.diceRolls.push(roll); }
  resetDiceRolls(): void { this.diceRolls = []; }

  printStats(): void {
    console.log(`|==============================|`);
    console.log(`Turns: ${this.turns}`);
    console.log(`Focus Tokens: ${this.focusTokens}`);
    console.log(`Used Focus Tokens: ${this.usedFocusTokens}`);
    console.log(`Lost Gear Dice: ${this.lostGear}`);
    console.log(`Lost Brake Dice: ${this.lostBrake}`);
    console.log(`Lost Coast Dice: ${this.lostCoast}`);
    console.log(`Weather Tokens: ${this.weatherToken}`);
    console.log(`Yellow Flag: ${this.yellowFlag}`);
    console.log(`Green Flag: ${this.greenFlag}`);
    console.log(`|==============================|`);
  }

  addCrashTokens(gear: string, section: string): void {
    let crashTokens = 0;
    if (gear === "3" && section === "R") crashTokens = 1;
    else if (gear === "4") crashTokens = section === "O" ? 1 : section === "R" ? 2 : 0;
    else if (gear === "5") {
      if (section === "Y") crashTokens = 1;
      else if (section === "O") crashTokens = 2;
      else if (section === "R") crashTokens = 3;
    } else if (gear === "6") {
      if (section === "Y") crashTokens = 2;
      else if (section === "O") crashTokens = 3;
      else if (section === "R") crashTokens = 4;
    }

    const tokenPool = ["⬛️", "🟥", "⬜️", "⛅️", "🟨", "🟩"];
    for (let i = 0; i < crashTokens; ++i) {
      const token = tokenPool[Math.floor(Math.random() * tokenPool.length)];
      if (token === "⬛️") this.lostGear++;
      if (token === "🟥") this.lostBrake++;
      if (token === "⬜️") this.lostCoast++;
      if (token === "⛅️") this.weatherToken++;
      if (token === "🟨") this.yellowFlag++;
      if (token === "🟩") this.greenFlag++;
      console.log(`Token ${i + 1}: ${token}`);
    }
  }

  addLapTime(gear: string): void {
    const timeMap: { [key: string]: number } = {
      "00": 120,
      "0": 60,
      "1": 50,
      "2": 40,
      "3": 30,
      "4": 20,
      "5": 15,
      "6": 10,
    };
    const timeToAdd = timeMap[gear] || 0;
    this.totalTime += timeToAdd;
    if (this.lapTime.length === 0) this.lapTime.push(timeToAdd);
    else this.lapTime[this.lapTime.length - 1] += timeToAdd;
  }

  getTotalTime(): string {
    const minutes = Math.floor(this.totalTime / 60);
    const seconds = this.totalTime % 60;
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  }

  getLapTime(): string[] {
    return this.lapTime.map(t => {
      const minutes = Math.floor(t / 60);
      const seconds = t % 60;
      return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
    });
  }

  resetStats(): void {
    this.turns = 0;
    this.focusTokens = 0;
    this.usedFocusTokens = 0;
    this.lostGear = 0;
    this.lostBrake = 0;
    this.lostCoast = 0;
    this.weatherToken = 0;
    this.yellowFlag = 0;
    this.greenFlag = 0;
    this.diceRolls = [];
    this.lapTime = [];
    this.totalTime = 0;
  }
}
