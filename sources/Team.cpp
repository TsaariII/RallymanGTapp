
#include "../includes/Driver.hpp"
#include "../includes/Team.hpp"
#include "../includes/Tile.hpp"
 
Team::Team(const std::string& name, const std::string& driver1Name, const std::string& driver2Name, TireType tire, Weather weather)
    : _Name(name),
      _Driver1(driver1Name, name, tire, weather),
      _Driver2(driver2Name, name, tire, weather) {}

std::string Team::getTeamName() const {
    return _Name;
}

Driver& Team::getDriver1() {
    return _Driver1;
}

Driver& Team::getDriver2() {
    return _Driver2;
}

// void Team::resetTeamStats() {
//     _Driver1.resetStats();
//     _Driver2.resetStats();
// }