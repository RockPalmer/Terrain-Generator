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

def getMaxX() -> int:
	global SCREEN_LAYOUT

	return max(x for x,_ in SCREEN_LAYOUT.keys())
def getMaxY() -> int:
	global SCREEN_LAYOUT

	return max(y for _,y in SCREEN_LAYOUT.keys())
def mapLayout(trn: dict[str,Screen]) -> None:
	global SCREEN_LAYOUT,FINAL_SCREEN_LAYOUT

	MAX_X = (getMaxX() + 1) * GRID_SIZE
	MAX_Y = (getMaxY() + 1) * GRID_SIZE

	nmap = [[None for i in range(MAX_Y)] for j in range(MAX_X)]

	for (x,y),k in SCREEN_LAYOUT.items():
		for i in range(GRID_SIZE):
			for j in range(GRID_SIZE):
				nmap[x * GRID_SIZE + i][y * GRID_SIZE + j] = trn[k][i,j]
	FINAL_SCREEN_LAYOUT = nmap

Color = tuple[int,int,int]
Point = tuple[int,int]

def rotate(p1: Point,p2: Point,theta: float) -> tuple[int,int]:
	return (
		int((p1[0] - p2[0]) * cos(theta) - (p1[1] - p2[1]) * sin(theta) + p2[0]),
		int((p1[0] - p2[0]) * sin(theta) + (p1[1] - p2[1]) * cos(theta) + p2[1]),
	)
def get_angled_distance(p1: Point,p2: Point,theta: int) -> int:
	p3 = rotate(p1,p2,-radians(theta))
	return p3[0] - p2[0]

# Grid settings
GRID_SIZE: int = 64
CELL_SIZE: int = 10  # Size of each square in pixels

LENGTH: int = GRID_SIZE * CELL_SIZE

NUM_CONTINENTS: int = 7

pygame.init()

def drawMap() -> None:
	global pygame,FINAL_SCREEN_LAYOUT

	window = pygame.display.set_mode((
		(getMaxX() + 1)*LENGTH,
		(getMaxY() + 1)*LENGTH,
	))
	pygame.display.set_caption("Window")

	for x in range(len(FINAL_SCREEN_LAYOUT)):
		for y in range(len(FINAL_SCREEN_LAYOUT[x])):
			rect = pygame.Rect(
				x * CELL_SIZE,
				y * CELL_SIZE,
				CELL_SIZE,
				CELL_SIZE,
			)
			pygame.draw.rect(window,FINAL_SCREEN_LAYOUT[x][y],rect)
	pygame.display.flip()

terrain: dict[str,Screen] = {}
terrain['lattitude']: Screen = Screen(GRID_SIZE)
terrain['tectonic plates']: Screen = Screen(GRID_SIZE)
terrain['tectonic plate direction']: Screen = Screen(GRID_SIZE)
terrain['pixel map']: Screen = Screen(GRID_SIZE)

terrain['pixel map']: Screen = keyMap(lambda x,y,v : (
	random.randint(0,255),
	random.randint(0,255),
	random.randint(0,255),
),terrain['pixel map'])

continent_centers: list[Point] = []
continent_directions: set[float] = set()
while len(continent_centers) < NUM_CONTINENTS:
	c: Point = (
		random.randint(0,GRID_SIZE - 1),
		random.randint(0,GRID_SIZE - 1),
	)
	if c not in continent_centers:
		continent_centers.append(c)
continent_centers = list(continent_centers)

def get_distance(p1: Point, p2: Point) -> float:
	return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
def get_closest_point(point: Point,centers: list[Point]):
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
for center in continent_centers:
	terrain['tectonic plates'][center] = center
terrain['tectonic plates'] = keyMap(
	lambda x,y,_: get_closest_point((x,y),continent_centers),
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
		lambda x,y,v: get_closest_point((x,y),continent_centers),
		terrain['tectonic plates'],
	)
terrain['tectonic plates (colored)'] = scrMap(
	lambda v : terrain['pixel map'][*v],
	terrain['tectonic plates'],
)

terrain['lattitude'] = keyMap(lambda x,y,v: y, terrain['lattitude'])
terrain['lattitude (colored)'] = scrMap(
	lambda v: int(abs(v - GRID_SIZE/2) * 2 * 255/GRID_SIZE),
	terrain['lattitude'],
)
terrain['lattitude (colored)'] = scrMap(lambda v: (v,v,v), terrain['lattitude (colored)'])
centers = terrain['tectonic plates'].aggregate(set)
directions = {center : random.randint(0,359) for center in centers}
terrain['tectonic plate directions'] = scrMap(
	lambda v : directions[v],
	terrain['tectonic plates'],
)
speed = {center : random.randint(0,10) for center in centers}
terrain['tectonic plate speeds'] = scrMap(
	lambda v : speeds[v],
	terrain['tectonic plates'],
)
terrain['distance in direction'] = keyMap(
	lambda x,y,u,v : get_angled_distance((x,y),u[x,y],v[x,y]),
	terrain['tectonic plates'],
	terrain['tectonic plate directions']
)
max_dist = max(terrain['distance in direction'].aggregate(set))
min_dist = min(terrain['distance in direction'].aggregate(set))
terrain['distance in direction (colored)'] = scrMap(
	lambda v : (
		int((v - min_dist) * 255/(max_dist - min_dist)),
		int((v - min_dist) * 255/(max_dist - min_dist)),
		int((v - min_dist) * 255/(max_dist - min_dist)),
	),
	terrain['distance in direction'],
)

SCREEN_LAYOUT[0,0] = 'tectonic plates (colored)'
SCREEN_LAYOUT[1,0] = 'distance in direction (colored)'

mapLayout(terrain)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()