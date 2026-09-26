from __future__ import annotations

class Interval:
	def __init__(self,min,max) -> None:
		self.min = min
		self.max = max
	def __add__(self,other) -> Interval:
		if isinstance(other,Interval):
			return (self + other.min) | (self + other.max)
		return Interval(
			self.min + other,
			self.max + other,
		)
	def __radd__(self,other) -> Interval:
		return self + other
	def __sub__(self,other) -> Interval:
		return self + -other
	def __rsub__(self,other) -> Interval:
		return -self + other
	def __mul__(self,other) -> Interval:
		if isinstance(other,Interval):
			return (self * other.min) | (self * other.max)
		if other < 0:
			return Interval(
				self.max,
				self.min,
			) * -other
		return Interval(
			self.min * other,
			self.max * other,
		)
	def __rmul__(self,other) -> Interval:
		return self * other
	def __truediv__(self,other) -> Interval:
		return self * (1/other)
	def __rtruediv__(self,other) -> Interval:
		if isinstance(other,Interval):
			return NotImplemented
		if other < 0:
			return -other / Interval(
				self.max,
				self.min,
			)
		return Interval(
			other / self.max,
			other / self.min,
		)
	def __pow__(self,other) -> Interval:
		if isinstance(other,Interval):
			return (self ** other.min) | (self ** other.max)
		if other % 2 == 0:
			if self.max < 0 and self.min < 0:
				return Interval(
					self.max,
					self.min,
				) ** other
			if self.max >= 0 and self.min < 0:
				return Interval(
					0,
					max(self.max,abs(self.min))
				) ** other
		return Interval(
			self.min ** other,
			self.max ** other,
		)
	def __or__(self,other) -> Interval:
		if isinstance(other,Interval):
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
			max(abs(self.min),abs(self.max))
		)
	def __repr__(self) -> str:
		return f"Interval({self.min},{self.max})"
	def __str__(self) -> str:
		return repr(self)