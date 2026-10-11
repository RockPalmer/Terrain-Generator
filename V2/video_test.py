import pygame,random
from perlin5 import perlin5
from perlin4 import perlin4
from Image import Image
from image_functions import scrMap
from math import (
	cos,
	sin,
	tau,
)

'''
(+t,0,0,0):
	x = 0 -> 1/2
(0,+t,0,0):
	x = 1/3 -> 2/3
(0,0,+t,0):
	y = 0 -> 1/2
(0,0,0,+t):
	y = 1/3 -> 2/3
'''

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
					sample = perlin4(nx,ny,nz,nw)
					value += sample * amplitude
					amplitude_sum += amplitude
					amplitude *= 0.5
					frequency *= 2.0
				noise_map[x,y] = value / amplitude_sum
		return noise_map

FRAMES = 50

CELL_SIZE = 4
GRID_SIZE = 128
LENGTH = GRID_SIZE * CELL_SIZE

pygame.init()
screen = pygame.display.set_mode((LENGTH,LENGTH))
clock = pygame.time.Clock()

running = True

gen = PerlinGenerator(size = GRID_SIZE)

frames = []
for frame in range(FRAMES):
	print(f"generating frame {frame + 1}")
	t = frame * 1 / FRAMES
	frames.append(gen.getAtTime(t).scale(-1,1,0,255))

for i in range(len(frames)):
	frames[i] = scrMap(
		lambda v : (int(v),int(v),int(v)),
		frames[i],
	)

index = 0
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			rect = pygame.Rect(
				i * CELL_SIZE,
				j * CELL_SIZE,
				CELL_SIZE,
				CELL_SIZE,
			)
			try:
				pygame.draw.rect(screen,frames[index][i,j],rect)
			except:
				print(frames[index][i,j])
				raise
	pygame.display.flip()
	clock.tick(60)
	index = (index + 1) % FRAMES

pygame.quit()