from __future__ import annotations
from typing import (
	Any,
	Callable,
	Generic,
	TypeVar,
)

T = TypeVar("T")

def scrMap(fun: Callable, *screens: tuple[Screen,...]) -> Screen:
	size = screens[0].size
	screen = Screen(size)
	for i in range(size):
		for j in range(size):
			scns = [scn[i,j] for scn in screens]
			screen[i,j] = fun(*scns)
	return screen
def keyMap(fun: Callable, *screens: tuple[Screen,...]) -> Screen:
	size = screens[0].size
	screen = Screen(size)
	for i in range(size):
		for j in range(size):
			screen[i,j] = fun(i,j,*[s[i,j] for s in screens])
	return screen
def ifMap(s1,s2,s3) -> Screen:
	if isinstance(s1,Screen):
		if isinstance(s2,Screen):
			if isinstance(s3,Screen):
				return scrMap(
					lambda a,b,c : a if b else c,
					s1,s2,s3
				)
			return scrMap(
				lambda a,b : a if b else s3,
				s1,s2
			)
		if isinstance(s3,Screen):
			return scrMap(
				lambda a,c : a if s2 else c,
				s1,s3
			)
		return scrMap(
			lambda a : a if s2 else s3,
			s1
		)
	if isinstance(s2,Screen):
		if isinstance(s3,Screen):
			return scrMap(
				lambda b,c : s1 if b else c,
				s2,s3
			)
		return scrMap(
			lambda b : s1 if b else s3,
			s2
		)
	if isinstance(s3,Screen):
		return scrMap(
			lambda c : s1 if s2 else c,
			s3
		)
	return s1 if s2 else s3

class Screen(Generic[T]):
	def __init__(self,size: int,value = None) -> None:
		self.size = size
		self.values = [[value for _ in range(size)] for _ in range(size)]
	def checkSame(self,x1,x2,y1,y2):
		values = set()
		for i in range(x1,x2):
			for j in range(y1,y2):
				values.add(self.values[i][j])
		return len(values) == 1
	def __len__(self) -> int:
		return len(self.values)**2
	def __iter__(self) -> iter:
		for row in self.values:
			yield from row
	def enumerate(self) -> iter:
		for i in range(self.size):
			for j in range(self.size):
				yield ((i,j),self[i,j])
	def __getitem__(self,index: tuple):
		if not isinstance(index,tuple):
			raise KeyError(f"Screen[{index}]")
		match len(index):
			case 2:
				if isinstance(index[0],int) and isinstance(index[1],int): return self.values[index[0]][index[1]]
				if isinstance(index[0],tuple) and isinstance(index[1],tuple) and len(index[0]) == 2 and len(index[1]) == 2:
					x1,x2 = index[1]
					y1,y2 = index[2]
					screen = Screen(x2 - x1)
					for x in range(x1,x2):
						for y in range(y1,y2):
							screen[x - x1,y - y1] = self[x,y]
					return screen
				raise KeyError
			case 3:
				if isinstance(index[1],int) and isinstance(index[2],int):
					x1 = index[1] * index[0]
					x2 = (index[1] + 1) * index[0]
					y1 = index[1] * index[0]
					y2 = (index[1] + 1) * index[0]

					if not self.checkSame(x1,x2,y1,y2): raise KeyError
					return self.values[x1][y1]
				if isinstance(index[1],tuple) and isinstance(index[2],tuple) and len(index[1]) == 2 and len(index[2]) == 2:
					x1,x2 = index[1]
					y1,y2 = index[2]
					x1 *= index[0]
					x2 *= index[0]
					y1 *= index[0]
					y2 *= index[0]
					screen = Screen(x2 - x1)
					for x in range(x1,x2):
						for y in range(y1,y2):
							screen[x - x1,y - y1] = self[x,y]
					return screen
				raise KeyError
			case _: raise KeyError
	def __setitem__(self,index: tuple,value: Any) -> None:
		if not isinstance(index,tuple):
			raise KeyError(f"Screen[{index}]")
		match len(index):
			case 2:
				if isinstance(index[0],int) and isinstance(index[1],int):
					self.values[index[0]][index[1]] = value
				elif isinstance(index[0],tuple) and isinstance(index[1],tuple):
					for x in range(*index[0]):
						for y in range(*index[1]):
							self[x,y] = value
				else: raise KeyError
			case 3:
				if isinstance(index[1],int) and isinstance(index[2],int):
					x1 = index[1] * index[0]
					x2 = (index[1] + 1) * index[0]
					y1 = index[1] * index[0]
					y2 = (index[1] + 1) * index[0]

					for x in range(x1,x2):
						for y in range(y1,y2):
							self[x,y] = value
				elif isinstance(index[1],tuple) and isinstance(index[2],tuple) and len(index[1]) == 2 and len(index[2]) == 2:
					x1,x2 = index[1]
					y1,y2 = index[2]
					x1 *= index[0]
					x2 *= index[0]
					y1 *= index[0]
					y2 *= index[0]
					for x in range(x1,x2):
						for y in range(y1,y2):
							self[x,y] = value
				else: raise KeyError
			case _: raise KeyError
	def __and__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u and v if isinstance(u,bool) and isinstance(v,bool) else u & v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			if isinstance(other,bool):
				return scrMap(
					lambda u : u and other if isinstance(u,bool) else u & other,
					self,
				)
			return scrMap(
				lambda u : u & other,
				self,
			)
		return NotImplemented
	def __or__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u or v if isinstance(u,bool) and isinstance(v,bool) else u | v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			if isinstance(other,bool):
				return scrMap(
					lambda u : u or other if isinstance(u,bool) else u | other,
					self,
				)
			return scrMap(
				lambda u : u | other,
				self,
			)
		return NotImplemented
	def __xor__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u ^ v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u ^ other,
				self,
			)
		return NotImplemented
	def __add__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u + v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u + other,
				self,
			)
		return NotImplemented
	def __radd__(self,other) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u + v,
				other,
				self,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : other + u,
				self,
			)
		return NotImplemented
	def __sub__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u - v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u - other,
				self,
			)
		return NotImplemented
	def __rsub__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u - v,
				other,
				self,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : other - u,
				self,
			)
		return NotImplemented
	def __mul__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u * v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u * other,
				self,
			)
		return NotImplemented
	def __rmul__(self,other) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u * v,
				other,
				self,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : other * u,
				self,
			)
		return NotImplemented
	def __truediv__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u / v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u / other,
				self,
			)
		return NotImplemented
	def __rtruediv__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u / v,
				other,
				self,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : other / u,
				self,
			)
		return NotImplemented
	def __floordiv__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u // v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u // other,
				self,
			)
		return NotImplemented
	def __rfloordiv__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u // v,
				other,
				self,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : other // u,
				self,
			)
		return NotImplemented
	def __mod__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u % v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u % other,
				self,
			)
		return NotImplemented
	def __rmod__(self,other: Any) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u % v,
				other,
				self,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : other % u,
				self,
			)
		return NotImplemented
	def __neg__(self) -> Screen:
		return scrMap(
			lambda v : -v,
			self,
		)
	def __invert__(self) -> Screen:
		return scrMap(
			lambda v : not v if isinstance(v,bool) else ~v,
			self,
		)
	def __pos__(self) -> Screen:
		return scrMap(
			lambda v : +v,
			self,
		)
	def __abs__(self) -> Screen:
		return scrMap(
			lambda v : abs(v),
			self,
		)
	def __eq__(self,other) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u == v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u == other,
				self,
			)
		return NotImplemented
	def __ne__(self,other) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u != v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u != other,
				self,
			)
		return NotImplemented
	def __lt__(self,other) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u < v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u < other,
				self,
			)
		return NotImplemented
	def __gt__(self,other) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u > v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u > other,
				self,
			)
		return NotImplemented
	def __le__(self,other) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u <= v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u <= other,
				self,
			)
		return NotImplemented
	def __ge__(self,other) -> Screen:
		if isinstance(other,Screen) and self.size == other.size:
			return scrMap(
				lambda u,v : u >= v,
				self,
				other,
			)
		if not isinstance(other,Screen):
			return scrMap(
				lambda u : u >= other,
				self,
			)
		return NotImplemented