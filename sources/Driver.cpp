#include "../includes/Driver.hpp"
#include <iostream>

Driver::Driver(const std::string &name, const std::string &team)
    : name(name), team(team), position(0), focusTokens(0), usedFocusTokens(0),
      lostGear(0), lostBrake(0), lostCoast(0),
      weatherToken(0), yellowFlag(0), greenFlag(0) {}

void Driver::addDiceRoll(const std::string& result) {
    diceRolls.push_back(result);
}

void Driver::addFocusToken() { focusTokens++; }
void Driver::addTurn() { turns++; };
void Driver::useFocusToken() { if (focusTokens > 0) { focusTokens--; usedFocusTokens++; } }
void Driver::setPosition(int pos) { position = pos; }
void Driver::setCurrentGear(const std::string& gear) { currentGear = gear; }

void Driver::addCrashTokens(const std::string &gear, const std::string &section)
{
    int crashTokens = 0;
    if (gear == "3" && section == "R") crashTokens = 1;
    else if (gear == "4") {
        if (section == "O") crashTokens = 1;
        else if (section == "R") crashTokens = 2;
    }
    else if (gear == "5") {
        if (section == "Y") crashTokens = 1;
        else if (section == "O") crashTokens = 2;
        else if (section == "R") crashTokens = 3;
    }
    else if (gear == "6")
    {
        if (section == "Y") crashTokens = 2;
        else if (section == "O") crashTokens = 3;
        else if (section == "R") crashTokens = 4;
    }
    const std::vector<std::string> tokenPool = {
        "⬛️", // -1 gear dice
        "🟥", // -1 brake dice
        "⬜️", // -1 coast dice
        "⛅️", // weather token
        "🟨", // yellow flag
        "🟩"  // green flag
    };
    int n = 0;
    for (int i = 0; i < crashTokens; ++i) {
        int randomIndex = rand() % tokenPool.size();
        std::string token = tokenPool[randomIndex];
        if (randomIndex == 0)
            lostGear += 1;
        if (randomIndex == 1)
            lostBrake += 1;
        if (randomIndex == 2)
            lostCoast+= 1;
        if (randomIndex == 3)
            weatherToken += 1;
        if (randomIndex == 4)
            yellowFlag += 1;
        if (randomIndex == 5)
            greenFlag += 1;
        std::cout << "Token number " << ++n << " " << tokenPool[randomIndex] << std::endl;
    }
}

std::string Driver::getName() const { return name; }
std::string Driver::getTeam() const { return team; }
int Driver::getPosition() const { return position; }
int Driver::getFocusTokens() const { return focusTokens; }
int Driver::getUsedFocusTokens() const { return usedFocusTokens; }
std::string Driver::getLastGear() const { return currentGear; }
std::vector<std::string> Driver::getDiceResults() const { return diceRolls; }

int Driver::getMinusGearDice() const { return lostGear; }
int Driver::getMinusBrakeDice() const { return lostBrake; }
int Driver::getMinusCoastDice() const { return lostCoast; }
int Driver::getWeatherToken() const { return weatherToken; }
int Driver::getYellowFlag() const { return yellowFlag; }
int Driver::getGreenFlag() const { return greenFlag; }

void Driver::resetStats() {
    position = 0;
    focusTokens = 0;
    usedFocusTokens = 0;
    diceRolls.clear();
    lostGear = lostBrake = lostCoast = 0;
    weatherToken = yellowFlag = greenFlag = 0;
}