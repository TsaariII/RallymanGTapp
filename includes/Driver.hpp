
#pragma once
# include <string>
# include <vector>

class Driver
{
    private:
        std::string name;
        std::string team;
        int position;
        std::string currentGear;
        int focusTokens;
        int usedFocusTokens;
        int lostGear;
        int lostBrake;
        int lostCoast;
        int weatherToken;
        int yellowFlag;
        int greenFlag;
        std::vector<std::string> diceRolls;
    public:
        Driver(const std::string &name, const std::string &team);
        void addDiceRoll(const std::string &result);
        void addFocusToken();
        void useFocusToken();
        void setPosition(int pos);
        void setCurrentGear(const std::string &gear);
        void addCrashTokens(const std::string &gear, const std::string &section);
        std::string getName() const;
        std::string getTeam() const;
        int getPosition() const;
        int getFocusTokens() const;
        int getUsedFocusTokens() const;
        std::string getLastGear() const;

        // For exporting stats
        std::vector<std::string> getDiceResults() const;
        int getMinusGearDice() const;
        int getMinusBrakeDice() const;
        int getMinusCoastDice() const;
        int getWeatherToken() const;
        int getYellowFlag() const;
        int getGreenFlag() const;

        void resetStats();
};