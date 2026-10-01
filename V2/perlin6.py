import math
import random
import itertools

# Permutation table
_perm = list(range(256))
random.Random(42).shuffle(_perm)
_perm *= 2

# 6D gradient vectors
# All vectors with exactly two non-zero components (+/-1)
_grad6 = []

for a in range(6):
	for b in range(a + 1, 6):
		for sa in (-1, 1):
			for sb in (-1, 1):
				g = [0, 0, 0, 0, 0, 0]
				g[a] = sa
				g[b] = sb
				_grad6.append(tuple(g))

def fade(t):
	"""Perlin's smooth interpolation curve."""
	return t * t * t * (t * (t * 6 - 15) + 10)
def dot(g, x, y, z, w, v, u):
	return (
		g[0] * x +
		g[1] * y +
		g[2] * z +
		g[3] * w +
		g[4] * v +
		g[5] * u
	)
def grad(hash_value, x, y, z, w, v, u):
	return dot(
		_grad6[hash_value % len(_grad6)],
		x, y, z, w, v, u
	)
def perlin6(x, y, z, w, v, u):
	"""
	6D Perlin noise.

	Returns approximately [-1, 1].
	"""

	# Find containing hypercube
	X = math.floor(x) & 255
	Y = math.floor(y) & 255
	Z = math.floor(z) & 255
	W = math.floor(w) & 255
	V = math.floor(v) & 255
	U = math.floor(u) & 255

	# Relative position inside cell
	x -= math.floor(x)
	y -= math.floor(y)
	z -= math.floor(z)
	w -= math.floor(w)
	v -= math.floor(v)
	u -= math.floor(u)

	# Fade curves
	fx = fade(x)
	fy = fade(y)
	fz = fade(z)
	fw = fade(w)
	fv = fade(v)
	fu = fade(u)


	def hash6(ix, iy, iz, iw, iv, iu):
		return _perm[
			_perm[
				_perm[
					_perm[
						_perm[
							_perm[ix & 255] + iy
						& 255] + iz
					& 255] + iw
				& 255] + iv
			& 255] + iu
		& 255]


	total = 0.0

	# Iterate over all 64 corners
	for dx, dy, dz, dw, dv, du in itertools.product((0, 1), repeat=6):

		weight_x = fx if dx else 1 - fx
		weight_y = fy if dy else 1 - fy
		weight_z = fz if dz else 1 - fz
		weight_w = fw if dw else 1 - fw
		weight_v = fv if dv else 1 - fv
		weight_u = fu if du else 1 - fu

		contribution = grad(
			hash6(
				X + dx,
				Y + dy,
				Z + dz,
				W + dw,
				V + dv,
				U + du
			),
			x - dx,
			y - dy,
			z - dz,
			w - dw,
			v - dv,
			u - du
		)

		total += (
			contribution *
			weight_x *
			weight_y *
			weight_z *
			weight_w *
			weight_v *
			weight_u
		)

	return total