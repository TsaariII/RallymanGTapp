
#pragma once
# include <string>
# include <vector>

class Track
{
private:
    std::string name;
    // std::vector<std::string> sections; // Example: {"yellow", "orange", "red", "yellow"}

public:
    Track(const std::string& name);

    // std::string getSection(int position);
    std::string getName();
};