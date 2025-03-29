
#pragma once
#include <string>
#include <vector>
#include <sqlite3.h>
#include "Tile.hpp"

class Track
{
    private:
        std::string _Name;
        std::vector<Tile> _Tiles;
        std::vector<std::string> _tracks = {
            "Albert Park", "Adelaide", "Anderstorp",
            "Algarve", "Autopolis", "Baku",
            "Bahrain", "Belle Isle", "Brands Hatch",
            "Brands Hatch Indy", "Bridgehampton",
            "Brno", "Bugatti le Mans", "Buriram",
            "Catalunya-Barcelona", "Circuit of The Americas",
            "Clastres", "Catalunya", "Croix-en-Ternois",
            "Daytona", "Donington Park", "Dubai", "Estoril",
            "Eboladrome", "Folembray", "Fuji", "Goodwood", "Hanoi",
            "Hockenheimring", "Hungaroring", "Igora Drive", "Imola",
            "Indianapolis", "Interlagos", "Jarama", "Jeddah", "Jerez",
            "Knockhill", "Korea", "Kyalami", "Kymiring", "Laguna Seca",
            "Las Levas", "Lausitzring", "Ledenon", "Lime Rock", "Long Beach",
            "Macau", "Magny-Cours", "Marina Bay", "Mas du Clos 1970", "Mexico City",
            "Miami", "Misano", "Mas du Clos 2022", "Mid-Ohio", "Monaco", "Montreal",
            "Moscow", "Mosport Park", "Most", "Motegi", "Mount Panorama", "Mugello",
            "Nogaro", "Norisring", "Okayama", "Oschersleben", "Oulton Park",
            "Pau-Ville", "Paul Ricard", "Red Bull Ring", "Road America", "Road Atlanta",
            "Sachsenring", "Saint-Eustache", "Sebring", "Sepang", "Shanghai", "Silverstone",
            "Slovakiaring", "Snetterton", "Sonoma", "Spa Francorchamps", "Suzuka",
            "Sportsland Sugo", "St. Petersburg", "Tsukuba", "TT Assen", "Valencia",
            "Vila Real", "Virginia", "Watkins Glen", "Zandvoort", "Zolder"
        };
    
        void                loadTrackFromDatabase(const std::string& dbName);

    public:
        Track(const std::string& trackName, const std::string& dbName = "tracks.db");
        const Tile&         getTile(int index) const;
        std::string         getName() const;
        bool                verifyTrackName( const std::string& trackName, const std::string& dbName) {
        int                 getTrackLength() const;
        void                printTrack() const;
};

int                     getValidTileIndex(const Track& track);
int                     getValidLaneIndex(const Track& track, int tileIndex);
int                     getValidSquareIndex(const Track& track, int tileIndex, int laneIndex);
