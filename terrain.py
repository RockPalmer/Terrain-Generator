from __future__ import annotations
from typing import (
	Any,
	Iterable,
	Callable
)
import numpy as np
import random

Real = int | float

def get_dist(x1 : int,y1 : int,x2 : int,y2 : int) -> float:
	return ((x1 - x2)**2 + (y1 - y2)**2)**0.5
def get_closest_point(x : int,y : int,points : set[Point]):
	dists = [get_dist(x,y,w,z) for w,z in points]
	min_dist = min(dists)
	return [
		point for point,dist in zip(points,dists) if dist == min_dist
	][0]
def clone(value : Any) -> Any:
	if isinstance(value,list):
		return [clone(v) for v in value]
	if isinstance(value,tuple):
		return tuple([clone(v) for v in value])
	if isinstance(value,set):
		return {clone(v) for v in value}
	if isinstance(value,frozenset):
		return frozenset([clone(v) for v in value])
	if isinstance(value,dict):
		return {clone(k) : clone(v) for k,v in value.items()}
	if hasattr(value,'__clone__'):
		return value.__clone__()
	return value

class Color:
	COLORS = {
		'white' : (255,255,255),
		'black' : (0,0,0),
		'green' : (77,251,43),
		'blue' : (0,0,255),
	}
	def __init__(self,*args) -> None:
		match len(args):
			case 1:
				self.red,self.green,self.blue = Color.COLORS[args[0]]
			case 3:
				self.red = args[0]
				self.green = args[1]
				self.blue = args[2]
			case _:
				raise TypeError
	def __str__(self) -> str:
		r = hex(self.red)[2:]
		if len(r) == 1:
			r = '0' + r
		g = hex(self.green)[2:]
		if len(r) == 1:
			g = '0' + g
		b = hex(self.blue)[2:]
		if len(r) == 1:
			b = '0' + b
		return '#' + r + g + b
	def __repr__(self) -> str:
		return str(self)
	def __getitem__(self,index : int) -> int:
		return self.astuple()[index]
	def __iter__(self) -> iter:
		return iter(self.astuple())
	def __len__(self) -> int:
		return len(self.astuple())
	def __eq__(self,other : Any) -> bool:
		if isinstance(other,Color):
			return self.astuple() == other.astuple()
		if isinstance(other,tuple | list):
			return self.astuple() == tuple(other)
		if isinstance(other,str):
			return self.name() == other
		return False
	def __ne__(self,other : Any) -> bool:
		return not (self == other)
	def __hash__(self) -> int:
		return hash(self.astuple())
	def __neg__(self,other) -> Color:
		return Color(
			-self.red,
			-self.green,
			-self.blue
		)
	def __pos__(self,other) -> Color:
		return Color(
			+self.red,
			+self.green,
			+self.blue
		)
	def __invert__(self,other) -> Color:
		return Color(
			~self.red,
			~self.green,
			~self.blue
		)
	def __abs__(self,other) -> Color:
		return Color(
			abs(self.red),
			abs(self.green),
			abs(self.blue)
		)
	def __mul__(self,other) -> Color:
		if isinstance(other,Color):
			return Color(
				self.red * other.red,
				self.green * other.green,
				self.blue * other.blue
			)
		return Color(
			self.red * other,
			self.green * other,
			self.blue * other
		)
	def __truediv__(self,other) -> Color:
		if isinstance(other,Color):
			return Color(
				self.red / other.red,
				self.green / other.green,
				self.blue / other.blue
			)
		return Color(
			self.red / other,
			self.green / other,
			self.blue / other
		)
	def __mod__(self,other) -> Color:
		if isinstance(other,Color):
			return Color(
				self.red % other.red,
				self.green % other.green,
				self.blue % other.blue
			)
		return Color(
			self.red % other,
			self.green % other,
			self.blue % other
		)
	def __floordiv__(self,other) -> Color:
		if isinstance(other,Color):
			return Color(
				self.red // other.red,
				self.green // other.green,
				self.blue // other.blue
			)
		return Color(
			self.red // other,
			self.green // other,
			self.blue // other
		)
	def __add__(self,other) -> Color:
		if isinstance(other,Color):
			return Color(
				self.red + other.red,
				self.green + other.green,
				self.blue + other.blue
			)
		return Color(
			self.red + other,
			self.green + other,
			self.blue + other
		)
	def __sub__(self,other) -> Color:
		if isinstance(other,Color):
			return Color(
				self.red - other.red,
				self.green - other.green,
				self.blue - other.blue
			)
		return Color(
			self.red - other,
			self.green - other,
			self.blue - other
		)
	def __matmul__(self,other) -> Color:
		if isinstance(other,Color):
			return Color(
				self.red @ other.red,
				self.green @ other.green,
				self.blue @ other.blue
			)
		return Color(
			self.red @ other,
			self.green @ other,
			self.blue @ other
		)
	def __and__(self,other) -> Color:
		if isinstance(other,Color):
			return Color(
				self.red & other.red,
				self.green & other.green,
				self.blue & other.blue
			)
		return Color(
			self.red & other,
			self.green & other,
			self.blue & other
		)
	def __or__(self,other) -> Color:
		if isinstance(other,Color):
			return Color(
				self.red | other.red,
				self.green | other.green,
				self.blue | other.blue
			)
		return Color(
			self.red | other,
			self.green | other,
			self.blue | other
		)
	def __xor__(self,other) -> Color:
		if isinstance(other,Color):
			return Color(
				self.red ^ other.red,
				self.green ^ other.green,
				self.blue ^ other.blue
			)
		return Color(
			self.red ^ other,
			self.green ^ other,
			self.blue ^ other
		)
	def name(self) -> str | None:
		x = [
			k for k,v in Color.COLORS.items() if v == self.astuple()
		]
		if len(x) == 0:
			return None
		return x[0]
	def astuple(self) -> tuple[int,int,int]:
		return (self.red,self.green,self.blue)
class Point:
	def __init__(self,x : int,y : int) -> None:
		self.x = x
		self.y = y
	def __str__(self) -> str:
		return str(self.astuple())
	def __repr__(self) -> str:
		return str(self)
	def __getitem__(self,index : int) -> int:
		return self.astuple()[index]
	def __iter__(self) -> iter:
		return iter(self.astuple())
	def __len__(self) -> int:
		return len(self.astuple())
	def __eq__(self,other : Any) -> bool:
		if isinstance(other,Point):
			return self.astuple() == other.astuple()
		if isinstance(other,tuple | list):
			return self.astuple() == tuple(other)
		return False
	def __ne__(self,other : Any) -> bool:
		return not (self == other)
	def __hash__(self) -> int:
		return hash(self.astuple())
	def astuple(self) -> tuple[int,int]:
		return (self.x,self.y)
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
	def __iter__(self) -> iter:
		for i in range(len(self)):
			for j in range(len(self)):
				yield self[i,j]
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
		elif isinstance(index,str):
			for i in range(len(other)):
				for j in range(len(other[i])):
					self.values[i][j][index] = other[i,j]
		else:
				raise KeyError(type(index).__name__ + ' : ' + str(index))
	def __delitem__(self,index : str) -> None:
		for i in range(len(self)):
			for j in range(len(self)):
				del self.values[i][j][index]
	def __neg__(self,other) -> Terrain:
		return Terrain(
			self.generator,
			[[-self[i,j] for j in len(self)] for i in len(self)]
		)
	def __pos__(self,other) -> Terrain:
		return Terrain(
			self.generator,
			[[+self[i,j] for j in len(self)] for i in len(self)]
		)
	def __invert__(self,other) -> Terrain:
		return Terrain(
			self.generator,
			[[~self[i,j] for j in len(self)] for i in len(self)]
		)
	def __abs__(self,other) -> Terrain:
		return Terrain(
			self.generator,
			[[abs(self[i,j]) for j in len(self)] for i in len(self)]
		)
	def __mul__(self,other) -> Terrain:
		if isinstance(other,Terrain) and len(self) == len(other):
			return Terrain(
				self.generator,
				[[self[i,j] * other[i,j] for j in len(self)] for i in len(self)]
			)
		return Terrain(
			self.generator,
			[[self[i,j] * other for j in len(self)] for i in len(self)]
		)
	def __truediv__(self,other) -> Terrain:
		if isinstance(other,Terrain) and len(self) == len(other):
			return Terrain(
				self.generator,
				[[self[i,j] / other[i,j] for j in len(self)] for i in len(self)]
			)
		return Terrain(
			self.generator,
			[[self[i,j] / other for j in len(self)] for i in len(self)]
		)
	def __mod__(self,other) -> Terrain:
		if isinstance(other,Terrain) and len(self) == len(other):
			return Terrain(
				self.generator,
				[[self[i,j] % other[i,j] for j in len(self)] for i in len(self)]
			)
		return Terrain(
			self.generator,
			[[self[i,j] % other for j in len(self)] for i in len(self)]
		)
	def __floordiv__(self,other) -> Terrain:
		if isinstance(other,Terrain) and len(self) == len(other):
			return Terrain(
				self.generator,
				[[self[i,j] // other[i,j] for j in len(self)] for i in len(self)]
			)
		return Terrain(
			self.generator,
			[[self[i,j] // other for j in len(self)] for i in len(self)]
		)
	def __add__(self,other) -> Terrain:
		if isinstance(other,Terrain) and len(self) == len(other):
			return Terrain(
				self.generator,
				[[self[i,j] + other[i,j] for j in len(self)] for i in len(self)]
			)
		return Terrain(
			self.generator,
			[[self[i,j] + other for j in len(self)] for i in len(self)]
		)
	def __sub__(self,other) -> Terrain:
		if isinstance(other,Terrain) and len(self) == len(other):
			return Terrain(
				self.generator,
				[[self[i,j] - other[i,j] for j in len(self)] for i in len(self)]
			)
		return Terrain(
			self.generator,
			[[self[i,j] - other for j in len(self)] for i in len(self)]
		)
	def __matmul__(self,other) -> Terrain:
		if isinstance(other,Terrain) and len(self) == len(other):
			return Terrain(
				self.generator,
				[[self[i,j] @ other[i,j] for j in len(self)] for i in len(self)]
			)
		return Terrain(
			self.generator,
			[[self[i,j] @ other for j in len(self)] for i in len(self)]
		)
	def __and__(self,other) -> Terrain:
		if isinstance(other,Terrain) and len(self) == len(other):
			return Terrain(
				self.generator,
				[[self[i,j] & other[i,j] for j in len(self)] for i in len(self)]
			)
		return Terrain(
			self.generator,
			[[self[i,j] & other for j in len(self)] for i in len(self)]
		)
	def __or__(self,other) -> Terrain:
		if isinstance(other,Terrain) and len(self) == len(other):
			return Terrain(
				self.generator,
				[[self[i,j] | other[i,j] for j in len(self)] for i in len(self)]
			)
		return Terrain(
			self.generator,
			[[self[i,j] | other for j in len(self)] for i in len(self)]
		)
	def __xor__(self,other) -> Terrain:
		if isinstance(other,Terrain) and len(self) == len(other):
			return Terrain(
				self.generator,
				[[self[i,j] ^ other[i,j] for j in len(self)] for i in len(self)]
			)
		return Terrain(
			self.generator,
			[[self[i,j] ^ other for j in len(self)] for i in len(self)]
		)
	def __clone__(self) -> Terrain:
		return Terrain(
			self.generator,
			clone(self.values)
		)
	def new(self) -> Terrain:
		return Terrain(
			self.generator,
			len(self)
		)
	def map(self,options : tuple[str,...],function : Callable,pct : bool = False) -> list[Terrain]:
		terrain = self.new()
		for i in range(len(self)):
			if pct:
				percent = str(i/len(self) * 100)[:20]
				print('\r' + percent + ' '*(20 - len(percent)) + '%',end = '')
			for j in range(len(self)):
				arguments = []
				for option in options:
					match option:
						case 'terrain':
							arguments.append(self)
						case 'index':
							arguments += [i,j]
						case 'value':
							arguments.append(self[i,j])
						case _:
							raise TypeError
				terrain[i,j] = function(*arguments)
		return terrain
	def foreach(self,options : tuple[str,...],function : Callable,pct : bool = False):
		for i in range(len(self)):
			if pct:
				percent = str(i/len(self) * 100)[:20]
				print('\r' + percent + ' '*(20 - len(percent)) + '%',end = '')
			for j in range(len(self)):
				arguments = []
				for option in options:
					match option:
						case 'terrain':
							arguments.append(self)
						case 'index':
							arguments += [i,j]
						case 'value':
							arguments.append(self[i,j])
						case _:
							raise TypeError
				function(*arguments)
	def as_array(self):
		return np.array(self.values)
	def generate_type(self,type_obj,*args):
		if type_obj == int:
			return self.generator.randint(*args)
		elif type_obj == Color:
			return Color(
				self.generate_type(int,0,255),
				self.generate_type(int,0,255),
				self.generate_type(int,0,255)
			)
		elif type_obj == Point:
			return Point(
				self.generate_type(int,0,len(self) - 1),
				self.generate_type(int,0,len(self) - 1)
			)
		else:
			raise KeyError(type_obj.__name__)
	def generate_list(self,length : int,type_obj,*args) -> list:
		values = []
		for i in range(length):
			values.append(
				self.generate_distinct(values,type_obj,*args)
			)
		return values
	def generate_distinct(self,values,type_obj,*args):
		value = self.generate_type(type_obj,*args)
		while value in values:
			value = self.generate_type(type_obj,*args)
		return value
	def generate(self,argument,length : int):
		if isinstance(argument,dict):
			key,value = list(argument.items())[0]
			if not isinstance(key,tuple):
				key = (key,)
			if not isinstance(value,tuple):
				value = (value,)
			return {
				k : v for k,v in zip(
					self.generate_list(length,*key),
					self.generate_list(length,*value),
				)
			}
		if isinstance(argument,set):
			value = list(argument)[0]
			if not isinstance(value,tuple):
				value = (value,)
			return set(self.generate_list(length,*value))
		if isinstance(argument,frozenset):
			value = list(argument)[0]
			if not isinstance(value,tuple):
				value = (value,)
			return frozenset(self.generate_list(length,*value))
		if isinstance(argument,list):
			value = list(argument)[0]
			if not isinstance(value,tuple):
				value = (value,)
			return self.generate_list(length,*value)
		if isinstance(argument,tuple):
			value = list(argument)[0]
			if not isinstance(value,tuple):
				value = (value,)
			return tuple(self.generate_list(length,*value))
	def range(self) -> list:
		values = []
		for value in self:
			if value not in values:
				values.append(value)
		return values
	def continents(self,count : int,iterations : int) -> Terrain:
		def inner(v,p,m,i,j):
			v[i,j] = m[
				get_closest_point(i,j,m.keys())
			]
			if v[i,j] not in p:
				p[v[i,j]] = set()
			p[v[i,j]].add((i,j))
		points = self.generate([Point],count)
		mappings = {points[i] : i for i in range(count)}
		vals = self.new()
		for p in range(iterations):
			points = {}
			vals.foreach(
				('index',),
				lambda i,j : inner(vals,points,mappings,i,j)
			)
			mappings = {
				(
					round(sum(coord[0] for coord in coords)/len(coords)),
					round(sum(coord[1] for coord in coords)/len(coords)),
				) : color for color,coords in points.items()
			}
		return vals
	def lattitudes(self,*sources : tuple[Point,...]) -> Terrain:
		max_dist = len(self)*2**0.5
		return self.map(
			('index',),
			lambda i,j : max_dist - min(
				get_dist(i,j,*source) for source in sources
			)
		)