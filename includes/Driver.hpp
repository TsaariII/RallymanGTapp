
#pragma once
#include "Stats.hpp"
#include "Tile.hpp"
#include "Track.hpp"
#include "Tire.hpp"
#include <string>

class Driver
{
    private:
        std::string _Name;
        std::string _Team;
        int _Position;
        std::string _CurrentGear;
        int _Lap;
        Stats _Stats;
        int _TileIndex;    
        int _SquareIndex;
        int _LaneIndex;
        int _InsideIndex;
        int _StartingTile;
        Tire _Tire;
    
    public:
        Driver(const std::string &_Name, const std::string &_Team, TireType tireType, Weather weather);
    
        void setPosition(int pos);
        void setCurrentGear(const std::string& gear);
        void setTileIndex(const int index);
        void setLaneIndex(const int index);
        void setSquareIndex(const int index);
        void setInsideIndex(const int index);
        void setStartingTile(const int index);
        void setLap(const int num);
        void setTire(TireType type, Weather weather);
        void moveForward(const Track& track);
        void changeLane(const Track& track);
    
        Stats &getStats();
        std::string getName() const;
        std::string getTeam() const;
        int getPosition() const;
        std::string getCurrentGear() const;
        int getLap() const;
        int getTileIndex() const;
        int getSquareIndex() const;
        int getLaneIndex() const;
        int getInsideIndex() const;
    };
    void changeLaneOrMove(Track &track, Driver &driver);