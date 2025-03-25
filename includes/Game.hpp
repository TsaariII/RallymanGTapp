
#pragma once
#include "Tire.hpp"
#include "Team.hpp"
#include "Dice.hpp"
#include <iostream>
#include <set>

class Game
{
    private:
        Track _Track;
        Weather _Weather;
        std::vector<Team> _Teams;
        std::vector<Driver*> _Drivers;
        void _SetupGame();
        void _SetWeather();
        void _SetTires();
        void _DriverPositions();
        void _PrintCountdown();
        void _RaceLoop();
        
    public:
        Game(const std::string &trackName);
        void start();
};
void setDriverStartingPosition(Driver* driver, Track& track, std::set<int>& assignedPositions);
void raceRound(std::vector<Driver*> drivers, const std::map<std::string, Dice>& diceMap, Track &track);