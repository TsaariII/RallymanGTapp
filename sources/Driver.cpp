#include "../includes/Driver.hpp"
#include "../includes/Stats.hpp"
#include <iostream>


Driver::Driver(const std::string &name, const std::string &team) 
    : name(name), team(team), position(0), lap(1), tileIndex(0), squareIndex(0), laneIndex(0), startingTile(0) {}
    
void Driver::setPosition(int pos) { position = pos; }
void Driver::setCurrentGear(const std::string& gear) { currentGear = gear; }
void Driver::setTileIndex(const int index) { tileIndex = index; };
void Driver::setLaneIndex(const int index) { laneIndex = index; };
void Driver::setSquareIndex(const int index) { squareIndex = index; };
void Driver::setInsideIndex(const int index) { insideIndex = index; };
void Driver::setStartingTile(const int index) { startingTile = index; };
void Driver::setLap(const int num) { lap = num; };

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
    auto it = currentTile.laneSquares.find(laneIndex);
    if (it == currentTile.laneSquares.end() || it->second.empty())
    {
        std::cerr << "Error: Driver is in a non-existing or empty lane!\n";
        return;
    }
    const std::vector<Square>& currentLaneSquares = it->second;
    if ((size_t)squareIndex + 1 < currentLaneSquares.size())
    {
        squareIndex++;
    }
    else
    {
        tileIndex++;
        if (tileIndex >= track.getTrackLength())
        {
            lap++;
            tileIndex = 0;
        }
        const Tile& nextTile = track.getTile(tileIndex);
        auto nextLaneIt = nextTile.laneSquares.find(laneIndex);
        if (nextLaneIt == nextTile.laneSquares.end() || nextLaneIt->second.empty())
        {
            std::cerr << "Error: Lane " << laneIndex << " does not exist in tile " << tileIndex << "!\n";
            return;
        }
        squareIndex = 0;
        std::cout << name << " moved to tile " << tileIndex << " (" << nextTile.color << ") in lane " << laneIndex << "\n";
    }
}

void Driver::changeLane(const Track& track, int direction)
{
    const Tile& currentTile = track.getTile(tileIndex);
    
    int newLane = laneIndex + direction;
    while (true)
    {
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
}

void changeToValidLane(Track &track, Driver &driver)
{
    int action;
    while (true) 
    {
        std::cout << "Choose action (1: Move Forward, 2: Change Lane): ";
        std::cin >> action;

        if (std::cin.fail() || (action != 1 && action != 2))
        {
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            std::cout << "Invalid action! Try again.\n";
        }
        else
            break;
    }
    if (action == 1)
    {
        driver.moveForward(track);
    }
    else if (action == 2)
    {
        int direction;
        std::cout << "Enter lane change direction (1: Left, -1: Right): ";
        std::cin >> direction;
        driver.changeLane(track, direction);
    }
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}