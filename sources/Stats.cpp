
#include "../includes/Stats.hpp"
#include <iostream>

Stats::Stats() : turns(0), focusTokens(0), usedFocusTokens(0), lostGear(0), 
                 lostBrake(0), lostCoast(0), weatherToken(0), yellowFlag(0), greenFlag(0) {}

// Getter Functions
int Stats::getTurns() const { return turns; }
int Stats::getFocusTokens() const { return focusTokens; }
int Stats::getUsedFocusTokens() const { return usedFocusTokens; }
int Stats::getLostGear() const { return lostGear; }
int Stats::getLostBrake() const { return lostBrake; }
int Stats::getLostCoast() const { return lostCoast; }
int Stats::getWeatherToken() const { return weatherToken; }
int Stats::getYellowFlag() const { return yellowFlag; }
int Stats::getGreenFlag() const { return greenFlag; }
std::vector<std::string> Stats::getDiceRolls() const { return diceRolls; }

// Setter Functions
void Stats::addTurn() { turns++; }
void Stats::addFocusToken() { focusTokens++; }
void Stats::useFocusToken() { if (focusTokens > 0) { focusTokens--; usedFocusTokens++; } }
void Stats::loseGear() { lostGear++; }
void Stats::loseBrake() { lostBrake++; }
void Stats::loseCoast() { lostCoast++; }
void Stats::addWeatherToken() { weatherToken++; }
void Stats::addYellowFlag() { yellowFlag++; }
void Stats::addGreenFlag() { greenFlag++; }
void Stats::addDiceRoll(const std::string& roll) { diceRolls.push_back(roll); }
void Stats::resetDiceRolls() { diceRolls.clear(); }

void Stats::printStats() 
{
    std::cout << "Turns: " << turns
            << "\nFocus Tokens: " << focusTokens
            << "\nUsed focus toksen: " << usedFocusTokens
            << "\nLost gear dice: " << lostGear
            << "\nLost brake dice: " << lostBrake
            << "\nLost coast dice: " << lostCoast
            << "\nWeather tokens: " << weatherToken
            << "\nYellow flag: " << yellowFlag
            << "\nGreen flag: " << greenFlag << std::endl;
}

void Stats::addCrashTokens(const std::string &gear, const std::string &section)
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

void Stats::addLapTime(const std::string &gear)
{
    int timeToAdd = 0;

    if (gear == "00") timeToAdd = 120;  // 2 minutes (120 seconds)
    else if (gear == "0") timeToAdd = 60; // 1 minute (60 seconds)
    else if (gear == "1") timeToAdd = 50;
    else if (gear == "2") timeToAdd = 40;
    else if (gear == "3") timeToAdd = 30;
    else if (gear == "4") timeToAdd = 20;
    else if (gear == "5") timeToAdd = 15;
    else if (gear == "6") timeToAdd = 10;

    totalTime += timeToAdd;

    if (lapTime.empty()) lapTime.push_back(timeToAdd);
    else lapTime.back() += timeToAdd;
}

std::string Stats::getTotalTime() const
{
    int minutes = totalTime / 60;
    int seconds = totalTime % 60;
    return std::to_string(minutes) + ":" + (seconds < 10 ? "0" : "") + std::to_string(seconds);
}

std::vector<std::string> Stats::getLapTime() const
{
    std::vector<std::string> formattedLaps;
    for (int time : lapTime)
    {
        int minutes = time / 60;
        int seconds = time % 60;
        formattedLaps.push_back(std::to_string(minutes) + ":" + (seconds < 10 ? "0" : "") + std::to_string(seconds));
    }
    return formattedLaps;
}

void Stats::resetStats()
{
    turns = 0;
    focusTokens = 0;
    usedFocusTokens = 0;
    lostGear = lostBrake = lostCoast = 0;
    weatherToken = yellowFlag = greenFlag = 0;
    diceRolls.clear();
}