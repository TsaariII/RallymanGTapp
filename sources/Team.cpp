
#include "../includes/Driver.hpp"
#include "../includes/Team.hpp"
#include "../includes/Tile.hpp"
 
Team::Team(const std::string& name, const std::string& driver1Name, const std::string& driver2Name)
    : teamName(name),
      driver1(driver1Name, name),
      driver2(driver2Name, name) {}

std::string Team::getTeamName() const {
    return teamName;
}

Driver& Team::getDriver1() {
    return driver1;
}

Driver& Team::getDriver2() {
    return driver2;
}

// void Team::resetTeamStats() {
//     driver1.resetStats();
//     driver2.resetStats();
// }