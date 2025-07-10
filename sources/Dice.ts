export class Dice {
  private sides: string[];

  constructor(sides: string[]) {
    this.sides = sides;
  }

  roll(): string {
    if (this.sides.length === 0) return "Invalid dice!";
    const index = Math.floor(Math.random() * this.sides.length);
    return this.sides[index];
  }
}

export function createDice(type: string): Dice {
  switch (type) {
    case "1": return new Dice(["1", "1", "1", "1", "1", "⚠️"]);
    case "2": return new Dice(["2", "2", "2", "2", "2", "⚠️"]);
    case "3": return new Dice(["3", "3", "3", "3", "⚠️", "⚠️"]);
    case "4": return new Dice(["4", "4", "4", "4", "⚠️", "⚠️"]);
    case "5": return new Dice(["5", "5", "5", "5", "⚠️", "⚠️"]);
    case "6": return new Dice(["6", "6", "6", "6", "⚠️", "⚠️"]);
    case "C": return new Dice(["⬜️", "⬜️", "⬜️", "⬜️", "⬜️", "⚠️"]);
    case "B": return new Dice(["🟥", "🟥", "🟥", "🟥", "⚠️", "⚠️"]);
    default: return new Dice([]);
  }
}