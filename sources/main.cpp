#include <iostream>
#include <string>
#include <map>
#include <sstream>
#include <set>
#include <thread>
#include <chrono> 
#include "../includes/Dice.hpp"
#include "../includes/Team.hpp"
#include "../includes/Driver.hpp"
#include "../includes/Track.hpp"
#include "../includes/Game.hpp"

int main()
{
    std::string trackName;
    std::cout << "Enter track name: ";
    std::getline(std::cin, trackName);
    Game game(trackName);
    game.start();
    return 0;
}