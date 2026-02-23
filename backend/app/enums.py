from enum import Enum

class Tires(Enum):
    NORMAL = 'Normal'
    SPRINT = 'Sprint'
    WET = 'Wet'

class TireCondition(Enum):
    GREEN = 'Green'
    YELLOW = 'Yellow'
    RED = 'Red'

class Weather(Enum):
    DRY = 'Dry'
    WET = 'Wet'