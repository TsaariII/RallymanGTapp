
#pragma once
#include <string>

enum class TireType { Normal, Sprint, Wet };
enum class ConditionStage { Green, Yellow, Red };
enum class Weather { Dry, Wet };

class Tire {
private:
    TireType _Type;
    int _TurnsUsed;
    ConditionStage _Condition;
    Weather _CurrentWeather;

public:
    Tire(TireType type, Weather weather);

    void useTurn();
    ConditionStage getCondition() const;
    int getMaxWarnings() const;
    int getAvailableBrakeDice() const;
    int getAvailableCoastDice() const;
    void setWeather(Weather w);
    std::string getTypeAsString() const;
};