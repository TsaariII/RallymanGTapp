import random
from typing import List
from dataclasses import dataclass, field

@dataclass
class Stats:
    def __init__(self) -> None:
        self.turns = 0
        self.focus_tokens = 0
        self.used_focus_tokens = 0
        self.lost_gear = 0
        self.lost_brake = 0
        self.lost_coast = 0
        self.weather_token = 0
        self.yellow_flag = 0
        self.green_flag = 0
        self.normal_tire = 0
        self.wet_tire = 0
        self.soft_tire = 0
        self.total_time = 0
        self.lap_time: list[int] = []
        self.dice_rolls: list[str] = []

    @property
    def total_time_str(self) -> str:
        min = self.total_time // 60
        sec = self.total_time % 60
        return f"{min}:{sec:02d}"

    @property
    def lap_time_str(self) -> List[str]:
        result = []
        for t in self.lap_time:
            min = self.total_time // 60
            sec = self.total_time % 60
            result.append(f"{min}:{sec:02d}")
        return  result

    def use_focus_token(self) -> None:
        if self.focus_tokens > 0:
            self.focus_tokens -= 1
            self.focus_tokens += 1

    def add_crash_tokens(self, gear: str, section: str) -> None:
        crash_table = {
        ('3', 'R'): 1,
        ('4', 'O'): 1,
        ('4', 'R'): 2,
        ('5', 'Y'): 1,
        ('5', 'O'): 2,
        ('5', 'R'): 3,
        ('6', 'Y'): 2,
        ('6', 'O'): 3,
        ('6', 'R'): 4,
    }
        crash_tokens = crash_table.get((gear, section), 0)
        token_pool = [
            '⬛️',  # -1 gear dice
            '🟥',  # -1 brake dice
            '⬜️',  # -1 coast dice
            '⛅️',  # weather token
            '🟨',  # yellow flag
            '🟩'  # green flag   
        ]
        token_effects = {
            '⬛️': 'lost_gear',
            '🟥': 'lost_brake',
            '⬜️': 'lost_coast',
            '⛅️': 'weather_token',
            '🟨': 'yellow_flag',
            '🟩': 'green_flag',
        }
        for c in range(1, crash_tokens + 1):
            token = random.choice(token_pool)
            attr = token_effects[token]
            setattr(self, attr, getattr(self, attr) + 1)
            print(f"Token number {c} {token}")
        
    def add_lap_time(self, gear: str) -> None:
        time_by_gear = {
            '00': 120,
            '0': 60,
            '1': 50,
            '2': 40,
            '3': 30,
            '4': 20,
            '5': 15,
            '6': 10,
        }
        time_to_add = time_by_gear.get(gear, 0)
        self.total_time += time_to_add
        if not self.lap_time:
            self.lap_time.append(time_to_add)
        else:
            self.lap_time[-1] += time_to_add

    def print_stats(self) -> None:
        print("|==============================|")
        print(f"\tLap time: {self.lap_time_str}")
        print(f"\tTotal time: {self.total_time_str}")
        print(f"\tTurns: {self.turns}")
        print(f"\tFocus Tokens: {self.focus_tokens}")
        print(f"\tUsed focus tokens: {self.used_focus_tokens}")
        print(f"\tLost gear dice: {self.lost_gear}")
        print(f"\tLost brake dice: {self.lost_brake}")
        print(f"\tLost coast dice: {self.lost_coast}")
        print(f"\tWeather tokens: {self.weather_token}")
        print(f"\tYellow flag: {self.yellow_flag}")
        print(f"\tGreen flag: {self.green_flag}")
        print("|==============================|")

    def reset_stats(self) -> None:
        self.turns = 0
        self.focus_tokens = 0
        self.used_focus_tokens = 0
        self.lost_gear = 0
        self.lost_brake = 0
        self.lost_coast = 0
        self.weather_token = 0
        self.yellow_flag = 0
        self.green_flag = 0
        self.dice_rolls.clear()
        self.total_time = 0
        self.lap_time.clear()