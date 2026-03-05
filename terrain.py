from __future__ import annotations
from random import randint
from typing import Any

class Terrain:
	def __init__(self,values) -> None:
		if isinstance(values,int):
			self.values = [[{} for i in range(values)] for j in range(values)]
		else:
			self.values = values
	def __str__(self) -> str:
		return '\n'.join(
			' '.join(
				str(self[i,j]) for j in range(len(self))
			) for i in range(len(self))
		)
	def __repr__(self) -> str:
		return str(self)
	def __getitem__(self,index : tuple | str) -> Any:
		if isinstance(index,tuple):
			match len(index):
				case 2:
					return self.values[index[0]][index[1]]
				case 3:
					return self.values[index[0]][index[1]][index[2]]
				case _:
					raise KeyError
		if isinstance(index,int):
			return self.values[index]
		if isinstance(index,str):
			return Screen([[self[i,j,index] for j in range(len(self.values[i]))] for i in range(len(self.values))])
	def __setitem__(self,index : tuple | str,other : Any) -> None:
		match len(index):
			case 2:
				self.values[index[0]][index[1]] = other
			case 3:
				self.values[index[0]][index[1]][index[2]] = other
			case _:
				raise KeyError
	def continents(self,count : int) -> Terrain:
		mapping = {
			(
				randint(0,len(self) - 1),
				randint(0,len(self) - 1)
			) : set() for i in range(count)
		}
		for i in range(len(self)):
			for j in range(len(self)):
				min_length = min((m - i)**2 + (n - j)**2 for m,n in mapping.keys())
				closest_indices = [m,n for m,n in mapping.keys() if (m - i)**2 + (n - j)**2 == min_length]
				mapping[closest_indices[0]].add((i,j))