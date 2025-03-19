#include "../includes/Driver.hpp"
#include "../includes/Stats.hpp"
#include <iostream>


Driver::Driver(const std::string &name, const std::string &team) 
    : name(name), team(team), position(0), lap(1), tileIndex(0), squareIndex(0), laneIndex(0) {}
    
void Driver::setPosition(int pos) { position = pos; }
void Driver::setCurrentGear(const std::string& gear) { currentGear = gear; }
void Driver::setTileIndex(const int index) { tileIndex = index; };
void Driver::setLaneIndex(const int index) { laneIndex = index; };
void Driver::setSquareIndex(const int index) { squareIndex = index; };
void Driver::setInsideIndex(const int index) { insideIndex = index; };

std::string Driver::getName() const { return name; };
std::string Driver::getTeam() const { return team; };
int Driver::getPosition() const { return position; };
std::string Driver::getCurrentGear() const {return currentGear; };
int Driver::getLap() const { return lap; };
Stats& Driver::getStats() { return stats; };
int Driver::getTileIndex() const { return tileIndex; }
int Driver::getSquareIndex() const { return squareIndex; }
int Driver::getLaneIndex() const { return laneIndex; }
int Driver::getInsideIndex() const { return insideIndex; };

void Driver::moveForward(const Track& track)
{
    const Tile& currentTile = track.getTile(tileIndex);

    // Get current lane's squares
    auto it = currentTile.laneSquares.find(laneIndex);
    if (it == currentTile.laneSquares.end() || it->second.empty())
    {
        std::cerr << "Error: Driver is in a non-existing or empty lane!\n";
        return;
    }

    // Get the squares in the current lane
    const std::vector<Square>& currentLaneSquares = it->second;

    // Check if we can move within the lane
    if ((size_t)squareIndex + 1 < currentLaneSquares.size())
    {
        squareIndex++;
    }
    else
    {
        // Move to the next tile
        tileIndex++;

        // Ensure we don't go out of bounds
        if (tileIndex >= track.getTrackLength())
        {
            std::cerr << "Error: Driver cannot move beyond the last tile!\n";
            tileIndex = track.getTrackLength() - 1;
            return;
        }

        // Get the new tile
        const Tile& nextTile = track.getTile(tileIndex);

        // Check if the next tile has the same lane
        auto nextLaneIt = nextTile.laneSquares.find(laneIndex);
        if (nextLaneIt == nextTile.laneSquares.end() || nextLaneIt->second.empty())
        {
            std::cerr << "Error: Lane " << laneIndex << " does not exist in tile " << tileIndex << "!\n";
            return;
        }

        // Move to the first square in the same lane of the next tile
        squareIndex = 0;
        std::cout << name << " moved to tile " << tileIndex << " (" << nextTile.color << ") in lane " << laneIndex << "\n";
    }
}

void Driver::changeLane(const Track& track, int direction)
{
    const Tile& currentTile = track.getTile(tileIndex);
    
    int newLane = laneIndex + direction;
    if (newLane >= 0 && newLane < currentTile.lanes)
    {
        laneIndex = newLane;
        std::cout << name << " switched to lane " << laneIndex << "\n";
    }
    else
    {
        std::cout << name << " can't switch lanes (out of bounds)\n";
    }
}