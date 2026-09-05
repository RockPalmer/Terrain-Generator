from __future__ import annotations
from typing import (
	Any,
	Callable,
)

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
			screen[i,j] = fun(i,j,*screens)
	return screen

class Screen:
	def __init__(self,size:int) -> None:
		self.size = size
		self.values = [[None for _ in range(size)] for _ in range(size)]
	def checkSame(self,x1,x2,y1,y2):
		values = set()
		for i in range(x1,x2):
			for j in range(y1,y2):
				values.add(self.values[i][j])
		return len(values) == 1
	def __len__(self) -> int:
		return self.values
	def __getitem__(self,index:tuple):
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
	def __setitem__(self,index:tuple,value:Any) -> None:
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
	def aggregate(self,fun: Callable) -> Any:
		return fun([item for sublist in self.values for item in sublist])