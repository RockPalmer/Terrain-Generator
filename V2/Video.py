from __future__ import annotations
from typing import (
	Any,
	Callable,
	Generic,
	TypeVar,
)
from Image import Image

T = TypeVar("T")

def scrMapVideo(fun: Callable,*screens: tuple[Video,...]) -> Video:
	length = screens[0].length
	size = screens[0].size
	screen = Video(size,length)
	for i in range(size):
		for j in range(size):
			for k in range(length):
				scns = [scn[i,j,k] for scn in screens]
				screen[i,j,k] = fun(*scns)
	return screen
def ifMapVideo(s1,s2,s3) -> Video:
	if isinstance(s1,Video):
		if isinstance(s2,Video):
			if isinstance(s3,Video):
				return scrMapVideo(
					lambda a,b,c : a if b else c,
					s1,s2,s3
				)
			return scrMapVideo(
				lambda a,b : a if b else s3,
				s1,s2
			)
		if isinstance(s3,Video):
			return scrMapVideo(
				lambda a,c : a if s2 else c,
				s1,s3
			)
		return scrMapVideo(
			lambda a : a if s2 else s3,
			s1
		)
	if isinstance(s2,Video):
		if isinstance(s3,Video):
			return scrMapVideo(
				lambda b,c : s1 if b else c,
				s2,s3
			)
		return scrMapVideo(
			lambda b : s1 if b else s3,
			s2
		)
	if isinstance(s3,Video):
		return scrMapVideo(
			lambda c : s1 if s2 else c,
			s3
		)
	return s1 if s2 else s3
def keyMapVideo(fun: Callable,size: int,length: int) -> Image:
	vid = Video(size)
	for i in range(size):
		for j in range(size):
			for k in range(length):
				vid[i,j,k] = fun(i,j,k)
	return vid

class Video(Generic[T]):
	def __init__(self,size: int,length: int,value = None) -> None:
		self.size = size
		self.length = length
		self.values = [Image(size) for i in range(length)]
	def __len__(self) -> int:
		return len(self.values[0]) * self.length
	def __iter__(self) -> iter:
		for image in self.values:
			yield from image
	def enumerate(self) -> iter:
		for i in range(self.size):
			for j in range(self.size):
				for k in range(self.length):
					yield ((i,j,k),self[i,j,k])
	def __getitem__(self,index: tuple|int):
		if isinstance(index,int):
			return self.values[index]
		if not isinstance(index,tuple) or len(index) != 3:
			raise KeyError(f"Video[{index}]")
		return self.values[index[2]][index[:-1]]
	def __setitem__(self,index: tuple,value: Any) -> None:
		if isinstance(index,int):
			self.values[index] = value
		elif not isinstance(index,tuple) or len(index) != 3:
			raise KeyError(f"Video[{index}]")
		else:
			self.values[index[2]][index[:-1]] = value
	def scale(self,*args) -> Video:
		match len(args):
			case 4: (minv1,maxv1,minv2,maxv2) = args
			case 2:
				vals = {v for v in self}
				minv1 = min(vals)
				maxv1 = max(vals)
				(minv2,maxv2) = args
			case _: raise ValueError
		diff1 = maxv1 - minv1
		diff2 = maxv2 - minv2
		return ((self - minv1) * diff2/diff1) + minv2
	def max(self):
		return max({v for v in self})
	def min(self):
		return min({v for v in self})
	def __and__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u and v if isinstance(u,bool) and isinstance(v,bool) else u & v,
				self,
				other,
			)
		if not isinstance(other,Video):
			if isinstance(other,bool):
				return scrMapVideo(
					lambda u : u and other if isinstance(u,bool) else u & other,
					self,
				)
			return scrMapVideo(
				lambda u : u & other,
				self,
			)
		return NotImplemented
	def __or__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u or v if isinstance(u,bool) and isinstance(v,bool) else u | v,
				self,
				other,
			)
		if not isinstance(other,Video):
			if isinstance(other,bool):
				return scrMapVideo(
					lambda u : u or other if isinstance(u,bool) else u | other,
					self,
				)
			return scrMapVideo(
				lambda u : u | other,
				self,
			)
		return NotImplemented
	def __xor__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u ^ v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u ^ other,
				self,
			)
		return NotImplemented
	def __add__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u + v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u + other,
				self,
			)
		return NotImplemented
	def __radd__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u + v,
				other,
				self,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : other + u,
				self,
			)
		return NotImplemented
	def __sub__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u - v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u - other,
				self,
			)
		return NotImplemented
	def __rsub__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u - v,
				other,
				self,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : other - u,
				self,
			)
		return NotImplemented
	def __mul__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u * v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u * other,
				self,
			)
		return NotImplemented
	def __rmul__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u * v,
				other,
				self,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : other * u,
				self,
			)
		return NotImplemented
	def __truediv__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u / v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u / other,
				self,
			)
		return NotImplemented
	def __rtruediv__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u / v,
				other,
				self,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : other / u,
				self,
			)
		return NotImplemented
	def __floordiv__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u // v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u // other,
				self,
			)
		return NotImplemented
	def __rfloordiv__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u // v,
				other,
				self,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : other // u,
				self,
			)
		return NotImplemented
	def __mod__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u % v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u % other,
				self,
			)
		return NotImplemented
	def __rmod__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u % v,
				other,
				self,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : other % u,
				self,
			)
		return NotImplemented
	def __pow__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u ** v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u ** other,
				self,
			)
		return NotImplemented
	def __rpow__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u ** v,
				other,
				self,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : other ** u,
				self,
			)
		return NotImplemented
	def __lshift__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u << v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u << other,
				self,
			)
		return NotImplemented
	def __rlshift__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u << v,
				other,
				self,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : other << u,
				self,
			)
		return NotImplemented
	def __rshift__(self,other: Any) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u >> v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u >> other,
				self,
			)
		return NotImplemented
	def __rrshift__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u >> v,
				other,
				self,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : other >> u,
				self,
			)
		return NotImplemented
	def __neg__(self) -> Video:
		return scrMapVideo(
			lambda v : -v,
			self,
		)
	def __invert__(self) -> Video:
		return scrMapVideo(
			lambda v : not v if isinstance(v,bool) else ~v,
			self,
		)
	def __pos__(self) -> Video:
		return scrMapVideo(
			lambda v : +v,
			self,
		)
	def __abs__(self) -> Video:
		return scrMapVideo(
			lambda v : abs(v),
			self,
		)
	def isNone(self) -> bool:
		return scrMapVideo(
			lambda v : v is None,
			self,
		)
	def __eq__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u == v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u == other,
				self,
			)
		return NotImplemented
	def __ne__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u != v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u != other,
				self,
			)
		return NotImplemented
	def __lt__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u < v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u < other,
				self,
			)
		return NotImplemented
	def __gt__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u > v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u > other,
				self,
			)
		return NotImplemented
	def __le__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u <= v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u <= other,
				self,
			)
		return NotImplemented
	def __ge__(self,other) -> Video:
		if isinstance(other,Video) and self.size == other.size:
			return scrMapVideo(
				lambda u,v : u >= v,
				self,
				other,
			)
		if not isinstance(other,Video):
			return scrMapVideo(
				lambda u : u >= other,
				self,
			)
		return NotImplemented