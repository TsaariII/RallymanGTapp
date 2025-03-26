#include <iostream>
#include <string>
#include <map>
#include <sstream>
#include <set>
#include <thread>
#include <chrono> 
#include "../includes/Dice.hpp"
#include "../includes/Team.hpp"
#include "../includes/Driver.hpp"
#include "../includes/Track.hpp"
#include "../includes/Game.hpp"

// std::vector<std::string> parseInput(const std::string& input)
// {
//     std::vector<std::string> diceSequence;
//     std::stringstream ss(input);
//     std::string item;
//     while (std::getline(ss, item, ','))
//     {
//         item.erase(0, item.find_first_not_of(" "));
//         item.erase(item.find_last_not_of(" ") + 1);
//         if (item == "C")
//             diceSequence.emplace_back("C");
//         else if (item == "B")
//             diceSequence.emplace_back("B");
//         else if (isdigit(item[0]) && stoi(item) >= 1 && stoi(item) <= 6)
//             diceSequence.emplace_back(item);
//         else
//         {
//             diceSequence.clear();
//             return diceSequence;
//         }
//     }
//     return diceSequence;
// }

// int getValidPosition(Driver *driver, std::set<int>& assignedPositions)
// {
//     int pos;
//     while (true)
//     {
//         std::cout << "Enter position for " << driver->getName()
//         << " from team " << driver->getTeam() << " (1-12): ";
//         std::cin >> pos;
//         if (std::cin.fail() || pos < 1 || pos > 12 || assignedPositions.count(pos))
//         {
//             std::cin.clear();
//             std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
//             std::cout << "Invalid or duplicate position! Try again.\n";
//         }
//         else
//         {
//             assignedPositions.insert(pos);
//             return pos;
//         }
//     }
// }

// void checkPositions(std::vector<Driver*> &drivers, Track &track) {
//     std::sort(drivers.begin(), drivers.end(), [&](Driver* a, Driver* b) {
//         if (a->getLap() != b->getLap()) 
//             return a->getLap() > b->getLap();

//         if (a->getTileIndex() != b->getTileIndex()) 
//             return a->getTileIndex() > b->getTileIndex();

//         if (a->getSquareIndex() != b->getSquareIndex()) 
//             return a->getSquareIndex() > b->getSquareIndex();
//         int tileId = a->getTileIndex();
//         if (tileId < track.getTrackLength()) {
//             const Tile& tile = track.getTile(tileId);
//             int aInsidePriority = tile.getInsidePriority(a->getLaneIndex());
//             int bInsidePriority = tile.getInsidePriority(b->getLaneIndex());

//             if (aInsidePriority != bInsidePriority)
//                 return aInsidePriority < bInsidePriority;
//         }
//         return false;
//     });
// }

// void setDriverStartingPosition(Driver* driver, Track& track, std::set<int>& assignedPositions)
// {
//     driver->setPosition(getValidPosition(driver, assignedPositions));
//     int tileIndex = getValidTileIndex(track);
//     driver->setStartingTile(tileIndex);
//     driver->setTileIndex(tileIndex);
//     if (tileIndex != 0)
//         driver->setLap(-1);
//     int laneIndex = getValidLaneIndex(track, tileIndex);
//     driver->setLaneIndex(laneIndex);
//     int squareIndex = getValidSquareIndex(track, tileIndex, laneIndex);
//     driver->setSquareIndex(squareIndex);
//     std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
// }

// void raceRound(std::vector<Driver*> drivers, const std::map<std::string, Dice>& diceMap, Track &track)
// {
//     checkPositions(drivers, track);
//     std::sort(drivers.begin(), drivers.end(), [](Driver* a, Driver* b) {
//         return a->getPosition() < b->getPosition();
//     });
//     for (Driver* driver : drivers)
//     {
//         std::cout << "Now rolling for " << driver->getName()
//         << " (Gear " << driver->getCurrentGear() << ")"
//         << " from team " << driver->getTeam()
//         << " (Position " << driver->getPosition() << ")" << std::endl;
//         std ::cout << "\tSTATS\n";
//         driver->getStats().printStats();
//         while (true)
//         {
//             std::cout << "Enter dice for this driver: ";
//             std::string input;
//             if (!std::getline(std::cin, input))
//             {
//                 std::cout << "\nEOF detected! Exiting turn safely...\n";
//                 return;
//             }
//             auto diceSequence = parseInput(input);
//             if (diceSequence.empty()) {
//                 std::cout << "Invalid dice input. Please try again." << std::endl;
//                 continue;
//             }
//             std::cout << "Choose roll mode: (1) One by one, (2) All at once: ";
//             int choice;
//             std::cin >> choice;
//             std::cin.ignore();
//             if (choice == 1)
//                 rollOneByOne(diceSequence, diceMap, *driver, track);
//             else if (choice == 2)
//                 rollAllAtOnce(diceSequence, diceMap, *driver, track);
//             else
//                 std::cout << "Invalid roll mode. Skipping this driver." << std::endl;
//             driver->getStats().addTurn();
//             driver->getStats().addLapTime(driver->getCurrentGear());
//             break;
//         }
//     }
// }

int main()
{
    std::string trackName;
    std::cout << "Enter track name: ";
    std::getline(std::cin, trackName);
    Game game(trackName);
    std::cout << "hello" << std::endl;
    game.start();
    std::cout  << "bye" << std::endl;
    return 0;
}