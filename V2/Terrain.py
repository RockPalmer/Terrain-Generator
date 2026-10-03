import pygame,random,json
from perlin5 import perlin5
from Image import Image
from Video import Video
from PerlinGenerator import PerlinGenerator
from image_functions import (
	scrMap,
	ifMap,
)
from math import (
	cos,
	sin,
	tau,
	e,
)
from pathlib import Path
from numpy import array
from functools import reduce
from operator import or_
from typing import (
	Callable,
	Any,
)
from Dropdown import Dropdown
from Interval import Interval

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

GRID_SIZE: int = 128
CELL_SIZE: int = 4
FRAMES: int = 50
FRAME_SPEED: int|float = 1
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
UI_PANEL_WIDTH: int = 500
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
SNOW_LEVEL: int = 60

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

FREQUENCIES = [2**i for i in range(TERRAIN_NOISE_OCTAVES)]
ARGS: dict[str,dict] = {
	'perlin noise 0' : {
		'terrain' : [],
		'nonterrain' : {
			'TERRAIN_NOISE_OCTAVES' : TERRAIN_NOISE_OCTAVES,
		},
	},
	'perlin noise 1' : {
		'terrain' : [],
		'nonterrain' : {
			'TERRAIN_NOISE_OCTAVES' : TERRAIN_NOISE_OCTAVES,
		},
	},
	'perlin noise 2' : {
		'terrain' : [],
		'nonterrain' : {
			'TERRAIN_NOISE_OCTAVES' : TERRAIN_NOISE_OCTAVES,
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
	'overworld surface fluctuation' : {
		'terrain' : [
			'overworld surface original',
		],
		'nonterrain' : {},
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
			'NOISE_SEED0' : NOISE_SEED,
			'GRID_SIZE' : GRID_SIZE,
		}
	},
	'overworld surface' : {
		'terrain' : [
			'overworld surface original',
			'overworld surface fluctuation',
			'overworld land',
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
	'overworld true surface derivative x-' : {
		'terrain' : [
			'overworld true surface',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld true surface derivative x+' : {
		'terrain' : [
			'overworld true surface',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld true surface derivative x' : {
		'terrain' : [
			'overworld true surface derivative x+',
			'overworld true surface derivative x-',
		],
		'nonterrain' : {},
	},
	'overworld true surface derivative y-' : {
		'terrain' : [
			'overworld true surface',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld true surface derivative y+' : {
		'terrain' : [
			'overworld true surface',
		],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld true surface derivative y' : {
		'terrain' : [
			'overworld true surface derivative y+',
			'overworld true surface derivative y-',
		],
		'nonterrain' : {},
	},
	'overworld surface normal magnitude' : {
		'terrain' : [
			'overworld true surface derivative x',
			'overworld true surface derivative y',
		],
		'nonterrain' : {},
	},
	'overworld surface normal x' : {
		'terrain' : [
			'overworld true surface derivative x',
			'overworld surface normal magnitude',
		],
		'nonterrain' : {},
	},
	'overworld surface normal y' : {
		'terrain' : [
			'overworld true surface derivative y',
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
			'overworld distance from sea level',
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
	'overworld coastline land side' : {
		'terrain' : [
			'overworld land',
		],
		'nonterrain' : {},
	},
	'overworld coastline water side' : {
		'terrain' : [
			'overworld land',
		],
		'nonterrain' : {},
	},
	'overworld coastline' : {
		'terrain' : [
			'overworld coastline land side',
			'overworld coastline water side',
		],
		'nonterrain' : {},
	},
	'overworld distance from sea level' : {
		'terrain' : [
			'overworld surface',
		],
		'nonterrain' : {
			'OVERWORLD_SEA_LEVEL' : OVERWORLD_SEA_LEVEL,
		},
	},
}
for i in range(TERRAIN_NOISE_OCTAVES):
	ARGS[f"perlin noise 0 {i}"] = {
		'terrain' : [],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
			'NOISE_SEED0' : NOISE_SEED,
			'TERRAIN_NOISE_SCALE' : TERRAIN_NOISE_SCALE,
			f"FREQUENCY0_{i}" : FREQUENCIES[i],
		},
	}
	ARGS['perlin noise 0']['terrain'].append(f"perlin noise 0 {i}")
	ARGS[f"perlin noise 1 {i}"] = {
		'terrain' : [],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
			'NOISE_SEED1' : NOISE_SEED + 1,
			'TERRAIN_NOISE_SCALE' : TERRAIN_NOISE_SCALE,
			f"FREQUENCY1_{i}" : FREQUENCIES[i],
		},
	}
	ARGS['perlin noise 1']['terrain'].append(f"perlin noise 1 {i}")
	ARGS[f"perlin noise 2 {i}"] = {
		'terrain' : [],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
			'NOISE_SEED2' : NOISE_SEED + 2,
			'TERRAIN_NOISE_SCALE' : TERRAIN_NOISE_SCALE,
			f"FREQUENCY1_{2}" : FREQUENCIES[2],
		},
	}
	ARGS['perlin noise 2']['terrain'].append(f"perlin noise 2 {i}")
ARGUMENTS: dict = {name : getArguments(name,ARGS) for name in ARGS}

RANGE: dict[str,Interval] = {}

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
def perlinVideo(size: int,speed: int|float,frames: int,seed: int|float = 0,scale: int = 1,octaves: int = 1) -> Video[float]:
	gen = PerlinGenerator(
		size = size,
		seed = seed,
		scale = scale,
		octaves = octaves,
	)
	vid = Video(size,frames)
	for frame in range(frames):
		print(f"generating perlin noise frame {frame + 1}/{frames}...")
		t = frame * speed / frames
		vid[frame] = gen.getAtTime(t)
	return vid
def layeredPerlinNoise(size: int,seed: int|float = 0,scale: int = 1,octaves: int = 1) -> Image[float]:
	print('generating perlin noise layers...')
	frequencies = [2**octave for octave in range(octaves)]
	amplitudes = [0.5**octave for octave in range(octaves)]
	layers = [
		perlinNoise(size,seed,scale,frequency) * amplitude for frequency,amplitude in zip(frequencies,amplitudes)
	]
	return sum(layers) / sum(amplitudes)
def perlinNoise(size: int,seed: int,scale: int,frequency: float) -> Image[float]:
	print('generating perlin noise layer...')
	factor: float = tau / size
	x: Image[int] = Image(size,lambda x,y : x) * factor
	y: Image[int] = Image(size,lambda x,y : y) * factor
	zeros: Image[int] = Image(size,0)
	cos_x: Image[float] = scrMap(cos,x) * scale
	sin_x: Image[float] = scrMap(sin,x) * scale
	cos_y: Image[float] = scrMap(cos,y) * scale
	sin_y: Image[float] = scrMap(sin,y) * scale
	nx: Image[float] = cos_x * frequency
	ny: Image[float] = sin_x * frequency
	nz: Image[float] = cos_y * frequency
	nw: Image[float] = sin_y * frequency + seed
	return scrMap(perlin5,nx,ny,nz,nw,zeros)
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
def getCurrentTilt(day: int,tilt: int|float) -> float:
	return -tilt + day * (2*tilt)/365
def lattitudeToAngle(latt: int,size: int) -> float:
	return latt * tau/size
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
def smudge(trn: Image) -> Image:
	points = {(i,j) for i in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS) for j in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS)}
	screen = Image(GRID_SIZE)
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
def getHumidity(*,land: Image[bool]) -> Image:
	print('generating humidity...')
	offsets = [(x,y) for x in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS + 1) for y in range(-HUMIDITY_SMUDGE_RADIUS,HUMIDITY_SMUDGE_RADIUS + 1) if getDistance((0,0),(x,y)) <= HUMIDITY_SMUDGE_RADIUS]
	humidity = Image(GRID_SIZE)
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			points = [((i + x) % GRID_SIZE,(j + y) % GRID_SIZE) for x,y in offsets]
			humidity[i,j] = len([p for p in points if not land[p]])/len(points)
	return humidity
def getSunlight(size: int,sunlightMax: int|float,sunlightMin: int|float,tilt: int|float) -> Image[float]: # float[0,GRID_SIZE]
	print('generating sunlight...')
	values = [getAvgSunlightValue(
		lattitude = y,
		sunlightMax = sunlightMax,
		sunlightMin = sunlightMin,
		size = size,
		tilt = tilt,
	) for y in range(size)]
	return Image(
		size,
		lambda x,y : values[y],
	)
def getBodiesOfWater(land: Image[bool],seaLevel: int|float,depthMax: int|float,octaves: int,scale: int|float,seed: int,size: int) -> list[set[Point]]:
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
def addColor(trn: dict[str,Image]) -> None:
	keys = list(trn.keys())
	for k in keys:
		print(f"adding color to {k}...")
		if isinstance(trn[k][0,0],bool):
			trn[k] = scrMap(
				lambda v : (255,255,255) if v else (0,0,0),
				trn[k],
			)
		elif isinstance(trn[k][0,0],int|float):
			if RANGE[k] == Interval(0,255):
				trn[k] = scrMap(
					lambda v : (int(v),int(v),int(v)),
					trn[k],
				)
			elif RANGE[k] == Interval(0,(1 << 24) - 1) or RANGE[k] == Interval(0,255 << 16):
				trn[k] = scrMap(intToColor,trn[k])
			else:
				trn[k] = scrMap(
					lambda v : (int(v),int(v),int(v)),
					trn[k].scale(RANGE[k].min,RANGE[k].max,0,255),
				)
		elif isinstance(trn[k][0,0],tuple) and len(trn[k][0,0]) == 2:
			trn[k] = scrMap(
				lambda v : pointToColor(v),
				trn[k],
			)
def redBlueScale(value: int|float) -> int:
	return int(value) << 16 | (255 - int(value))
def intToColor(value: int|float) -> Color:
	return (
		(int(value) >> 16) & 0xFF,
		(int(value) >> 8) & 0xFF,
		int(value) & 0xFF,
	)
def storeTerrainValues(terrain: dict[str,Image]) -> None:
	for name in terrain:
		storeTerrain(name,terrain[name])
def storeTerrain(name: str,terrain: Image|Video) -> None:
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
	if isinstance(terrain,Image):
		with open(filename,mode = 'w') as f:
			f.write(json.dumps({
				'arguments' : ARGUMENTS[name],
				'type' : 'Image',
				'terrain' : [[terrain[x,y] for y in range(terrain.size)] for x in range(terrain.size)]
			}))
	elif isinstance(terrain,Video):
		with open(filename,mode = 'w') as f:
			f.write(json.dumps({
				'arguments' : ARGUMENTS[name],
				'type' : 'Video',
				'terrain' : [[[terrain[x,y,t] for y in range(terrain.size)] for x in range(terrain.size)] for t in range(terrain.length)]
			}))
	else:
		raise TypeError
def loadTerrainValues() -> dict[str,Image]:
	terrain = {}
	for entry in TERRAIN_DIRECTORY.iterdir():
		if not entry.is_file(): continue
		name = '_'.join(entry.name.split('_')[:-1])
		content = loadTerrain(entry)
		if content['arguments'] == ARGUMENTS[name]:
			match content['type']:
				case 'Image':
					terrain[name] = Image(
						len(content['terrain']),
						lambda x,y : content['terrain'][x][y],
					)
				case _:
					raise TypeError
	return terrain
def loadTerrain(filename: Path) -> dict[str,list|dict]:
	with open(filename,mode = 'r') as f:
		content = json.loads(f.read())
	return content
def getDependentTerrains(name: str) -> set[str]:
	args = set()
	for k,v in ARGS.items():
		if name in v['terrain']:
			args.add(k)
			args |= getDependentTerrains(k)
	return args
def cleanMapping(name: str,terrain: dict[str,Image]) -> None:
	for n in getDependentTerrains(name):
		if n in terrain:
			print(f"need to regenerate {n}...")
			del terrain[n]
def clearCache() -> None:
	for entry in TERRAIN_DIRECTORY.iterdir():
		entry.unlink()

TERRAIN = loadTerrainValues()
LENGTH: int = GRID_SIZE * CELL_SIZE

amplitudes = [0.5**i for i in range(TERRAIN_NOISE_OCTAVES)]
total_amplitude = sum(amplitudes)

clearCache()
for i in range(TERRAIN_NOISE_OCTAVES):
	str_val_0 = f"perlin noise 0 {i}"
	str_val_1 = f"perlin noise 1 {i}"
	str_val_2 = f"perlin noise 2 {i}"
	if str_val_0 not in TERRAIN:
		TERRAIN[str_val_0] = perlinNoise(
			size = GRID_SIZE,
			seed = NOISE_SEED,
			scale = TERRAIN_NOISE_SCALE,
			frequency = FREQUENCIES[i],
		)
		cleanMapping(str_val_0,TERRAIN)
	RANGE[str_val_0] = Interval(-1,1)
	if str_val_1 not in TERRAIN:
		TERRAIN[str_val_1] = perlinNoise(
			size = GRID_SIZE,
			seed = NOISE_SEED,
			scale = TERRAIN_NOISE_SCALE,
			frequency = FREQUENCIES[i],
		)
		cleanMapping(str_val_1,TERRAIN)
	RANGE[str_val_1] = Interval(-1,1)
	if str_val_2 not in TERRAIN:
		TERRAIN[str_val_2] = perlinNoise(
			size = GRID_SIZE,
			seed = NOISE_SEED,
			scale = TERRAIN_NOISE_SCALE,
			frequency = FREQUENCIES[i],
		)
		cleanMapping(str_val_2,TERRAIN)
	RANGE[str_val_2] = Interval(-1,1)
if 'perlin noise 0' not in TERRAIN:
	print('generating perlin noise 0...')
	'''
	TERRAIN['perlin noise 0']: Image[float] = sum(
		TERRAIN[f"perlin noise 0 {i}"] * amplitudes[i] for i in range(TERRAIN_NOISE_OCTAVES)
	) / total_amplitude
	'''
	TERRAIN['perlin noise 0']: Image[float] = layeredPerlinNoise(
		size = GRID_SIZE,
		seed = NOISE_SEED,
		scale = TERRAIN_NOISE_SCALE,
		octaves = TERRAIN_NOISE_OCTAVES,
	)
	cleanMapping('perlin noise 0',TERRAIN)
RANGE['perlin noise 0'] = Interval(-1,1)
if 'perlin noise 1' not in TERRAIN:
	print('generating perlin noise 1...')
	'''
	TERRAIN['perlin noise 1']: Image[float] = sum(
		TERRAIN[f"perlin noise 1 {i}"] * amplitudes[i] for i in range(TERRAIN_NOISE_OCTAVES)
	) / total_amplitude
	'''

	TERRAIN['perlin noise 1']: Image[float] = layeredPerlinNoise(
		size = GRID_SIZE,
		seed = NOISE_SEED + 1,
		scale = TERRAIN_NOISE_SCALE,
		octaves = TERRAIN_NOISE_OCTAVES,
	)
	cleanMapping('perlin noise 1',TERRAIN)
RANGE['perlin noise 1'] = Interval(-1,1)
if 'perlin noise 2' not in TERRAIN:
	print('generating perlin noise 2...')
	'''
	TERRAIN['perlin noise 2']: Image[float] = sum(
		TERRAIN[f"perlin noise 2 {i}"] * amplitudes[i] for i in range(TERRAIN_NOISE_OCTAVES)
	) / total_amplitude
	'''
	TERRAIN['perlin noise 2']: Image[float] = layeredPerlinNoise(
		size = GRID_SIZE,
		seed = NOISE_SEED + 2,
		scale = TERRAIN_NOISE_SCALE,
		octaves = TERRAIN_NOISE_OCTAVES,
	)
	cleanMapping('perlin noise 2',TERRAIN)
RANGE['perlin noise 2'] = Interval(-1,1)
if 'overworld surface original' not in TERRAIN:
	print('generating overworld surface original...')
	TERRAIN['overworld surface original']: Image[float] = TERRAIN['perlin noise 0'].scale(-1,1,OVERWORLD_SURFACE_MIN,OVERWORLD_SURFACE_MAX)
	cleanMapping('overworld surface original',TERRAIN)
RANGE['overworld surface original'] = Interval(OVERWORLD_SURFACE_MIN,OVERWORLD_SURFACE_MAX)
if 'overworld land' not in TERRAIN:
	print('generating overworld land...')
	TERRAIN['overworld land']: Image[bool] = TERRAIN['overworld surface original'] > OVERWORLD_SEA_LEVEL
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
	cleanMapping('overworld land',TERRAIN)
if 'overworld surface fluctuation' not in TERRAIN:
	print('generating overworld surface fluctuation...')
	TERRAIN['overworld surface fluctuation']: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : (
			(
				TERRAIN['overworld surface original'][(x + 1) % GRID_SIZE,(y + 1) % GRID_SIZE] - TERRAIN['overworld surface original'][x,y] +
				TERRAIN['overworld surface original'][(x + 1) % GRID_SIZE,y] - TERRAIN['overworld surface original'][x,y] +
				TERRAIN['overworld surface original'][(x + 1) % GRID_SIZE,(y - 1) % GRID_SIZE] - TERRAIN['overworld surface original'][x,y] +
				TERRAIN['overworld surface original'][x,(y + 1) % GRID_SIZE] - TERRAIN['overworld surface original'][x,y] +
				TERRAIN['overworld surface original'][x,(y - 1) % GRID_SIZE] - TERRAIN['overworld surface original'][x,y] +
				TERRAIN['overworld surface original'][(x - 1) % GRID_SIZE,(y + 1) % GRID_SIZE] - TERRAIN['overworld surface original'][x,y] +
				TERRAIN['overworld surface original'][(x - 1) % GRID_SIZE,y] - TERRAIN['overworld surface original'][x,y] +
				TERRAIN['overworld surface original'][(x - 1) % GRID_SIZE,(y - 1) % GRID_SIZE] - TERRAIN['overworld surface original'][x,y]
			)/8
		),
	).scale(0,1)
	cleanMapping('overworld surface fluctuation',TERRAIN)
RANGE['overworld surface fluctuation'] = Interval(0,1)
if 'overworld surface' not in TERRAIN:
	print('generating overworld surface...')
	TERRAIN['overworld surface']: Image[float] = ifMap(
		(
			(
				TERRAIN['overworld surface original'] - OVERWORLD_SEA_LEVEL
			) * (
				1 + TERRAIN['overworld surface fluctuation']
			) + OVERWORLD_SEA_LEVEL
		),
		TERRAIN['overworld land'],
		TERRAIN['overworld surface original'],
	)
	cleanMapping('overworld surface',TERRAIN)
RANGE['overworld surface'] = RANGE['overworld surface original']
if 'overworld depth' not in TERRAIN:
	print('generating overworld depth...')
	TERRAIN['overworld depth']: Image[float] = TERRAIN['perlin noise 1'].scale(-1,1,OVERWORLD_DEPTH_MIN,OVERWORLD_DEPTH_MAX)
	cleanMapping('overworld depth',TERRAIN)
RANGE['overworld depth'] = Interval(OVERWORLD_DEPTH_MIN,OVERWORLD_DEPTH_MAX)
if 'midworld surface' not in TERRAIN:
	print('generating midworld surface...')
	TERRAIN['midworld surface']: Image[float] = TERRAIN['perlin noise 2'].scale(-1,1,MIDWORLD_SURFACE_MIN,MIDWORLD_SURFACE_MAX)
	cleanMapping('midworld surface',TERRAIN)
RANGE['midworld surface'] = Interval(MIDWORLD_SURFACE_MIN,MIDWORLD_SURFACE_MAX)
if 'overworld coastline land side' not in TERRAIN:
	print('generating overworld coastline land side...')
	x = Image(
		GRID_SIZE,
		lambda x,y : not all(
			TERRAIN['overworld land'][
				(x + i) % GRID_SIZE,
				(y + j) % GRID_SIZE,
			] for i in range(-1,2) for j in range(-1,2)
		),
	)
	TERRAIN['overworld coastline land side']: Image[bool] = TERRAIN['overworld land'] & x
	cleanMapping('overworld coastline land side',TERRAIN)
if 'overworld coastline water side' not in TERRAIN:
	print('generating overworld coastline water side...')
	x = Image(
		GRID_SIZE,
		lambda x,y : any(
			TERRAIN['overworld land'][
				(x + i) % GRID_SIZE,
				(y + j) % GRID_SIZE,
			] for i in range(-1,2) for j in range(-1,2)
		),
	)
	TERRAIN['overworld coastline water side']: Image[bool] = ~TERRAIN['overworld land'] & x
	cleanMapping('overworld coastline water side',TERRAIN)
if 'overworld coastline' not in TERRAIN:
	print('generating overworld coastline...')
	TERRAIN['overworld coastline'] = TERRAIN['overworld coastline land side'] | TERRAIN['overworld coastline water side']
	cleanMapping('overworld coastline',TERRAIN)
if 'overworld bodies of water' not in TERRAIN:
	print('generating overworld bodies of water...')
	colors = []
	rng = random.Random(NOISE_SEED)
	while len(colors) < len(bodiesMap):
		c = rng.randint(0,255 << 16)
		if c not in colors:
			colors.append(c)
	TERRAIN['overworld bodies of water']: Image[int|None] = Image(GRID_SIZE)
	for i,body in enumerate(bodiesMap):
		for point in body:
			TERRAIN['overworld bodies of water'][point] = colors[i]
	TERRAIN['overworld bodies of water']: Image[int] = ifMap(
		0,
		TERRAIN['overworld bodies of water'].isNone(),
		TERRAIN['overworld bodies of water'],
	)
	cleanMapping('overworld bodies of water',TERRAIN)
RANGE['overworld bodies of water'] = Interval(0,255 << 16)
if 'overworld true surface' not in TERRAIN:
	print('generating overworld true surface...')
	TERRAIN['overworld true surface']: Image[float] = ifMap(
		TERRAIN['overworld surface'],
		TERRAIN['overworld land'],
		OVERWORLD_SEA_LEVEL,
	)
	cleanMapping('overworld true surface',TERRAIN)
RANGE['overworld true surface'] = RANGE['overworld surface'] | OVERWORLD_SEA_LEVEL
if 'overworld true surface derivative x-' not in TERRAIN:
	print('generating overworld true surface derivative x-...')
	TERRAIN['overworld true surface derivative x-']: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld true surface'][x,y] - TERRAIN['overworld true surface'][(x - 1) % GRID_SIZE,y],
	)
	cleanMapping('overworld true surface derivative x-',TERRAIN)
RANGE['overworld true surface derivative x-'] = RANGE['overworld true surface'] - RANGE['overworld true surface']
if 'overworld true surface derivative x+' not in TERRAIN:
	print('generating overworld true surface derivative x+...')
	TERRAIN['overworld true surface derivative x+']: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld true surface'][(x + 1) % GRID_SIZE,y] - TERRAIN['overworld true surface'][x,y],
	)
	cleanMapping('overworld true surface derivative x+',TERRAIN)
RANGE['overworld true surface derivative x+'] = RANGE['overworld true surface'] - RANGE['overworld true surface']
if 'overworld true surface derivative x' not in TERRAIN:
	print('generating overworld true surface derivative x...')
	TERRAIN['overworld true surface derivative x']: Image[float] = (TERRAIN['overworld true surface derivative x-'] + TERRAIN['overworld true surface derivative x+']) / 2
	cleanMapping('overworld true surface derivative x',TERRAIN)
RANGE['overworld true surface derivative x'] = (RANGE['overworld true surface derivative x-'] + RANGE['overworld true surface derivative x+']) / 2
if 'overworld true surface derivative y-' not in TERRAIN:
	print('generating overworld true surface derivative y-...')
	TERRAIN['overworld true surface derivative y-']: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld true surface'][x,y] - TERRAIN['overworld true surface'][x,(y - 1) % GRID_SIZE],
	)
	cleanMapping('overworld true surface derivative y-',TERRAIN)
RANGE['overworld true surface derivative y-'] = RANGE['overworld true surface'] - RANGE['overworld true surface']
if 'overworld true surface derivative y+' not in TERRAIN:
	print('generating overworld true surface derivative y+...')
	TERRAIN['overworld true surface derivative y+']: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld true surface'][x,(y + 1) % GRID_SIZE] - TERRAIN['overworld true surface'][x,y],
	)
	cleanMapping('overworld true surface derivative y+',TERRAIN)
RANGE['overworld true surface derivative y+'] = RANGE['overworld true surface'] - RANGE['overworld true surface']
if 'overworld true surface derivative y' not in TERRAIN:
	print('generating overworld true surface derivative y...')
	TERRAIN['overworld true surface derivative y'] = (TERRAIN['overworld true surface derivative y-'] + TERRAIN['overworld true surface derivative y+']) / 2
	cleanMapping('overworld true surface derivative y',TERRAIN)
RANGE['overworld true surface derivative y'] = (RANGE['overworld true surface derivative y-'] + RANGE['overworld true surface derivative y+']) / 2
if 'overworld surface normal magnitude' not in TERRAIN:
	print('generating overworld surface normal magnitude...')
	TERRAIN['overworld surface normal magnitude']: Image[float] = (1 + TERRAIN['overworld true surface derivative x']**2 + TERRAIN['overworld true surface derivative y']**2)**0.5
	cleanMapping('overworld surface normal magnitude',TERRAIN)
RANGE['overworld surface normal magnitude'] = (1 + RANGE['overworld true surface derivative x']**2 + RANGE['overworld true surface derivative y']**2)**0.5
if 'overworld surface normal x' not in TERRAIN:
	print('generating overworld surface normal x...')
	TERRAIN['overworld surface normal x']: Image[float] = -TERRAIN['overworld true surface derivative x'] / TERRAIN['overworld surface normal magnitude']
	cleanMapping('overworld surface normal x',TERRAIN)
RANGE['overworld surface normal x'] = -RANGE['overworld true surface derivative x'] / RANGE['overworld surface normal magnitude']
if 'overworld surface normal y' not in TERRAIN:
	print('generating overworld surface normal y...')
	TERRAIN['overworld surface normal y']: Image[float] = -TERRAIN['overworld true surface derivative y'] / TERRAIN['overworld surface normal magnitude']
	cleanMapping('overworld surface normal y',TERRAIN)
RANGE['overworld surface normal y'] = -RANGE['overworld true surface derivative y'] / RANGE['overworld surface normal magnitude']
if 'overworld surface normal z' not in TERRAIN:
	print('generating overworld surface normal z...')
	TERRAIN['overworld surface normal z']: Image[float] = 1 / TERRAIN['overworld surface normal magnitude']
	cleanMapping('overworld surface normal z',TERRAIN)
RANGE['overworld surface normal z'] = 1 / RANGE['overworld surface normal magnitude']
if 'midworld land' not in TERRAIN:
	print('generating midworld land...')
	TERRAIN['midworld land']: Image[bool] = TERRAIN['midworld surface'] > MIDWORLD_SEA_LEVEL
	cleanMapping('midworld land',TERRAIN)
if 'overworld depth altitude' not in TERRAIN:
	print('generating overworld depth altitude...')
	TERRAIN['overworld depth altitude']: Image[float] = OVERWORLD_DEPTH_OVERLAP_HEIGHT + MIDWORLD_ALTITUDE_OVERLAP_HEIGHT - TERRAIN['overworld depth']
	cleanMapping('overworld depth altitude',TERRAIN)
RANGE['overworld depth altitude'] = OVERWORLD_DEPTH_OVERLAP_HEIGHT + MIDWORLD_ALTITUDE_OVERLAP_HEIGHT - RANGE['overworld depth']
if 'overworld thickness' not in TERRAIN:
	print('generating overworld thickness...')
	TERRAIN['overworld thickness']: Image[float] = TERRAIN['overworld surface'] + TERRAIN['overworld depth']
	cleanMapping('overworld thickness',TERRAIN)
RANGE['overworld thickness'] = RANGE['overworld surface'] + RANGE['overworld depth']
if 'overworld-midworld connections' not in TERRAIN:
	print('generating overworld-midworld connections...')
	TERRAIN['overworld-midworld connections']: Image[bool] = TERRAIN['midworld surface'] >= TERRAIN['overworld depth altitude']
	cleanMapping('overworld-midworld connections',TERRAIN)
if 'midworld open space' not in TERRAIN:
	print('generating midworld open space...')
	TERRAIN['midworld open space']: Image[float] = ifMap(
		0,
		TERRAIN['overworld-midworld connections'],
		TERRAIN['overworld depth altitude'] - TERRAIN['midworld surface'],
	)
	cleanMapping('midworld open space',TERRAIN)
RANGE['midworld open space'] = 0 | (RANGE['overworld depth altitude'] - RANGE['midworld surface'])
if 'overworld sunlight' not in TERRAIN:
	print('generating overworld sunlight...')
	TERRAIN['overworld sunlight']: Image[float] = getSunlight(
		size = GRID_SIZE,
		sunlightMax = OVERWORLD_SUNLIGHT_MAX,
		sunlightMin = OVERWORLD_SUNLIGHT_MIN,
		tilt = AXIS_TILT,
	)
	cleanMapping('overworld sunlight',TERRAIN)
RANGE['overworld sunlight'] = Interval(OVERWORLD_SUNLIGHT_MIN,OVERWORLD_SUNLIGHT_MAX)
if 'overworld distance from sea level' not in TERRAIN:
	print('generating overworld distance from sea level...')
	TERRAIN['overworld distance from sea level']: Image[float] = abs(TERRAIN['overworld surface'] - OVERWORLD_SEA_LEVEL)
	cleanMapping('overworld distance from sea level',TERRAIN)
RANGE['overworld distance from sea level'] = abs(RANGE['overworld surface'] - OVERWORLD_SEA_LEVEL)
if 'overworld temperature' not in TERRAIN:
	print('generating overworld temperature...')
	TERRAIN['overworld temperature']: Image[float] = (TERRAIN['overworld sunlight'] + (RANGE['overworld distance from sea level'].max - TERRAIN['overworld distance from sea level']))/2
	TERRAIN['overworld temperature']: Image[float] = ifMap(
		TERRAIN['overworld temperature'],
		TERRAIN['overworld land'],
		TERRAIN['overworld temperature'] - OVERWORLD_TEMPERATURE_LAND_DIFFERENCE,
	)
	cleanMapping('overworld temperature',TERRAIN)
RANGE['overworld temperature'] = (
	(RANGE['overworld sunlight'] + (RANGE['overworld distance from sea level'].max - RANGE['overworld distance from sea level']))
) | (
	RANGE['overworld sunlight'] + (RANGE['overworld distance from sea level'].max - RANGE['overworld distance from sea level']) - OVERWORLD_TEMPERATURE_LAND_DIFFERENCE
)
if 'snow' not in TERRAIN:
	print('generating snow...')
	TERRAIN['snow']: Image[bool] = TERRAIN['overworld temperature'] <= SNOW_LEVEL
	cleanMapping('snow',TERRAIN)
if 'overworld temperature derivative x+' not in TERRAIN:
	print('generating overworld temperature derivative x+...')
	TERRAIN['overworld temperature derivative x+']: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld temperature'][(x + 1) % GRID_SIZE,y] - TERRAIN['overworld temperature'][x,y],
	)
	cleanMapping('overworld temperature derivative x+',TERRAIN)
RANGE['overworld temperature derivative x+'] = RANGE['overworld temperature'] - RANGE['overworld temperature']
if 'overworld temperature derivative y+' not in TERRAIN:
	print('generating overworld temperature derivative y+...')
	TERRAIN['overworld temperature derivative y+']: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld temperature'][x,(y + 1) % GRID_SIZE] - TERRAIN['overworld temperature'][x,y],
	)
	cleanMapping('overworld temperature derivative y+',TERRAIN)
RANGE['overworld temperature derivative y+'] = RANGE['overworld temperature'] - RANGE['overworld temperature']
if 'overworld temperature derivative x-' not in TERRAIN:
	print('generating overworld temperature derivative x-...')
	TERRAIN['overworld temperature derivative x-']: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld temperature'][x,y] - TERRAIN['overworld temperature'][(x - 1) % GRID_SIZE,y],
	)
	cleanMapping('overworld temperature derivative x-',TERRAIN)
RANGE['overworld temperature derivative x-'] = RANGE['overworld temperature'] - RANGE['overworld temperature']
if 'overworld temperature derivative y-' not in TERRAIN:
	print('generating overworld temperature derivative y-...')
	TERRAIN['overworld temperature derivative y-']: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld temperature'][x,y] - TERRAIN['overworld temperature'][x,(y - 1) % GRID_SIZE],
	)
	cleanMapping('overworld temperature derivative y-',TERRAIN)
RANGE['overworld temperature derivative y-'] = RANGE['overworld temperature'] - RANGE['overworld temperature']
if 'overworld temperature derivative x' not in TERRAIN:
	print('generating overworld temperature derivative x...')
	TERRAIN['overworld temperature derivative x']: Image[float] = (TERRAIN['overworld temperature derivative x+'] + TERRAIN['overworld temperature derivative x-'])/2
	cleanMapping('overworld temperature derivative x',TERRAIN)
RANGE['overworld temperature derivative x'] = (RANGE['overworld temperature derivative x+'] + RANGE['overworld temperature derivative x-'])/2
if 'overworld temperature derivative y' not in TERRAIN:
	print('generating overworld temperature derivative y...')
	TERRAIN['overworld temperature derivative y']: Image[float] = (TERRAIN['overworld temperature derivative y+'] + TERRAIN['overworld temperature derivative y-'])/2
	cleanMapping('overworld temperature derivative y',TERRAIN)
RANGE['overworld temperature derivative y'] = (RANGE['overworld temperature derivative y+'] + RANGE['overworld temperature derivative y-'])/2
if 'overworld-midworld connection edges' not in TERRAIN:
	print('generating overworld-midworld connection edges...')
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
	TERRAIN['overworld-midworld connection edges']: Image[bool] = Image(
		GRID_SIZE,
		lambda x,y : not TERRAIN['overworld-midworld connections'][x,y] and any(
			TERRAIN['overworld-midworld connections'][(x + i) % GRID_SIZE,(y + j) % GRID_SIZE] for i,j in offsets
		),
	)
	cleanMapping('overworld-midworld connection edges',TERRAIN)
if 'potential midworld water' not in TERRAIN:
	print('generating potential midworld water...')
	TERRAIN['potential midworld water']: Image[bool] = TERRAIN['midworld land'] & ~(
		TERRAIN['overworld-midworld connections'] | TERRAIN['overworld land']
	)
	cleanMapping('potential midworld water',TERRAIN)
if 'midworld water' not in TERRAIN:
	print('generating midworld water...')
	TERRAIN['midworld water']: Image[float] = Image(GRID_SIZE,0)
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
	TERRAIN['midworld water']: Image[bool] = TERRAIN['midworld water'] >= 1
	cleanMapping('midworld water',TERRAIN)
if 'overworld greenery' not in TERRAIN:
	print('generating overworld greenery...')
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
	cleanMapping('overworld greenery',TERRAIN)
RANGE['overworld greenery'] = Interval(0,(1 << 24) - 1)
if 'midworld greenery' not in TERRAIN:
	print('generating midworld greenery...')
	midworld_surface_v1 = TERRAIN['midworld surface'] - MIDWORLD_SEA_LEVEL/2
	midworld_surface_v2 = TERRAIN['midworld surface'] + MIDWORLD_SEA_LEVEL
	midworld_surface_v3 = scrMap(int,midworld_surface_v1/2)
	TERRAIN['midworld greenery']: Image[int] = ifMap(
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
	cleanMapping('midworld greenery',TERRAIN)
RANGE['midworld greenery'] = Interval(0,(1 << 24) - 1)
if 'overworld cloud density' not in TERRAIN:
	print('generating overworld cloud density...')
	TERRAIN['overworld cloud density']: Image[float] = Image(
		GRID_SIZE,
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
	)
	cleanMapping('overworld cloud density',TERRAIN)
values = {v for v in TERRAIN['overworld cloud density']}
RANGE['overworld cloud density'] = Interval(
	min(values),
	max(values),
)

storeTerrainValues(TERRAIN)

pygame.init()
CLOCK = pygame.time.Clock()

font = pygame.font.SysFont("Arial",20)

addColor(TERRAIN)

WINDOW = pygame.display.set_mode((LENGTH + UI_PANEL_WIDTH,LENGTH))
pygame.display.set_caption("Window")
DROPDOWN = Dropdown(
	x = LENGTH + UI_PANEL_MARGIN,
	y = UI_PANEL_MARGIN,
	width = UI_PANEL_WIDTH - 2 * UI_PANEL_MARGIN,
	height = 40,
	options = sorted(list(TERRAIN.keys())),
)

# Keep the window open
current_selected = DROPDOWN.selected
running = True
index = 0
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		DROPDOWN.handle_event(event)
	ui_panel = pygame.Rect(LENGTH,0,UI_PANEL_WIDTH,LENGTH)
	pygame.draw.rect(WINDOW,UI_RECT_COLOR,ui_panel)
	if current_selected != DROPDOWN.selected:
		print(DROPDOWN.selected)
		current_selected = DROPDOWN.selected
	sel = TERRAIN[DROPDOWN.selected]
	if isinstance(sel,Image):
		for i in range(GRID_SIZE):
			for j in range(GRID_SIZE):
				rect = pygame.Rect(
					i * CELL_SIZE,
					j * CELL_SIZE,
					CELL_SIZE,
					CELL_SIZE,
				)
				try:
					pygame.draw.rect(WINDOW,sel[i,j],rect)
				except:
					print(sel[i,j])
					raise
	else:
		k = (index // 10) % FRAMES
		for i in range(GRID_SIZE):
			for j in range(GRID_SIZE):
				rect = pygame.Rect(
					i * CELL_SIZE,
					j * CELL_SIZE,
					CELL_SIZE,
					CELL_SIZE,
				)
				try:
					pygame.draw.rect(WINDOW,sel,rect)
				except:
					print(TERRAIN[DROPDOWN.selected][i,j,k])
					raise
	index += 1
	DROPDOWN.draw(WINDOW)
	pygame.display.flip()
	CLOCK.tick(60)

pygame.quit()