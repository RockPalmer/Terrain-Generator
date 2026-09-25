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
from Dropdown import Dropdown

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

def getArguments(name: str,arguments: dict[str,dict]) -> dict[str,Any]:
	args = arguments[name]['nonterrain']
	for trn in arguments[name]['terrain']:
		args |= getArguments(trn,arguments)
	return args

TERRAIN_DIRECTORY = Path('terrain')
TERRAIN_DIRECTORY.mkdir(parents = True,exist_ok = True)

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
TERRAIN_NOISE_SCALE: int = 1
TERRAIN_NOISE_OCTAVES: int = 8
NOISE_SEED: int = 0
AXIS_TILT: float = 23.44 * tau/360
HUMIDITY_SMUDGE_RADIUS: int = 7
UI_PANEL_WIDTH: int = 400
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
OVERWORLD_TEMPERATURE_LAND_DIFFERENCE: int = 6
SNOW_LEVEL: int = 50

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
RADIUS: float = GRID_SIZE/tau

OVERWORLD_CLOUD_DENSITY_WIDTH: float = GRID_SIZE * OVERWORLD_CLOUD_DENSITY_FACTOR
OVERWORLD_DEPTH_OVERLAP_HEIGHT: float = OVERWORLD_DEPTH_OVERLAP_HEIGHT_FACTOR * OVERWORLD_DEPTH_MAX
MIDWORLD_ALTITUDE_OVERLAP_HEIGHT: float = MIDWORLD_ALTITUDE_OVERLAP_HEIGHT_FACTOR * MIDWORLD_SURFACE_MAX
OVERWORLD_THICKNESS_MAX: float = OVERWORLD_SURFACE_MAX + OVERWORLD_DEPTH_MAX

ARGS: dict[str,dict] = {
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
		'nonterrain' : {
			'MIDWORLD_SURFACE_MAX' : MIDWORLD_SURFACE_MAX,
		},
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
	'midworld land' : {
		'terrain' : [
			'midworld surface',
		],
		'nonterrain' : {
			'MIDWORLD_SEA_LEVEL' : MIDWORLD_SEA_LEVEL,
		},
	},
	'overworld depth altitude' : {
		'terrain' : [
			'overworld depth',
		],
		'nonterrain' : {
			'OVERWORLD_DEPTH_OVERLAP_HEIGHT' : OVERWORLD_DEPTH_OVERLAP_HEIGHT,
			'MIDWORLD_ALTITUDE_OVERLAP_HEIGHT' : MIDWORLD_ALTITUDE_OVERLAP_HEIGHT,
		},
	},
	'overworld thickness' : {
		'terrain' : [
			'overworld surface',
			'overworld depth',
		],
		'nonterrain' : {},
	},
	'overworld-midworld connections' : {
		'terrain' : [
			'midworld surface',
			'overworld depth altitude',
		],
		'nonterrain' : {},
	},
	'midworld open space' : {
		'terrain' : [
			'overworld-midworld connections',
			'overworld depth altitude',
			'midworld surface',
		],
		'nonterrain' : {},
	},
	'overworld sunlight' : {
		'terrain' : [],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
			'OVERWORLD_SUNLIGHT_MAX' : OVERWORLD_SUNLIGHT_MAX,
			'OVERWORLD_SUNLIGHT_MIN' : OVERWORLD_SUNLIGHT_MIN,
			'AXIS_TILT' : AXIS_TILT,
		},
	},
	'overworld temperature' : {
		'terrain' : [
			'overworld sunlight',
			'overworld surface',
			'overworld land',
		],
		'nonterrain' : {
			'OVERWORLD_TEMPERATURE_MIN' : OVERWORLD_TEMPERATURE_MIN,
			'OVERWORLD_TEMPERATURE_MAX' : OVERWORLD_TEMPERATURE_MAX,
			'OVERWORLD_TEMPERATURE_LAND_DIFFERENCE' : OVERWORLD_TEMPERATURE_LAND_DIFFERENCE,
		},
	},
	'snow' : {
		'terrain' : [
			'overworld temperature',
		],
		'nonterrain' : {
			'SNOW_LEVEL' : SNOW_LEVEL,
		},
	},
	'overworld temperature derivative x+' : {
		'terrain' : [
			'overworld temperature',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld temperature derivative x-' : {
		'terrain' : [
			'overworld temperature',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld temperature derivative y+' : {
		'terrain' : [
			'overworld temperature',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld temperature derivative y-' : {
		'terrain' : [
			'overworld temperature',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld temperature derivative x' : {
		'terrain' : [
			'overworld temperature derivative x+',
			'overworld temperature derivative x-',
		],
		'nonterrain' : {},
	},
	'overworld temperature derivative y' : {
		'terrain' : [
			'overworld temperature derivative y+',
			'overworld temperature derivative y-',
		],
		'nonterrain' : {},
	},
	'overworld-midworld connection edges' : {
		'terrain' : [
			'overworld-midworld connections',
		],
		'nonterrain' : {},
	},
	'potential midworld water' : {
		'terrain' : [
			'midworld land',
			'overworld-midworld connections',
			'overworld land',
		],
		'nonterrain' : {},
	},
	'midworld water' : {
		'terrain' : [
			'potential midworld water',
			'overworld thickness',
			'midworld surface',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
			'OVERWORLD_THICKNESS_MAX' : OVERWORLD_THICKNESS_MAX,
			'MIDWORLD_WATER_FACTOR' : MIDWORLD_WATER_FACTOR,
		},
	},
	'overworld greenery' : {
		'terrain' : [
			'snow',
			'overworld surface',
			'overworld land',
		],
		'nonterrain' : {},
	},
	'midworld greenery' : {
		'terrain' : [
			'overworld-midworld connections',
			'midworld surface',
			'midworld water',
			'midworld land',
		],
		'nonterrain' : {
			'MIDWORLD_SEA_LEVEL' : MIDWORLD_SEA_LEVEL,
		},
	},
	'overworld cloud density' : {
		'terrain' : [],
		'nonterrain' : {
			'OVERWORLD_CLOUD_DENSITY_STRENGTH' : OVERWORLD_CLOUD_DENSITY_STRENGTH,
			'OVERWORLD_CLOUD_DENSITY_WIDTH' : OVERWORLD_CLOUD_DENSITY_WIDTH,
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld coastline' : {
		'terrain' : [
			'overworld land',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld coastline land side' : {
		'terrain' : [
			'overworld coastline',
			'overworld land',
		],
		'nonterrain' : {},
	},
	'overworld coastline water side' : {
		'terrain' : [
			'overworld coastline',
			'overworld land',
		],
		'nonterrain' : {},
	},
}
ARGUMENTS: dict = {name : getArguments(name,ARGS) for name in ARGS}

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
def perlinNoise(size: int,seed: int|float = 0,scale: int = 1,octaves: int = 1) -> Screen[float]:
	print('generating perlin noise...')
	"""
	Generate seamless wrapping 2D Perlin noise using 4D Perlin.

	Returns:
	    list[list[float]]: values approximately [-1, 1]
	"""
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
				angle_x = tau * x / size
				angle_y = tau * y / size
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
def getCurrentTilt(day: int,tilt: int|float) -> float:
	return -tilt + day * (2*tilt)/365
def lattitudeToAngle(latt: int,size: int) -> float:
	return latt * tau/size
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
def getAngleForDay(latt: int,day: int,size: int,tilt: int|float) -> float:
	return (lattitudeToAngle(latt,size) + getCurrentTilt(day,tilt)) % tau
def getVectorForDay(latt: int,day: int,size: int,tilt: int|float) -> tuple[float,float]: # (float[-GRID_SIZE/tau,GRID_SIZE/tau],float[-GRID_SIZE/tau,GRID_SIZE/tau])
	theta = getAngleForDay(latt,day,size,tilt)
	return (
		(size/tau) * cos(theta),
		(size/tau) * sin(theta),
	)
def getSunlightValue(latt: int,day: int,size: int,tilt: int|float) -> float: # float[-(GRID_SIZE/tau)**2,(GRID_SIZE/tau)**2]
	x,y = getVectorForDay(latt,day,size,tilt)
	return x * -(size/tau)
def getNormalizedSunlightValue(latt: int,day: int,size: int,tilt: int|float) -> float: # float[-(GRID_SIZE/tau)**2,(GRID_SIZE/tau)**2]
	return (
		getSunlightValue(latt,day,size,tilt) + getSunlightValue(size - latt,day,size,tilt)
	)/2
def getAvgSunlightValue(lattitude: int,sunlightMax: int|float,sunlightMin: int|float,size: int,tilt: int|float) -> float: # float[0,GRID_SIZE]
	values = [getNormalizedSunlightValue(lattitude,day,size,tilt) for day in range(365)]
	return (sum(values)/len(values) + (size/tau)**2) * (sunlightMax - sunlightMin)/(2 * (size/tau)**2) + sunlightMin
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
	offsets = [(x,y) for x in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS + 1) for y in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS + 1) if getDistance((0,0),(x,y)) <= HUMIDITY_SMUDGE_RADIUS]
	humidity = Screen(GRID_SIZE)
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			points = [((i + x) % GRID_SIZE,(j + y) % GRID_SIZE) for x,y in offsets]
			humidity[i,j] = len([p for p in points if not land[p]])/len(points)
	return humidity
def getSunlight(size: int,sunlightMax: int|float,sunlightMin: int|float,tilt: int|float) -> Screen[float]: # float[0,GRID_SIZE]
	print('generating sunlight...')
	values = [getAvgSunlightValue(
		lattitude = y,
		sunlightMax = sunlightMax,
		sunlightMin = sunlightMin,
		size = size,
		tilt = tilt,
	) for y in range(size)]
	return keyMap(
		lambda x,y : values[y],
		size,
	)
def getBodiesOfWater(land: Screen[bool],seaLevel: int|float,depthMax: int|float,octaves: int,scale: int|float,seed: int,size: int) -> list[set[Point]]:
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
def redBlueScale(value: int|float) -> int:
	return int(value) << 16 | (255 - int(value))
def intToColor(value: int) -> Color:
	return (
		(value >> 16) & 0xFF,
		(value >> 8) & 0xFF,
		value & 0xFF,
	)
def storeTerrainValues(terrain: dict[str,Screen]) -> None:
	for name in terrain:
		storeTerrain(name,terrain[name])
def storeTerrain(name: str,terrain: Screen) -> None:
	print(f"storing {name}...")
	i = 0
	filename = Path(f"terrain/{name}_{i}.json")
	while filename.is_file():
		with open(filename,mode = 'r') as f:
			content = json.loads(f.read())
		if content['arguments'] != ARGUMENTS[name]:
			i += 1
			filename = Path(f"terrain/{name}_{i}.json")
		else:
			return
	with open(filename,mode = 'w') as f:
		f.write(json.dumps({
			'arguments' : ARGUMENTS[name],
			'terrain' : [[terrain[x,y] for y in range(terrain.size)] for x in range(terrain.size)]
		}))
def loadTerrainValues() -> dict[str,Screen]:
	terrain = {}
	for entry in TERRAIN_DIRECTORY.iterdir():
		if not entry.is_file(): continue
		name = '_'.join(entry.name.split('_')[:-1])
		print(f"loading {name}...")
		content = loadTerrain(entry)
		if content['arguments'] == ARGUMENTS[name]:
			terrain[name] = keyMap(
				lambda x,y : content['terrain'][x][y],
				len(content['terrain']),
			)
	return terrain
def loadTerrain(filename: Path) -> dict[str,list|dict]:
	with open(filename,mode = 'r') as f:
		content = json.loads(f.read())
	return content

TERRAIN = loadTerrainValues()
LENGTH: int = GRID_SIZE * CELL_SIZE

if 'perlin noise 0' not in TERRAIN:
	TERRAIN['perlin noise 0']: Screen[float] = perlinNoise(
		size = GRID_SIZE,
		seed = NOISE_SEED,
		scale = TERRAIN_NOISE_SCALE,
		octaves = TERRAIN_NOISE_OCTAVES,
	)
if 'perlin noise 1' not in TERRAIN:
	TERRAIN['perlin noise 1']: Screen[float] = perlinNoise(
		size = GRID_SIZE,
		seed = NOISE_SEED + 1,
		scale = TERRAIN_NOISE_SCALE,
		octaves = TERRAIN_NOISE_OCTAVES,
	)
if 'perlin noise 2' not in TERRAIN:
	TERRAIN['perlin noise 2']: Screen[float] = perlinNoise(
		size = GRID_SIZE,
		seed = NOISE_SEED + 2,
		scale = TERRAIN_NOISE_SCALE,
		octaves = TERRAIN_NOISE_OCTAVES,
	)
if 'overworld surface original' not in TERRAIN:
	TERRAIN['overworld surface original']: Screen[float] = (
		TERRAIN['perlin noise 0'] + 1
	) * OVERWORLD_SURFACE_MAX/2
if 'overworld surface scaled' not in TERRAIN:
	maxv = TERRAIN['overworld surface original'].max()
	nmaxv = (255 + maxv)/2
	TERRAIN['overworld surface scaled']: Screen[float] = (TERRAIN['overworld surface original'] - OVERWORLD_SEA_LEVEL) * nmaxv/maxv + OVERWORLD_SEA_LEVEL
if 'overworld depth' not in TERRAIN:
	TERRAIN['overworld depth']: Screen[float] = (
		TERRAIN['perlin noise 1'] + 1
	) * OVERWORLD_DEPTH_MAX/2
if 'midworld surface' not in TERRAIN:
	TERRAIN['midworld surface']: Screen[float] = (
		TERRAIN['perlin noise 2'] + 1
	) * MIDWORLD_SURFACE_MAX/2
if 'overworld land' not in TERRAIN:
	TERRAIN['overworld land']: Screen[bool] = TERRAIN['overworld surface original'] > OVERWORLD_SEA_LEVEL
	bodiesMap = getBodiesOfWater(
		land = TERRAIN['overworld land'],
		seaLevel = OVERWORLD_SEA_LEVEL,
		depthMax = OVERWORLD_DEPTH_MAX,
		octaves = TERRAIN_NOISE_OCTAVES,
		scale = TERRAIN_NOISE_SCALE,
		seed = NOISE_SEED,
		size = GRID_SIZE,
	)
	total = sum(len(b) for b in bodiesMap)
	for points in bodiesMap:
		if len(points) <= 0.1 * total:
			for point in points:
				TERRAIN['overworld land'][point] = True
if 'overworld coastline' not in TERRAIN:
	TERRAIN['overworld coastline']: Screen[bool] = keyMap(
		lambda x,y,v : v and not all(
			TERRAIN['overworld land'][
				(x + i) % GRID_SIZE,
				(y + j) % GRID_SIZE,
			] for i in range(-1,2) for j in range(-1,2)
		),
		TERRAIN['overworld land'],
	)
if 'overworld coastline land side' not in TERRAIN:
	TERRAIN['overworld coastline land side']: Screen[float] = TERRAIN['overworld coastline'] & TERRAIN['overworld land']
if 'overworld coastline water side' not in TERRAIN:
	TERRAIN['overworld coastline water side']: Screen[float] = TERRAIN['overworld coastline'] & ~TERRAIN['overworld land']
if 'overworld bodies of water' not in TERRAIN:
	colors = []
	rng = random.Random(NOISE_SEED)
	while len(colors) < len(bodiesMap):
		c = rng.randint(0,(1 << 24) - 1)
		if c not in colors:
			colors.append(c)
	TERRAIN['overworld bodies of water']: Screen[int|None] = Screen(GRID_SIZE)
	for i,body in enumerate(bodiesMap):
		for point in body:
			TERRAIN['overworld bodies of water'][point] = colors[i]
	TERRAIN['overworld bodies of water']: Screen[int] = ifMap(
		0,
		TERRAIN['overworld bodies of water'].isNone(),
		TERRAIN['overworld bodies of water'],
	)
if 'overworld surface' not in TERRAIN:
	TERRAIN['overworld surface']: Screen[float] = ifMap(
		TERRAIN['overworld surface scaled'],
		TERRAIN['overworld land'],
		TERRAIN['overworld surface original'],
	)
if 'overworld true surface' not in TERRAIN:
	TERRAIN['overworld true surface']: Screen[float] = ifMap(
		TERRAIN['overworld surface'],
		TERRAIN['overworld land'],
		OVERWORLD_SEA_LEVEL,
	)
if 'overworld surface derivative x-' not in TERRAIN:
	TERRAIN['overworld surface derivative x-']: Screen[float] = keyMap(
		lambda x,y : TERRAIN['overworld true surface'][x,y] - TERRAIN['overworld true surface'][(x - 1) % GRID_SIZE,y],
		GRID_SIZE,
	)
if 'overworld surface derivative x+' not in TERRAIN:
	TERRAIN['overworld surface derivative x+']: Screen[float] = keyMap(
		lambda x,y : TERRAIN['overworld true surface'][(x + 1) % GRID_SIZE,y] - TERRAIN['overworld true surface'][x,y],
		GRID_SIZE,
	)
if 'overworld surface derivative x' not in TERRAIN:
	TERRAIN['overworld surface derivative x']: Screen[float] = (
		(TERRAIN['overworld surface derivative x-'] + TERRAIN['overworld surface derivative x+']) / 2
	).scale(0,255)
if 'overworld surface derivative y-' not in TERRAIN:
	TERRAIN['overworld surface derivative y-']: Screen[float] = keyMap(
		lambda x,y : TERRAIN['overworld true surface'][x,y] - TERRAIN['overworld true surface'][x,(y - 1) % GRID_SIZE],
		GRID_SIZE,
	)
if 'overworld surface derivative y+' not in TERRAIN:
	TERRAIN['overworld surface derivative y+']: Screen[float] = keyMap(
		lambda x,y : TERRAIN['overworld true surface'][x,(y + 1) % GRID_SIZE] - TERRAIN['overworld true surface'][x,y],
		GRID_SIZE,
	)
if 'overworld surface derivative y' not in TERRAIN:
	TERRAIN['overworld surface derivative y'] = (
		(TERRAIN['overworld surface derivative y-'] + TERRAIN['overworld surface derivative y+']) / 2
	).scale(0,255)
if 'overworld surface normal magnitude' not in TERRAIN:
	TERRAIN['overworld surface normal magnitude']: Screen[float] = (1 + TERRAIN['overworld surface derivative x']**2 + TERRAIN['overworld surface derivative y']**2)**0.5
if 'overworld surface normal x' not in TERRAIN:
	TERRAIN['overworld surface normal x']: Screen[float] = -TERRAIN['overworld surface derivative x'] / TERRAIN['overworld surface normal magnitude']
if 'overworld surface normal y' not in TERRAIN:
	TERRAIN['overworld surface normal y']: Screen[float] = -TERRAIN['overworld surface derivative y'] / TERRAIN['overworld surface normal magnitude']
if 'overworld surface normal z' not in TERRAIN:
	TERRAIN['overworld surface normal z']: Screen[float] = 1 / TERRAIN['overworld surface normal magnitude']
if 'overworld surface wind x' not in TERRAIN:
	TERRAIN['overworld surface wind x']: Screen[float] = Screen(GRID_SIZE,0)
	for i in range(GRID_SIZE):
		if i >= 0 and i < (1/6) * GRID_SIZE - GRID_SIZE/18:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = -MAX_SPEED
		elif i >= (1/6) * GRID_SIZE - GRID_SIZE/18 and i < (1/6) * GRID_SIZE:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = 0
		elif i >= (1/6) * GRID_SIZE and i < (2/6) * GRID_SIZE:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = MAX_SPEED
		elif i >= (2/6) * GRID_SIZE and i < (2/6) * GRID_SIZE + GRID_SIZE/18:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = 0
		elif i >= (2/6) * GRID_SIZE + GRID_SIZE/18 and i < (3/6) * GRID_SIZE - GRID_SIZE/18:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = -MAX_SPEED
		elif i >= (3/6) * GRID_SIZE - GRID_SIZE/18 and i < (3/6) * GRID_SIZE + GRID_SIZE/18:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = 0
		elif i >= (3/6) * GRID_SIZE + GRID_SIZE/18 and i < (4/6) * GRID_SIZE - GRID_SIZE/18:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = MAX_SPEED
		elif i >= (4/6) * GRID_SIZE - GRID_SIZE/18 and i < (4/6) * GRID_SIZE:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = 0
		elif i >= (4/6) * GRID_SIZE and i < (5/6) * GRID_SIZE:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = -MAX_SPEED
		elif i >= (5/6) * GRID_SIZE and i < (5/6) * GRID_SIZE + GRID_SIZE/12:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = 0
		else:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind x'][j,i] = MAX_SPEED
	TERRAIN['overworld surface wind x'] = TERRAIN['overworld surface wind x'].scale(-MAX_SPEED,MAX_SPEED,0,255)
if 'overworld surface wind y' not in TERRAIN:
	TERRAIN['overworld surface wind y']: Screen[float] = Screen(GRID_SIZE,0)
	for i in range(GRID_SIZE):
		if i >= 0 and i < (1/6) * GRID_SIZE - GRID_SIZE/18:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = -MAX_SPEED
		elif i >= (1/6) * GRID_SIZE - GRID_SIZE/18 and i < (1/6) * GRID_SIZE:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = 0
		elif i >= (1/6) * GRID_SIZE and i < (2/6) * GRID_SIZE:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = MAX_SPEED
		elif i >= (2/6) * GRID_SIZE and i < (2/6) * GRID_SIZE + GRID_SIZE/18:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = 0
		elif i >= (2/6) * GRID_SIZE + GRID_SIZE/18 and i < (3/6) * GRID_SIZE - GRID_SIZE/18:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = -MAX_SPEED
		elif i >= (3/6) * GRID_SIZE - GRID_SIZE/18 and i < (3/6) * GRID_SIZE + GRID_SIZE/18:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = 0
		elif i >= (3/6) * GRID_SIZE + GRID_SIZE/18 and i < (4/6) * GRID_SIZE - GRID_SIZE/18:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = MAX_SPEED
		elif i >= (4/6) * GRID_SIZE - GRID_SIZE/18 and i < (4/6) * GRID_SIZE:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = 0
		elif i >= (4/6) * GRID_SIZE and i < (5/6) * GRID_SIZE:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = -MAX_SPEED
		elif i >= (5/6) * GRID_SIZE and i < (5/6) * GRID_SIZE + GRID_SIZE/12:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = 0
		else:
			for j in range(GRID_SIZE):
				TERRAIN['overworld surface wind y'][j,i] = MAX_SPEED
	TERRAIN['overworld surface wind y'] = TERRAIN['overworld surface wind y'].scale(-MAX_SPEED,MAX_SPEED,0,255)
if 'midworld land' not in TERRAIN:
	TERRAIN['midworld land']: Screen[bool] = TERRAIN['midworld surface'] > MIDWORLD_SEA_LEVEL
if 'overworld depth altitude' not in TERRAIN:
	TERRAIN['overworld depth altitude']: Screen[float] = OVERWORLD_DEPTH_OVERLAP_HEIGHT + MIDWORLD_ALTITUDE_OVERLAP_HEIGHT - TERRAIN['overworld depth']
if 'overworld thickness' not in TERRAIN:
	TERRAIN['overworld thickness']: Screen[float] = TERRAIN['overworld surface'] + TERRAIN['overworld depth']
if 'overworld-midworld connections' not in TERRAIN:
	TERRAIN['overworld-midworld connections']: Screen[bool] = TERRAIN['midworld surface'] >= TERRAIN['overworld depth altitude']
if 'midworld open space' not in TERRAIN:
	TERRAIN['midworld open space']: Screen[float] = ifMap(
		0,
		TERRAIN['overworld-midworld connections'],
		TERRAIN['overworld depth altitude'] - TERRAIN['midworld surface'],
	)
if 'overworld sunlight' not in TERRAIN:
	TERRAIN['overworld sunlight']: Screen[float] = getSunlight(
		size = GRID_SIZE,
		sunlightMax = OVERWORLD_SUNLIGHT_MAX,
		sunlightMin = OVERWORLD_SUNLIGHT_MIN,
		tilt = AXIS_TILT,
	)
if 'overworld temperature' not in TERRAIN:
	TERRAIN['overworld temperature']: Screen[float] = (TERRAIN['overworld sunlight'] + TERRAIN['overworld surface']) / 2
	TERRAIN['overworld temperature']: Screen[float] = TERRAIN['overworld temperature'] * (OVERWORLD_TEMPERATURE_MAX - OVERWORLD_TEMPERATURE_MIN)/GRID_SIZE + OVERWORLD_TEMPERATURE_MIN
	TERRAIN['overworld temperature']: Screen[float] = ifMap(
		TERRAIN['overworld temperature'],
		TERRAIN['overworld land'],
		TERRAIN['overworld temperature'] - OVERWORLD_TEMPERATURE_LAND_DIFFERENCE,
	)
	TERRAIN['overworld temperature']: Screen[float] = TERRAIN['overworld temperature'].scale(OVERWORLD_TEMPERATURE_MIN,OVERWORLD_TEMPERATURE_MAX,0,GRID_SIZE)
if 'snow' not in TERRAIN:
	TERRAIN['snow']: Screen[bool] = TERRAIN['overworld temperature'] <= SNOW_LEVEL
if 'overworld temperature derivative x+' not in TERRAIN:
	TERRAIN['overworld temperature derivative x+']: Screen[float] = keyMap(
		lambda x,y : TERRAIN['overworld temperature'][(x + 1) % GRID_SIZE,y] - TERRAIN['overworld temperature'][x,y],
		GRID_SIZE,
	)
if 'overworld temperature derivative y+' not in TERRAIN:
	TERRAIN['overworld temperature derivative y+']: Screen[float] = keyMap(
		lambda x,y : TERRAIN['overworld temperature'][x,(y + 1) % GRID_SIZE] - TERRAIN['overworld temperature'][x,y],
		GRID_SIZE,
	)
if 'overworld temperature derivative x-' not in TERRAIN:
	TERRAIN['overworld temperature derivative x-']: Screen[float] = keyMap(
		lambda x,y : TERRAIN['overworld temperature'][x,y] - TERRAIN['overworld temperature'][(x - 1) % GRID_SIZE,y],
		GRID_SIZE,
	)
if 'overworld temperature derivative y-' not in TERRAIN:
	TERRAIN['overworld temperature derivative y-']: Screen[float] = keyMap(
		lambda x,y : TERRAIN['overworld temperature'][x,y] - TERRAIN['overworld temperature'][x,(y - 1) % GRID_SIZE],
		GRID_SIZE,
	)
if 'overworld temperature derivative x' not in TERRAIN:
	TERRAIN['overworld temperature derivative x']: Screen[float] = (
		(TERRAIN['overworld temperature derivative x+'] + TERRAIN['overworld temperature derivative x-'])/2
	).scale(0,255)
if 'overworld temperature derivative y' not in TERRAIN:
	TERRAIN['overworld temperature derivative y']: Screen[float] = (
		(TERRAIN['overworld temperature derivative y+'] + TERRAIN['overworld temperature derivative y-'])/2
	).scale(0,255)
if 'overworld temperature' not in TERRAIN:
	TERRAIN['overworld temperature']: Screen[float] = scrMap(redBlueScale,TERRAIN['overworld temperature'])
if 'overworld-midworld connection edges' not in TERRAIN:
	offsets = {
		(-1,-1),
		(-1,0),
		(-1,1),
		(0,-1),
		(0,1),
		(1,-1),
		(1,0),
		(1,1),
	}
	TERRAIN['overworld-midworld connection edges']: Screen[bool] = keyMap(
		lambda x,y : not TERRAIN['overworld-midworld connections'][i,j] and any(
			TERRAIN['overworld-midworld connections'][(x + i) % GRID_SIZE,(y + j) % GRID_SIZE] for i,j in offsets
		),
		GRID_SIZE,
	)
if 'potential midworld water' not in TERRAIN:
	TERRAIN['potential midworld water']: Screen[bool] = TERRAIN['midworld land'] & ~(
		TERRAIN['overworld-midworld connections'] | TERRAIN['overworld land']
	)
if 'midworld water' not in TERRAIN:
	TERRAIN['midworld water']: Screen[float] = Screen(GRID_SIZE,0)
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
	TERRAIN['midworld water']: Screen[bool] = TERRAIN['midworld water'] >= 1
if 'overworld greenery' not in TERRAIN:
	overworld_surface_int = scrMap(int,TERRAIN['overworld surface'])
	TERRAIN['overworld greenery'] = ifMap(
		(255 << 16) | (255 << 8) | 255,
		TERRAIN['snow'],
		ifMap(
			overworld_surface_int << 8,
			TERRAIN['overworld land'],
			overworld_surface_int,
		)
	)
if 'midworld greenery' not in TERRAIN:
	midworld_surface_v1 = TERRAIN['midworld surface'] - MIDWORLD_SEA_LEVEL/2
	midworld_surface_v2 = TERRAIN['midworld surface'] + MIDWORLD_SEA_LEVEL
	midworld_surface_v3 = scrMap(int,midworld_surface_v1/2)
	TERRAIN['midworld greenery']: Screen[int] = ifMap(
		0,
		TERRAIN['overworld-midworld connections'],
		ifMap(
			scrMap(int,TERRAIN['midworld surface']),
			TERRAIN['midworld water'],
			ifMap(
				(
					midworld_surface_v3 << 16
				) | (
					scrMap(int,midworld_surface_v1) << 8
				) | (
					midworld_surface_v3
				),
				TERRAIN['midworld land'],
				(
					scrMap(int,midworld_surface_v2) << 16
				) | (
					scrMap(int,midworld_surface_v2/2) << 8
				),
			)
		),
	)
if 'overworld cloud density' not in TERRAIN:
	TERRAIN['overworld cloud density']: Screen[int] = keyMap(
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
	).scale(0,255)

storeTerrainValues(TERRAIN)

pygame.init()
CLOCK = pygame.time.Clock()

font = pygame.font.SysFont("Arial",20)

def drawMap(window,width,height) -> None:
	global pygame,FINAL_SCREEN_LAYOUT,SCREEN_LAYOUT

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

TERRAIN['overworld greenery'] = scrMap(intToColor,TERRAIN['overworld greenery'])
TERRAIN['midworld greenery'] = scrMap(intToColor,TERRAIN['midworld greenery'])

addColor(TERRAIN)

SCREEN_LAYOUT[0,0] = 'overworld greenery'
SCREEN_LAYOUT[1,0] = 'overworld temperature derivative x'
SCREEN_LAYOUT[2,0] = 'overworld temperature derivative y'

mapLayout(TERRAIN)

#W = (getMaxX(SCREEN_LAYOUT) + 1)*LENGTH
#H = (getMaxY(SCREEN_LAYOUT) + 1)*LENGTH
W = LENGTH
H = LENGTH

WINDOW = pygame.display.set_mode((W + UI_PANEL_WIDTH,H))
pygame.display.set_caption("Window")
DROPDOWN = Dropdown(
	x = W + UI_PANEL_MARGIN,
	y = UI_PANEL_MARGIN,
	width = UI_PANEL_WIDTH - 2 * UI_PANEL_MARGIN,
	height = 40,
	options = sorted(list(TERRAIN.keys())),
)

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		DROPDOWN.handle_event(event)
	ui_panel = pygame.Rect(W,0,UI_PANEL_WIDTH,H)
	pygame.draw.rect(WINDOW,UI_RECT_COLOR,ui_panel)
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			rect = pygame.Rect(
				i * CELL_SIZE,
				j * CELL_SIZE,
				CELL_SIZE,
				CELL_SIZE,
			)
			try:
				pygame.draw.rect(WINDOW,TERRAIN[DROPDOWN.selected][i,j],rect)
			except:
				print(TERRAIN[DROPDOWN.selected][i,j])
				raise
	DROPDOWN.draw(WINDOW)
	pygame.display.flip()
	CLOCK.tick(60)

pygame.quit()