from __future__ import annotations
from typing import (
	Any,
	Callable,
	Generic,
	TypeVar,
)

T = TypeVar("T")

def scrMapImage(fun: Callable,*screens: tuple[Image,...]) -> Image:
	size = screens[0].size
	screen = Image(size)
	for i in range(size):
		for j in range(size):
			scns = [scn[i,j] for scn in screens]
			screen[i,j] = fun(*scns)
	return screen
def ifMapImage(s1,s2,s3) -> Image:
	if isinstance(s1,Image):
		if isinstance(s2,Image):
			if isinstance(s3,Image):
				return scrMapImage(
					lambda a,b,c : a if b else c,
					s1,s2,s3
				)
			return scrMapImage(
				lambda a,b : a if b else s3,
				s1,s2
			)
		if isinstance(s3,Image):
			return scrMapImage(
				lambda a,c : a if s2 else c,
				s1,s3
			)
		return scrMapImage(
			lambda a : a if s2 else s3,
			s1
		)
	if isinstance(s2,Image):
		if isinstance(s3,Image):
			return scrMapImage(
				lambda b,c : s1 if b else c,
				s2,s3
			)
		return scrMapImage(
			lambda b : s1 if b else s3,
			s2
		)
	if isinstance(s3,Image):
		return scrMapImage(
			lambda c : s1 if s2 else c,
			s3
		)
	return s1 if s2 else s3
def keyMapImage(fun: Callable,size: int) -> Image:
	img = Image(size)
	for i in range(size):
		for j in range(size):
			img[i,j] = fun(i,j)
	return img

class Image(Generic[T]):
	def __init__(self,size: int,value = None) -> None:
		self.size = size
		self.values = [[value for _ in range(size)] for _ in range(size)]
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
		if not isinstance(index,tuple) or len(index) != 2:
			raise KeyError(f"Image[{index}]")
		return self.values[index[0]][index[1]]
	def __setitem__(self,index: tuple,value: Any) -> None:
		if not isinstance(index,tuple) or len(index) != 2:
			raise KeyError(f"Image[{index}]")
		self.values[index[0]][index[1]] = value
	def scale(self,*args) -> Image:
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
	def __and__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u and v if isinstance(u,bool) and isinstance(v,bool) else u & v,
				self,
				other,
			)
		if not isinstance(other,Image):
			if isinstance(other,bool):
				return scrMapImage(
					lambda u : u and other if isinstance(u,bool) else u & other,
					self,
				)
			return scrMapImage(
				lambda u : u & other,
				self,
			)
		return NotImplemented
	def __or__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u or v if isinstance(u,bool) and isinstance(v,bool) else u | v,
				self,
				other,
			)
		if not isinstance(other,Image):
			if isinstance(other,bool):
				return scrMapImage(
					lambda u : u or other if isinstance(u,bool) else u | other,
					self,
				)
			return scrMapImage(
				lambda u : u | other,
				self,
			)
		return NotImplemented
	def __xor__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u ^ v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u ^ other,
				self,
			)
		return NotImplemented
	def __add__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u + v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u + other,
				self,
			)
		return NotImplemented
	def __radd__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u + v,
				other,
				self,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : other + u,
				self,
			)
		return NotImplemented
	def __sub__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u - v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u - other,
				self,
			)
		return NotImplemented
	def __rsub__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u - v,
				other,
				self,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : other - u,
				self,
			)
		return NotImplemented
	def __mul__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u * v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u * other,
				self,
			)
		return NotImplemented
	def __rmul__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u * v,
				other,
				self,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : other * u,
				self,
			)
		return NotImplemented
	def __truediv__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u / v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u / other,
				self,
			)
		return NotImplemented
	def __rtruediv__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u / v,
				other,
				self,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : other / u,
				self,
			)
		return NotImplemented
	def __floordiv__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u // v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u // other,
				self,
			)
		return NotImplemented
	def __rfloordiv__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u // v,
				other,
				self,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : other // u,
				self,
			)
		return NotImplemented
	def __mod__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u % v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u % other,
				self,
			)
		return NotImplemented
	def __rmod__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u % v,
				other,
				self,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : other % u,
				self,
			)
		return NotImplemented
	def __pow__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u ** v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u ** other,
				self,
			)
		return NotImplemented
	def __rpow__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u ** v,
				other,
				self,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : other ** u,
				self,
			)
		return NotImplemented
	def __lshift__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u << v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u << other,
				self,
			)
		return NotImplemented
	def __rlshift__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u << v,
				other,
				self,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : other << u,
				self,
			)
		return NotImplemented
	def __rshift__(self,other: Any) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u >> v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u >> other,
				self,
			)
		return NotImplemented
	def __rrshift__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u >> v,
				other,
				self,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : other >> u,
				self,
			)
		return NotImplemented
	def __neg__(self) -> Image:
		return scrMapImage(
			lambda v : -v,
			self,
		)
	def __invert__(self) -> Image:
		return scrMapImage(
			lambda v : not v if isinstance(v,bool) else ~v,
			self,
		)
	def __pos__(self) -> Image:
		return scrMapImage(
			lambda v : +v,
			self,
		)
	def __abs__(self) -> Image:
		return scrMapImage(
			lambda v : abs(v),
			self,
		)
	def isNone(self) -> bool:
		return scrMapImage(
			lambda v : v is None,
			self,
		)
	def __eq__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u == v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u == other,
				self,
			)
		return NotImplemented
	def __ne__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u != v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u != other,
				self,
			)
		return NotImplemented
	def __lt__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u < v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u < other,
				self,
			)
		return NotImplemented
	def __gt__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u > v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u > other,
				self,
			)
		return NotImplemented
	def __le__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u <= v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u <= other,
				self,
			)
		return NotImplemented
	def __ge__(self,other) -> Image:
		if isinstance(other,Image) and self.size == other.size:
			return scrMapImage(
				lambda u,v : u >= v,
				self,
				other,
			)
		if not isinstance(other,Image):
			return scrMapImage(
				lambda u : u >= other,
				self,
			)
		return NotImplemented