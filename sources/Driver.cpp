#include "../includes/Driver.hpp"
#include "../includes/Stats.hpp"
#include <iostream>


Driver::Driver(const std::string &name, const std::string &team) 
    : name(name), team(team), position(0), tileIndex(0), squareIndex(0), laneIndex(0) {}
    
void Driver::setPosition(int pos) { position = pos; }
void Driver::setCurrentGear(const std::string& gear) { currentGear = gear; }
void Driver::setTileIndex(const int index) { tileIndex = index; };
void Driver::setLaneIndex(const int index) { laneIndex = index; };
void Driver::setSquareIndex(const int index) { squareIndex = index; };

std::string Driver::getName() const { return name; };
std::string Driver::getTeam() const { return team; };
int Driver::getPosition() const { return position; };
std::string Driver::getCurrentGear() const {return currentGear; };
Stats& Driver::getStats() { return stats; };
int Driver::getTileIndex() const { return tileIndex; }
int Driver::getSquareIndex() const { return squareIndex; }
int Driver::getLaneIndex() const { return laneIndex; }

void Driver::moveForward(const Track& track)
{
    const Tile& currentTile = track.getTile(tileIndex);

    if ((size_t)squareIndex + 1 < currentTile.squares.size())
    {
        squareIndex++;
    }
    else
    {
        tileIndex++;
        squareIndex = 0;
        std::cout << name << " moved to tile " << tileIndex + 1 << " (" << currentTile.color << ")\n";
    }
}

void Driver::changeLane(const Track& track, int direction)
{
    const Tile& currentTile = track.getTile(tileIndex);
    
    int newLane = laneIndex + direction;
    if (newLane >= 0 && newLane < currentTile.lanes) {
        laneIndex = newLane;
        std::cout << name << " switched to lane " << laneIndex + 1 << "\n";
    } else {
        std::cout << name << " can't switch lanes (out of bounds)\n";
    }
}