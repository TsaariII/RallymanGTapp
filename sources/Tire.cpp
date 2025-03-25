
#include "../includes/Tire.hpp"

Tire::Tire(TireType type, Weather weather) : _Type(type), _TurnsUsed(0), _Condition(ConditionStage::Green), _CurrentWeather(weather) {}

void Tire::useTurn()
{
    _TurnsUsed++;
    int green, yellow;
    switch (_Type)
    {
    case TireType::Normal:
        green = 10;
        yellow = green + 25;
        break;
    case TireType::Sprint:
        green = 10;
        yellow = green + 30;
        break;
    case TireType::Wet:
        green = 9;
        yellow = green + 15;
        break;
    }
    if (_TurnsUsed <= green)
        _Condition = ConditionStage::Green;
    if (_TurnsUsed <= yellow)
        _Condition = ConditionStage::Yellow;
    else 
        _Condition = ConditionStage::Red;
}
ConditionStage Tire::getCondition() const { return _Condition; }
int Tire::getMaxWarnings() const
{
    int base = 3;
    if (_Type == TireType::Wet && _CurrentWeather == Weather::Dry)
        base -= 1;
    else if ((_Type == TireType::Normal || _Type == TireType::Sprint) && _CurrentWeather == Weather::Wet)
        base -= 1;
    if (_Condition == ConditionStage::Yellow)
        base -= 1;
    else if (_Condition == ConditionStage::Red)
        base -= 2;
    return (std::max(base, 0));
}
int Tire::getAvailableBrakeDice() const
{
    if (_CurrentWeather == Weather::Wet)
    {
        if (_Type == TireType::Wet)
            return 2;
        else
            return 1;
    }
    return 3;
}
int Tire::getAvailableCoastDice() const
{
    if (_CurrentWeather == Weather::Dry && _Type == TireType::Wet)
        return 1;
    return 2;
}
void Tire::setWeather(Weather w) { _CurrentWeather = w; }
std::string Tire::getTypeAsString() const
{
    switch (_Type)
    {
        case TireType::Normal: return "Normal";
        case TireType::Sprint: return "Sprint";
        case TireType::Wet: return "Wet";
    }
    return "Unknown";
}