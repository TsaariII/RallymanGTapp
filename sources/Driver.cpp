#include "../includes/Driver.hpp"
#include "../includes/Stats.hpp"
#include <iostream>


Driver::Driver(const std::string &_Name, const std::string &_Team, TireType tireType, Weather weather) 
    : _Name(_Name), _Team(_Team), _Position(0), _CurrentGear("0"), _Lap(1), _TileIndex(0), _SquareIndex(0), _LaneIndex(0), _StartingTile(0), _Tire(tireType, weather) {}
    
void Driver::setPosition(int pos) { _Position = pos; }
void Driver::setCurrentGear(const std::string& gear) { _CurrentGear = gear; }
void Driver::setTileIndex(const int index) { _TileIndex = index; };
void Driver::setLaneIndex(const int index) { _LaneIndex = index; };
void Driver::setSquareIndex(const int index) { _SquareIndex = index; };
void Driver::setInsideIndex(const int index) { _InsideIndex = index; };
void Driver::setStartingTile(const int index) { _StartingTile = index; };
void Driver::setLap(const int num) { _Lap = num; };
void Driver::setTire(TireType type, Weather weather) { _Tire = Tire(type, weather); };

std::string Driver::getName() const { return _Name; };
std::string Driver::getTeam() const { return _Team; };
int Driver::getPosition() const { return _Position; };
std::string Driver::getCurrentGear() const {return _CurrentGear; };
int Driver::getLap() const { return _Lap; };
Stats& Driver::getStats() { return _Stats; };
int Driver::getTileIndex() const { return _TileIndex; }
int Driver::getSquareIndex() const { return _SquareIndex; }
int Driver::getLaneIndex() const { return _LaneIndex; }
int Driver::getInsideIndex() const { return _InsideIndex; };

void Driver::moveForward(const Track& track)
{
    const Tile& currentTile = track.getTile(_TileIndex);
    auto it = currentTile.laneSquares.find(_LaneIndex);
    if (it == currentTile.laneSquares.end() || it->second.empty())
    {
        std::cerr << "Error: Driver is in a non-existing or empty lane!\n";
        return;
    }
    const std::vector<Square>& currentLaneSquares = it->second;
    if ((size_t)_SquareIndex + 1 < currentLaneSquares.size())
    {
        _SquareIndex++;
    }
    else
    {
        _TileIndex++;
        if (_TileIndex >= track.getTrackLength())
        {
            _Lap++;
            _TileIndex = 0;
        }
        const Tile& nextTile = track.getTile(_TileIndex);
        auto nextLaneIt = nextTile.laneSquares.find(_LaneIndex);
        if (nextLaneIt == nextTile.laneSquares.end() || nextLaneIt->second.empty())
        {
            std::cerr << "Error: Lane " << _LaneIndex << " does not exist in tile " << _TileIndex << "!\n";
            return;
        }
        _SquareIndex = 0;
        std::cout << _Name << " moved to tile " << _TileIndex << " (" << nextTile.color << ") in lane " << _LaneIndex << "\n";
    }
}

void Driver::changeLane(const Track& track)
{
    const Tile& currentTile = track.getTile(_TileIndex);
    while (true)
    {
        int direction;
        std::cout << "Enter lane change direction (1: Left, -1: Right): ";
        std::cin >> direction;
        int newLane = _LaneIndex + direction;
        std::cout << "new lane: " << newLane << std::endl;
        if (newLane >= 0 && newLane <= currentTile.lanes)
        {
            _LaneIndex = newLane;
            std::cout << _Name << " switched to lane " << _LaneIndex << "\n";
            break ;
        }
        else
        {
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            std::cout << "Invalid lane! Try again.\n";
        }
    }
}

void changeLaneOrMove(Track &track, Driver &driver)
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
        driver.moveForward(track); 
    else if (action == 2)
        driver.changeLane(track);
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}