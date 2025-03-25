
#include "../includes/Stats.hpp"
#include <iostream>

Stats::Stats() : _Turns(0), _FocusTokens(0), _UsedFocusTokens(0), _LostGear(0), 
                 _LostBrake(0), _LostCoast(0), _WeatherToken(0), _YellowFlag(0), _GreenFlag(0), _NormalTire(0), _WetTire(0), _SoftTire(0) {}

// Getter Functions
int Stats::getTurns() const { return _Turns; }
int Stats::getFocusTokens() const { return _FocusTokens; }
int Stats::getUsedFocusTokens() const { return _UsedFocusTokens; }
int Stats::getLostGear() const { return _LostGear; }
int Stats::getLostBrake() const { return _LostBrake; }
int Stats::getLostCoast() const { return _LostCoast; }
int Stats::getWeatherToken() const { return _WeatherToken; }
int Stats::getYellowFlag() const { return _YellowFlag; }
int Stats::getGreenFlag() const { return _GreenFlag; }
int Stats::getNormalTire() const { return _NormalTire; }
int Stats::getWetTire() const { return _WetTire; }
int Stats::getSoftTire() const { return _SoftTire; }
std::vector<std::string> Stats::getDiceRolls() const { return _DiceRolls; }

// Setter Functions
void Stats::addTurn() { _Turns++; }
void Stats::addFocusToken() { _FocusTokens++; }
void Stats::useFocusToken() { if (_FocusTokens > 0) { _FocusTokens--; _UsedFocusTokens++; } }
void Stats::loseGear() { _LostGear++; }
void Stats::loseBrake() { _LostBrake++; }
void Stats::loseCoast() { _LostCoast++; }
void Stats::addWeatherToken() { _WeatherToken++; }
void Stats::addYellowFlag() { _YellowFlag++; }
void Stats::addGreenFlag() { _GreenFlag++; }
void Stats::addNormalTire() { _NormalTire++; }
void Stats::addWetTire() { _WetTire++; }
void Stats::addSoftTire() { _SoftTire++; }
void Stats::addDiceRoll(const std::string& roll) { _DiceRolls.push_back(roll); }
void Stats::resetDiceRolls() { _DiceRolls.clear(); }

void Stats::printStats() 
{
    std::cout << "|==============================|" << std::endl;
    std::cout << "Turns: " << _Turns
            << "\nFocus Tokens: " << _FocusTokens
            << "\nUsed focus toksen: " << _UsedFocusTokens
            << "\nLost gear dice: " << _LostGear
            << "\nLost brake dice: " << _LostBrake
            << "\nLost coast dice: " << _LostCoast
            << "\nWeather tokens: " << _WeatherToken
            << "\nYellow flag: " << _YellowFlag
            << "\nGreen flag: " << _GreenFlag << std::endl;
    std::cout << "|==============================|" << std::endl;
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
            _LostGear += 1;
        if (randomIndex == 1)
            _LostBrake += 1;
        if (randomIndex == 2)
            _LostCoast+= 1;
        if (randomIndex == 3)
            _WeatherToken += 1;
        if (randomIndex == 4)
            _YellowFlag += 1;
        if (randomIndex == 5)
            _GreenFlag += 1;
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

    _TotalTime += timeToAdd;

    if (_LapTime.empty()) _LapTime.push_back(timeToAdd);
    else _LapTime.back() += timeToAdd;
}

std::string Stats::getTotalTime() const
{
    int minutes = _TotalTime / 60;
    int seconds = _TotalTime % 60;
    return std::to_string(minutes) + ":" + (seconds < 10 ? "0" : "") + std::to_string(seconds);
}

std::vector<std::string> Stats::getLapTime() const
{
    std::vector<std::string> formattedLaps;
    for (int time : _LapTime)
    {
        int minutes = time / 60;
        int seconds = time % 60;
        formattedLaps.push_back(std::to_string(minutes) + ":" + (seconds < 10 ? "0" : "") + std::to_string(seconds));
    }
    return formattedLaps;
}

void Stats::resetStats()
{
    _Turns = 0;
    _FocusTokens = 0;
    _UsedFocusTokens = 0;
    _LostGear = _LostBrake = _LostCoast = 0;
    _WeatherToken = _YellowFlag = _GreenFlag = 0;
    _DiceRolls.clear();
}