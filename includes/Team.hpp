
#pragma once
# include "../includes/Driver.hpp"
# include <string>

class Team {
private:
    std::string _Name;
    Driver _Driver1; // Primary (P)
    Driver _Driver2; // Secondary (S)

public:
    Team(const std::string& name, const std::string& driver1Name, const std::string& driver2Name, TireType tire, Weather weather);

    std::string getTeamName() const;
    Driver& getDriver1();
    Driver& getDriver2();
    // void resetTeamStats();
};