#pragma once

#include <vector>
#include <string>
#include <map>
#include "../includes/Driver.hpp"

class Dice
{
private:
    std::vector<std::string> _Sides;

public:
    Dice(const std::vector<std::string> &sides);
    ~Dice();
    std::string roll() const;
};

Dice createDice(const std::string& type);

void rollOneByOne(const std::vector<std::string> &diceSequence, const std::map<std::string, Dice>& diceMap, Driver &driver, Track &track);
void rollAllAtOnce(const std::vector<std::string> &diceSequence, const std::map<std::string, Dice>& diceMap, Driver &driver, Track &track);
