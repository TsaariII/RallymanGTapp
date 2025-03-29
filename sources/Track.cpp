
#include "../includes/Track.hpp"
#include <iostream>

bool    Track::verifyTrackName( const std::string& trackName, const std::string& dbName) {
    for (auto it = _tracks.begin(); it != _tracks.end(); it++)
    {
        if (trackName == *it)
        {
            // also insert here to check inside the tracks directory if we have it

            return (true);
        }
    }
    return (false);
}

Track::Track(const std::string& trackName, const std::string& dbName) : _Name(trackName) {
    if (verifyTrackName(trackName, dbName));
        loadTrackFromDatabase(dbName);
    else
        return ;
}

void Track::loadTrackFromDatabase(const std::string& dbName)
{
    sqlite3* db;
    sqlite3_stmt* stmt;
    int rc = sqlite3_open(dbName.c_str(), &db);
    if (rc)
    {
        std::cerr << "Can't open database: " << sqlite3_errmsg(db) << std::endl;
        return;
    }

    std::string queryTiles = "SELECT id, position, color, lanes FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name = ?) ORDER BY position;";
    rc = sqlite3_prepare_v2(db, queryTiles.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK)
    {
        std::cerr << "SQL error: " << sqlite3_errmsg(db) << std::endl;
        sqlite3_close(db);
        return;
    }

    sqlite3_bind_text(stmt, 1, _Name.c_str(), -1, SQLITE_STATIC);
    
    while (sqlite3_step(stmt) == SQLITE_ROW)
    {
        int tileId = sqlite3_column_int(stmt, 0);
        std::string color = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
        int lanes = sqlite3_column_int(stmt, 3);
        Tile tile(color, lanes);

        sqlite3_stmt* stmt2;
        std::string querySquares = "SELECT lane, position, inside_lane FROM squares WHERE tile_id = ? ORDER BY lane, position;";
        rc = sqlite3_prepare_v2(db, querySquares.c_str(), -1, &stmt2, nullptr);
        if (rc == SQLITE_OK)
        {
            sqlite3_bind_int(stmt2, 1, tileId);  // Ensure correct filtering
            while (sqlite3_step(stmt2) == SQLITE_ROW)
            {
                int lane = sqlite3_column_int(stmt2, 0);
                int position = sqlite3_column_int(stmt2, 1);
                int insideLane = sqlite3_column_int(stmt2, 2);

                // Ensure that laneSquares[lane] is properly initialized
                if (tile.laneSquares.find(lane) == tile.laneSquares.end())
                    tile.laneSquares[lane] = std::vector<Square>();  // Initialize if not exists

                tile.addSquare(lane, position, insideLane);
            }
            sqlite3_finalize(stmt2);
        }
        else
        {
            std::cerr << "SQL error fetching squares: " << sqlite3_errmsg(db) << std::endl;
        }

        _Tiles.push_back(std::move(tile));  // ✅ Push after loading squares
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
}

const Tile& Track::getTile(int index) const {
    return _Tiles.at(index);
}

std::string Track::getName() const {
    return _Name;
}

int Track::getTrackLength() const {
    return _Tiles.size();
}

void Track::printTrack() const
{
    std::cout << "Track: " << _Name << " (Length: " << _Tiles.size() << " _Tiles)\n";
    for (size_t i = 0; i < _Tiles.size(); ++i)
    {
        std::cout << "Tile " << i  << " (" << _Tiles[i].color << "): ";
        for (const auto& [lane, squares] : _Tiles[i].laneSquares)
        {
            std::cout << "[Lane " << lane << ": Squares " << squares.size() << "] ";
        }
        std::cout << std::endl;
    }
}

int getValidTileIndex(const Track& track)
{
    int tile;
    while (true)
    {
        std::cout << "Enter starting tile (0 - " << track.getTrackLength() - 1 << "): ";
        std::cin >> tile;
        if (std::cin.fail() || tile < 0 || tile >= track.getTrackLength())
        {
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            std::cout << "Invalid tile! Try again.\n";
        }
        else
            return tile;
    }
}

int getValidLaneIndex(const Track& track, int tileIndex)
{
    int lane;
    const Tile& tile = track.getTile(tileIndex);
    
    while (true)
    {
        std::cout << "Enter lane (1 - " << tile.lanes << "): ";
        std::cin >> lane;
        if (std::cin.fail() || lane < 1 || lane > tile.lanes)
        {
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            std::cout << "Invalid lane! Try again.\n";
        }
        else if (tile.laneSquares.find(lane) == tile.laneSquares.end())
        {
            std::cout << "Error: Invalid lane index or empty lane!\n";
        }
        else
        {
            return lane;
        }
    }
}

int getValidSquareIndex(const Track& track, int tileIndex, int laneIndex)
{
    int sqr;
    const Tile& tile = track.getTile(tileIndex);
    
    if (tile.laneSquares.find(laneIndex) == tile.laneSquares.end() || tile.laneSquares.at(laneIndex).empty()) {
        std::cerr << "Error: Invalid lane index or empty lane!\n";
        return -1;
    }
    int maxSquareIndex = tile.laneSquares.at(laneIndex).size() - 1;
    while (true)
    {
        std::cout << "Enter square (0 - " << maxSquareIndex << "): ";
        std::cin >> sqr;

        if (std::cin.fail() || sqr < 0 || sqr > maxSquareIndex)
        {
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            std::cout << "Invalid square! Try again.\n";
        }
        else
        {
            return sqr;
        }
    }
}
