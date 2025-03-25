
#include "../includes/Game.hpp"
#include <set>
#include <thread>
#include <chrono> 

Game::Game(const std::string &trackName) : _Track(trackName) {
    _SetWeather();
}

void Game::_SetupGame() {
    std::vector<Team> _Teams = {
        Team("Evante", "Collins", "Cooper", TireType::Normal, Weather::Dry),
        // Team("Scorpion", "Rasch", "Hines"),
        // Team("Musubu", "Dai", "Tremblay"),
        // Team("Principe", "Venturella", "Saldutti"),
        // Team("Cohete", "Sköld", "Rudolf"),
        // Team("Kobra", "Karhu", "Toledano")
    };
    std::vector<Driver*> _Drivers;
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
    while (true)
    {
        raceRound(_Drivers, diceMap, _Track);
        std::cout << "End of race turn. Continue to next? (y/n): ";
        std::string cont;
        std::getline(std::cin, cont);
        if (cont == "n")
            break;
    }
}
void Game::start() {
    _SetWeather();
    _SetupGame();
    _DriverPositions();
    _PrintCountdown();
    _RaceLoop();
}