import math
import random
import itertools

# Permutation table
_perm = list(range(256))
random.Random(42).shuffle(_perm)
_perm *= 2

# 5D gradient vectors
# Using vectors with components in {-1,0,1} and exactly two non-zero components
_grad5 = []

for a in range(5):
	for b in range(a + 1, 5):
		for sa in (-1, 1):
			for sb in (-1, 1):
				g = [0, 0, 0, 0, 0]
				g[a] = sa
				g[b] = sb
				_grad5.append(tuple(g))

def fade(t):
	"""Perlin's smooth interpolation curve."""
	return t * t * t * (t * (t * 6 - 15) + 10)
def lerp(a, b, t):
	"""Linear interpolation."""
	return a + t * (b - a)
def dot(g, x, y, z, w, v):
	return (
		g[0] * x +
		g[1] * y +
		g[2] * z +
		g[3] * w +
		g[4] * v
	)
def grad(hash_value, x, y, z, w, v):
	return dot(
		_grad5[hash_value % len(_grad5)],
		x, y, z, w, v
	)
def perlin5(x, y, z, w, v):
	"""
	5D Perlin noise.

	Returns approximately [-1, 1].
	"""

	# Find containing 5D hypercube
	X = math.floor(x) & 255
	Y = math.floor(y) & 255
	Z = math.floor(z) & 255
	W = math.floor(w) & 255
	V = math.floor(v) & 255

	# Relative coordinates inside cell
	x -= math.floor(x)
	y -= math.floor(y)
	z -= math.floor(z)
	w -= math.floor(w)
	v -= math.floor(v)

	# Fade curves
	u = fade(x)
	f = fade(y)
	t = fade(z)
	s = fade(w)
	r = fade(v)


	def hash5(ix, iy, iz, iw, iv):
		return _perm[
			_perm[
				_perm[
					_perm[
						_perm[ix & 255] + iy
					& 255] + iz
				& 255] + iw
			& 255] + iv
		& 255]


	total = 0.0

	# Interpolate over all 32 corners
	for dx, dy, dz, dw, dv in itertools.product((0, 1), repeat=5):

		weight_x = u if dx else 1 - u
		weight_y = f if dy else 1 - f
		weight_z = t if dz else 1 - t
		weight_w = s if dw else 1 - s
		weight_v = r if dv else 1 - r

		contribution = grad(
			hash5(
				X + dx,
				Y + dy,
				Z + dz,
				W + dw,
				V + dv
			),
			x - dx,
			y - dy,
			z - dz,
			w - dw,
			v - dv
		)

		total += (
			contribution *
			weight_x *
			weight_y *
			weight_z *
			weight_w *
			weight_v
		)

	return total