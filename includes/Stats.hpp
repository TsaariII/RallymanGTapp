
#pragma once

#include <vector>
#include <string>

class Stats
{
    private:
        int turns;
        int focusTokens;
        int usedFocusTokens;
        int lostGear;
        int lostBrake;
        int lostCoast;
        int weatherToken;
        int yellowFlag;
        int greenFlag;
        int totalTime;
        std::vector<int> lapTime;
        std::vector<std::string> diceRolls;

    public:
        Stats();  // Constructor

        // Getter functions
        int getTurns() const;
        int getFocusTokens() const;
        int getUsedFocusTokens() const;
        int getLostGear() const;
        int getLostBrake() const;
        int getLostCoast() const;
        int getWeatherToken() const;
        int getYellowFlag() const;
        int getGreenFlag() const;
        std::vector<std::string> getDiceRolls() const;
        std::string getTotalTime() const;
        std::vector<std::string> getLapTime() const;
        void printStats();

        // Setter functions
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
        void addDiceRoll(const std::string& roll);
        void addLapTime(const std::string &gear);

        void resetDiceRolls();
        void resetStats();
};
