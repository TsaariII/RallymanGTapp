
#pragma once
#include "Stats.hpp"
#include "Tile.hpp"
#include "Track.hpp"
#include <string>

class Driver
{
    private:
        const std::string name;
        const std::string team;
        int position;
        std::string currentGear;
        Stats stats;
        int tileIndex;    
        int squareIndex;
        int laneIndex;
    
    public:
        Driver(const std::string &name, const std::string &team);
    
        void setPosition(int pos);
        void setCurrentGear(const std::string& gear);
        void setTileIndex(const int index);
        void setLaneIndex(const int index);
        void setSquareIndex(const int index);
        
        void moveForward(const Track& track);
        void changeLane(const Track& track, int direction); // -1 left, +1 right
    
        Stats &getStats();
        std::string getName() const;
        std::string getTeam() const;
        int getPosition() const;
        std::string getCurrentGear() const;
        int getTileIndex() const;
        int getSquareIndex() const;
        int getLaneIndex() const;
    };