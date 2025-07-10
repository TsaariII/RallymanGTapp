
export type TireType = "Normal" | "Sprint" | "Wet";
export type Weather = "Dry" | "Wet";
export type ConditionStage = "Green" | "Yellow" | "Red";

export class Tire {
  private type: TireType;
  private turnsUsed = 0;
  private condition: ConditionStage = "Green";
  private currentWeather: Weather;

  constructor(type: TireType, weather: Weather) {
    this.type = type;
    this.currentWeather = weather;
  }

  useTurn(): void {
    this.turnsUsed++;
    let green: number, yellow: number;
    switch (this.type) {
      case "Normal": green = 10; yellow = 35; break;
      case "Sprint": green = 10; yellow = 40; break;
      case "Wet": green = 9; yellow = 24; break;
    }

    if (this.turnsUsed <= green)
      this.condition = "Green";
    else if (this.turnsUsed <= yellow)
      this.condition = "Yellow";
    else
      this.condition = "Red";
  }

  getCondition(): ConditionStage {
    return this.condition;
  }

  getMaxWarnings(): number {
    let base = 3;
    if (this.type === "Wet" && this.currentWeather === "Dry")
      base--;
    else if ((this.type === "Normal" || this.type === "Sprint") && this.currentWeather === "Wet")
      base--;

    if (this.condition === "Yellow")
      base--;
    else if (this.condition === "Red")
      base -= 2;

    return Math.max(base, 0);
  }

  getAvailableBrakeDice(): number {
    if (this.currentWeather === "Wet") {
      return this.type === "Wet" ? 2 : 1;
    }
    return 3;
  }

  getAvailableCoastDice(): number {
    if (this.currentWeather === "Dry" && this.type === "Wet")
      return 1;
    return 2;
  }

  setWeather(w: Weather): void {
    this.currentWeather = w;
  }

  getTypeAsString(): string {
    return this.type;
  }
}
