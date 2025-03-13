#pragma once

#include <vector>
#include <string>
#include <map>
#include "../includes/Driver.hpp"

class Dice
{
private:
    std::vector<std::string> sides;

public:
    Dice(const std::vector<std::string> &sides);
    std::string roll() const;
};

// Dice creation
Dice createDice(const std::string& type);

// Roll modes
void rollOneByOne(const std::vector<std::string> &diceSequence, const std::map<std::string, Dice>& diceMap, Driver &driver, Track &track);
void rollAllAtOnce(const std::vector<std::string> &diceSequence, const std::map<std::string, Dice>& diceMap, Driver &driver, Track &track);
