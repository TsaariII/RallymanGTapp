
#include "../includes/Track.hpp"
#include <iostream>

Track::Track(const std::string& trackName, const std::string& dbName) : name(trackName) {
    loadTrackFromDatabase(dbName);
}

void Track::loadTrackFromDatabase(const std::string& dbName)
{
    sqlite3* db;
    sqlite3_stmt* stmt;
    int rc = sqlite3_open(dbName.c_str(), &db);
    if (rc) {
        std::cerr << "Can't open database: " << sqlite3_errmsg(db) << std::endl;
        return;
    }
    std::string queryTiles = "SELECT id, position, color, lanes FROM tiles WHERE track_id = (SELECT id FROM tracks WHERE name = ?) ORDER BY position;";
    rc = sqlite3_prepare_v2(db, queryTiles.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        std::cerr << "SQL error: " << sqlite3_errmsg(db) << std::endl;
        sqlite3_close(db);
        return;
    }
    sqlite3_bind_text(stmt, 1, name.c_str(), -1, SQLITE_STATIC);
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        int tileId = sqlite3_column_int(stmt, 0);
        std::string color = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
        int lanes = sqlite3_column_int(stmt, 3);
        Tile tile(color, lanes);
        sqlite3_stmt* stmt2;
        std::string querySquares = "SELECT lane, position FROM squares WHERE tile_id = ? ORDER BY position;";
        rc = sqlite3_prepare_v2(db, querySquares.c_str(), -1, &stmt2, nullptr);
        sqlite3_bind_int(stmt2, 1, tileId);

        while (sqlite3_step(stmt2) == SQLITE_ROW) {
            int lane = sqlite3_column_int(stmt2, 0);
            int position = sqlite3_column_int(stmt2, 1);
            tile.addSquare(lane, position);
        }
        sqlite3_finalize(stmt2);
        tiles.push_back(tile);
    }
    sqlite3_finalize(stmt);
    sqlite3_close(db);
}

const Tile& Track::getTile(int index) const {
    return tiles.at(index);
}

std::string Track::getName() const {
    return name;
}

int Track::getTrackLength() const {
    return tiles.size();
}

void Track::printTrack() const
{
    std::cout << "Track: " << name << " (Length: " << tiles.size() << " tiles)\n";
    for (size_t i = 0; i < tiles.size(); ++i)
    {
        std::cout << "Tile " << i + 1 << " (" << tiles[i].color << "): ";
        for (const auto& square : tiles[i].squares)
        {
            std::cout << "[Lane " << square.lane << ", Squares " << square.pos << "] ";
        }
        std::cout << std::endl;
    }
}