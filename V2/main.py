import pygame,random
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

SCREEN_LAYOUT = {}
FINAL_SCREEN_LAYOUT = []

Color = tuple[int,int,int]
Point = tuple[int,int]
Vector = tuple[float,float]

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
def rotate(p1: Point,p2: Point,theta: float) -> tuple[int,int]:
	return (
		int((p1[0] - p2[0]) * cos(theta) - (p1[1] - p2[1]) * sin(theta) + p2[0]),
		int((p1[0] - p2[0]) * sin(theta) + (p1[1] - p2[1]) * cos(theta) + p2[1]),
	)
def get_angled_distance(p1: Point,p2: Point,theta: int) -> int:
	p3 = rotate(p1,p2,-radians(theta))
	return p3[0] - p2[0]
def get_closest_point(point: Point,centers: list[Point]) -> Point:
	x,y = point
	distances = [get_distance((x,y),(a,b)) for a,b in centers]
	min_dist = min(distances)
	index = distances.index(min_dist)
	return centers[index]
def get_centroid(points: set[Point]) -> Point:
	return (
		sum(p[0] for p in points)/len(points),
		sum(p[1] for p in points)/len(points),
	)
def get_distance(p1: Point, p2: Point) -> float:
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
	nvalues = tuple(values)
	results = set()
	for i,v1 in enumerate(nvalues):
		for v2 in nvalues[i + 1:]:
			results.add(frozenset([v1,v2]))
	return results

# Grid settings
GRID_SIZE: int = 64
CELL_SIZE: int = 5  # Size of each square in pixels
MAX_ANGLE = 359
MAX_COLOR = 255
MAX_THICKNESS = 255
MAX_LEAN_STRENGTH = 255

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
move_directions: set[int] = {center : random.randint(0,MAX_ANGLE) for center in centers}
lean_directions: set[int] = {center : random.randint(0,MAX_ANGLE) for center in centers}
lean_strengths: set[int] = {center : random.randint(0,MAX_LEAN_STRENGTH) for center in centers}
thickness: set[int] = {center : random.randint(0,MAX_THICKNESS) for center in centers}

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
)
terrain['tectonic plates'] = keyMap(
	lambda x,y,_: get_closest_point((x,y),centers),
	terrain['tectonic plates'],
)
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
		lambda x,y,v: get_closest_point((x,y),centers),
		terrain['tectonic plates'],
	)
centers = set(centers)
terrain['lattitude'] = keyMap(lambda x,y,v: y, Screen(GRID_SIZE))
terrain['tectonic plate thickness'] = scrMap(
	lambda v : thickness[v],
	terrain['tectonic plates'],
)
terrain['tectonic plate move directions'] = scrMap(
	lambda v : move_directions[v],
	terrain['tectonic plates'],
)
terrain['tectonic plate lean directions'] = scrMap(
	lambda v : lean_directions[v],
	terrain['tectonic plates'],
)
terrain['tectonic plate move directions (colored)'] = keyMap(
	lambda x,y,u,v : get_angled_distance((x,y),u[x,y],v[x,y]),
	terrain['tectonic plates'],
	terrain['tectonic plate move directions'],
)
terrain['tectonic plate lean directions (colored)'] = keyMap(
	lambda x,y,u,v : get_angled_distance((x,y),u[x,y],v[x,y]),
	terrain['tectonic plates'],
	terrain['tectonic plate lean directions'],
)
move_dist_ranges: dict[Point,tuple[int,int]] = {}
lean_dist_ranges: dict[Point,tuple[int,int]] = {}
for center in centers:
	move_dists = {dist for (x,y),dist in terrain['tectonic plate move directions (colored)'].enumerate() if terrain['tectonic plates'][x,y] == center}
	lean_dists = {dist for (x,y),dist in terrain['tectonic plate lean directions (colored)'].enumerate() if terrain['tectonic plates'][x,y] == center}
	move_dist_ranges[center] = (max(move_dists),min(move_dists))
	lean_dist_ranges[center] = (max(lean_dists),min(lean_dists))
terrain['neighbors'] = keyMap(
	lambda x,y,v : get_neighbors(x,y,v),
	terrain['tectonic plates'],
)
terrain['edges'] = scrMap(
	lambda v : v if len(v) > 1 else frozenset([]),
	terrain['neighbors'],
)
terrain['true edges'] = scrMap(
	lambda v : v if len(v) == 2 else frozenset([]),
	terrain['neighbors'],
)
edges: set[frozenset[Point]] = set()
for neighbor_set in terrain['neighbors']:
	match len(neighbor_set):
		case 1: edges.add(neighbor_set)
		case 0: pass
		case _: edges |= getPairs(neighbor_set)
edges: set[tuple[Point,Point]] = {tuple(edge) for edge in edges}

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
terrain['tectonic plate lean directions (colored)'] = scrMap(
	lambda u,v : (
		int((u - lean_dist_ranges[v][1]) * MAX_COLOR/(lean_dist_ranges[v][0] - lean_dist_ranges[v][1])),
		int((u - lean_dist_ranges[v][1]) * MAX_COLOR/(lean_dist_ranges[v][0] - lean_dist_ranges[v][1])),
		int((u - lean_dist_ranges[v][1]) * MAX_COLOR/(lean_dist_ranges[v][0] - lean_dist_ranges[v][1])),
	),
	terrain['tectonic plate lean directions (colored)'],
	terrain['tectonic plates'],
)
terrain['tectonic plate move directions (colored)'] = scrMap(
	lambda u,v : (
		int((u - move_dist_ranges[v][1]) * MAX_COLOR/(move_dist_ranges[v][0] - move_dist_ranges[v][1])),
		int((u - move_dist_ranges[v][1]) * MAX_COLOR/(move_dist_ranges[v][0] - move_dist_ranges[v][1])),
		int((u - move_dist_ranges[v][1]) * MAX_COLOR/(move_dist_ranges[v][0] - move_dist_ranges[v][1])),
	),
	terrain['tectonic plate move directions (colored)'],
	terrain['tectonic plates'],
)
terrain['tectonic plates (colored)'] = scrMap(
	lambda v : terrain['noise'][*v],
	terrain['tectonic plates'],
)
terrain['edges (colored)'] = scrMap(
	lambda u : (
		sum(terrain['tectonic plates (colored)'][p][0] for p in u) % 256,
		sum(terrain['tectonic plates (colored)'][p][1] for p in u) % 256,
		sum(terrain['tectonic plates (colored)'][p][2] for p in u) % 256,
	),
	terrain['edges'],
)

SCREEN_LAYOUT[0,0] = 'tectonic plates (colored)'
SCREEN_LAYOUT[1,0] = 'tectonic plate move directions (colored)'
SCREEN_LAYOUT[1,1] = 'tectonic plate lean directions (colored)'
SCREEN_LAYOUT[0,1] = 'tectonic plate thickness (colored)'

mapLayout(terrain)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()