from __future__ import annotations
from typing import List
from enums import Tires, Weather
from driver import Driver

class Team:
    def __init__(
        self,
        name: str,
        driver_1_name: str,
        driver_2_name: str,
        tires: Tires,
        weather: Weather
    ) -> None:
        self.name = name
        self.drivers: List[Driver] = [
            Driver(driver_1_name, name, tires, weather),
            Driver(driver_2_name, name, tires, weather)
        ]
    @property
    def driver1(self) -> Driver:
        return self.drivers[0]
    @property
    def driver2(self) -> Driver:
        return self.drivers[1]
        