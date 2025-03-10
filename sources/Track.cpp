
#include "../includes/Track.hpp"

Track::Track(const std::string &newName) :
    name(newName) {};

// std::string Track::getSection(int position) { return };
std::string Track::getName() { return name; };