
#include "../includes/Dice.hpp"
#include "../includes/Driver.hpp"
#include "../includes/Track.hpp"
#include <iostream>
#include <sstream>
#include <cstdlib>
#include <ctime>
#include <map>

Dice::Dice(const std::vector<std::string>& sides) : _Sides(sides) {}
Dice::~Dice() {};

std::string Dice::roll() const
{
    if (_Sides.empty())
        return "Invalid dice!";
    int index = rand() % _Sides.size();
    return _Sides[index];
}

Dice createDice(const std::string &type)
{
    if (type == "1")
        return Dice({"1", "1", "1", "1", "1", "⚠️"});
    if (type == "2")
        return Dice({"2", "2", "2", "2", "2", "⚠️"});
    if (type == "3")
        return Dice({"3", "3", "3", "3", "⚠️", "⚠️"});
    if (type == "4")
        return Dice({"4", "4", "4", "4", "⚠️", "⚠️"});
    if (type == "5")
        return Dice({"5", "5", "5", "5", "⚠️", "⚠️"});
    if (type == "6")
        return Dice({"6", "6", "6", "6", "⚠️", "⚠️"});
    if (type == "C")
        return Dice({"⬜️", "⬜️", "⬜️", "⬜️", "⬜️", "⚠️"});
    if (type == "B")
        return Dice({"🟥", "🟥", "🟥", "🟥", "⚠️", "⚠️"});
    return Dice({});
}

void coastOrBreak(Driver &driver, const std::vector<std::string> &diceSequence, std::string &gear)
{
    if (gear == "C") {
        if (diceSequence.front() == "C") {
            gear = driver.getCurrentGear();
            return ;
        }
        for(size_t i = 0; i < diceSequence.size(); i++) {
            if (diceSequence[i] == "C") {
                gear = diceSequence[i - 1];
                return ;
            }
        }
    }
    if (gear == "B") {
        for(size_t i = 0; i < diceSequence.size(); i++) {
            if (diceSequence[i] == "B") {
                while (i + 1 < diceSequence.size() && diceSequence[i + 1] == "B")
                    i++;
                if (i + 1 < diceSequence.size())
                    gear = diceSequence[i + 1];
                return ;
            }
        }
    }
}

// void checkColorInput(Driver &driver, std::string gear, std::string section)
// {
//     while (true)
//     {
//         std::cout << "Enter track section color: ";
//         std::cin >> section;
//         if (section == "O" || section == "Y" || section == "R")
//         {
//             driver.getStats().addCrashTokens(gear, section);
//             std::cout << "Lost control and spun!" << std::endl;
//             break ;
//         }
//         else
//         {
//             std::cin.clear(); // Clear the error state if input failed
//             std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Discard invalid input
//             std::cout << "Please enter O, Y or R." << std::endl;
//         }
//     }
//     return ;
// }

void rollOneByOne(const std::vector<std::string> &diceSequence, const std::map<std::string, Dice> &diceMap, Driver &driver, Track &track)
{
    int crash = 0;
    std::string gear;
    for (size_t i = 0; i < diceSequence.size(); i++)
    {
        std::cout << diceSequence[i] << " ";
        std::string result = diceMap.at(diceSequence[i]).roll();
        std::cout << result << std::endl;
        if (result == "⚠️")
            crash ++;
        if (crash == 3)
        {
            coastOrBreak(driver, diceSequence, result);
            std::cout << "You lost control on " << gear << " gear" << std::endl;
            driver.getStats().addCrashTokens(gear, track.getTile(driver.getTileIndex()).color);
            gear = (std::stoi(gear) >= 3) ? "00" : "0";
            driver.setCurrentGear(gear);
            int lane = getValidLaneIndex(track, driver.getTileIndex());
            driver.setLaneIndex(lane);
            int sqr = getValidSquareIndex(track, driver.getTileIndex(), lane);
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            driver.setSquareIndex(sqr);
            return ;
        }
        driver.moveForward(track);
        int lane = getValidLaneIndex(track, driver.getTileIndex());
        driver.setLaneIndex(lane);
        int sqr = getValidSquareIndex(track, driver.getTileIndex(), lane);
        driver.setSquareIndex(sqr);
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        std::cout << "Press Enter to continue or type 'exit' to return to dice selection: ";
        std::string choice;
        std::getline(std::cin, choice);
        if (choice == "exit")
            return ;
    }
}

void rollAllAtOnce(const std::vector<std::string> &diceSequence, const std::map<std::string, Dice> &diceMap, Driver &driver, Track &track)
{
    int tokens = diceSequence.size();
    int crash = 0;
    int moves = 0;
    std::string gear;
    for (size_t i = 0; i < diceSequence.size(); i++)
    {
        if (crash == 3)
        {
            gear = diceSequence[i - 1];
            break ;
        }
        std::cout << diceSequence[i] << " ";
        std::string result = diceMap.at(diceSequence[i]).roll();
        std::cout << result << std::endl;
        if (diceSequence[i] == "B")
        {
            moves--;
            tokens -= 1;
        }
        if (result == "⚠️")
            crash++;
        moves++;
    }
    if (gear.empty())
        gear = diceSequence.back();
    std::cout << "Gear is: " << gear << std::endl;
    coastOrBreak(driver, diceSequence, gear);
    for (int i = 0; i < moves; i++)
    {
        std::cout << "Entering for dice " << i + 1 << std::endl;
        driver.moveForward(track);
        int lane = getValidLaneIndex(track, driver.getTileIndex());
        driver.setLaneIndex(lane);
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
    if (crash == 3)
    {
        std::cout << "You lost control on " << gear << " gear" << std::endl;
        driver.getStats().addCrashTokens(gear, track.getTile(driver.getTileIndex()).color);
        gear = (std::stoi(gear) >= 3) ? "00" : "0";
        driver.setCurrentGear(gear);
        int lane = getValidLaneIndex(track, driver.getTileIndex());
        driver.setLaneIndex(lane);
        int sqr = getValidSquareIndex(track, driver.getTileIndex(), lane);
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        driver.setSquareIndex(sqr);
    }
    std::cout << "Tokens earned: " << tokens << std::endl;
    // std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}