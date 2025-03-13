CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE tiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER NOT NULL,
    position INTEGER NOT NULL, -- Position of the tile in the track
    color TEXT NOT NULL, -- "Y", "O", "R"
    FOREIGN KEY (track_id) REFERENCES tracks(id)
);

CREATE TABLE squares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tile_id INTEGER NOT NULL,
    lane INTEGER NOT NULL, -- 1, 2 or 3 lane
    position INTEGER NOT NULL, -- Position of the square within the lane
    FOREIGN KEY (tile_id) REFERENCES tiles(id)
);

-- Insert example track data
INSERT INTO tracks (name) VALUES ('Albert Park');

ALTER TABLE tiles ADD COLUMN lanes INTEGER NOT NULL DEFAULT 3;

INSERT INTO tiles (track_id, position, color) VALUES
    ((SELECT id FROM tracks WHERE name='Albert Park'), 1, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 2, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 3, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 4, 'O'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 5, 'O'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 6, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 7, 'O'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 8, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 9, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 10, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 11, 'O'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 12, 'O'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 13, 'O'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 14, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 15, 'O'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 16, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 17, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 18, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 19, 'O'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 20, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 21, 'Y'),
    ((SELECT id FROM tracks WHERE name='Albert Park'), 22, 'Y');

-- Using WITH CTEs for efficiency
WITH tile1 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 1
),
tile2 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 2
),
tile3 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 3
),
tile4 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 4
),
tile5 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 5
),
tile6 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 6
),
tile7 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 7
),
tile8 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 8
),
tile9 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 9
),
tile10 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 10
),
tile11 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 11
),
tile12 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 12
),
tile13 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 13
),
tile14 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 14
),
tile15 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 15
),
tile16 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 16
),
tile17 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 17
),
tile18 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 18
),
tile19 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 19
),
tile20 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 20
),
tile21 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 21
),
tile22 AS (
    SELECT id FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name='Albert Park') AND position = 22
)

INSERT INTO squares (tile_id, lane, position) VALUES
    ((SELECT id FROM tile1), 1, 3),
    ((SELECT id FROM tile1), 2, 3),
    ((SELECT id FROM tile1), 3, 3),

    ((SELECT id FROM tile2), 1, 3),
    ((SELECT id FROM tile2), 2, 3),
    ((SELECT id FROM tile2), 3, 3),
    
    ((SELECT id FROM tile3), 1, 3),
    ((SELECT id FROM tile3), 2, 3),
    ((SELECT id FROM tile3), 3, 3),

    ((SELECT id FROM tile4), 1, 2),
    ((SELECT id FROM tile4), 2, 2),
    ((SELECT id FROM tile4), 3, 3),

    ((SELECT id FROM tile5), 1, 4),
    ((SELECT id FROM tile5), 2, 3),
    ((SELECT id FROM tile5), 3, 3),
    
    ((SELECT id FROM tile6), 1, 3),
    ((SELECT id FROM tile6), 2, 4),
    ((SELECT id FROM tile6), 3, 4),

    ((SELECT id FROM tile7), 1, 3),
    ((SELECT id FROM tile7), 2, 3),
    ((SELECT id FROM tile7), 3, 3),

    ((SELECT id FROM tile8), 1, 3),
    ((SELECT id FROM tile8), 2, 3),
    ((SELECT id FROM tile8), 3, 4),

    ((SELECT id FROM tile9), 1, 3),
    ((SELECT id FROM tile9), 2, 3),
    ((SELECT id FROM tile9), 3, 3),

    ((SELECT id FROM tile10), 1, 2),
    ((SELECT id FROM tile10), 2, 2),
    ((SELECT id FROM tile10), 3, 2),

    ((SELECT id FROM tile11), 1, 3),
    ((SELECT id FROM tile11), 2, 3),
    ((SELECT id FROM tile11), 3, 4),

    ((SELECT id FROM tile12), 1, 3),
    ((SELECT id FROM tile12), 2, 3),
    ((SELECT id FROM tile12), 3, 2),

    ((SELECT id FROM tile13), 1, 3),
    ((SELECT id FROM tile13), 2, 3),
    ((SELECT id FROM tile13), 3, 2),

    ((SELECT id FROM tile14), 1, 3),
    ((SELECT id FROM tile14), 2, 3),
    ((SELECT id FROM tile14), 3, 3),

    ((SELECT id FROM tile15), 1, 3),
    ((SELECT id FROM tile15), 2, 4),
    ((SELECT id FROM tile15), 3, 4),

    ((SELECT id FROM tile16), 1, 2),
    ((SELECT id FROM tile16), 2, 2),
    ((SELECT id FROM tile16), 3, 2),

    ((SELECT id FROM tile17), 1, 3),
    ((SELECT id FROM tile17), 2, 3),
    ((SELECT id FROM tile17), 3, 4),

    ((SELECT id FROM tile18), 1, 3),
    ((SELECT id FROM tile18), 2, 3),
    ((SELECT id FROM tile18), 3, 3),

    ((SELECT id FROM tile19), 1, 4),
    ((SELECT id FROM tile19), 2, 4),
    ((SELECT id FROM tile19), 3, 5),

    ((SELECT id FROM tile20), 1, 4),
    ((SELECT id FROM tile20), 2, 3),
    ((SELECT id FROM tile20), 3, 3),

    ((SELECT id FROM tile21), 1, 1),
    ((SELECT id FROM tile21), 2, 1),
    ((SELECT id FROM tile21), 3, 2),

    ((SELECT id FROM tile22), 1, 3),
    ((SELECT id FROM tile22), 2, 3),
    ((SELECT id FROM tile22), 3, 3);