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
	e,
)
from itertools import product

SCREEN_LAYOUT = {}
FINAL_SCREEN_LAYOUT = []

Color = tuple[int,int,int]
Point = tuple[int,int]
GRID_SIZE: int = 256
CELL_SIZE: int = 2  # Size of each square in pixels
MAX_ANGLE = 359
MAX_COLOR = 255
LATTITUDE_EFFECT_DISTANCE = 1000
LATTITUDE_EFFECT_STRENGTH = 50
MAX_THICKNESS = 255
SNOW_THRESHHOLD = 160
HUMIDITY_RANGE = (GRID_SIZE >> 5) - 1
SEA_LEVEL = 130
TERRAIN_BUSINESS = 1
TERRAIN_JAGGEDNESS = 8
AXIS_TILT = 23.44
HUMIDITY_SMUDGE_RADIUS = 12
DIAMETER = GRID_SIZE/pi
RADIUS = DIAMETER/2

# a(x - x0) + b(y - y0) + c(z - z0) = 0
# a(x - a) + b(y - b) + c(z - c) = 0
# ax - a2 + by - b2 + cz - c2 = 0

itera = 0
def prt(v):
	global itera

	print('  '*itera,end='')
	print(v)
def up():
	global itera

	itera += 1
def dn():
	global itera

	itera -= 1
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
def getDistance(p1: Point, p2: Point) -> float:
	dx = abs(p1[0] - p2[0])
	dy = abs(p1[1] - p2[1])
	if dx > GRID_SIZE / 2: dx = GRID_SIZE - dx
	if dy > GRID_SIZE / 2: dy = GRID_SIZE - dy
	return (dx**2 + dy**2)**0.5
def getAverageDistance(point: Point,trn: Screen) -> float:
	distances = []

	for i in range(-HUMIDITY_RANGE,HUMIDITY_RANGE + 1):
		for j in range(-HUMIDITY_RANGE,HUMIDITY_RANGE + 1):
			x = (point[0] + i) % GRID_SIZE
			y = (point[1] + j) % GRID_SIZE
			if not trn[x,y]:
				a = getDistance(point,(x,y))
				if a == 256:
					print((point,(x,y)))
				distances.append(a)
			else:
				distances.append(GRID_SIZE - 1)
	x = sum(distances)/len(distances)
	if x == 256:
		print(x)
	return x
def getCurrentTilt(day: int) -> float:
	min_tilt = -AXIS_TILT
	max_tilt = AXIS_TILT
	return min_tilt + day * (max_tilt - min_tilt)/365
# float[0,359]
def lattitudeToAngle(latt: int) -> float:
	return latt * 359/GRID_SIZE
# int[0,359]
def getAngleForDay(latt: int,day: int) -> float:
	return (lattitudeToAngle(latt) + getCurrentTilt(day)) % 360
# (float[-RADIUS,RADIUS],float[-RADIUS,RADIUS])
def getVectorForDay(latt: int,day: int) -> tuple[float,float]:
	theta = getAngleForDay(latt,day)
	return (
		RADIUS * cos(radians(theta)),
		RADIUS * sin(radians(theta)),
	)
# float[-RADIUS**2,RADIUS**2]
def getSunlightValue(latt: int,day: int) -> float:
	x,y = getVectorForDay(latt,day)
	return x * -RADIUS
# float[-RADIUS**2,RADIUS**2]
def getNormalizedSunlightValue(latt: int,day: int) -> float:
	return (
		getSunlightValue(latt,day) + getSunlightValue(GRID_SIZE - latt,day)
	)/2
def getAvgSunlightValue(latt: int) -> float:
	values = [getNormalizedSunlightValue(latt,day) for day in range(364)]
	return (sum(values)/len(values) + RADIUS**2) * 255/(2 * RADIUS**2)
def smudge(trn: Screen) -> Screen:
	points = set()
	for i in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS):
		for j in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS):
			if i**2 + j**2 <= HUMIDITY_SMUDGE_RADIUS**2:
				points.add((i,j))
	screen = Screen(GRID_SIZE)
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			pts = {
				(
					(i + a) % GRID_SIZE,
					(j + b) % GRID_SIZE,
				) for (a,b) in points
			}
			values = [trn[pt] for pt in pts]
			screen[i,j] = sum(values)/len(values)
	return screen

TERRAIN: dict[str,Screen] = {}

# Grid settings

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
			try:
				pygame.draw.rect(window,FINAL_SCREEN_LAYOUT[x][y],rect)
			except:
				print(FINAL_SCREEN_LAYOUT[x][y])
				raise
	pygame.display.flip()

# y = 10e^(-(x - 127)^2)

pnoise = perlinNoise(
	size = GRID_SIZE,
	seed = random.randint(0,255),
	scale = TERRAIN_BUSINESS,
	octaves = TERRAIN_JAGGEDNESS,
)
print('generating altitude...')
TERRAIN['altitude'] = keyMap(
	lambda x,y,v : (pnoise[x,y] + 1) * 255/2,
	Screen(GRID_SIZE),
)
print('generating land...')
TERRAIN['land'] = scrMap(
	lambda v : v > SEA_LEVEL,
	TERRAIN['altitude'],
)
print('generating humidity...')
TERRAIN['humidity'] = 255 - smudge(
	scrMap(
		lambda v : 255 if v else 0,
		TERRAIN['land'],
	)
)
print('generating sunlight...')
TERRAIN['sunlight'] = keyMap(
	lambda x,y,v : getAvgSunlightValue(y),
	Screen(GRID_SIZE),
)
print('generating snow...')
TERRAIN['snow'] = scrMap(
	lambda u,v : (255 - u)/7 + v > SNOW_THRESHHOLD,
	TERRAIN['sunlight'],
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
TERRAIN['land (colored)'] = scrMap(
	lambda v : (255,255,255) if v else (0,0,0),
	TERRAIN['land'],
)
TERRAIN['sunlight (colored)'] = scrMap(
	lambda v : (
		int(v),
		int(v),
		int(v),
	),
	TERRAIN['sunlight'],
)
TERRAIN['humidity (colored)'] = scrMap(
	lambda v : (
		int(v),
		int(v),
		int(v),
	),
	TERRAIN['humidity'],
)
TERRAIN['greenery'] = scrMap(
	lambda w,u,v : (255,255,255) if w else (
		u[0] // 2,
		u[0] + (255 - u[0]) // 3,
		u[2] // 2,
	) if v else (
		u[0] // 2,
		u[1] // 2,
		(255 + u[0]) // 2,
	),
	TERRAIN['snow'],
	TERRAIN['altitude (colored)'],
	TERRAIN['land'],
)

SCREEN_LAYOUT[0,0] = 'greenery'
SCREEN_LAYOUT[1,0] = 'humidity (colored)'

mapLayout(TERRAIN)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()