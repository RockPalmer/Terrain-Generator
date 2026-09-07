import pygame,random
from noise import pnoise2
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
	radians,
)
from itertools import product

SCREEN_LAYOUT = {}
FINAL_SCREEN_LAYOUT = []

Color = tuple[int,int,int]
Point = tuple[int,int]
Vector = tuple[float,float]

'''
x == 0 -> W
y == 0 -> N
'''

def getAlternatePoints(point: Point) -> set[Point]:
	x,y = point
	return {
		(x - GRID_SIZE,y - GRID_SIZE),
		(x - GRID_SIZE,y),
		(x - GRID_SIZE,y + GRID_SIZE),
		(x,y - GRID_SIZE),
		(x,y),
		(x,y + GRID_SIZE),
		(x + GRID_SIZE,y - GRID_SIZE),
		(x + GRID_SIZE,y),
		(x + GRID_SIZE,y + GRID_SIZE),
	}
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
	return (
		int((p1[0] - p2[0]) * cos(theta) - (p1[1] - p2[1]) * sin(theta) + p2[0]),
		int((p1[0] - p2[0]) * sin(theta) + (p1[1] - p2[1]) * cos(theta) + p2[1]),
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
def getCorrectPoint(point: Point,guide: Point,trn: Screen) -> Point:
	sides = getSides(guide,trn)
	if len(sides) == 0: return point
	points = list(getAlternatePoints(point))
	dists = [getDistance(pt,guide) for pt in points]
	minDist = min(dists)
	minDistIndices = [i for i,dist in enumerate(dists) if dist == minDist]
	pts = [points[i] for i in minDistIndices]
	if len(pts) == 1: return pts[0]
	if pt in pts: return pt
	raise ValueError
def getAngledDistance(p1: Point,center: Point,theta: int,trn: Screen) -> int: # int[-63,63]
	p3 = rotate(
		getCorrectPoint(p1,center,trn),
		center,
		-radians(theta)
	)
	return p3[0] - center[0]
def getClosestPoint(point: Point,centers: list[Point]) -> Point:
	points = getAlternatePoints(point)
	point_pairs = list(product(points,set(centers)))
	distances = [getDistance(p,c) for p,c in point_pairs]
	min_dist = min(distances)
	index = distances.index(min_dist)
	return point_pairs[index][1]
def get_centroid(points: set[Point]) -> Point:
	return (
		sum(p[0] for p in points)/len(points),
		sum(p[1] for p in points)/len(points),
	)
def getDistance(p1: Point, p2: Point) -> float:
	return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
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
def getVectorBetween(p1: Point,p2: Point) -> Vector:
	return (
		p2[0] - p1[0],
		p2[1] - p1[1],
	)
def getPerpVector(v: Vector) -> Vector:
	x,y = v
	return (-y,x)
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
lean_directions: dict[Point,int] = {center : random.randint(0,MAX_ANGLE) for center in centers} # Point => int[0,359]
lean_strengths: dict[Point,int] = {center : random.randint(0,MAX_THICKNESS) for center in centers} # Point => int[0,255]

pnoise = {
	center : generateNoise(
		3*GRID_SIZE,
		3*GRID_SIZE,
		GRID_SIZE//(
			NUM_CONTINENTS >> 1
		),
		i
	) for i,center in enumerate(centers)
} # Point => float[-1,1]
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
terrain['tectonic plate thickness'] = keyMap(
	lambda x,y,v : int(
		(pnoise[v[x,y]][
			*[v + GRID_SIZE for v in getCorrectPoint((x,y),v[x,y],v)]
		] + 1) * MAX_THICKNESS/2
	),
	terrain['tectonic plates'],
) # int[0,255]
average_thickness: dict[Point,list[int]] = {} # Point => list[int[0,255]]
for x in range(GRID_SIZE):
	for y in range(GRID_SIZE):
		if terrain['tectonic plates'][x,y] not in average_thickness:
			average_thickness[terrain['tectonic plates'][x,y]] = []
		average_thickness[terrain['tectonic plates'][x,y]].append(terrain['tectonic plate thickness'][x,y])
average_thickness: dict[Point,float] = {center : sum(v)//len(v) for center,v in average_thickness.items()} # Point => int[0,255]
lean_inversions: dict[Point,bool] = {center : random.randint(0,1) == 1 for center in centers} # Point => bool
terrain['lean inverted'] = scrMap(
	lambda v : lean_inversions[v],
	terrain['tectonic plates'],
)
terrain['tectonic plate average thickness'] = scrMap(
	lambda v : average_thickness[v],
	terrain['tectonic plates'],
) # int[0,255]
terrain['tectonic plate lean height'] = scrMap(
	lambda v : lean_strengths[v],
	terrain['tectonic plates'],
) # int[0,255]
terrain['tectonic plate move direction'] = scrMap(
	lambda v : move_directions[v],
	terrain['tectonic plates'],
) # int[0,359]
terrain['tectonic plate move amount'] = keyMap(
	lambda x,y,u,v : (getAngledDistance((x,y),u[x,y],v[x,y],u) + GRID_SIZE) * MAX_THICKNESS/(2 * GRID_SIZE),
	terrain['tectonic plates'],
	terrain['tectonic plate move direction'],
) # int[0,255]
terrain['tectonic plate altitude bottom'] = scrMap(
	lambda a,bc : a + b if c else a + (MAX_THICKNESS - b),
	terrain['tectonic plate move amount'],
	terrain['tectonic plate lean height'],
	terrain['lean inverted'],
) # int[0,255] * int[0,255]
terrain['tectonic plate altitude top'] = scrMap(
	lambda a,b : a + b,
	terrain['tectonic plate altitude bottom'],
	terrain['tectonic plate thickness'],
) # 
move_dist_ranges: dict[Point,tuple[int,int]] = {}
lean_dist_ranges: dict[Point,tuple[int,int]] = {}
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
edge_altitude_tops: dict[frozenset[Point],dict[Point,list[int]]] = {edge : {point : [] for point in edge} for edge in edges}
edge_altitude_bottoms: dict[frozenset[Point],dict[Point,list[int]]] = {edge : {point : [] for point in edge} for edge in edges}
for x in range(GRID_SIZE):
	for y in range(GRID_SIZE):
		for edge in edges:
			if edge == terrain['edges'][x,y]:
				edge_altitude_tops[edge][terrain['tectonic plates'][x,y]].append(terrain['tectonic plate altitude top'][x,y])
				edge_altitude_bottoms[edge][terrain['tectonic plates'][x,y]].append(terrain['tectonic plate altitude bottom'][x,y])
edge_altitude_tops: dict[frozenset[Point],dict[Point,int]] = {edge : {point: sum(vals)//len(vals) for point,vals in cents.items} for edge,cents in edge_altitude_tops.items()}
edge_altitude_bottoms: dict[frozenset[Point],dict[Point,int]] = {edge : {point: sum(vals)//len(vals) for point,vals in cents.items} for edge,cents in edge_altitude_bottoms.items()}
edge_boundary_types = {}
for edge in edge_altitude_tops:
	cents = tuple(edge_altitude_tops[edge].keys())
	if len(cents) != 2: raise ValueError(len(cents))
	if edge_altitude_tops[edge][cents[0]] < edge_altitude_bottoms[edge][cents[1]]:
		edge_boundary_types[edge] = {
			cents[0] : False,
			cents[1] : True,
		}
	elif edge_altitude_tops[edge][cents[1]] < edge_altitude_bottoms[edge][cents[0]]:
		edge_boundary_types[edge] = {
			cents[1] : False,
			cents[0] : True,
		}
	else:
		edge_boundary_types[edge] = {
			cents[1] : True,
			cents[0] : True,
		}

terrain['edge altitude top'] = scrMap(
	lambda is_conjunction,conts,center : edge_altitude_tops[edge][center] if is_edge else getConjunctionHeight(const,edge_altitude_tops,center) if is_conjunction else 0,
	terrain['is conjunction'],
	terrain['conjunctions'],
	terrain['tectonic plates'],
)
terrain['edge altitude bottom'] = scrMap(
	lambda is_conjunction,conts,center : getConjunctionHeight(const,edge_altitude_bottoms,center) if is_conjunction else 0,
	terrain['is conjunction'],
	terrain['conjunctions'],
	terrain['tectonic plates'],
)

min_alt_bot = min(v for v in terrain['tectonic plate altitude bottom'])
max_alt_bot = max(v for v in terrain['tectonic plate altitude bottom'])
min_alt_top = min(v for v in terrain['tectonic plate altitude top'])
max_alt_top = max(v for v in terrain['tectonic plate altitude top'])

terrain['lattitude (colored)'] = scrMap(
	lambda v: (
		int(abs(v - GRID_SIZE/2) * 2 * MAX_COLOR/GRID_SIZE),
		int(abs(v - GRID_SIZE/2) * 2 * MAX_COLOR/GRID_SIZE),
		int(abs(v - GRID_SIZE/2) * 2 * MAX_COLOR/GRID_SIZE),
	),
	terrain['lattitude'],
)
terrain['tectonic plate thickness (colored)'] = scrMap(
	lambda v : (v,v,v),
	terrain['tectonic plate thickness'],
)
terrain['tectonic plate average thickness (colored)'] = scrMap(
	lambda v : (
		int((v + 1) * 127),
		int((v + 1) * 127),
		int((v + 1) * 127),
	),
	terrain['tectonic plate average thickness'],
)
terrain['tectonic plate lean height (colored)'] = scrMap(
	lambda v : (
		int(v * MAX_COLOR/MAX_THICKNESS),
		int(v * MAX_COLOR/MAX_THICKNESS),
		int(v * MAX_COLOR/MAX_THICKNESS),
	),
	terrain['tectonic plate lean height'],
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
terrain['tectonic plate altitude bottom (colored)'] = scrMap(
	lambda v : (
		int((v - min_alt_bot) * MAX_COLOR/(max_alt_bot - min_alt_bot)),
		int((v - min_alt_bot) * MAX_COLOR/(max_alt_bot - min_alt_bot)),
		int((v - min_alt_bot) * MAX_COLOR/(max_alt_bot - min_alt_bot)),
	),
	terrain['tectonic plate altitude bottom'],
)
terrain['tectonic plate altitude top (colored)'] = scrMap(
	lambda v : (
		int((v - min_alt_top) * MAX_COLOR/(max_alt_top - min_alt_top)),
		int((v - min_alt_top) * MAX_COLOR/(max_alt_top - min_alt_top)),
		int((v - min_alt_top) * MAX_COLOR/(max_alt_top - min_alt_top)),
	),
	terrain['tectonic plate altitude top'],
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

SCREEN_LAYOUT[0,0] = 'tectonic plates (colored)'
SCREEN_LAYOUT[1,0] = 'tectonic plate move direction (colored)'
SCREEN_LAYOUT[0,1] = 'tectonic plate thickness (colored)'
SCREEN_LAYOUT[1,1] = 'tectonic plate lean height (colored)'
SCREEN_LAYOUT[2,0] = 'tectonic plate altitude bottom (colored)'
SCREEN_LAYOUT[2,1] = 'tectonic plate altitude top (colored)'

mapLayout(terrain)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()