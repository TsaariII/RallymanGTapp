
#include "../includes/Game.hpp"
#include <set>
#include <thread>
#include <chrono> 

Game::Game(const std::string &trackName) : _Track(trackName) {
    _SetWeather();
}

void Game::_SetupGame() {
    _Teams = {
        Team("Evante", "Collins", "Cooper", TireType::Normal, Weather::Dry),
        // Team("Scorpion", "Rasch", "Hines"),
        // Team("Musubu", "Dai", "Tremblay"),
        // Team("Principe", "Venturella", "Saldutti"),
        // Team("Cohete", "Sköld", "Rudolf"),
        // Team("Kobra", "Karhu", "Toledano")
    };
    _Drivers.clear();
    for (auto& team : _Teams) {
        _Drivers.push_back(&team.getDriver1());
        _Drivers.push_back(&team.getDriver2());
    }
}
void Game::_SetWeather() {
    std::string input;
    std::cout << "Select weather Dry or Wet" << std::endl;
    std::getline(std::cin, input);
    if (input == "Dry")
        _Weather = Weather::Dry;
    else
        _Weather = Weather::Wet;
}
void Game::_SetTires() {
    std::cout << "\n=== Tire Selection ===\n";
    std::cout << "Available tire types:\n";
    std::cout << "1. Normal\n2. Sprint\n3. Wet\n";

    for (Team& team : _Teams) {
        for (Driver* driver : { &team.getDriver1(), &team.getDriver2() }) {
            int choice;
            while (true) {
                std::cout << "Select tire type for " << driver->getName() << " from team " << driver->getTeam() << ": ";
                std::cin >> choice;

                if (std::cin.fail() || choice < 1 || choice > 3) {
                    std::cin.clear();
                    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                    std::cout << "Invalid choice. Please enter 1, 2, or 3.\n";
                } else {
                    break;
                }
            }

            TireType selectedTire = TireType::Normal;
            if (choice == 2) selectedTire = TireType::Sprint;
            else if (choice == 3) selectedTire = TireType::Wet;

            driver->setTire(selectedTire, _Weather);  // Set tire with current weather
            // std::cout << "Set " << driver->getName() << "'s tire to " << driver->getTireTypeAsString() << "\n";
        }
    }

    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Clean leftover input
}

void Game::_DriverPositions() {
    std::set<int> assignedPositions;
    for (Driver* driver : _Drivers) {
        std::cout << "Setting position for " << driver->getName()
                  << " (gear: " << driver->getCurrentGear() << ")"
                  << " from team " << driver->getTeam() << "\n";
        setDriverStartingPosition(driver, _Track, assignedPositions);
    }
}
void Game::_PrintCountdown() {
    for (int i = 1; i <= 5; i++) {
        std::cout << "\r";
        for (int j = 0; j < i; j++) {
            std::cout << "🔴 ";
        }
        std::cout << std::flush;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    std::cout << "\nRace begins!!" << std::endl;
}
void Game::_RaceLoop()
{
    std::map<std::string, Dice> diceMap = {
        {"1", createDice("1")}, {"2", createDice("2")},
        {"3", createDice("3")}, {"4", createDice("4")},
        {"5", createDice("5")}, {"6", createDice("6")},
        {"C", createDice("C")}, {"B", createDice("B")}
    };
    std::cout << "blorp" << std::endl;
    while (true)
    {
        std::cout << "blorp1" << std::endl;
        raceRound(_Drivers, diceMap, _Track);
        std::cout << "End of race turn. Continue to next? (y/n): ";
        std::string cont;
        std::getline(std::cin, cont);
        if (cont == "n")
            break;
    }
}

std::vector<std::string> Game::parseInput(const std::string& input)
{
    std::vector<std::string> diceSequence;
    std::stringstream ss(input);
    std::string item;
    while (std::getline(ss, item, ','))
    {
        item.erase(0, item.find_first_not_of(" "));
        item.erase(item.find_last_not_of(" ") + 1);
        if (item == "C")
            diceSequence.emplace_back("C");
        else if (item == "B")
            diceSequence.emplace_back("B");
        else if (isdigit(item[0]) && stoi(item) >= 1 && stoi(item) <= 6)
            diceSequence.emplace_back(item);
        else
        {
            diceSequence.clear();
            return diceSequence;
        }
    }
    return diceSequence;
}

int Game::getValidPosition(Driver *driver, std::set<int>& assignedPositions)
{
    int pos;
    while (true)
    {
        std::cout << "Enter position for " << driver->getName()
        << " from team " << driver->getTeam() << " (1-12): ";
        std::cin >> pos;
        if (std::cin.fail() || pos < 1 || pos > 12 || assignedPositions.count(pos))
        {
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            std::cout << "Invalid or duplicate position! Try again.\n";
        }
        else
        {
            assignedPositions.insert(pos);
            return pos;
        }
    }
}

void Game::checkPositions(std::vector<Driver*> &drivers, Track &track) {
    std::sort(drivers.begin(), drivers.end(), [&](Driver* a, Driver* b) {
        if (a->getLap() != b->getLap()) 
            return a->getLap() > b->getLap();

        if (a->getTileIndex() != b->getTileIndex()) 
            return a->getTileIndex() > b->getTileIndex();

        if (a->getSquareIndex() != b->getSquareIndex()) 
            return a->getSquareIndex() > b->getSquareIndex();
        int tileId = a->getTileIndex();
        if (tileId < track.getTrackLength()) {
            const Tile& tile = track.getTile(tileId);
            int aInsidePriority = tile.getInsidePriority(a->getLaneIndex());
            int bInsidePriority = tile.getInsidePriority(b->getLaneIndex());

            if (aInsidePriority != bInsidePriority)
                return aInsidePriority < bInsidePriority;
        }
        return false;
    });
}

void Game::setDriverStartingPosition(Driver* driver, Track& track, std::set<int>& assignedPositions)
{
    driver->setPosition(getValidPosition(driver, assignedPositions));
    int tileIndex = getValidTileIndex(track);
    driver->setStartingTile(tileIndex);
    driver->setTileIndex(tileIndex);
    if (tileIndex != 0)
        driver->setLap(-1);
    int laneIndex = getValidLaneIndex(track, tileIndex);
    driver->setLaneIndex(laneIndex);
    int squareIndex = getValidSquareIndex(track, tileIndex, laneIndex);
    driver->setSquareIndex(squareIndex);
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}

void Game::raceRound(std::vector<Driver*> drivers, const std::map<std::string, Dice>& diceMap, Track &track)
{
    checkPositions(drivers, track);
    std::sort(drivers.begin(), drivers.end(), [](Driver* a, Driver* b) {
        return a->getPosition() < b->getPosition();
    });
    for (Driver* driver : drivers)
    {
        std::cout << "Now rolling for " << driver->getName()
        << " (Gear " << driver->getCurrentGear() << ")"
        << " from team " << driver->getTeam()
        << " (Position " << driver->getPosition() << ")" << std::endl;
        std ::cout << "\tSTATS\n";
        driver->getStats().printStats();
        while (true)
        {
            std::cout << "Enter dice for this driver: ";
            std::string input;
            if (!std::getline(std::cin, input))
            {
                std::cout << "\nEOF detected! Exiting turn safely...\n";
                return;
            }
            auto diceSequence = parseInput(input);
            if (diceSequence.empty()) {
                std::cout << "Invalid dice input. Please try again." << std::endl;
                continue;
            }
            std::cout << "Choose roll mode: (1) One by one, (2) All at once: ";
            int choice;
            std::cin >> choice;
            std::cin.ignore();
            if (choice == 1)
                rollOneByOne(diceSequence, diceMap, *driver, track);
            else if (choice == 2)
                rollAllAtOnce(diceSequence, diceMap, *driver, track);
            else
                std::cout << "Invalid roll mode. Skipping this driver." << std::endl;
            driver->getStats().addTurn();
            driver->getStats().addLapTime(driver->getCurrentGear());
            break;
        }
    }
}

void Game::start() {
    //_SetWeather();
    _SetupGame();
    _DriverPositions();
   _PrintCountdown();
    _RaceLoop();
}