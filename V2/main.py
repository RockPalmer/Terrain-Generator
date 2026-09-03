import pygame,random
from Screen import (
	scrMap,
	keyMap,
	Screen,
)
from bidict import bidict

Color = tuple[int,int,int]
Point = tuple[int,int]
Angle = int

# Grid settings
GRID_SIZE: int = 64
CELL_SIZE: int = 10  # Size of each square in pixels

def Color_to_int(value: Color) -> int:
	return value[0] << 16 | value[1] << 8 | value[2]
def Point_to_int(value: Point) -> int:
	return value[0] * GRID_SIZE + value[1]

LENGTH: int = GRID_SIZE * CELL_SIZE

NUM_CONTINENTS: int = 7

pygame.init()
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

def is_fault_line(x,y,v):
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
	for x,y in points:
		if x >= 0 and y >= 0 and x < v.size and y < v.size:
			values.add(v[x,y])
	return len(values) > 1
def get_corner(x,y,v):
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
	pcount = 0
	values = set()
	for x,y in points:
		if x >= 0 and y >= 0 and x < v.size and y < v.size:
			pcount += 1
			values.add(v[x,y])
	if len(values) > 2 or (
		len(values) > 1 and
		pcount < len(points)
	):
		return values
	return set()

terrain['fault lines'] = keyMap(
	lambda x,y,v: is_fault_line(x,y,v),
	terrain['tectonic plates'],
)
terrain['fault lines (colored)'] = scrMap(
	lambda v: (255,255,255) if v else (0,0,0),
	terrain['fault lines']
)
terrain['tectonic plate edges'] = scrMap(
	lambda x,y: y if x else None,
	terrain['fault lines'],
	terrain['tectonic plates'],
)
terrain['tectonic plate edges (colored)'] = scrMap(
	lambda v : terrain['pixel map'][v] if v is not None else (0,0,0),
	terrain['tectonic plate edges'],
)
terrain['tectonic plate directions'] = scrMap(
	lambda v : int((v[0] * GRID_SIZE + v[1]) * 360/GRID_SIZE**2),
	terrain['tectonic plates'],
)
terrain['tectonic plate corners'] = keyMap(
	lambda x,y,v : get_corner(x,y,v),
	terrain['tectonic plates']
)
terrain['tectonic plate corners (colored)'] = keyMap(
	lambda x,y,u,v : u[x,y] if len(v[x,y]) > 0 else (0,0,0),
	terrain['tectonic plates (colored)'],
	terrain['tectonic plate corners'],
)
terrain['tectonic plate corners unique'] = 

corners = set()
for x in range(GRID_SIZE):
	for y in range(GRID_SIZE):
		if terrain['tectonic plate corners'][x,y] is not None:
			corners

window = pygame.display.set_mode((2*LENGTH,LENGTH))
pygame.display.set_caption("64x64 Random Colored Squares")

# Draw the grid
for y in range(GRID_SIZE):
	for x in range(GRID_SIZE):
		rect = pygame.Rect(
			x * CELL_SIZE,
			y * CELL_SIZE,
			CELL_SIZE,
			CELL_SIZE,
		)
		pygame.draw.rect(window,terrain['tectonic plate corners (colored)'][x,y],rect)
for y in range(GRID_SIZE):
	for x in range(GRID_SIZE):
		rect = pygame.Rect(
			(x + GRID_SIZE) * CELL_SIZE,
			y * CELL_SIZE,
			CELL_SIZE,
			CELL_SIZE,
		)
		pygame.draw.rect(window,terrain['tectonic plates (colored)'][x,y],rect)

pygame.display.flip()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()