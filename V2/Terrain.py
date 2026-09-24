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
from typing import (
	Callable,
	Any,
)

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
OVERWORLD_TEMPERATURE_RANGE: tuple[float,float] = (-89.2,56.7)
OVERWORLD_SUNLIGHT_RANGE: tuple[int,int] = (0,256)
OVERWORLD_SEA_LEVEL_FACTOR = 0.55
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

OVERWORLD_TEMPERATURE_MIN: float = OVERWORLD_TEMPERATURE_RANGE[0]
OVERWORLD_TEMPERATURE_MAX: float = OVERWORLD_TEMPERATURE_RANGE[1]
OVERWORLD_SUNLIGHT_MIN: int = OVERWORLD_SUNLIGHT_RANGE[0]
OVERWORLD_SUNLIGHT_MAX: int = OVERWORLD_SUNLIGHT_RANGE[1] - 1
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
def perlinNoise(size: int,seed: int|float = 0,scale: int = 1,octaves: int = 1) -> Screen[float]:
	print('generating perlin noise...')
	"""
	Generate seamless wrapping 2D Perlin noise using 4D Perlin.

	Returns:
	    list[list[float]]: values approximately [-1, 1]
	"""
	filename = Path(f"pnoise_{size}_{seed}_{scale}_{octaves}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y : values[x][y],
			size,
		)
	rng = random.Random(seed)
	seed_offset = rng.random() * 10000.0
	noise_map = Screen(size)
	for y in range(size):
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
			noise_map[x,y] = value / amplitude_sum
	values = [[noise_map[x,y] for y in range(size)] for x in range(size)]
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
def getVectorForDay(latt: int,day: int) -> tuple[float,float]: # (float[-GRID_SIZE/2pi,GRID_SIZE/2pi],float[-GRID_SIZE/2pi,GRID_SIZE/2pi])
	theta = getAngleForDay(latt,day)
	return (
		RADIUS * cos(theta),
		RADIUS * sin(theta),
	)
def getSunlightValue(latt: int,day: int) -> float: # float[-(GRID_SIZE/2pi)**2,(GRID_SIZE/2pi)**2]
	x,y = getVectorForDay(latt,day)
	return x * -RADIUS
def getNormalizedSunlightValue(latt: int,day: int) -> float: # float[-(GRID_SIZE/2pi)**2,(GRID_SIZE/2pi)**2]
	return (
		getSunlightValue(latt,day) + getSunlightValue(GRID_SIZE - latt,day)
	)/2
def getAvgSunlightValue(latt: int) -> float: # float[0,GRID_SIZE]
	values = [getNormalizedSunlightValue(latt,day) for day in range(365)]
	return (sum(values)/len(values) + RADIUS**2) * (OVERWORLD_SUNLIGHT_MAX - OVERWORLD_SUNLIGHT_MIN)/(2 * RADIUS**2) + OVERWORLD_SUNLIGHT_MIN
def smudge(trn: Screen) -> Screen:
	points = {(i,j) for i in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS) for j in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS)}
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
	filename = Path(f"humidity_{NOISE_SEED}_{TERRAIN_NOISE_SCALE}_{TERRAIN_NOISE_OCTAVES}_{GRID_SIZE}_{OVERWORLD_SEA_LEVEL_FACTOR}_{HUMIDITY_SMUDGE_RADIUS}.json")
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
def getSunlight() -> Screen[float]: # float[0,GRID_SIZE]
	print('generating sunlight...')
	filename = Path(f"sunlight_{GRID_SIZE}_{AXIS_TILT}.json")
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
) -> Screen[Color]:
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
) -> Screen[Color]:
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
def getBodiesOfWater(land: Screen[bool],seaLevel: int|float,depthMax: int|float,octaves: int,scale: int|float,seed: int,size: int) -> list[set[Point]]:
	filename = Path(f"bodiesOfWater_{seaLevel}_{depthMax}_{octaves}_{scale}_{seed}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		return [{tuple(u) for u in v} for v in json.loads(content)]
	def neighbors(p1,p2):
		return (
			p1[0] == p2[0] and (
				(p1[1] + 1) % size == p2[1] or
				(p1[1] - 1) % size == p2[1]
			) or p1[1] == p2[1] and (
				(p1[0] + 1) % size == p2[0] or
				(p1[0] - 1) % size == p2[0]
			)
		)
	def belongsTo(p,b):
		return any(neighbors(p,pt) for pt in b)
	points: list[Point] = [(i,j) for i in range(size) for j in range(size) if not land[i,j]]
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
	values = [[list(u) for u in v] for v in bodies]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
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
def redBlueScale(value: int|float) -> Color:
	return (
		int(value),
		0,
		255 - int(value),
	)

ARGUMENTS: dict[str,dict[str,list[str]]] = {
	'perlin noise 0' : {
		'terrain' : [],
		'nonterrain' : {
			'NOISE_SEED' : NOISE_SEED,
			'TERRAIN_NOISE_SCALE' : TERRAIN_NOISE_SCALE,
			'TERRAIN_NOISE_OCTAVES' : TERRAIN_NOISE_OCTAVES,
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'perlin noise 1' : {
		'terrain' : [],
		'nonterrain' : {
			'NOISE_SEED' : NOISE_SEED,
			'TERRAIN_NOISE_SCALE' : TERRAIN_NOISE_SCALE,
			'TERRAIN_NOISE_OCTAVES' : TERRAIN_NOISE_OCTAVES,
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'perlin noise 2' : {
		'terrain' : [],
		'nonterrain' : {
			'NOISE_SEED' : NOISE_SEED,
			'TERRAIN_NOISE_SCALE' : TERRAIN_NOISE_SCALE,
			'TERRAIN_NOISE_OCTAVES' : TERRAIN_NOISE_OCTAVES,
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld surface original' : {
		'terrain' : [
			'perlin noise 0',
		],
		'nonterrain' : {
			'OVERWORLD_SURFACE_MAX' : OVERWORLD_SURFACE_MAX,
		},
	},
	'overworld surface scaled' : {
		'terrain' : [
			'overworld surface original',
		],
		'nonterrain' : {
			'OVERWORLD_SEA_LEVEL' : OVERWORLD_SEA_LEVEL,
		},
	},
	'overworld depth' : {
		'terrain' : [
			'perlin noise 1',
		],
		'nonterrain' : {
			'OVERWORLD_DEPTH_MAX' : OVERWORLD_DEPTH_MAX,
		},
	},
	'midworld surface' : {
		'terrain' : [
			'perlin noise 2',
		],
		'nonterrain' : [
			'MIDWORLD_SURFACE_MAX' : MIDWORLD_SURFACE_MAX,
		],
	},
	'overworld land' : {
		'terrain' : [
			'overworld surface original',
		],
		'nonterrain' : {
			'OVERWORLD_SEA_LEVEL' : OVERWORLD_SEA_LEVEL,
		},
	},
	'overworld bodies of water' : {
		'terrain' : [
			'overworld land',
		],
		'nonterrain' : {
			'OVERWORLD_SEA_LEVEL' : OVERWORLD_SEA_LEVEL,
			'OVERWORLD_DEPTH_MAX' : OVERWORLD_DEPTH_MAX,
			'TERRAIN_NOISE_OCTAVES' : TERRAIN_NOISE_OCTAVES,
			'TERRAIN_NOISE_SCALE' : TERRAIN_NOISE_SCALE,
			'NOISE_SEED' : NOISE_SEED,
			'GRID_SIZE' : GRID_SIZE,
		}
	},
	'overworld surface' : {
		'terrain' : [
			'overworld surface scaled',
			'overworld land',
			'overworld surface original',
		],
		'nonterrain' : {},
	},
	'overworld true surface' : {
		'terrain' : [
			'overworld surface',
			'overworld land',
		],
		'nonterrain' : {
			'OVERWORLD_SEA_LEVEL' : OVERWORLD_SEA_LEVEL,
		},
	},
	'overworld surface derivative x-' : {
		'terrain' : [
			'overworld true surface',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld surface derivative x+' : {
		'terrain' : [
			'overworld true surface',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld surface derivative x' : {
		'terrain' : [
			'overworld surface derivative x+',
			'overworld surface derivative x-',
		],
		'nonterrain' : {},
	},
	'overworld surface derivative y-' : {
		'terrain' : [
			'overworld true surface',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld surface derivative y+' : {
		'terrain' : [
			'overworld true surface',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld surface derivative y' : {
		'terrain' : [
			'overworld surface derivative y+',
			'overworld surface derivative y-',
		],
		'nonterrain' : {},
	},
	'overworld surface normal magnitude' : {
		'terrain' : [
			'overworld surface derivative x',
			'overworld surface derivative y',
		],
		'nonterrain' : {},
	},
	'overworld surface normal x' : {
		'terrain' : [
			'overworld surface derivative x',
			'overworld surface normal magnitude',
		],
		'nonterrain' : {},
	},
	'overworld surface normal y' : {
		'terrain' : [
			'overworld surface derivative y',
			'overworld surface normal magnitude',
		],
		'nonterrain' : {},
	},
	'overworld surface normal z' : {
		'terrain' : [
			'overworld surface normal magnitude',
		],
		'nonterrain' : {},
	},
	'overworld surface wind x' : {
		'terrain' : [],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
			'MAX_SPEED' : GRID_SIZE,
		},
	},
	'overworld surface wind y' : {
		'terrain' : [],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
			'MAX_SPEED' : GRID_SIZE,
		},
	},
}
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

TERRAIN['perlin noise 0'] = perlinNoise(
	size = GRID_SIZE,
	seed = NOISE_SEED,
	scale = TERRAIN_NOISE_SCALE,
	octaves = TERRAIN_NOISE_OCTAVES,
)
TERRAIN['perlin noise 1'] = perlinNoise(
	size = GRID_SIZE,
	seed = NOISE_SEED + 1,
	scale = TERRAIN_NOISE_SCALE,
	octaves = TERRAIN_NOISE_OCTAVES,
)
TERRAIN['perlin noise 2'] = perlinNoise(
	size = GRID_SIZE,
	seed = NOISE_SEED + 2,
	scale = TERRAIN_NOISE_SCALE,
	octaves = TERRAIN_NOISE_OCTAVES,
)
TERRAIN['overworld surface original']: Screen[float] = (
	TERRAIN['perlin noise 0'] + 1
) * OVERWORLD_SURFACE_MAX/2
maxv = max({v for v in TERRAIN['overworld surface original']})
nmaxv = (255 + maxv)/2
factor = (nmaxv - OVERWORLD_SEA_LEVEL)/(maxv - OVERWORLD_SEA_LEVEL)
TERRAIN['overworld surface scaled'] = (TERRAIN['overworld surface original'] - OVERWORLD_SEA_LEVEL) * factor + OVERWORLD_SEA_LEVEL
TERRAIN['overworld depth']: Screen[float] = (
	TERRAIN['perlin noise 1'] + 1
) * OVERWORLD_DEPTH_MAX/2
TERRAIN['midworld surface']: Screen[float] = (
	TERRAIN['perlin noise 2'] + 1
) * MIDWORLD_SURFACE_MAX/2
TERRAIN['overworld land']: Screen[bool] = TERRAIN['overworld surface original'] > OVERWORLD_SEA_LEVEL
bodiesMap = getBodiesOfWater(
	land = TERRAIN['overworld land'],
	seaLevel = OVERWORLD_SEA_LEVEL,
	depthMax = OVERWORLD_DEPTH_MAX,
	octaves = TERRAIN_NOISE_OCTAVES,
	scale = TERRAIN_NOISE_SCALE,
	seed = NOISE_SEED,
)
total = sum(len(b) for b in bodiesMap)
for points in bodiesMap:
	if len(points) <= 0.1 * total:
		for point in points:
			TERRAIN['overworld land'][point] = True
TERRAIN['overworld coastline'] = keyMap(
	lambda x,y,v : v and not all(
		TERRAIN['overworld land'][
			(x + i) % GRID_SIZE,
			(y + j) % GRID_SIZE,
		] for i in range(-1,2) for j in range(-1,2)
	),
	TERRAIN['overworld land'],
)
TERRAIN['overworld coastline land side'] = TERRAIN['overworld coastline'] & TERRAIN['overworld land']
TERRAIN['overworld coastline water side'] = TERRAIN['overworld coastline'] & ~TERRAIN['overworld land']
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
TERRAIN['overworld surface'] = ifMap(
	TERRAIN['overworld surface scaled'],
	TERRAIN['overworld land'],
	TERRAIN['overworld surface original'],
)
TERRAIN['overworld true surface'] = ifMap(
	TERRAIN['overworld surface'],
	TERRAIN['overworld land'],
	OVERWORLD_SEA_LEVEL,
)
TERRAIN['overworld surface derivative x-'] = keyMap(
	lambda x,y : TERRAIN['overworld true surface'][x,y] - TERRAIN['overworld true surface'][(x - 1) % GRID_SIZE,y],
	GRID_SIZE,
)
TERRAIN['overworld surface derivative x+'] = keyMap(
	lambda x,y : TERRAIN['overworld true surface'][(x + 1) % GRID_SIZE,y] - TERRAIN['overworld true surface'][x,y],
	GRID_SIZE,
)
TERRAIN['overworld surface derivative x'] = (TERRAIN['overworld surface derivative x-'] + TERRAIN['overworld surface derivative x+']) / 2
vals = {v for v in TERRAIN['overworld surface derivative x']}
maxv = max(vals)
minv = min(vals)
TERRAIN['overworld surface derivative x'] = (TERRAIN['overworld surface derivative x'] - minv) * 255/(maxv - minv)
TERRAIN['overworld surface derivative y-'] = keyMap(
	lambda x,y : TERRAIN['overworld true surface'][x,y] - TERRAIN['overworld true surface'][x,(y - 1) % GRID_SIZE],
	GRID_SIZE,
)
TERRAIN['overworld surface derivative y+'] = keyMap(
	lambda x,y : TERRAIN['overworld true surface'][x,(y + 1) % GRID_SIZE] - TERRAIN['overworld true surface'][x,y],
	GRID_SIZE,
)
TERRAIN['overworld surface derivative y'] = (TERRAIN['overworld surface derivative y-'] + TERRAIN['overworld surface derivative y+']) / 2
vals = {v for v in TERRAIN['overworld surface derivative y']}
maxv = max(vals)
minv = min(vals)
TERRAIN['overworld surface derivative y'] = (TERRAIN['overworld surface derivative y'] - minv) * 255/(maxv - minv)
TERRAIN['overworld surface normal magnitude'] = (1 + TERRAIN['overworld surface derivative x']**2 + TERRAIN['overworld surface derivative y']**2)**0.5
TERRAIN['overworld surface normal x'] = -TERRAIN['overworld surface derivative x'] / TERRAIN['overworld surface normal magnitude']
TERRAIN['overworld surface normal y'] = -TERRAIN['overworld surface derivative y'] / TERRAIN['overworld surface normal magnitude']
TERRAIN['overworld surface normal z'] = 1 / TERRAIN['overworld surface normal magnitude']
TERRAIN['overworld surface wind x'] = Screen(GRID_SIZE,0)
TERRAIN['overworld surface wind y'] = Screen(GRID_SIZE,0)
for i in range(GRID_SIZE):
	if i >= 0 and i < (1/6) * GRID_SIZE - GRID_SIZE/18:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = -MAX_SPEED
			TERRAIN['overworld surface wind y'][j,i] = -MAX_SPEED
	elif i >= (1/6) * GRID_SIZE - GRID_SIZE/18 and i < (1/6) * GRID_SIZE:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = 0
			TERRAIN['overworld surface wind y'][j,i] = 0
	elif i >= (1/6) * GRID_SIZE and i < (2/6) * GRID_SIZE:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = MAX_SPEED
			TERRAIN['overworld surface wind y'][j,i] = MAX_SPEED
	elif i >= (2/6) * GRID_SIZE and i < (2/6) * GRID_SIZE + GRID_SIZE/18:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = 0
			TERRAIN['overworld surface wind y'][j,i] = 0
	elif i >= (2/6) * GRID_SIZE + GRID_SIZE/18 and i < (3/6) * GRID_SIZE - GRID_SIZE/18:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = -MAX_SPEED
			TERRAIN['overworld surface wind y'][j,i] = -MAX_SPEED
	elif i >= (3/6) * GRID_SIZE - GRID_SIZE/18 and i < (3/6) * GRID_SIZE + GRID_SIZE/18:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = 0
			TERRAIN['overworld surface wind y'][j,i] = 0
	elif i >= (3/6) * GRID_SIZE + GRID_SIZE/18 and i < (4/6) * GRID_SIZE - GRID_SIZE/18:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = MAX_SPEED
			TERRAIN['overworld surface wind y'][j,i] = MAX_SPEED
	elif i >= (4/6) * GRID_SIZE - GRID_SIZE/18 and i < (4/6) * GRID_SIZE:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = 0
			TERRAIN['overworld surface wind y'][j,i] = 0
	elif i >= (4/6) * GRID_SIZE and i < (5/6) * GRID_SIZE:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = -MAX_SPEED
			TERRAIN['overworld surface wind y'][j,i] = -MAX_SPEED
	elif i >= (5/6) * GRID_SIZE and i < (5/6) * GRID_SIZE + GRID_SIZE/12:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = 0
			TERRAIN['overworld surface wind y'][j,i] = 0
	else:
		for j in range(GRID_SIZE):
			TERRAIN['overworld surface wind x'][j,i] = MAX_SPEED
			TERRAIN['overworld surface wind y'][j,i] = MAX_SPEED
TERRAIN['overworld surface wind x'] = (TERRAIN['overworld surface wind x'] + MAX_SPEED) * 255/(2*MAX_SPEED)
TERRAIN['overworld surface wind y'] = (TERRAIN['overworld surface wind y'] + MAX_SPEED) * 255/(2*MAX_SPEED)
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
TERRAIN['overworld sunlight'] = getSunlight()
TERRAIN['overworld temperature'] = (TERRAIN['overworld sunlight'] + TERRAIN['overworld surface']) / 2
TERRAIN['overworld temperature'] = TERRAIN['overworld temperature'] * (OVERWORLD_TEMPERATURE_MAX - OVERWORLD_TEMPERATURE_MIN)/255 + OVERWORLD_TEMPERATURE_MIN
TERRAIN['overworld temperature'] = ifMap(
	TERRAIN['overworld temperature'],
	TERRAIN['overworld land'],
	TERRAIN['overworld temperature'] - 6,
)
TERRAIN['snow'] = TERRAIN['overworld temperature'] <= 0
TERRAIN['overworld temperature'] = (TERRAIN['overworld temperature'] - OVERWORLD_TEMPERATURE_MIN) * 255/(OVERWORLD_TEMPERATURE_MAX - OVERWORLD_TEMPERATURE_MIN)
TERRAIN['overworld temperature derivative x+'] = keyMap(
	lambda x,y : TERRAIN['overworld temperature'][(x + 1) % GRID_SIZE,y] - TERRAIN['overworld temperature'][x,y],
	GRID_SIZE,
)
TERRAIN['overworld temperature derivative y+'] = keyMap(
	lambda x,y : TERRAIN['overworld temperature'][x,(y + 1) % GRID_SIZE] - TERRAIN['overworld temperature'][x,y],
	GRID_SIZE,
)
TERRAIN['overworld temperature derivative x-'] = keyMap(
	lambda x,y : TERRAIN['overworld temperature'][x,y] - TERRAIN['overworld temperature'][(x - 1) % GRID_SIZE,y],
	GRID_SIZE,
)
TERRAIN['overworld temperature derivative y-'] = keyMap(
	lambda x,y : TERRAIN['overworld temperature'][x,y] - TERRAIN['overworld temperature'][x,(y - 1) % GRID_SIZE],
	GRID_SIZE,
)
TERRAIN['overworld temperature derivative x'] = (TERRAIN['overworld temperature derivative x+'] + TERRAIN['overworld temperature derivative x-'])/2
TERRAIN['overworld temperature derivative y'] = (TERRAIN['overworld temperature derivative y+'] + TERRAIN['overworld temperature derivative y-'])/2
maxv = max(v for v in TERRAIN['overworld temperature derivative x'])
minv = min(v for v in TERRAIN['overworld temperature derivative x'])
TERRAIN['overworld temperature derivative x'] = (TERRAIN['overworld temperature derivative x'] - minv) * 255/(maxv - minv)
maxv = max(v for v in TERRAIN['overworld temperature derivative y'])
minv = min(v for v in TERRAIN['overworld temperature derivative y'])
TERRAIN['overworld temperature derivative y'] = (TERRAIN['overworld temperature derivative y'] - minv) * 255/(maxv - minv)
TERRAIN['overworld temperature'] = scrMap(redBlueScale,TERRAIN['overworld temperature'])
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
	sunlight = TERRAIN['overworld sunlight'],
)
TERRAIN['midworld greenery'] = getMidworldGreenery(
	altitude = TERRAIN['midworld surface'],
	land = TERRAIN['midworld land'],
	connected = TERRAIN['overworld-midworld connections'],
	water = TERRAIN['midworld water'],
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

SCREEN_LAYOUT[0,0] = 'overworld greenery'
SCREEN_LAYOUT[1,0] = 'overworld temperature derivative x'
SCREEN_LAYOUT[2,0] = 'overworld temperature derivative y'

mapLayout(TERRAIN)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()