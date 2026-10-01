import random
from perlin5 import perlin5
from Image import Image
from math import (
	cos,
	sin,
	tau,
)

class PerlinGenerator:
	def __init__(self,size: int,seed: int|float = 0,scale: int = 1,octaves: int = 1) -> None:
		self.size = size
		self.scale = scale
		self.octaves = octaves
		self.seed_offset = seed
	def getAtTime(self,t: int|float) -> Image:
		noise_map = Image(self.size)
		for y in range(self.size):
			for x in range(self.size):
				value = 0.0
				amplitude = 1.0
				frequency = 1.0
				amplitude_sum = 0.0
				for octave in range(self.octaves):
					# Map grid coordinates onto a torus
					angle_x = tau * x / self.size
					angle_y = tau * y / self.size
					nx = cos(angle_x) * self.scale * frequency
					ny = sin(angle_x) * self.scale * frequency
					nz = cos(angle_y) * self.scale * frequency
					nw = sin(angle_y) * self.scale * frequency + self.seed_offset
					sample = perlin5(nx,ny,nz,nw,t)
					value += sample * amplitude
					amplitude_sum += amplitude
					amplitude *= 0.5
					frequency *= 2.0
				noise_map[x,y] = value / amplitude_sum
		return noise_map