
#pragma once
#include <string>
#include <vector>
#include <map>

struct Square
{
    int lane;
    int pos;
    int insidePriority;
    Square(int l, int p, int inP) : lane(l), pos(p), insidePriority(inP) {}

};

class Tile
{
    public:
        std::string color;
        int lanes;
        std::map<int, std::vector<Square>> laneSquares; // Group squares by lane

        Tile(std::string c, int l) : color(std::move(c)), lanes(l) {}
    
        void addSquare(int lane, int pos, int inPos)
        {
            if (laneSquares.find(lane) == laneSquares.end())
                laneSquares[lane] = std::vector<Square>(); // Ensure lane exists before adding squares
        
            laneSquares[lane].emplace_back(lane, pos, inPos);
        }
        int getInsidePriority(int lane) const {
            auto it = laneSquares.find(lane);
            if (it != laneSquares.end() && !it->second.empty()) {
                return it->second.front().insidePriority; // The first square represents the lane's priority
            }
            return 100; // Default high number means outside lane
        }
};