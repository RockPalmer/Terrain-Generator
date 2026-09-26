from __future__ import annotations

class Interval:
	def __init__(self,min,max) -> None:
		self.min = min
		self.max = max
	def __add__(self,other) -> Interval:
		if isinstance(other,Interval):
			return Interval(
				self.min + other.min,
				self.max + other.max,
			)
		return Interval(
			self.min + other,
			self.max + other,
		)
	def __sub__(self,other) -> Interval:
		if isinstance(other,Interval):
			return Interval(
				self.min - other.max,
				self.max - other.min,
			)
		return Interval(
			self.min - other,
			self.max - other,
		)
	def __mul__(self,other) -> Interval:
		if isinstance(other,Interval):
			return Interval(
				self.min * other.min,
				self.max * other.max,
			)
		return Interval(
			self.min * other,
			self.max * other,
		)
	def __truediv__(self,other) -> Interval:
		if isinstance(other,Interval):
			return Interval(
				self.min / other.max,
				self.max / other.min,
			)
		return Interval(
			self.min / other,
			self.max / other,
		)
	def __rtruediv__(self,other) -> Interval:
		if isinstance(other,Interval):
			return NotImplemented
		return Interval(
			other / self.max,
			other / self.min,
		)
	def __pow__(self,other) -> Interval:
		if isinstance(other,Interval):
			values = {
				self.min ** other.min,
				self.min ** other.max,
				self.max ** other.min,
				self.max ** other.max,
			}
			return Interval(
				min(values),
				max(values),
			)
		values = {
			self.min ** other,
			self.max ** other,
		}
		return Interval(
			min(values),
			max(values),
		)
	def __rpow__(self,other) -> Interval:
		if isinstance(other,Interval):
			return NotImplemented
		values = {other ** self.min,other ** self.max}
		return Interval(
			min(values),
			max(values),
		)
	def __or__(self,other) -> Interval:
		return Interval(
			min(self.min,other.min),
			max(self.max,other.max),
		)
		if other < self.min:
			return Interval(
				other,
				self.max,
			)
		if other > self.min:
			return Interval(
				self.min,
				other,
			)
		return self
	def __ror__(self,other) -> Interval:
		if not isinstance(other,Interval):
			return self | other
		return NotImplemented
	def __eq__(self,other) -> bool:
		return self.min == other.min and self.max == other.max
	def __neg__(self) -> Interval:
		return Interval(
			-self.max,
			-self.min,
		)
	def __pos__(self) -> Interval:
		return self
	def __abs__(self) -> Interval:
		return Interval(
			0,
			abs(self.min,self.max)
		)