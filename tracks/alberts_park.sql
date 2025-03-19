-- Create Tracks Table
CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Create Tiles Table
CREATE TABLE tiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER NOT NULL,
    position INTEGER NOT NULL, -- Position of the tile in the track
    color TEXT NOT NULL CHECK (color IN ('Y', 'O', 'R')), -- "Y", "O", "R"
    lanes INTEGER NOT NULL DEFAULT 3, -- Number of lanes in the tile
    FOREIGN KEY (track_id) REFERENCES tracks(id)
);

-- Create Squares Table
CREATE TABLE squares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tile_id INTEGER NOT NULL,
    lane INTEGER NOT NULL CHECK (lane BETWEEN 1 AND 3), -- Lane number (1, 2, or 3)
    position INTEGER NOT NULL, -- Position of the square within the lane
    inside_lane INTEGER NOT NULL DEFAULT 1, -- 1, 2 or depending on how inner the lane is on this square
    FOREIGN KEY (tile_id) REFERENCES tiles(id)
);

-- Insert Track
INSERT INTO tracks (name) VALUES ('Albert Park');

-- Insert Tiles
INSERT INTO tiles (track_id, position, color, lanes) VALUES
    ((SELECT id FROM tracks WHERE name='Albert Park'), 1, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 2, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 3, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 4, 'O', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 5, 'O', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 6, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 7, 'O', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 8, 'Y', 2),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 9, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 10, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 11, 'O', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 12, 'O', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 13, 'O', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 14, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 15, 'O', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 16, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 17, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 18, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 19, 'O', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 20, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 21, 'Y', 3),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 22, 'Y', 3);

-- Insert Squares with Inside Lane Information
INSERT INTO squares (tile_id, lane, position, inside_lane)
SELECT id, 1, 1, 1 FROM tiles WHERE position = 1 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 1 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 1 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 1 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 1 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 1 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 1 UNION ALL
SELECT id, 3, 2, 3 FROM tiles WHERE position = 1 UNION ALL
SELECT id, 3, 3, 3 FROM tiles WHERE position = 1 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 2 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 2 UNION ALL
SELECT id, 1, 3, 2 FROM tiles WHERE position = 2 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 2 UNION ALL
SELECT id, 2, 2, 1 FROM tiles WHERE position = 2 UNION ALL
SELECT id, 2, 3, 1 FROM tiles WHERE position = 2 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 2 UNION ALL
SELECT id, 3, 2, 2 FROM tiles WHERE position = 2 UNION ALL
SELECT id, 3, 3, 1 FROM tiles WHERE position = 2 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 3 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 3 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 3 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 3 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 3 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 3 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 3 UNION ALL
SELECT id, 3, 2, 3 FROM tiles WHERE position = 3 UNION ALL
SELECT id, 3, 3, 3 FROM tiles WHERE position = 3 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 4 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 4 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 4 UNION ALL
SELECT id, 2, 2, 1 FROM tiles WHERE position = 4 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 4 UNION ALL
SELECT id, 3, 2, 2 FROM tiles WHERE position = 4 UNION ALL

SELECT id, 1, 1, 3 FROM tiles WHERE position = 5 UNION ALL
SELECT id, 1, 2, 2 FROM tiles WHERE position = 5 UNION ALL
SELECT id, 1, 3, 2 FROM tiles WHERE position = 5 UNION ALL
SELECT id, 1, 4, 1 FROM tiles WHERE position = 5 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 5 UNION ALL
SELECT id, 2, 2, 1 FROM tiles WHERE position = 5 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 5 UNION ALL
SELECT id, 3, 1, 1 FROM tiles WHERE position = 5 UNION ALL
SELECT id, 3, 2, 1 FROM tiles WHERE position = 5 UNION ALL
SELECT id, 3, 3, 3 FROM tiles WHERE position = 5 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 6 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 6 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 6 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 6 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 6 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 6 UNION ALL
SELECT id, 2, 4, 2 FROM tiles WHERE position = 6 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 6 UNION ALL
SELECT id, 3, 2, 2 FROM tiles WHERE position = 6 UNION ALL
SELECT id, 3, 3, 2 FROM tiles WHERE position = 6 UNION ALL
SELECT id, 3, 4, 3 FROM tiles WHERE position = 6 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 7 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 7 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 7 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 7 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 7 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 7 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 7 UNION ALL
SELECT id, 3, 2, 3 FROM tiles WHERE position = 7 UNION ALL
SELECT id, 3, 3, 3 FROM tiles WHERE position = 7 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 8 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 8 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 8 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 8 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 8 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 8 UNION ALL
SELECT id, 2, 4, 2 FROM tiles WHERE position = 8 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 9 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 9 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 9 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 9 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 9 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 9 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 9 UNION ALL
SELECT id, 3, 2, 2 FROM tiles WHERE position = 9 UNION ALL
SELECT id, 3, 3, 3 FROM tiles WHERE position = 9 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 10 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 10 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 10 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 10 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 10 UNION ALL
SELECT id, 3, 2, 3 FROM tiles WHERE position = 10 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 11 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 11 UNION ALL
SELECT id, 1, 3, 3 FROM tiles WHERE position = 11 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 11 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 11 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 11 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 11 UNION ALL
SELECT id, 3, 2, 2 FROM tiles WHERE position = 11 UNION ALL
SELECT id, 3, 3, 2 FROM tiles WHERE position = 11 UNION ALL
SELECT id, 3, 4, 1 FROM tiles WHERE position = 11 UNION ALL

SELECT id, 1, 1, 3 FROM tiles WHERE position = 12 UNION ALL
SELECT id, 1, 2, 3 FROM tiles WHERE position = 12 UNION ALL
SELECT id, 1, 3, 3 FROM tiles WHERE position = 12 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 12 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 12 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 12 UNION ALL
SELECT id, 3, 1, 1 FROM tiles WHERE position = 12 UNION ALL
SELECT id, 3, 2, 1 FROM tiles WHERE position = 12 UNION ALL

SELECT id, 1, 1, 3 FROM tiles WHERE position = 13 UNION ALL
SELECT id, 1, 2, 3 FROM tiles WHERE position = 13 UNION ALL
SELECT id, 1, 3, 3 FROM tiles WHERE position = 13 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 13 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 13 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 13 UNION ALL
SELECT id, 3, 1, 1 FROM tiles WHERE position = 13 UNION ALL
SELECT id, 3, 2, 1 FROM tiles WHERE position = 13 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 14 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 14 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 14 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 14 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 14 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 14 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 14 UNION ALL
SELECT id, 3, 2, 3 FROM tiles WHERE position = 14 UNION ALL
SELECT id, 3, 3, 2 FROM tiles WHERE position = 14 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 15 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 15 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 15 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 15 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 15 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 15 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 15 UNION ALL
SELECT id, 3, 2, 3 FROM tiles WHERE position = 15 UNION ALL
SELECT id, 3, 3, 2 FROM tiles WHERE position = 15 UNION ALL
SELECT id, 3, 4, 2 FROM tiles WHERE position = 15 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 16 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 16 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 16 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 16 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 16 UNION ALL
SELECT id, 3, 2, 3 FROM tiles WHERE position = 16 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 17 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 17 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 17 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 17 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 17 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 17 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 17 UNION ALL
SELECT id, 3, 2, 3 FROM tiles WHERE position = 17 UNION ALL
SELECT id, 3, 3, 2 FROM tiles WHERE position = 17 UNION ALL
SELECT id, 3, 4, 2 FROM tiles WHERE position = 17 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 18 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 18 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 18 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 18 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 18 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 18 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 18 UNION ALL
SELECT id, 3, 2, 3 FROM tiles WHERE position = 18 UNION ALL
SELECT id, 3, 3, 3 FROM tiles WHERE position = 18 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 1, 3, 3 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 1, 4, 3 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 2, 4, 2 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 3, 2, 2 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 3, 3, 2 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 3, 4, 1 FROM tiles WHERE position = 19 UNION ALL
SELECT id, 3, 5, 1 FROM tiles WHERE position = 19 UNION ALL

SELECT id, 1, 1, 3 FROM tiles WHERE position = 20 UNION ALL
SELECT id, 1, 2, 2 FROM tiles WHERE position = 20 UNION ALL
SELECT id, 1, 3, 2 FROM tiles WHERE position = 20 UNION ALL
SELECT id, 1, 4, 1 FROM tiles WHERE position = 20 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 20 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 20 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 20 UNION ALL
SELECT id, 3, 1, 1 FROM tiles WHERE position = 20 UNION ALL
SELECT id, 3, 2, 1 FROM tiles WHERE position = 20 UNION ALL
SELECT id, 3, 3, 3 FROM tiles WHERE position = 20 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 21 UNION ALL
SELECT id, 2, 1, 1 FROM tiles WHERE position = 21 UNION ALL
SELECT id, 3, 1, 2 FROM tiles WHERE position = 21 UNION ALL
SELECT id, 3, 2, 2 FROM tiles WHERE position = 21 UNION ALL

SELECT id, 1, 1, 1 FROM tiles WHERE position = 22 UNION ALL
SELECT id, 1, 2, 1 FROM tiles WHERE position = 22 UNION ALL
SELECT id, 1, 3, 1 FROM tiles WHERE position = 22 UNION ALL
SELECT id, 2, 1, 2 FROM tiles WHERE position = 22 UNION ALL
SELECT id, 2, 2, 2 FROM tiles WHERE position = 22 UNION ALL
SELECT id, 2, 3, 2 FROM tiles WHERE position = 22 UNION ALL
SELECT id, 3, 1, 3 FROM tiles WHERE position = 22 UNION ALL
SELECT id, 3, 2, 3 FROM tiles WHERE position = 22 UNION ALL
SELECT id, 3, 3, 3 FROM tiles WHERE position = 22;
