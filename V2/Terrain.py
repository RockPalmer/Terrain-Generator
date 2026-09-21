import pygame,random,json
from perlin import perlin4
from Screen import (
	scrMap,
	keyMap,
	ifMap,
	Screen,
)
from math import (
	cos,
	sin,
	tan,
	tau,
	pi,
	e,
	floor,
	ceil,
)
from pathlib import Path
from numpy import (
	array,
	dot,
)
from numpy.linalg import norm
from itertools import product
from functools import reduce
from operator import or_

SCREEN_LAYOUT = {}
FINAL_SCREEN_LAYOUT = []

Color = tuple[int,int,int]
Point = tuple[int,int]

COLOR_SCALE = [
	(255,i,0) for i in range(0,255)
] + [
	(255 - i,255,0) for i in range(0,255)
] + [
	(0,255,i) for i in range(0,255)
] + [
	(0,255 - i,255) for i in range(0,255)
] + [
	(i,0,255) for i in range(0,255)
] + [
	(255,0,255 - i) for i in range(0,255)
]

GRID_SIZE: int = 256
CELL_SIZE: int = 2
OVERWORLD_SURFACE_RANGE: tuple[int,int] = (0,256)
OVERWORLD_DEPTH_RANGE: tuple[int,int] = (0,256)
MIDWORLD_SURFACE_RANGE: tuple[int,int] = (0,256)
MIDWORLD_DEPTH_RANGE: tuple[int,int] = (0,256)
OVERWORLD_SEA_LEVEL_FACTOR = 0.51
MIDWORLD_SEA_LEVEL_FACTOR = 0.4
SNOW_LEVEL_FACTOR = 0.7
TERRAIN_NOISE_SCALE: int = 1
TERRAIN_NOISE_OCTAVES: int = 8
NOISE_SEED: int = 0
AXIS_TILT: float = 23.44 * tau/360
HUMIDITY_SMUDGE_RADIUS: int = 7
UI_PANEL_WIDTH: int = 200
UI_PANEL_MARGIN: int = 20
NUM_CONTINENTS: int = 12
NUM_CONTINENT_RUNS: int = 5
UI_RECT_COLOR: Color = (255,198,183)
MAX_COLOR_INTEGER: int = 255**3 - 1
ADJUSTED_EDGE_AMPLITUDE: int = 32
MAX_SPEED: int = 20
MAX_POINT_INTEGER: int = GRID_SIZE**2 - 1
OVERWORLD_DEPTH_OVERLAP_HEIGHT_FACTOR: float = 0.5
MIDWORLD_WATER_FACTOR: float = 1.5
MIDWORLD_ALTITUDE_OVERLAP_HEIGHT_FACTOR: float = OVERWORLD_DEPTH_OVERLAP_HEIGHT_FACTOR
OVERWORLD_CLOUD_DENSITY_FACTOR: float = 0.1
OVERWORLD_CLOUD_DENSITY_STRENGTH: int = 20

OVERWORLD_SURFACE_MIN: int = OVERWORLD_SURFACE_RANGE[0]
OVERWORLD_SURFACE_MAX: int = OVERWORLD_SURFACE_RANGE[1] - 1
OVERWORLD_DEPTH_MIN: int = OVERWORLD_DEPTH_RANGE[0]
OVERWORLD_DEPTH_MAX: int = OVERWORLD_DEPTH_RANGE[1] - 1
MIDWORLD_SURFACE_MIN: int = MIDWORLD_SURFACE_RANGE[0]
MIDWORLD_SURFACE_MAX: int = MIDWORLD_SURFACE_RANGE[1] - 1
MIDWORLD_DEPTH_MIN: int = MIDWORLD_DEPTH_RANGE[0]
MIDWORLD_DEPTH_MAX: int = MIDWORLD_DEPTH_RANGE[1] - 1
OVERWORLD_SEA_LEVEL: float = OVERWORLD_SEA_LEVEL_FACTOR * OVERWORLD_SURFACE_MAX
MIDWORLD_SEA_LEVEL: float = MIDWORLD_SEA_LEVEL_FACTOR * MIDWORLD_SURFACE_MAX
DIAMETER: float = GRID_SIZE/pi
RADIUS: float = DIAMETER/2

OVERWORLD_CLOUD_DENSITY_WIDTH: float = GRID_SIZE * OVERWORLD_CLOUD_DENSITY_FACTOR
OVERWORLD_DEPTH_OVERLAP_HEIGHT: float = OVERWORLD_DEPTH_OVERLAP_HEIGHT_FACTOR * OVERWORLD_DEPTH_MAX
MIDWORLD_ALTITUDE_OVERLAP_HEIGHT: float = MIDWORLD_ALTITUDE_OVERLAP_HEIGHT_FACTOR * MIDWORLD_SURFACE_MAX
SNOW_LEVEL: float = OVERWORLD_SURFACE_MAX * SNOW_LEVEL_FACTOR
OVERWORLD_THICKNESS_MAX: float = OVERWORLD_SURFACE_MAX + OVERWORLD_DEPTH_MAX

itera = 0

float_n1_1 = float

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
def flm(value) -> str:
	if isinstance(value,float):
		return str(value).replace('.','-')
	return str(value)
def perlinNoise(seed: int|float = 0,scale: int = 1,octaves: int = 1) -> Screen[float]:
	print('generating perlin noise...')
	"""
	Generate seamless wrapping 2D Perlin noise using 4D Perlin.

	Returns:
	    list[list[float]]: values approximately [-1, 1]
	"""
	filename = Path(f"pnoise_{flm(GRID_SIZE)}_{flm(seed)}_{flm(scale)}_{flm(octaves)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y : values[x][y],
			GRID_SIZE,
		)
	rng = random.Random(seed)
	seed_offset = rng.random() * 10000.0
	noise_map = Screen(GRID_SIZE)
	for y in range(GRID_SIZE):
		row = []
		for x in range(GRID_SIZE):
			value = 0.0
			amplitude = 1.0
			frequency = 1.0
			amplitude_sum = 0.0
			for octave in range(octaves):
				# Map grid coordinates onto a torus
				angle_x = 2.0 * pi * x / GRID_SIZE
				angle_y = 2.0 * pi * y / GRID_SIZE
				nx = cos(angle_x) * scale * frequency
				ny = sin(angle_x) * scale * frequency
				nz = cos(angle_y) * scale * frequency
				nw = sin(angle_y) * scale * frequency + seed_offset
				sample = perlin4(nx,ny,nz,nw)
				value += sample * amplitude
				amplitude_sum += amplitude
				amplitude *= 0.5
				frequency *= 2.0
			noise_map[y,x] = value / amplitude_sum
	values = [[noise_map[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return noise_map
def pointToColor(point: Point) -> Color:
	value = round((point[0] * 255 + point[1]) * MAX_COLOR_INTEGER/MAX_POINT_INTEGER)
	return (
		value & 255,
		(value >> 8) & 255,
		(value >> 16) & 255,
	)
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
def getDistance(p1: Point, p2: Point) -> float:
	dx = abs(p1[0] - p2[0])
	dy = abs(p1[1] - p2[1])
	if dx > GRID_SIZE / 2: dx = GRID_SIZE - dx
	if dy > GRID_SIZE / 2: dy = GRID_SIZE - dy
	return (dx**2 + dy**2)**0.5
def getVector(p1: Point,p2: Point) -> array:
	return array([
		((p2[0] - p1[0] + GRID_SIZE//2) % GRID_SIZE) - GRID_SIZE//2,
		((p2[1] - p1[1] + GRID_SIZE//2) % GRID_SIZE) - GRID_SIZE//2,
	])
def getCurrentTilt(day: int) -> float:
	min_tilt = -AXIS_TILT
	max_tilt = AXIS_TILT
	return min_tilt + day * (max_tilt - min_tilt)/365
def lattitudeToAngle(latt: int) -> float:
	return latt * tau/GRID_SIZE
def randPoint(rng) -> Point:
	return (
		rng.randint(0,GRID_SIZE),
		rng.randint(0,GRID_SIZE),
	)
def randColor(rng) -> Color:
	return (
		rng.randint(0,255),
		rng.randint(0,255),
		rng.randint(0,255),
	)
def getCentroid(points: list[Point]) -> Point:
	return (
		round(sum(p[0] for p in points)/len(points)),
		round(sum(p[1] for p in points)/len(points)),
	)
def getAngleForDay(latt: int,day: int) -> float:
	return (lattitudeToAngle(latt) + getCurrentTilt(day)) % tau
def getVectorForDay(latt: int,day: int) -> tuple[float,float]:
	theta = getAngleForDay(latt,day)
	return (
		RADIUS * cos(theta),
		RADIUS * sin(theta),
	)
def getSunlightValue(latt: int,day: int) -> float:
	x,y = getVectorForDay(latt,day)
	return x * -RADIUS
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
def getHumidity(*,land: Screen[bool]) -> Screen:
	print('generating humidity...')
	filename = Path(f"humidity_{flm(NOISE_SEED)}_{flm(TERRAIN_NOISE_SCALE)}_{flm(TERRAIN_NOISE_OCTAVES)}_{flm(GRID_SIZE)}_{flm(OVERWORLD_SEA_LEVEL_FACTOR)}_{flm(HUMIDITY_SMUDGE_RADIUS)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y : values[x][y],
			GRID_SIZE,
		)
	offsets = [(x,y) for x in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS + 1) for y in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS + 1) if getDistance((0,0),(x,y)) <= HUMIDITY_SMUDGE_RADIUS]
	humidity = Screen(GRID_SIZE)
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			points = [((i + x) % GRID_SIZE,(j + y) % GRID_SIZE) for x,y in offsets]
			humidity[i,j] = len([p for p in points if not land[p]])/len(points)
	values = [[humidity[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return humidity
def getSunlight() -> Screen:
	print('generating sunlight...')
	filename = Path(f"sunlight_{flm(GRID_SIZE)}_{flm(AXIS_TILT)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		sunlight = json.loads(content)
		return keyMap(
			lambda x,y : sunlight[y],
			GRID_SIZE,
		)
	values = [getAvgSunlightValue(y) for y in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return keyMap(
		lambda x,y : values[y],
		GRID_SIZE,
	)
def getOverworldGreenery(
	*,
	altitude: Screen|None = None,
	land: Screen|None = None,
	snow : Screen|None = None,
	sunlight: Screen|None = None,
) -> Screen:
	print('generating top greenery...')
	if land is None:
		land = getLand(altitude = altitude)
	if snow is None:
		if sunlight is None:
			sunlight = getSunlight()
		snow = getSnow(sunlight = sunlight,altitude = altitude)
	return scrMap(
		lambda w,u,v : (255,255,255) if w else (
			0,int(u),0
		) if v else (
			0,0,int(u)
		),
		snow,
		altitude,
		land,
	)
def getMidworldGreenery(
	*,
	altitude: Screen[int],
	land: Screen[bool],
	connected: Screen[bool],
	water: Screen[bool]
) -> Screen:
	print('generating bottom greenery...')
	if land is None:
		land = getLand(altitude = altitude)
	return scrMap(
		lambda con,u,l,w : (0,0,0) if con else (
			0,0,int(u)
		) if w else (
			int((u - MIDWORLD_SEA_LEVEL/2)/2),
			int(u - MIDWORLD_SEA_LEVEL/2),
			int((u - MIDWORLD_SEA_LEVEL/2)/2),
		) if l else (
			int(u + MIDWORLD_SEA_LEVEL),
			int((u + MIDWORLD_SEA_LEVEL)/2),
			0,
		),
		connected,
		altitude,
		land,
		water,
	)
def getConnectedEdges(*,connected: Screen[bool]) -> Screen[bool]:
	print('generating connected edges...')
	points = {
		(-1,-1),
		(-1,0),
		(-1,1),
		(0,-1),
		(0,1),
		(1,-1),
		(1,0),
		(1,1),
	}
	result = Screen(GRID_SIZE)
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			result[i,j] = not connected[i,j] and any(connected[(x + i) % GRID_SIZE,(y + j) % GRID_SIZE] for x,y in points)
	return result
def getBodiesOfWater(land: Screen[bool]) -> list[set[Point]]:
	print('START')
	def neighbors(p1,p2):
		return (
			p1[0] == p2[0] and (
				(p1[1] + 1) % GRID_SIZE == p2[1] or
				(p1[1] - 1) % GRID_SIZE == p2[1]
			) or p1[1] == p2[1] and (
				(p1[0] + 1) % GRID_SIZE == p2[0] or
				(p1[0] - 1) % GRID_SIZE == p2[0]
			)
		)
	def belongsTo(p,b):
		return any(neighbors(p,pt) for pt in b)
	points: list[Point] = [(i,j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if not land[i,j]]
	bodies: list[set[Point]] = []
	for point in points:
		indices = set()
		for i,body in enumerate(bodies):
			if belongsTo(point,body):
				indices.add(i)
		if len(indices) > 0:
			bodies = [
				{point} | reduce(
					or_,
					[body for i,body in enumerate(bodies) if i in indices]
				)
			] + [body for i,body in enumerate(bodies) if i not in indices]
		else:
			bodies.append({point})
	print('END')
	return bodies
def addColor(trn: dict[str,Screen]) -> None:
	keys = list(trn.keys())
	for k in keys:
		if isinstance(trn[k][0,0],bool):
			trn[k] = scrMap(
				lambda v : (255,255,255) if v else (0,0,0),
				trn[k],
			)
		elif isinstance(trn[k][0,0],int|float):
			trn[k] = scrMap(
				lambda v : (int(v),int(v),int(v)),
				trn[k],
			)
		elif isinstance(trn[k][0,0],tuple) and len(trn[k][0,0]) == 2:
			trn[k] = scrMap(
				lambda v : pointToColor(v),
				trn[k],
			)

TERRAIN: dict[str,Screen] = {}

# Grid settings

LENGTH: int = GRID_SIZE * CELL_SIZE

pygame.init()

font = pygame.font.SysFont("Arial",20)

def drawMap() -> None:
	global pygame,FINAL_SCREEN_LAYOUT,SCREEN_LAYOUT

	width = (getMaxX(SCREEN_LAYOUT) + 1)*LENGTH
	height = (getMaxY(SCREEN_LAYOUT) + 1)*LENGTH

	window = pygame.display.set_mode((width + UI_PANEL_WIDTH,height))
	pygame.display.set_caption("Window")
	ui_panel = pygame.Rect(width,0,UI_PANEL_WIDTH,height)
	pygame.draw.rect(window,UI_RECT_COLOR,ui_panel)
	text_surface = font.render(str(OVERWORLD_SEA_LEVEL_FACTOR),True,(0,0,0))
	text_rect = text_surface.get_rect(center=(width + UI_PANEL_WIDTH//2,UI_PANEL_MARGIN))
	window.blit(text_surface, text_rect)

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

TERRAIN['overworld surface']: Screen[float] = (
	perlinNoise(
		seed = NOISE_SEED,
		scale = TERRAIN_NOISE_SCALE,
		octaves = TERRAIN_NOISE_OCTAVES,
	) + 1
) * OVERWORLD_SURFACE_MAX/2
TERRAIN['overworld depth']: Screen[float] = (
	perlinNoise(
		seed = NOISE_SEED + 1,
		scale = TERRAIN_NOISE_SCALE,
		octaves = TERRAIN_NOISE_OCTAVES,
	) + 1
) * OVERWORLD_DEPTH_MAX/2
TERRAIN['midworld surface']: Screen[float] = (
	perlinNoise(
		seed = NOISE_SEED + 2,
		scale = TERRAIN_NOISE_SCALE,
		octaves = TERRAIN_NOISE_OCTAVES,
	) + 1
) * MIDWORLD_SURFACE_MAX/2
TERRAIN['overworld land']: Screen[bool] = TERRAIN['overworld surface'] > OVERWORLD_SEA_LEVEL
TERRAIN['midworld land']: Screen[bool] = TERRAIN['midworld surface'] > MIDWORLD_SEA_LEVEL
TERRAIN['overworld depth altitude']: Screen[float] = OVERWORLD_DEPTH_OVERLAP_HEIGHT + MIDWORLD_ALTITUDE_OVERLAP_HEIGHT - TERRAIN['overworld depth']
TERRAIN['overworld thickness']: Screen[float] = TERRAIN['overworld surface'] + TERRAIN['overworld depth']
TERRAIN['overworld-midworld connections']: Screen[bool] = TERRAIN['midworld surface'] >= (
	OVERWORLD_DEPTH_OVERLAP_HEIGHT + MIDWORLD_ALTITUDE_OVERLAP_HEIGHT - TERRAIN['overworld depth']
)
TERRAIN['midworld open space'] = ifMap(
	0,
	TERRAIN['overworld-midworld connections'],
	TERRAIN['overworld depth altitude'] - TERRAIN['midworld surface'],
)
TERRAIN['sunlight'] = getSunlight()
TERRAIN['snow'] = ((OVERWORLD_SURFACE_MAX - TERRAIN['sunlight']) + TERRAIN['overworld surface'])/2 > SNOW_LEVEL
TERRAIN['overworld-midworld connection edges'] = getConnectedEdges(
	connected = TERRAIN['overworld-midworld connections'],
)
TERRAIN['potential midworld water'] = TERRAIN['midworld land'] & ~(TERRAIN['overworld-midworld connections'] | TERRAIN['overworld land'])
TERRAIN['midworld water'] = Screen(GRID_SIZE,0)
for i in range(GRID_SIZE):
	for j in range(GRID_SIZE):
		if TERRAIN['potential midworld water'][i,j]:
			total = (OVERWORLD_THICKNESS_MAX - TERRAIN['overworld thickness'][i,j]) * MIDWORLD_WATER_FACTOR/OVERWORLD_THICKNESS_MAX
			a = i
			b = j
			while True:
				points = [
					((a - 1) % GRID_SIZE,(b - 1) % GRID_SIZE),
					((a - 1) % GRID_SIZE,b),
					((a - 1) % GRID_SIZE,(b + 1) % GRID_SIZE),
					(a,(b - 1) % GRID_SIZE),
					(a,(b + 1) % GRID_SIZE),
					((a + 1) % GRID_SIZE,(b - 1) % GRID_SIZE),
					((a + 1) % GRID_SIZE,b),
					((a + 1) % GRID_SIZE,(b + 1) % GRID_SIZE),
				]
				heights = [TERRAIN['midworld surface'][p] + TERRAIN['midworld water'][p] for p in points]
				minHeight = min(heights)
				if minHeight >= TERRAIN['midworld surface'][a,b] + TERRAIN['midworld water'][a,b]:
					break
				index = heights.index(minHeight)
				minPoint = points[index]
				a,b = minPoint
			if TERRAIN['midworld land'][a,b]:
				TERRAIN['midworld water'][a,b] += total
TERRAIN['midworld water'] = TERRAIN['midworld water'] >= 1
TERRAIN['overworld greenery'] = getOverworldGreenery(
	altitude = TERRAIN['overworld surface'],
	land = TERRAIN['overworld land'],
	snow = TERRAIN['snow'],
	sunlight = TERRAIN['sunlight'],
)
TERRAIN['midworld greenery'] = getMidworldGreenery(
	altitude = TERRAIN['midworld surface'],
	land = TERRAIN['midworld land'],
	connected = TERRAIN['overworld-midworld connections'],
	water = TERRAIN['midworld water'],
)
bodiesMap = getBodiesOfWater(TERRAIN['overworld land'])
colors = []
rng = random.Random(NOISE_SEED)
while len(colors) < len(bodiesMap):
	c = randColor(rng)
	if c not in colors:
		colors.append(c)
bodiesOfWater = {}
for i,body in enumerate(bodiesMap):
	for point in body:
		bodiesOfWater[point] = colors[i]
for i in range(GRID_SIZE):
	for j in range(GRID_SIZE):
		if (i,j) not in bodiesOfWater:
			bodiesOfWater[i,j] = None
TERRAIN['overworld bodies of water'] = keyMap(
	lambda x,y : bodiesOfWater[x,y] if bodiesOfWater[x,y] is not None else (0,0,0),
	GRID_SIZE,
)

TERRAIN['overworld coastline'] = keyMap(
	lambda x,y,v : v and not all(
		TERRAIN['overworld land'][
			(x + i) % GRID_SIZE,
			(y + j) % GRID_SIZE,
		] for i in range(-1,2) for j in range(-1,2)
	),
	TERRAIN['overworld land'],
)
TERRAIN['overworld cloud density'] = keyMap(
	lambda x,y : OVERWORLD_CLOUD_DENSITY_STRENGTH*e**(
		-(
			(
				(
					2/OVERWORLD_CLOUD_DENSITY_WIDTH
				)*(
					y - GRID_SIZE / 2
				)
			)**2
		)
	),
	GRID_SIZE,
)

TERRAIN['overworld cloud density'] *= 255/OVERWORLD_CLOUD_DENSITY_STRENGTH

addColor(TERRAIN)

SCREEN_LAYOUT[0,0] = 'overworld bodies of water'

mapLayout(TERRAIN)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()