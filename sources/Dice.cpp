
#include "../includes/Dice.hpp"
#include "../includes/Driver.hpp"
#include <iostream>
#include <sstream>
#include <cstdlib>
#include <ctime>
#include <map>

// Dice class implementations
Dice::Dice(const std::vector<std::string>& sides) : sides(sides) {}

std::string Dice::roll() const {
    if (sides.empty()) return "Invalid dice!";
    int index = rand() % sides.size();
    return sides[index];
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
    if (gear == "C")
    {
        for(size_t i = 0; i < diceSequence.size(); i++)
        {
            if (diceSequence[0] == "C")
            {
                gear = driver.getLastGear();
                break ;
            }
            if (diceSequence[i + 1] == "C")
            {
                gear = diceSequence[i];
                break ;
            }
        }
    }
    if (gear == "B")
    {
        for(size_t i = 0; i < diceSequence.size(); i++)
        {
            while (diceSequence[i] == "B")
            {
                if (diceSequence[i + 1] != "B")
                {
                    gear = diceSequence[i];
                    break ;
                }
                i++;
            }
        }
    }
}

void checkColorInput(Driver &driver, std::string gear, std::string section)
{
    while (true)
    {
        std::cout << "Enter track section color: ";
        std::cin >> section;
        if (section == "O" || section == "Y" || section == "R")
        {
            driver.addCrashTokens(gear, section);
            std::cout << "Lost control and spun!" << std::endl;
            break ;
        }
        else
        {
            std::cin.clear(); // Clear the error state if input failed
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Discard invalid input
            std::cout << "Please enter O, Y or R." << std::endl;
        }
    }
    return ;
}

void rollOneByOne(const std::vector<std::string> &diceSequence, const std::map<std::string, Dice> &diceMap, Driver &driver, std::string section)
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
            gear = diceSequence[i];
            coastOrBreak(driver, diceSequence, result);
            std::cout << "You lost control on " << gear << " gear" << std::endl;
            checkColorInput(driver, gear, section);
            return ;
        }
        std::cout << "Press Enter to continue or type 'exit' to return to dice selection: ";
        std::string choice;
        std::getline(std::cin, choice);
        if (choice == "exit")
            return ;
    }
}

void rollAllAtOnce(const std::vector<std::string> &diceSequence, const std::map<std::string, Dice> &diceMap, Driver &driver, std::string section)
{
    int tokens = diceSequence.size();
    int crash = 0;
    int marked = 0;
    std::string gear;
    for (size_t i = 0; i < diceSequence.size(); i++)
    {
        std::cout << diceSequence[i] << " ";
        std::string result = diceMap.at(diceSequence[i]).roll();
        std::cout << result << std::endl;
        if (diceSequence[i] == "B")
            tokens -= 1;
        if (result == "⚠️")
            crash++;
        if (crash == 3 && !marked)
        {
            gear = diceSequence[i];
            marked = 1;
        }
    }
    coastOrBreak(driver, diceSequence, gear);
    if (crash >= 3)
    {
        std::cout << "You lost control on " << gear << " gear" << std::endl;
        checkColorInput(driver, gear, section);
    }
    std::cout << "Tokens earned: " << tokens << std::endl;
}