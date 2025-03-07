#include <iostream>
#include <string>
#include <map>
#include <sstream>
#include <set>
#include "../includes/Dice.hpp"
#include "../includes/Team.hpp"
#include "../includes/Driver.hpp"

std::vector<std::string> parseInput(const std::string& input) {
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

void setPositions(std::vector<Driver*> drivers)
{
    std::set<int> assignedPositions;
    int pos;
    for (Driver* driver : drivers)
    {
        while (true)
        {
            std::cout << "Enter position for " << driver->getName()
                      << " from team " << driver->getTeam() << " (1-12): ";
            std::cin >> pos;
            // Check for valid input and uniqueness
            if (std::cin.fail() || pos < 1 || pos > 12 || assignedPositions.count(pos))
            {
                std::cin.clear(); // Clear the error state if input failed
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Discard invalid input
                std::cout << "Invalid or duplicate position. Please enter a unique number between 1 and 12." << std::endl;
            }
            else
            {
                assignedPositions.insert(pos);
                driver->setPosition(pos);
                break;
            }
        }
    }
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); 
}

void raceTurn(std::vector<Team>& teams, const std::map<std::string, Dice>& diceMap, std::string &trackSection)
{
    std::vector<Driver*> drivers;
    for (auto& team : teams) {
        drivers.push_back(&team.getDriver1());
        drivers.push_back(&team.getDriver2());
    }
    setPositions(drivers);
    std::sort(drivers.begin(), drivers.end(), [](Driver* a, Driver* b) {
        return a->getPosition() < b->getPosition();
    });
    std::cout << "Race begins!!" << std::endl;
    for (Driver* driver : drivers)
    {
        std::cout << "Now rolling for " << driver->getName()
                << " from team " << driver->getTeam()
                << " (Position " << driver->getPosition() << ")" << std::endl;
        while (true) // Loop until valid dice input is given
        {
            std::cout << "Enter dice for this driver: ";
            std::string input;
            std::getline(std::cin, input);
            auto diceSequence = parseInput(input);
            if (diceSequence.empty()) {
                std::cout << "Invalid dice input. Please try again." << std::endl;
                continue; // Ask again
            }
            std::cout << "Choose roll mode: (1) One by one, (2) All at once: ";
            int choice;
            std::cin >> choice;
            std::cin.ignore();
            if (choice == 1)
                rollOneByOne(diceSequence, diceMap, *driver, trackSection);
            else if (choice == 2)
                rollAllAtOnce(diceSequence, diceMap, *driver, trackSection);
            else
                std::cout << "Invalid roll mode. Skipping this driver." << std::endl;
            break; // Exit loop after successful roll
        }
    }
}

int main()
{
    std::vector<Team> teams = {
        Team("Evante", "Collins", "Cooper"),
        Team("Scorpion", "Rasch", "Hines"),
        Team("Musubu", "Dai", "Tremblay"),
        Team("Principe", "Venturella", "Saldutti"),
        Team("Cohete", "Sköld", "Rudolf"),
        Team("Kobra", "Karhu", "Toledano")
    };
    srand(static_cast<unsigned int>(time(nullptr)));
    std::map<std::string, Dice> diceMap = {
        {"1", createDice("1")}, {"2", createDice("2")},
        {"3", createDice("3")}, {"4", createDice("4")},
        {"5", createDice("5")}, {"6", createDice("6")},
        {"C", createDice("C")}, {"B", createDice("B")}
    };
    std::string trackSection = "yellow";
    while (true)
    {
        raceTurn(teams, diceMap, trackSection);
        std::cout << "End of race turn. Continue to next? (y/n): ";
        std::string cont;
        std::getline(std::cin, cont);
        if (cont == "n")
            break;
    }
    return 0;
}