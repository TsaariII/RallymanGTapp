
import Database from 'better-sqlite3';

export type Square = { lane: number; position: number; insideLane: number };
export type Tile = {
  color: string;
  lanes: number;
  laneSquares: Record<number, Square[]>;
};

export class Track {
  private name: string;
  private tiles: Tile[] = [];

  constructor(name: string, dbName = 'tracks.db') {
    this.name = name;
    this.loadTrackFromDatabase(dbName);
  }

  private loadTrackFromDatabase(dbName: string): void {
    const db = new Database(dbName);
    const stmt = db.prepare(
      `SELECT id, position, color, lanes FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name = ?) ORDER BY position;`
    );

    const tilesData = stmt.all(this.name);

    for (const tileRow of tilesData) {
      const tile: Tile = {
        color: tileRow.color,
        lanes: tileRow.lanes,
        laneSquares: {}
      };

      const squareStmt = db.prepare(
        `SELECT lane, position, inside_lane FROM squares WHERE tile_id = ? ORDER BY lane, position;`
      );

      const squareData = squareStmt.all(tileRow.id);
      for (const sqr of squareData) {
        if (!tile.laneSquares[sqr.lane]) {
          tile.laneSquares[sqr.lane] = [];
        }
        tile.laneSquares[sqr.lane].push({
          lane: sqr.lane,
          position: sqr.position,
          insideLane: sqr.inside_lane
        });
      }

      this.tiles.push(tile);
    }

    db.close();
  }

  getTile(index: number): Tile {
    return this.tiles.at(index) as Tile;
  }

  getTrackLength(): number {
    return this.tiles.length;
  }

  getName(): string {
    return this.name;
  }

  printTrack(): void {
    console.log(`Track: ${this.name} (Length: ${this.tiles.length} tiles)`);
    this.tiles.forEach((tile, i) => {
      console.log(`Tile ${i} (${tile.color}):`);
      for (const [lane, squares] of Object.entries(tile.laneSquares)) {
        console.log(`  Lane ${lane}: ${squares.length} squares`);
      }
    });
  }
}
