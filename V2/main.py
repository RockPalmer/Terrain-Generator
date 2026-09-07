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
Vector = tuple[float,float]

def perlinNoise(size,seed=0,scale=1,octaves=1):
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
def generateNoise(width: int,height: int,scale: int,base: int) -> dict[Point,float]:
	arr = zeros((height, width))
	for i in range(height):
		for j in range(width):
			arr[i,j] = pnoise2(
				i / scale,
				j / scale,
				octaves = 1,
				base = base,
			)
	values = arr.tolist()
	result = {}
	for i in range(len(values)):
		for j in range(len(values[i])):
			result[i,j] = values[i][j]
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
def rotate(p1: Point,p2: Point,theta: float) -> Point:
	dx,dy = getVector(p2,p1)
	return (
		int(dx * cos(theta) - dy * sin(theta) + p2[0]),
		int(dx * sin(theta) + dy * cos(theta) + p2[1]),
	)
def getSides(center: Point,trn: Screen) -> set[str]:
	sides = set()
	for x in range(GRID_SIZE):
		if trn[x,0] == center:
			sides.add('N')
			break
	for x in range(GRID_SIZE):
		if trn[x,GRID_SIZE - 1] == center:
			sides.add('S')
			break
	for y in range(GRID_SIZE):
		if trn[0,y] == center:
			sides.add('W')
			break
	for y in range(GRID_SIZE):
		if trn[GRID_SIZE - 1,y] == center:
			sides.add('E')
			break
	return sides
def getAngledDistance(p1: Point,p2: Point,theta: int) -> int: # int[-63,63]
	p3 = rotate(p1,p2,-radians(theta))
	return p3[0] - p2[0]
def getClosestPoint(point: Point,centers: list[Point]) -> Point:
	cents = list(centers)
	distances = [getDistance(point,center) for center in cents]
	minDist = min(distances)
	minDistIndex = distances.index(minDist)
	return cents[minDistIndex]
def get_centroid(points: set[Point]) -> Point:
	return (
		sum(p[0] for p in points)/len(points),
		sum(p[1] for p in points)/len(points),
	)
def getDistance(p1: Point, p2: Point) -> float:
	dx = abs(p1[0] - p2[0])
	dy = abs(p1[1] - p2[1])
	if dx > GRID_SIZE / 2: dx = GRID_SIZE - dx
	if dy > GRID_SIZE / 2: dy = GRID_SIZE - dy
	return (dx**2 + dy**2)**0.5
def getVector(p1: Point,p2: Point) -> tuple[int,int]:
	return (
		int(((p2[0] - p1[0] + GRID_SIZE / 2) % GRID_SIZE) - GRID_SIZE / 2),
		int(((p2[1] - p1[1] + GRID_SIZE / 2) % GRID_SIZE) - GRID_SIZE / 2),
	)
def get_neighbors(x: int,y: int,v: Screen) -> frozenset[Point]:
	points = {
		(x - 1,y - 1),
		(x - 1,y),
		(x - 1,y + 1),
		(x,y - 1),
		(x,y),
		(x,y + 1),
		(x + 1,y - 1),
		(x + 1,y),
		(x + 1,y + 1),
	}
	values = set()
	for i,j in points:
		if i >= 0 and j >= 0 and i < v.size and j < v.size:
			values.add(v[i,j])
	return frozenset(values)
def getPairs(values: frozenset) -> set[frozenset]:
	return {frozenset(v) for v in product(set(values),set(values))} - {frozenset([v,v]) for v in values}
def getConjunctionHeight(centers: frozenset[Point],alts: dict[frozenset[Point],dict[Point,int]],cont: Point) -> int:
	pairs: set[frozenset[Point]] = getPairs(centers)
	vals = [alts[pair][cont] for pair in pairs]
	return sum(vals)//len(vals)

# Grid settings
GRID_SIZE: int = 256
CELL_SIZE: int = 1  # Size of each square in pixels
MAX_ANGLE = 359
MAX_COLOR = 255
MAX_THICKNESS = 255

LENGTH: int = GRID_SIZE * CELL_SIZE

NUM_CONTINENTS: int = 12

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

terrain: dict[str,Screen] = {}

centers: list[Point] = []
while len(centers) < NUM_CONTINENTS:
	c: Point = (
		random.randint(0,GRID_SIZE - 1),
		random.randint(0,GRID_SIZE - 1),
	)
	if c not in centers:
		centers.append(c)
move_directions: dict[Point,int] = {center : random.randint(0,MAX_ANGLE) for center in centers} # Point => int[0,359]
heights: dict[Point,int] = {center : random.randint(0,MAX_THICKNESS) for center in centers} # Point => int[0,255]

pnoise = {}
for i,center in enumerate(centers):
	pnoise[center] = perlinNoise(
		GRID_SIZE,
		i,
	)
	print(i)
print('pnoise')
terrain['tectonic plates'] = Screen(GRID_SIZE)
for center in centers:
	terrain['tectonic plates'][center] = center
terrain['noise']: Screen = keyMap(
	lambda x,y,v : (
		random.randint(0,MAX_COLOR - 1),
		random.randint(0,MAX_COLOR - 1),
		random.randint(0,MAX_COLOR - 1),
	),
	Screen(GRID_SIZE),
) # Color
terrain['tectonic plates'] = keyMap(
	lambda x,y,_: getClosestPoint((x,y),centers),
	terrain['tectonic plates'],
) # Point
for i in range(5):
	continent_sets = {}
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			x = terrain['tectonic plates'][i,j]
			if x not in continent_sets:
				continent_sets[x] = set()
			continent_sets[x].add((i,j))
	continent_color_map = [get_centroid(v) for k,v in continent_sets.items()]
	terrain['tectonic plates'] = keyMap(
		lambda x,y,v: getClosestPoint((x,y),centers),
		terrain['tectonic plates'],
	)
centers = set(centers)
terrain['lattitude'] = keyMap(lambda x,y,v: y, Screen(GRID_SIZE))
terrain['tectonic plate move direction'] = scrMap(
	lambda v : move_directions[v],
	terrain['tectonic plates'],
) # int[0,359]
terrain['tectonic plate move amount'] = keyMap(
	lambda x,y,u,v : (getAngledDistance((x,y),u[x,y],v[x,y]) + GRID_SIZE) * MAX_THICKNESS/(2 * GRID_SIZE),
	terrain['tectonic plates'],
	terrain['tectonic plate move direction'],
) # int[0,255]
terrain['tectonic plate height'] = scrMap(
	lambda v : heights[v],
	terrain['tectonic plates'],
) # int[0,359]
move_dist_ranges: dict[Point,tuple[int,int]] = {}
for center in centers:
	move_dists = {dist for (x,y),dist in terrain['tectonic plate move amount'].enumerate() if terrain['tectonic plates'][x,y] == center}
	move_dist_ranges[center] = (max(move_dists),min(move_dists))
terrain['neighbors'] = keyMap(
	lambda x,y,v : get_neighbors(x,y,v),
	terrain['tectonic plates'],
)
terrain['is conjunction'] = scrMap(
	lambda v : len(v) > 1,
	terrain['neighbors'],
)
terrain['conjunctions'] = scrMap(
	lambda u,v : v if u else frozenset([]),
	terrain['is conjunction'],
	terrain['neighbors'],
)
terrain['is edge'] = scrMap(
	lambda v : len(v) == 2,
	terrain['neighbors'],
)
terrain['edges'] = scrMap(
	lambda u,v : v if u else frozenset([]),
	terrain['is edge'],
	terrain['neighbors'],
)
edges: set[frozenset[Point]] = {edge for edge in terrain['edges']}
edge_differences = {edge : 0 for edge in edges}
for edge in edges:
	c1,c2 = tuple(edge)
	edge_differences[edge] = abs(terrain['tectonic plate height'][c1] - terrain['tectonic plate height'][c2])
edge_boundary_types = {edge : {point : bool for point in edge} for edge in edges}


terrain['lattitude (colored)'] = scrMap(
	lambda v: (
		int(abs(v - GRID_SIZE/2) * 2 * MAX_COLOR/GRID_SIZE),
		int(abs(v - GRID_SIZE/2) * 2 * MAX_COLOR/GRID_SIZE),
		int(abs(v - GRID_SIZE/2) * 2 * MAX_COLOR/GRID_SIZE),
	),
	terrain['lattitude'],
)
terrain['tectonic plate move direction (colored)'] = scrMap(
	lambda u,v : (
		int((u - move_dist_ranges[v][1]) * MAX_COLOR/(move_dist_ranges[v][0] - move_dist_ranges[v][1])),
		int((u - move_dist_ranges[v][1]) * MAX_COLOR/(move_dist_ranges[v][0] - move_dist_ranges[v][1])),
		int((u - move_dist_ranges[v][1]) * MAX_COLOR/(move_dist_ranges[v][0] - move_dist_ranges[v][1])),
	),
	terrain['tectonic plate move amount'],
	terrain['tectonic plates'],
)
terrain['tectonic plate height (colored)'] = scrMap(
	lambda v : (v,v,v),
	terrain['tectonic plate height'],
)
terrain['tectonic plates (colored)'] = scrMap(
	lambda v : terrain['noise'][*v],
	terrain['tectonic plates'],
)
terrain['conjunctions (colored)'] = scrMap(
	lambda u : (
		sum(terrain['tectonic plates (colored)'][p][0] for p in u) % 256,
		sum(terrain['tectonic plates (colored)'][p][1] for p in u) % 256,
		sum(terrain['tectonic plates (colored)'][p][2] for p in u) % 256,
	),
	terrain['conjunctions'],
)
terrain['edges (colored)'] = scrMap(
	lambda u : (
		sum(terrain['tectonic plates (colored)'][p][0] for p in u) % 256,
		sum(terrain['tectonic plates (colored)'][p][1] for p in u) % 256,
		sum(terrain['tectonic plates (colored)'][p][2] for p in u) % 256,
	),
	terrain['edges'],
)

SCREEN_LAYOUT[0,0] = 'tectonic plate move direction (colored)'
SCREEN_LAYOUT[1,0] = 'edges (colored)'
SCREEN_LAYOUT[0,1] = 'tectonic plate height (colored)'
SCREEN_LAYOUT[1,1] = 'tectonic plates (colored)'

mapLayout(terrain)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()