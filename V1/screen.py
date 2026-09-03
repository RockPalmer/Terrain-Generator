from __future__ import annotations
from typing import Any
from random import randint
from glb import *
from math import ceil
import numpy as np

def select_rand(values : list) -> Any:
	return values[randint(0,len(values) - 1)]

class Screen:
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
	def __len__(self) -> int:
		return len(self.values)
	def clone(self) -> Screen:
		if len(self) == 0 or len(self[0]) == 0:
			return Screen(self.values)
		if not isinstance(self[0,0],dict):
			return Screen([[self[i,j] for j in len(self)] for i in len(self)])
		return Screen([[{k : self[i,j,k] for k in self[i,j]} for j in range(len(self))] for i in range(len(self))])
	def as_array(self):
		return np.array(self.values)
	def continents(self,count : int) -> Terrain:
		def get_continent_name(index : int) -> str:
			if index <= 10:
				return str(index - 1)
			if index <= 36:
				return chr(index + 54)
			if index <= 62:
				return chr(index + 60)
			raise TypeError
		
		indices = {
			(
				randint(0,len(self) - 1),
				randint(0,len(self) - 1)
			) : get_continent_name(i) for i in range(count)
		}
		mapping = {k : set() for k in indices.keys()}
		for i in range(len(self)):
			for j in range(len(self)):
				min_length = min((m - i)**2 + (n - j)**2 for m,n in indices.values())
				closest_indices = [m,n for m,n in indices.keys() if (m - i)**2 + (n - j)**2 == min_length]
				mapping[closest_indices[0]].add((i,j))
		for k,v in mapping.items():
			for m,n in 
		