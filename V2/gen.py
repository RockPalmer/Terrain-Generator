import pygame,random
from noise import pnoise2
from perlin import perlin4
from numpy import zeros
from Screen import (
	scrMap,
	keyMap,
	Screen,
)
from bidict import bidict
from math import (
	cos,
	sin,
	tan,
	radians,
	pi,
)
from itertools import product

SCREEN_LAYOUT = {}
FINAL_SCREEN_LAYOUT = []

Color = tuple[int,int,int]
Point = tuple[int,int]

#  = m(255)2

def perlinNoise(size: int,seed: int|float = 0,scale: int = 1,octaves: int = 1) -> dict[Point,float]:
	"""
	Generate seamless wrapping 2D Perlin noise using 4D Perlin.

	Returns:
	    list[list[float]]: values approximately [-1, 1]
	"""
	rng = random.Random(seed)
	seed_offset = rng.random() * 10000.0
	noise_map = []
	for y in range(size):
		row = []
		for x in range(size):
			value = 0.0
			amplitude = 1.0
			frequency = 1.0
			amplitude_sum = 0.0
			for octave in range(octaves):
				# Map grid coordinates onto a torus
				angle_x = 2.0 * pi * x / size
				angle_y = 2.0 * pi * y / size
				nx = cos(angle_x) * scale * frequency
				ny = sin(angle_x) * scale * frequency
				nz = cos(angle_y) * scale * frequency
				nw = sin(angle_y) * scale * frequency + seed_offset
				sample = perlin4(nx,ny,nz,nw)
				value += sample * amplitude
				amplitude_sum += amplitude
				amplitude *= 0.5
				frequency *= 2.0
			row.append(value / amplitude_sum)
		noise_map.append(row)
	result = {}
	for i in range(size):
		for j in range(size):
			result[i,j] = noise_map[i][j]
	return result
def getMaxX(layout: dict[Point,str]) -> int:
	return max(x for x,_ in layout.keys())
def getMaxY(layout: dict[Point,str]) -> int:
	return max(y for _,y in layout.keys())
def mapLayout(trn: dict[str,Screen]) -> None:
	global SCREEN_LAYOUT,FINAL_SCREEN_LAYOUT

	MAX_X = (getMaxX(SCREEN_LAYOUT) + 1) * GRID_SIZE
	MAX_Y = (getMaxY(SCREEN_LAYOUT) + 1) * GRID_SIZE

	FINAL_SCREEN_LAYOUT = [[None for i in range(MAX_Y)] for j in range(MAX_X)]

	covered = set()

	for (x,y),k in SCREEN_LAYOUT.items():
		for i in range(GRID_SIZE):
			for j in range(GRID_SIZE):
				covered.add((
					x * GRID_SIZE + i,
					y * GRID_SIZE + j,
				))
				FINAL_SCREEN_LAYOUT[x * GRID_SIZE + i][y * GRID_SIZE + j] = trn[k][i,j]
def getLattitude(y: int) -> float:
	circumference = GRID_SIZE
	diameter = circumference/pi
	radius = diameter/2
	return radius + (radius**2 + y**2)**0.5

# Grid settings
GRID_SIZE: int = 256
CELL_SIZE: int = 1  # Size of each square in pixels
MAX_ANGLE = 359
MAX_COLOR = 255
MAX_THICKNESS = 255
SEA_LEVEL = 140
TERRAIN: dict[str,Screen] = {}

LENGTH: int = GRID_SIZE * CELL_SIZE

pygame.init()

def drawMap() -> None:
	global pygame,FINAL_SCREEN_LAYOUT,SCREEN_LAYOUT

	window = pygame.display.set_mode((
		(getMaxX(SCREEN_LAYOUT) + 1)*LENGTH,
		(getMaxY(SCREEN_LAYOUT) + 1)*LENGTH,
	))
	pygame.display.set_caption("Window")

	covered = set()
	for x in range(len(FINAL_SCREEN_LAYOUT)):
		for y in range(len(FINAL_SCREEN_LAYOUT[x])):
			covered.add((x,y))
			rect = pygame.Rect(
				x * CELL_SIZE,
				y * CELL_SIZE,
				CELL_SIZE,
				CELL_SIZE,
			)
			pygame.draw.rect(window,FINAL_SCREEN_LAYOUT[x][y],rect)
	pygame.display.flip()

pnoise = perlinNoise(
	size = GRID_SIZE,
	seed = random.randint(0,255),
	octaves = 5,
)
TERRAIN['altitude'] = keyMap(
	lambda x,y,v : (pnoise[x,y] + 1) * 255/2,
	Screen(GRID_SIZE),
)
TERRAIN['lattitude'] = keyMap(
	lambda x,y,v : -1/(20*(abs(y - GRID_SIZE / 2)-150)),
	Screen(GRID_SIZE),
)
max_latt = max({v for v in TERRAIN['lattitude']})
min_latt = min({v for v in TERRAIN['lattitude']})
TERRAIN['lattitude'] = (TERRAIN['lattitude'] - min_latt) * 50/(max_latt - min_latt)
TERRAIN['altitude'] = TERRAIN['altitude'] + TERRAIN['lattitude']
max_alt = max({v for v in TERRAIN['altitude']})
min_alt = min({v for v in TERRAIN['altitude']})
TERRAIN['is land'] = scrMap(
	lambda v : v > SEA_LEVEL,
	TERRAIN['altitude'],
)

TERRAIN['altitude (colored)'] = scrMap(
	lambda v : (
		int(v),
		int(v),
		int(v),
	),
	TERRAIN['altitude'],
)
TERRAIN['lattitude (colored)'] = scrMap(
	lambda v : (
		int(v),
		int(v),
		int(v),
	),
	TERRAIN['lattitude'],
)
TERRAIN['is land (colored)'] = scrMap(
	lambda v : (255,255,255) if v else (0,0,0),
	TERRAIN['is land'],
)
TERRAIN['greenery'] = scrMap(
	lambda u,v : (
		u[0] // 2,
		u[0] + (255 - u[0]) // 3,
		u[2] // 2,
	) if v else (
		u[0] // 2,
		u[1] // 2,
		(255 + u[0]) // 2,
	),
	TERRAIN['altitude (colored)'],
	TERRAIN['is land'],
)
SCREEN_LAYOUT[0,0] = 'greenery'
SCREEN_LAYOUT[1,0] = 'greenery'
SCREEN_LAYOUT[2,0] = 'greenery'
SCREEN_LAYOUT[0,1] = 'greenery'
SCREEN_LAYOUT[1,1] = 'greenery'
SCREEN_LAYOUT[2,1] = 'greenery'
SCREEN_LAYOUT[0,2] = 'greenery'
SCREEN_LAYOUT[1,2] = 'greenery'
SCREEN_LAYOUT[2,2] = 'greenery'

mapLayout(TERRAIN)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()