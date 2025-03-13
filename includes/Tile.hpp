
#pragma once
#include <string>
#include <vector>

struct Square
{
    int lane;
    int pos;
    Square(int l, int p) : lane(l), pos(p) {}

};

class Tile
{
    public:
        std::string color;
        int lanes;
        std::vector <Square> squares;
    
        Tile(std::string c, int l) : color(std::move(c)), lanes(l) {}
    
        void addSquare(int lane, int pos) { squares.emplace_back(lane, pos); };
        // bool isExit(int squareIndex) const {  // Check if driver is at the end of the tile
        //     return squareIndex >= pos - 1;
        // }
};