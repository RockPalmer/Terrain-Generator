from __future__ import annotations
from typing import Any
import numpy as np
import random

Point = tuple[int,int]
Color = tuple[int,int,int]
Real = int | float

COLORS = {
	'white' : (255,255,255),
	'black' : (0,0,0),
	'green' : (77,251,43),
	'blue' : (0,0,255),
}
def rgb(*args):
	global COLORS

	if len(args) == 1:
		return COLORS[args[0].lower()]
	return list(args)
def get_dist(x1 : int,y1 : int,x2 : int,y2 : int) -> float:
	return ((x1 - x2)**2 + (y1 - y2)**2)**0.5
def get_closest_point(x : int,y : int,points : set[Point]):
	dists = [get_dist(x,y,w,z) for w,z in points]
	min_dist = min(dists)
	return [
		point for point,dist in zip(points,dists) if dist == min_dist
	][0]

class Terrain:
	def __init__(self,seed,values) -> None:
		if isinstance(seed,int):
			self.generator = random.Random(seed)
		else:
			self.generator = seed
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
	def __len__(self) -> int:
		return len(self.values)
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
			return Terrain(
				self.generator,
				[[self[i,j,index] for j in range(len(self.values[i]))] for i in range(len(self.values))]
			)
	def __setitem__(self,index : tuple | str,other : Any) -> None:
		if isinstance(index,tuple):
			match len(index):
				case 2:
					self.values[index[0]][index[1]] = other
				case 3:
					self.values[index[0]][index[1]][index[2]] = other
				case _:
					raise KeyError
		if isinstance(index,str):
			for i in range(len(other)):
				for j in range(len(other[i])):
					self.values[i][j][index] = other[i,j,index]
		raise KeyError
	def __delitem__(self,index : str) -> None:
		for i in range(len(self)):
			for j in range(len(self)):
				del self.values[i][j][index]
	def keys(self) -> set[Point]:
		return {(i,j) for i in range(len(self)) for j in range(len(self))}
	def as_array(self):
		return np.array(self.values)
	def randint(self,bottom : int,top : int) -> int:
		return self.generator.randint(bottom,top)
	def randcolor(self) -> Color:
		return (
			self.randint(0,255),
			self.randint(0,255),
			self.randint(0,255),
		)
	def randcoord(self) -> Point:
		return (
			self.randint(0,len(self) - 1),
			self.randint(0,len(self) - 1),
		)
	def continents(self,count : int,iterations : int) -> Terrain:
		colors = set()
		coords = set()
		while len(colors) < count:
			c = self.randcolor()
			if c == (0,0,0):
				continue
			colors.add(c)
		while len(coords) < count:
			coords.add(self.randcoord())
		mappings = {
			coord : color for coord,color in zip(coords,colors)
		}
		vals = [
			[
				self[i,j] for i in range(len(self))
			] for j in range(len(self))
		]
		for p in range(iterations):
			print('Iteration ' + str(p))
			points = {}
			for i in range(len(self)):
				percent = str(i/len(self) * 100)[:20]
				print('\r' + percent + ' '*(20 - len(percent)) + '%',end = '')
				for j in range(len(self)):
					vals[i][j]['continent'] = mappings[
						get_closest_point(i,j,mappings.keys())
					]
					if vals[i][j]['continent'] not in points:
						points[vals[i][j]['continent']] = set()
					points[vals[i][j]['continent']].add((i,j))
			print('')
			mappings = {
				(
					round(sum(coord[0] for coord in coords)/len(coords)),
					round(sum(coord[1] for coord in coords)/len(coords)),
				) : color for color,coords in points.items()
			}
		return Terrain(self.generator,vals)
	def lattitudes(
		self,
		maximum : Real,
		minimum : Real,
		color : Callable[[Real,Real,Real],Color],
		poles : tuple[tuple[bool,bool],tuple[bool,bool]],
		smoothing_factor : int
	) -> Terrain:
		(nw,ne) = poles[0]
		(sw,se) = poles[1]
		for i in range(len(self)):
			for j in range(len(self)):
				self[i,j,lattitude] = minimum
		sources = set()
		if nw:
			self[0,0,'lattitude'] = maximum
			sources.add((0,0))
		if ne:
			self[0,len(self) - 1,'lattitude'] = maximum
			sources.add((0,len(self) - 1))
		if sw:
			self[len(self) - 1,0,'lattitude'] = maximum
			sources.add((len(self) - 1,0))
		if se:
			self[len(self) - 1,len(self) - 1,'lattitude'] = maximum
			sources.add((len(self) - 1,len(self) - 1))
		vals = [self[i,j] for i in range(len(self))] for j in range(len(self))]
		for i in range(len(dists)):
			for j in range(len(dists)):
				for source in sources:
					vals[i][j][source] = get_dist(i,j,source[0],source[1]) - minimum
				x = list(vals[i][j].values())
				vals[i][j] = sum(x)/len(x)
		for i in range(len(self)):
			for j in range(len(self)):
				vals[i][j][]