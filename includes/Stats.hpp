
#pragma once

#include <vector>
#include <string>

class Stats
{
    private:
        int _Turns;
        int _FocusTokens;
        int _UsedFocusTokens;
        int _LostGear;
        int _LostBrake;
        int _LostCoast;
        int _WeatherToken;
        int _YellowFlag;
        int _GreenFlag;
        int _NormalTire;
        int _WetTire;
        int _SoftTire;
        int _TotalTime;
        std::vector<int> _LapTime;
        std::vector<std::string> _DiceRolls;

    public:
        Stats();

        int getTurns() const;
        int getFocusTokens() const;
        int getUsedFocusTokens() const;
        int getLostGear() const;
        int getLostBrake() const;
        int getLostCoast() const;
        int getWeatherToken() const;
        int getYellowFlag() const;
        int getGreenFlag() const;
        int getNormalTire() const;
        int getWetTire() const;
        int getSoftTire() const;
        std::vector<std::string> getDiceRolls() const;
        std::string getTotalTime() const;
        std::vector<std::string> getLapTime() const;
        void printStats();

        void addCrashTokens(const std::string &gear, const std::string &section);
        void addTurn();
        void addFocusToken();
        void useFocusToken();
        void loseGear();
        void loseBrake();
        void loseCoast();
        void addWeatherToken();
        void addYellowFlag();
        void addGreenFlag();
        void addNormalTire(); 
        void addWetTire();
        void addSoftTire(); 
        void addDiceRoll(const std::string& roll);
        void addLapTime(const std::string &gear);

        void resetDiceRolls();
        void resetStats();
};
