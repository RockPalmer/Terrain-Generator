import math
import random


# Permutation table
_perm = list(range(256))
random.Random(42).shuffle(_perm)
_perm *= 2
# 4D gradient vectors (32 directions)
_grad4 = [
	(0, 1, 1, 0), (0, 1, -1, 0), (0, -1, 1, 0), (0, -1, -1, 0),
	(1, 0, 1, 0), (1, 0, -1, 0), (-1, 0, 1, 0), (-1, 0, -1, 0),
	(1, 1, 0, 0), (1, -1, 0, 0), (-1, 1, 0, 0), (-1, -1, 0, 0),

	(0, 1, 0, 1), (0, 1, 0, -1), (0, -1, 0, 1), (0, -1, 0, -1),
	(1, 0, 0, 1), (1, 0, 0, -1), (-1, 0, 0, 1), (-1, 0, 0, -1),

	(0, 0, 1, 1), (0, 0, 1, -1), (0, 0, -1, 1), (0, 0, -1, -1),
	(1, 0, 1, 0), (1, 0, -1, 0), (-1, 0, 1, 0), (-1, 0, -1, 0),

	(1, 1, 1, 0), (-1, 1, 1, 0), (1, -1, 1, 0), (1, 1, -1, 0)
]


def fade(t):
	"""Perlin's smooth interpolation curve."""
	return t * t * t * (t * (t * 6 - 15) + 10)
def lerp(a, b, t):
	"""Linear interpolation."""
	return a + t * (b - a)
def dot(g, x, y, z, w):
	return g[0]*x + g[1]*y + g[2]*z + g[3]*w
def grad(hash_value, x, y, z, w):
	return dot(_grad4[hash_value % len(_grad4)], x, y, z, w)
def perlin4(x,y,z,w):
	"""
	4D Perlin noise.

	Returns approximately [-1, 1].
	"""

	# Find unit hypercube containing point
	X = math.floor(x) & 255
	Y = math.floor(y) & 255
	Z = math.floor(z) & 255
	W = math.floor(w) & 255

	# Relative coordinates
	x -= math.floor(x)
	y -= math.floor(y)
	z -= math.floor(z)
	w -= math.floor(w)

	# Fade curves
	u = fade(x)
	v = fade(y)
	t = fade(z)
	s = fade(w)

	def hash4(ix, iy, iz, iw):
		return _perm[
			_perm[
				_perm[
					_perm[ix & 255] + iy
				& 255] + iz
			& 255] + iw
		& 255]

	total = 0.0

	# Interpolate over the 16 corners of the hypercube
	for dx in (0, 1):
		for dy in (0, 1):
			for dz in (0, 1):
				for dw in (0, 1):
					weight_x = u if dx else 1 - u
					weight_y = v if dy else 1 - v
					weight_z = t if dz else 1 - t
					weight_w = s if dw else 1 - s

					contribution = grad(
						hash4(X + dx, Y + dy, Z + dz, W + dw),
						x - dx,
						y - dy,
						z - dz,
						w - dw
					)

					total += (
						contribution *
						weight_x *
						weight_y *
						weight_z *
						weight_w
					)

	return total