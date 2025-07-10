
import { Stats } from "./Stats.ts";
import { Tire, TireType, Weather } from "./Tire.ts";
import { Track } from "./Track.ts";

export class Driver {
  private name: string;
  private team: string;
  private position = 0;
  private currentGear = "0";
  private lap = 1;
  private tileIndex = 0;
  private squareIndex = 0;
  private laneIndex = 0;
  private startingTile = 0;
  private insideIndex = 0;
  private tire: Tire;
  private stats = new Stats();

  constructor(name: string, team: string, tireType: TireType, weather: Weather) {
    this.name = name;
    this.team = team;
    this.tire = new Tire(tireType, weather);
  }

  // Setters
  setPosition(pos: number): void { this.position = pos; }
  setCurrentGear(gear: string): void { this.currentGear = gear; }
  setTileIndex(index: number): void { this.tileIndex = index; }
  setLaneIndex(index: number): void { this.laneIndex = index; }
  setSquareIndex(index: number): void { this.squareIndex = index; }
  setInsideIndex(index: number): void { this.insideIndex = index; }
  setStartingTile(index: number): void { this.startingTile = index; }
  setLap(num: number): void { this.lap = num; }
  setTire(type: TireType, weather: Weather): void { this.tire = new Tire(type, weather); }

  // Getters
  getName(): string { return this.name; }
  getTeam(): string { return this.team; }
  getPosition(): number { return this.position; }
  getCurrentGear(): string { return this.currentGear; }
  getLap(): number { return this.lap; }
  getStats(): Stats { return this.stats; }
  getTileIndex(): number { return this.tileIndex; }
  getSquareIndex(): number { return this.squareIndex; }
  getLaneIndex(): number { return this.laneIndex; }
  getInsideIndex(): number { return this.insideIndex; }

  moveForward(track: Track): void {
    const currentTile = track.getTile(this.tileIndex);
    const currentLane = currentTile.laneSquares[this.laneIndex];
    if (!currentLane || currentLane.length === 0) {
      console.error("Error: Driver is in a non-existing or empty lane!");
      return;
    }

    if (this.squareIndex + 1 < currentLane.length) {
      this.squareIndex++;
    } else {
      this.tileIndex++;
      if (this.tileIndex >= track.getTrackLength()) {
        this.lap++;
        this.tileIndex = 0;
      }
      const nextTile = track.getTile(this.tileIndex);
      const nextLane = nextTile.laneSquares[this.laneIndex];
      if (!nextLane || nextLane.length === 0) {
        console.error(`Error: Lane ${this.laneIndex} does not exist in tile ${this.tileIndex}!`);
        return;
      }
      this.squareIndex = 0;
      console.log(`${this.name} moved to tile ${this.tileIndex} (${nextTile.color}) in lane ${this.laneIndex}`);
    }
  }

  changeLane(track: Track, direction: number): void {
    const currentTile = track.getTile(this.tileIndex);
    const newLane = this.laneIndex + direction;
    if (newLane >= 0 && newLane <= currentTile.lanes) {
      this.laneIndex = newLane;
      console.log(`${this.name} switched to lane ${this.laneIndex}`);
    } else {
      console.log("Invalid lane change direction!");
    }
  }
}
