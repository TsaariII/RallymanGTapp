
import { Driver } from "./Driver.ts";
import { TireType, Weather } from "./Tire.ts";

export class Team {
  private name: string;
  private driver1: Driver;
  private driver2: Driver;

  constructor(name: string, driver1Name: string, driver2Name: string, tire: TireType, weather: Weather) {
    this.name = name;
    this.driver1 = new Driver(driver1Name, name, tire, weather);
    this.driver2 = new Driver(driver2Name, name, tire, weather);
  }

  getTeamName(): string {
    return this.name;
  }

  getDriver1(): Driver {
    return this.driver1;
  }

  getDriver2(): Driver {
    return this.driver2;
  }
}
