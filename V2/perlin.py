import math
import random
import itertools
from typing import Iterable

_perm = list(range(256))
random.Random(42).shuffle(_perm)
_perm *= 2

_grad = {}

def fade(t: float) -> float:
	return t * t * t * (t * (t * 6 - 15) + 10)
def lerp(a: float,b: float,t: float) -> float:
	return a + t * (b - a)
def dot(a: Iterable[float],b: Iterable[float]) -> float:
	return sum(p * q for p,q in zip(a,b))
def __grad(d: int) -> None:
	global _grad

	if d in _grad: return

	_grad[d] = []
	for a in range(d):
		for b in range(a + 1, d):
			for sa in (-1, 1):
				for sb in (-1, 1):
					g = [0 for i in range(d)]
					g[a] = sa
					g[b] = sb
					_grad[d].append(tuple(g))
def grad(hash_value,*v):
	__grad(len(v))
	__grad(hash_value % len(_grad[len(v)]))
	return dot(
		_grad[len(v)][hash_value % len(_grad[len(v)])],
		v
	)
def HASH(*v):
	if len(v) == 1: return _perm[v[0] & 255]
	return _perm[
		HASH(*v[:-1]) + v[-1] & 255
	]
def perlin(*v):
	V = [math.floor(x) & 255 for x in v]
	a = [x - math.floor(x) for x in v]
	u = [fade(x) for x in a]
	total = 0
	for d in itertools.product((0,1),repeat = len(v)):
		w = [ui if di else 1 - ui for ui,di in zip(u,d)]
		contribution = grad(
			HASH(*[Vi + di for Vi,di in zip(V,d)]),
			*[ai - di for ai,di in zip(a,d)]
		)
		c = contribution
		for wi in w:
			c *= wi
		total += c
	return total