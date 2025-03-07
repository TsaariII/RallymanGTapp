
#pragma once
# include "../includes/Driver.hpp"
# include <string>

class Team {
private:
    std::string teamName;
    Driver driver1; // Primary (P)
    Driver driver2; // Secondary (S)

public:
    Team(const std::string& name, const std::string& driver1Name, const std::string& driver2Name);

    std::string getTeamName() const;
    Driver& getDriver1();
    Driver& getDriver2();
    void resetTeamStats();
};