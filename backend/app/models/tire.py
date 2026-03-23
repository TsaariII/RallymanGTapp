from __future__ import annotations
from dataclasses import dataclass
from backend.app.models.enums import Tires, TireCondition, Weather

@dataclass
class Tire:
	type: Tires
	weather: Weather
	turns: int = 0
	condition: TireCondition = TireCondition.GREEN

	WEAR_THRESHOLDS = {
        Tires.NORMAL: (10, 10 + 25),
        Tires.SPRINT: (10, 10 + 30),
        Tires.WET: (9, 9 + 15)
    }
	def use_turn(self) -> None:
		self.turns += 1
		green_limit, yellow_limit = self.WEAR_THRESHOLDS[self.type]
		if self.turns <= green_limit:
			self.condition = TireCondition.GREEN
		elif self.turns <= yellow_limit:
			self.condition = TireCondition.YELLOW
		else:
			self.condition = TireCondition.RED
	
	@property
	def max_warnings(self) -> int:
		"""
		Base 3 warnings, then:
		- mismatch tire/weather: -1
		- YELLOW: -1
        - RED: -2
		"""
		base = 3
		if self.type == Tires.WET and self.weather == Weather.DRY:
			base -= 1
		elif self.type in (Tires.NORMAL, Tires.SPRINT) and self.weather == Weather.WET:
			base -= 1
		if self.condition == TireCondition.YELLOW:
			base -= 1
		elif self.condition == TireCondition.RED:
			base -= 2
		return max(base, 0)

	@property	
	def available_break_dice(self) -> int:
		"""
		In wet: Wet tire = 2 brake dice, others = 1.
		In dry: always 3.
		"""
		if self.weather == Weather.WET:
			return 2 if self.type == Tires.WET else 1
		return 3
	
	@property
	def available_coast_dice(self) -> int:
		"""
		Wet tire in dry: 1 coast.
		Otherwise: 2.
		"""
		if self.weather == Weather.DRY and self.type == Tires.WET:
			return 1
		return 2
	
	def set_weather(self, weather: Weather) -> None:
		self.weather = weather

	@property
	def type_label(self) -> str:
		return self.type.value