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
IntVector = tuple[int,int]
FloatVector = tuple[float,float]
Vector = IntVector | FloatVector

# (int,int|float,int,int) -> (Point => float[-1,1])
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
def dot(v1: Vector,v2: Vector) -> int|float|Vector:
	if isinstance(v1,tuple) and isinstance(v2,tuple): return v1[0] * v2[0] + v1[1] * v2[1]
	if isinstance(v1,tuple) and not isinstance(v2,tuple): return dot(v2,v1)
	return (v1 * v2[0],v1 * v2[1])
def proj(a: Vector,b: Vector) -> Vector:
	return dot(
		dot(a,b)/dot(b,b),
		b
	)
def angleToVector(angle: int) -> FloatVector:
	return (
		cos(radians(angle)),
		sin(radians(angle)),
	)
def magnitude(v: Vector) -> int|float:
	return (v[0]**2 + v[1]**2)**0.5
def unitVector(v: Vector) -> Vector:
	return (
		v[0] / magnitude(v),
		v[1] / magnitude(v),
	)
def smudge(point: Point,trn: Screen,res: int) -> Screen:
	screen = Screen(GRID_SIZE)
	x,y = point
	points = set()
	for i in range(-res,res + 1):
		for j in range(-res,res + 1):
			points.add((x + i,y + j))
	values = []
	for i,j in points:
		if i >= 0 and j >= 0 and i < GRID_SIZE and j < GRID_SIZE:
			values.append(trn[i,j])
	return sum(values)/len(values)

# Grid settings
GRID_SIZE: int = 256
CELL_SIZE: int = 3  # Size of each square in pixels
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
heights: dict[Point,int] = {center : random.randint(0,MAX_THICKNESS//8) for center in centers} # Point => int[0,255]

pnoise = {}
for i,center in enumerate(centers):
	pnoise[center] = perlinNoise(
		size = GRID_SIZE,
		seed = random.randint(0,255),
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
) # int[0,255]
terrain['tectonic plate thickness'] = keyMap(
	lambda x,y,v : int((pnoise[v[x,y]][x,y] + 1) * MAX_THICKNESS/2),
	terrain['tectonic plates'],
) # int[0,255]
terrain['tectonic plate top'] = terrain['tectonic plate height'] + terrain['tectonic plate thickness'] # int[0,510]
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
edges: set[frozenset[Point]] = {edge for edge in terrain['edges'] if len(edge) > 0}
edge_boundary_is_overlapping: dict[tuple[Point,Point],dict[Point,bool]] = {edge : {point : False for point in edge} for edge in edges}
for edge in edges:
	c1,c2 = tuple(edge)
	if terrain['tectonic plate top'][c1] < terrain['tectonic plate top'][c2]:
		edge_boundary_is_overlapping[edge][c1] = False
		edge_boundary_is_overlapping[edge][c2] = True
	elif terrain['tectonic plate top'][c1] > terrain['tectonic plate top'][c2]:
		edge_boundary_is_overlapping[edge][c1] = True
		edge_boundary_is_overlapping[edge][c2] = False
	else:
		edge_boundary_is_overlapping[edge][c1] = True
		edge_boundary_is_overlapping[edge][c2] = True
edge_boundary_overlaps: dict[frozenset[Point],int] = {edge : 0 for edge in edges}
for edge in edges:
	c1,c2 = tuple(edge)
	if terrain['tectonic plate top'][c1] < terrain['tectonic plate top'][c2]:
		edge_boundary_overlaps[edge] = abs(terrain['tectonic plate top'][c2] - terrain['tectonic plate height'][c1]) # int[0,510]
	elif terrain['tectonic plate top'][c1] > terrain['tectonic plate top'][c2]:
		edge_boundary_overlaps[edge] = abs(terrain['tectonic plate top'][c1] - terrain['tectonic plate height'][c2]) # int[0,510]
	else:
		edge_boundary_overlaps[edge] = min(
			terrain['tectonic plate thickness'][c1],
			terrain['tectonic plate thickness'][c2],
		) # int[0,255]
edge_boundary_convergence: dict[frozenset[Point],float] = {edge : 0 for edge in edges}
edge_boundary_strikeslip: dict[frozenset[Point],float] = {edge : 0 for edge in edges}
for edge in edges:
	c1,c2 = tuple(edge)
	v12 = unitVector(getVector(c1,c2))
	v21 = unitVector(getVector(c2,c1))
	v1 = angleToVector(terrain['tectonic plate move direction'][c1])
	v2 = angleToVector(terrain['tectonic plate move direction'][c2])
	pv12 = unitVector(proj(v1,v12))
	pv21 = unitVector(proj(v2,v21))
	sv12 = unitVector(proj(v1,v2))
	sv21 = unitVector(proj(v2,v1))
	edge_boundary_convergence[edge] = (dot(pv12,v12) + dot(pv21,v21)) / 2
	edge_boundary_strikeslip[edge] = (dot(v1,sv12) + dot(v2,sv21)) / 2
terrain['closest neighbor'] = keyMap(
	lambda x,y,v : getClosestPoint((x,y),list(centers - {v[x,y]})),
	terrain['tectonic plates'],
)
terrain['edge is overlapping'] = scrMap(
	lambda u,v : edge_boundary_is_overlapping[frozenset([u,v])][v],
	terrain['closest neighbor'],
	terrain['tectonic plates'],
)
terrain['edge overlaps'] = scrMap(
	lambda u,v : edge_boundary_overlaps[frozenset([u,v])],
	terrain['closest neighbor'],
	terrain['tectonic plates'],
)
terrain['edge boundary convergence'] = scrMap(
	lambda u,v : int((edge_boundary_convergence[frozenset([u,v])] + 1) * MAX_THICKNESS/2),
	terrain['closest neighbor'],
	terrain['tectonic plates'],
)
terrain['edge boundary strikeslip'] = scrMap(
	lambda u,v : int((edge_boundary_strikeslip[frozenset([u,v])] + 1) * MAX_THICKNESS/2),
	terrain['closest neighbor'],
	terrain['tectonic plates'],
)
terrain['base altitude'] = scrMap(
	lambda a,b,c : (a + b) / 2 + c,
	terrain['edge overlaps'],
	terrain['edge boundary convergence'],
	terrain['tectonic plate top'],
)
terrain['neighbors 2'] = keyMap(
	lambda x,y,v : get_neighbors(x,y,v),
	terrain['closest neighbor'],
)
terrain['is conjunction 2'] = scrMap(
	lambda v : len(v) > 1,
	terrain['neighbors 2'],
)
terrain['base altitude'] = keyMap(
	lambda x,y,u,v : u[x,y] if not v[x,y] else smudge((x,y),u,4),
	terrain['base altitude'],
	terrain['is conjunction 2'],
)
terrain['base altitude'] = scrMap(
	lambda v : int(v),
	terrain['base altitude'],
)
max_base_altitiude = max({v for v in terrain['base altitude']})
top_layer = perlinNoise(
	size = GRID_SIZE,
	seed = random.randint(0,255),
)
terrain['top layer'] = keyMap(
	lambda x,y,v : top_layer[x,y],
	Screen(GRID_SIZE),
)

terrain['altitude'] = terrain['base altitude']
max_altitiude = max({v for v in terrain['altitude']})

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
	lambda v : terrain['noise'][v],
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
terrain['tectonic plate thickness (colored)'] = scrMap(
	lambda v : (
		v * MAX_COLOR/MAX_THICKNESS,
		v * MAX_COLOR/MAX_THICKNESS,
		v * MAX_COLOR/MAX_THICKNESS,
	),
	terrain['tectonic plate thickness'],
)
terrain['closest neighbor (colored)'] = scrMap(
	lambda v : terrain['noise'][v],
	terrain['closest neighbor'],
)
terrain['edge is overlapping (colored)'] = scrMap(
	lambda v : (MAX_COLOR,MAX_COLOR,MAX_COLOR) if v else (0,0,0),
	terrain['edge is overlapping'],
)
terrain['edge overlaps (colored)'] = scrMap(
	lambda v : (
		int(v * MAX_COLOR/(2*MAX_THICKNESS)),
		int(v * MAX_COLOR/(2*MAX_THICKNESS)),
		int(v * MAX_COLOR/(2*MAX_THICKNESS)),
	),
	terrain['edge overlaps'],
)
terrain['edge boundary convergence (colored)'] = scrMap(
	lambda v : (
		int(v * MAX_COLOR/MAX_THICKNESS),
		int(v * MAX_COLOR/MAX_THICKNESS),
		int(v * MAX_COLOR/MAX_THICKNESS),
	),
	terrain['edge boundary convergence'],
)
terrain['edge boundary strikeslip (colored)'] = scrMap(
	lambda v : (
		int(v * MAX_COLOR/MAX_THICKNESS),
		int(v * MAX_COLOR/MAX_THICKNESS),
		int(v * MAX_COLOR/MAX_THICKNESS),
	),
	terrain['edge boundary strikeslip'],
)
terrain['base altitude (colored)'] = scrMap(
	lambda v : (
		int(v * (MAX_COLOR/max_base_altitiude)),
		int(v * (MAX_COLOR/max_base_altitiude)),
		int(v * (MAX_COLOR/max_base_altitiude)),
	),
	terrain['base altitude'],
)
terrain['altitude (colored)'] = scrMap(
	lambda v : (
		int(v * (MAX_COLOR/max_altitiude)),
		int(v * (MAX_COLOR/max_altitiude)),
		int(v * (MAX_COLOR/max_altitiude)),
	),
	terrain['altitude'],
)


#SCREEN_LAYOUT[0,0] = 'tectonic plate move direction (colored)'
#SCREEN_LAYOUT[1,0] = 'edges (colored)'
#SCREEN_LAYOUT[0,1] = 'tectonic plate height (colored)'
#SCREEN_LAYOUT[1,1] = 'tectonic plates (colored)'
#SCREEN_LAYOUT[2,0] = 'closest neighbor (colored)'
#SCREEN_LAYOUT[2,1] = 'tectonic plate thickness (colored)'
#SCREEN_LAYOUT[3,0] = 'edge boundary convergence (colored)'
#SCREEN_LAYOUT[3,1] = 'edge boundary strikeslip (colored)'
#SCREEN_LAYOUT[4,0] = 'edge overlaps (colored)'
#SCREEN_LAYOUT[4,1] = 'base altitude (colored)'
SCREEN_LAYOUT[0,0] = 'altitude (colored)'

mapLayout(terrain)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()