
#pragma once
#include <string>
#include <vector>
#include <sqlite3.h>
#include "Tile.hpp"

class Track
{
private:
    std::string name;
    std::vector<Tile> tiles;
    void loadTrackFromDatabase(const std::string& dbName);

public:
    Track(const std::string& trackName, const std::string& dbName = "tracks.db");
    const Tile &getTile(int index) const;
    std::string getName() const;
    int getTrackLength() const;
    void printTrack() const;
};

int getValidTileIndex(const Track& track);
int getValidLaneIndex(const Track& track, int tileIndex);
int getValidSquareIndex(const Track& track, int tileIndex, int laneIndex);
