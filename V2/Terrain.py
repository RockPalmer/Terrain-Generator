import pygame,random,json
from perlin4 import perlin4
from perlin5 import perlin5
from perlin6 import perlin6
from perlin import perlin
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
	pi,
	e,
	acos,
	floor,
	ceil,
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
from NoiseBlock import NoiseBlock
from collections import deque

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

NOISE_DIRECTORY = Path('noise')
NOISE_DIRECTORY.mkdir(parents = True,exist_ok = True)

GRID_SIZE: int = 256
CELL_SIZE: int = 4
OVERWORLD_SURFACE_RANGE: Interval = Interval(0,255)
OVERWORLD_DEPTH_RANGE: Interval = Interval(0,255)
MIDWORLD_SURFACE_RANGE: Interval = Interval(0,255)
OVERWORLD_TEMPERATURE_RANGE: Interval = Interval(-89.2,56.7)
OVERWORLD_SUNLIGHT_RANGE: Interval = Interval(0,255)
OVERWORLD_PRESSURE_RANGE: Interval = Interval(0,255)
OVERWORLD_HUMIDITY_RANGE: Interval = Interval(0,255)
OVERWORLD_RAIN_RANGE: Interval = Interval(0,255)
OVERWORLD_SNOW_RANGE: Interval = Interval(0,255)
OVERWORLD_WATER_RATIO = 0.71
MIDWORLD_WATER_RATIO = 0.4
TERRAIN_NOISE_SCALE: int = 1
OVERWORLD_PRESSURE_SCALE: float = 0.75
OVERWORLD_PRESSURE_FREQUENCY: int|float = 1
TERRAIN_NOISE_OCTAVES: int = 8
NOISE_SEED: int = 600
AXIS_TILT: float = 23.44 * tau/360
UI_PANEL_WIDTH: int = 500
UI_PANEL_MARGIN: int = 20
UI_RECT_COLOR: Color = (255,198,183)
MAX_COLOR_INTEGER: int = 255**3 - 1
MAX_POINT_INTEGER: int = GRID_SIZE**2 - 1
OVERWORLD_DEPTH_OVERLAP_HEIGHT_FACTOR: float = 0.5
MIDWORLD_WATER_FACTOR: float = 1.5
OVERWORLD_TEMPERATURE_LAND_DIFFERENCE: int = 6
OVERWORLD_SNOW_LEVEL: int = 150
OVERWORLD_ICE_LEVEL: int = -40
WATER_RATIO_RADIUS: int = 12
OVERWORLD_CLOUD_FACTOR = 0.6
OVERWORLD_CLOUD_LEVEL = OVERWORLD_CLOUD_FACTOR * (OVERWORLD_RAIN_RANGE.max - OVERWORLD_RAIN_RANGE.min) + OVERWORLD_RAIN_RANGE.min

RADIUS: float = GRID_SIZE / tau
MIDWORLD_ALTITUDE_OVERLAP_HEIGHT_FACTOR: float = OVERWORLD_DEPTH_OVERLAP_HEIGHT_FACTOR

OVERWORLD_DEPTH_OVERLAP_HEIGHT: float = OVERWORLD_DEPTH_OVERLAP_HEIGHT_FACTOR * OVERWORLD_DEPTH_RANGE.max
MIDWORLD_ALTITUDE_OVERLAP_HEIGHT: float = MIDWORLD_ALTITUDE_OVERLAP_HEIGHT_FACTOR * MIDWORLD_SURFACE_RANGE.max
OVERWORLD_THICKNESS_MAX: float = OVERWORLD_SURFACE_RANGE.max + OVERWORLD_DEPTH_RANGE.max

FREQUENCIES = [2**i for i in range(TERRAIN_NOISE_OCTAVES)]
ARGS: dict[str,dict] = {
	'overworld clouds' : {
		'terrain' : [
			'overworld rain',
			'overworld snow',
		],
		'nonterrain' : {
			'OVERWORLD_CLOUD_LEVEL' : OVERWORLD_CLOUD_LEVEL,
		},
	},
	'overworld surface original' : {
		'terrain' : [],
		'nonterrain' : {
			'OVERWORLD_SURFACE_MAX' : OVERWORLD_SURFACE_RANGE.max,
			'OVERWORLD_SURFACE_MIN' : OVERWORLD_SURFACE_RANGE.min,
		},
	},
	'overworld land' : {
		'terrain' : [
			'overworld surface original',
		],
		'nonterrain' : {
			'OVERWORLD_WATER_RATIO' : OVERWORLD_WATER_RATIO,
		},
	},
	'overworld surface fluctuation' : {
		'terrain' : [
			'overworld surface original',
		],
		'nonterrain' : {},
	},
	'overworld surface' : {
		'terrain' : [
			'overworld surface original',
			'overworld land',
			'overworld surface fluctuation',
		],
		'nonterrain' : {},
	},
	'overworld depth' : {
		'terrain' : [],
		'nonterrain' : {
			'OVERWORLD_DEPTH_MAX' : OVERWORLD_DEPTH_RANGE.max,
			'OVERWORLD_DEPTH_MIN' : OVERWORLD_DEPTH_RANGE.min,
		},
	},
	'midworld surface' : {
		'terrain' : [],
		'nonterrain' : {
			'MIDWORLD_SURFACE_MAX' : MIDWORLD_SURFACE_RANGE.max,
			'MIDWORLD_SURFACE_MIN' : MIDWORLD_SURFACE_RANGE.min,
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
			'overworld coastline water side',
			'overworld coastline land side',
		],
		'nonterrain' : {},
	},
	'overworld true surface' : {
		'terrain' : [
			'overworld surface',
			'overworld land',
		],
		'nonterrain' : {
			'WATER_RATIO_RADIUS' : WATER_RATIO_RADIUS,
		},
	},
	'overworld true surface differential x' : {
		'terrain' : [
			'overworld true surface',
		],
		'nonterrain' : {},
	},
	'overworld true surface differential y' : {
		'terrain' : [
			'overworld true surface',
		],
		'nonterrain' : {},
	},
	'midworld land' : {
		'terrain' : [
			'midworld surface',
		],
		'nonterrain' : {
			'MIDWORLD_WATER_RATIO' : MIDWORLD_WATER_RATIO,
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
			'OVERWORLD_SUNLIGHT_MAX' : OVERWORLD_SUNLIGHT_RANGE.max,
			'OVERWORLD_SUNLIGHT_MIN' : OVERWORLD_SUNLIGHT_RANGE.min,
			'AXIS_TILT' : AXIS_TILT,
		},
	},
	'overworld distance from sea level' : {
		'terrain' : [
			'overworld surface',
		],
		'nonterrain' : {
			'OVERWORLD_WATER_RATIO' : OVERWORLD_WATER_RATIO,
		},
	},
	'overworld general wind magnitude' : {
		'terrain' : [],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld general wind angle' : {
		'terrain' : [],
		'nonterrain' : {
			'GRID_SIZE' : GRID_SIZE,
		},
	},
	'overworld pressure' : {
		'terrain' : [
			'overworld true surface',
			'overworld sunlight',
		],
		'nonterrain' : {
			'OVERWORLD_PRESSURE_MAX' : OVERWORLD_PRESSURE_RANGE.max,
			'OVERWORLD_PRESSURE_MIN' : OVERWORLD_PRESSURE_RANGE.min,
		},
	},
	'overworld pressure differential x' : {
		'terrain' : [
			'overworld pressure',
		],
		'nonterrain' : {},
	},
	'overworld pressure differential y' : {
		'terrain' : [
			'overworld pressure',
		],
		'nonterrain' : {},
	},
	'overworld temperature' : {
		'terrain' : [
			'overworld sunlight',
			'overworld distance from sea level',
			'overworld land',
		],
		'nonterrain' : {
			'OVERWORLD_TEMPERATURE_LAND_DIFFERENCE' : OVERWORLD_TEMPERATURE_LAND_DIFFERENCE,
			'OVERWORLD_TEMPERATURE_MAX' : OVERWORLD_TEMPERATURE_RANGE.max,
			'OVERWORLD_TEMPERATURE_MIN' : OVERWORLD_TEMPERATURE_RANGE.min,
		},
	},
	'overworld water ratio' : {
		'terrain' : [
			'overworld land',
		],
		'nonterrain' : {
			'WATER_RATIO_RADIUS' : WATER_RATIO_RADIUS,
		},
	},
	'overworld humidity' : {
		'terrain' : [
			'overworld pressure',
			'overworld temperature',
			'overworld water ratio',
		],
		'nonterrain' : {
			'OVERWORLD_HUMIDITY_MAX' : OVERWORLD_HUMIDITY_RANGE.max,
			'OVERWORLD_HUMIDITY_MIN' : OVERWORLD_HUMIDITY_RANGE.min,
		},
	},
	'overworld rain' : {
		'terrain' : [
			'overworld temperature',
			'overworld humidity',
		],
		'nonterrain' : {
			'OVERWORLD_RAIN_MAX' : OVERWORLD_RAIN_RANGE.max,
			'OVERWORLD_RAIN_MIN' : OVERWORLD_RAIN_RANGE.min,
		},
	},
	'overworld snow' : {
		'terrain' : [
			'overworld temperature',
			'overworld humidity',
			'overworld pressure',
		],
		'nonterrain' : {
			'OVERWORLD_RAIN_MAX' : OVERWORLD_RAIN_RANGE.max,
			'OVERWORLD_RAIN_MIN' : OVERWORLD_RAIN_RANGE.min,
		},
	},
	'snow' : {
		'terrain' : [
			'overworld snow',
		],
		'nonterrain' : {
			'OVERWORLD_SNOW_LEVEL' : OVERWORLD_SNOW_LEVEL,
		},
	},
	'ice' : {
		'terrain' : [
			'overworld temperature',
			'overworld land',
		],
		'nonterrain' : {
			'OVERWORLD_ICE_LEVEL' : OVERWORLD_ICE_LEVEL,
		},
	},
	'overworld temperature differential x' : {
		'terrain' : [
			'overworld temperature',
		],
		'nonterrain' : {},
	},
	'overworld temperature differential y' : {
		'terrain' : [
			'overworld temperature',
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
			'overworld land',
			'overworld-midworld connections',
		],
		'nonterrain' : {},
	},
	'midworld water' : {
		'terrain' : [
			'potential midworld water',
			'overworld thickness',
			'midworld surface',
			'midworld land',
		],
		'nonterrain' : {
			'MIDWORLD_WATER_FACTOR' : MIDWORLD_WATER_FACTOR,
			'OVERWORLD_THICKNESS_MAX' : OVERWORLD_THICKNESS_MAX,
		},
	},
	'overworld greenery' : {
		'terrain' : [
			'overworld surface',
			'snow',
			'overworld land',
		],
		'nonterrain' : {},
	},
	'midworld greenery' : {
		'terrain' : [
			'midworld surface',
			'overworld-midworld connections',
			'midworld water',
			'midworld land',
		],
		'nonterrain' : {
			'MIDWORLD_WATER_RATIO' : MIDWORLD_WATER_RATIO,
		},
	},
}
NOISE_DEPENDENCIES = set()
NOISE_MAP = {}
for i in range(TERRAIN_NOISE_OCTAVES):
	NOISE_DEPENDENCIES |= {
		(
			'overworld surface original',
			NoiseBlock(
				dimensions = 4,
				size = GRID_SIZE,
				seed = NOISE_SEED,
				scale = TERRAIN_NOISE_SCALE,
				frequency = FREQUENCIES[i],
				time = 0,
			),
		),(
			'overworld depth',
			NoiseBlock(
				dimensions = 4,
				size = GRID_SIZE,
				seed = NOISE_SEED + 1,
				scale = TERRAIN_NOISE_SCALE,
				frequency = FREQUENCIES[i],
				time = 0,
			),
		),(
			'midworld surface',
			NoiseBlock(
				dimensions = 4,
				size = GRID_SIZE,
				seed = NOISE_SEED + 2,
				scale = TERRAIN_NOISE_SCALE,
				frequency = FREQUENCIES[i],
				time = 0,
			),
		),
	}
NOISE_DEPENDENCIES.add(
	(
		'overworld pressure',
		NoiseBlock(
			dimensions = 4,
			size = GRID_SIZE,
			seed = NOISE_SEED + 3,
			scale = OVERWORLD_PRESSURE_SCALE,
			frequency = OVERWORLD_PRESSURE_FREQUENCY,
			time = 0,
		),
	)
)
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
def intToColor(value: int|float) -> Color:
	return (
		(int(value) >> 16) & 0xFF,
		(int(value) >> 8) & 0xFF,
		int(value) & 0xFF,
	)
def perlinNoise(block: NoiseBlock) -> Image[float]:
	print(f"generating {block}...")
	dimensions,size,seed,scale,frequency,time = tuple(block)
	seed_offset = seed
	noise_map = Image(size)
	for y in range(size):
		for x in range(size):
			# Map grid coordinates onto a torus
			angle_x = tau * x / size
			angle_y = tau * y / size
			nx = cos(angle_x) * scale * frequency
			ny = sin(angle_x) * scale * frequency
			nz = cos(angle_y) * scale * frequency
			nw = sin(angle_y) * scale * frequency + seed_offset
			noise_map[x,y] = perlin4(nx,ny,nz + time,nw)
	return noise_map
def perlinNoise2(block: NoiseBlock) -> Image[float]:
	print('generating perlin noise...')
	dimensions,size,seed,scale,frequency,time = tuple(block)
	factor = tau / scale
	x = Image(size,lambda i,j : i)
	y = Image(size,lambda i,j : j)
	angle_x = factor * x
	angle_y = factor * y
	nx = scrMap(cos,angle_x) * scale * frequency
	ny = scrMap(sin,angle_x) * scale * frequency
	nz = scrMap(cos,angle_y) * scale * frequency
	nw = scrMap(sin,angle_y) * scale * frequency + seed
	return scrMap(perlin4,nx,ny,nz + time,nw)
def pointToColor(point: Point) -> Color:
	value = round((point[0] * 255 + point[1]) * MAX_COLOR_INTEGER/MAX_POINT_INTEGER)
	return Color(value)
def getDistance(p1: Point, p2: Point) -> float:
	dx = abs(p1[0] - p2[0])
	dy = abs(p1[1] - p2[1])
	if dx > GRID_SIZE / 2: dx = GRID_SIZE - dx
	if dy > GRID_SIZE / 2: dy = GRID_SIZE - dy
	return (dx**2 + dy**2)**0.5
def getGenWindMagnitude(y: int|float,size: int) -> float:
	if y >= size / 4: return getGenWindMagnitude(y % (size / 4),size)
	return size / 8 - abs(y - size / 8)
def getGenWindAngle(y: int|float,size: int) -> float:
	if y <= size / 4: return 3 * pi - y * pi / (size / 4)
	if y < size / 2: return 3 * pi + (y - size / 4) * pi / (size / 4)
	if y == size / 2: return 0
	if y <= 3 * size / 4: return pi + (3 * size / 4 - y) * pi / (size / 4)
	return pi - (size - y) * pi / (size / 4)
def getNextPixelByAngle(start: Point,angle: float,size: int) -> Point:
	x,y = start
	if 0 <= angle and angle < pi / 2: return ((x + 1) % size,y)
	if pi / 2 < angle and angle < 3/2 * pi: return (x,(y - 1) % size)
	if 3/2 * pi <= angle and angle < 5/2 * pi: return ((x - 1) % size,y)
	if 5/2 * pi <= angle and angle < 7/2 * pi: return (x,(y + 1) % size)
	if 7/2 * pi <= angle and angle < 4 * pi: return ((x + 1) % size,y)
	raise ValueError
def getCurrentTilt(day: int,tilt: int|float) -> float: # [-tilt,tilt]
	return -tilt + day * 2 * tilt/365
def lattitudeToAngle(latt: int,size: int) -> float: # [0,tau]
	return latt * tau/size
def getAngleForDay(latt: int,day: int,size: int,tilt: int|float) -> float: # [0,tau]
	return (
		lattitudeToAngle(latt,size) + getCurrentTilt(day,tilt)
	) % tau
def getVectorForDay(latt: int,day: int,size: int,tilt: int|float) -> tuple[float,float]: # <[0,RADIUS],[0,RADIUS]>
	theta = getAngleForDay(latt,day,size,tilt) # [0,tau]
	return (
		(size/tau) * cos(theta), # [0,RADIUS]
		(size/tau) * sin(theta), # [0,RADIUS]
	)
def getSunlightValue(lattitude: int,day: int,size: int,tilt: int|float) -> float: # 
	# get angle 
	x,y = getVectorForDay(lattitude,day,size,tilt) # <[0,RADIUS],[0,RADIUS]>
	return x * -size/tau
def getNormalizedSunlightValue(lattitude: int,day: int,size: int,tilt: int|float) -> float:
	# Get average sunlight between top and bottom of globe
	return (
		getSunlightValue(lattitude,day,size,tilt) + getSunlightValue(size - lattitude,day,size,tilt)
	)/2
def getAvgSunlightValue(lattitude: int,sunlightMax: int|float,sunlightMin: int|float,size: int,tilt: int|float) -> float: # float[0,GRID_SIZE]
	# get sunlight at lattitude for each day of year
	values = [getNormalizedSunlightValue(lattitude,day,size,tilt) for day in range(365)]
	# return average sunlight value at that lattitude
	return (
		sum(values)/len(values) + (size/tau)**2
	) * (
		sunlightMax - sunlightMin
	) / (
		2 * (size/tau)**2
	) + sunlightMin
def getSunlight(size: int,sunlightMax: int|float,sunlightMin: int|float,tilt: int|float) -> Image[float]: # float[0,size]
	# get average sunlight for each pixel
	values = [
		getAvgSunlightValue(
			lattitude = y,
			sunlightMax = sunlightMax,
			sunlightMin = sunlightMin,
			size = size,
			tilt = tilt,
		) for y in range(size)
	]
	return Image(
		size,
		lambda x,y : values[y],
	)
def getGraphDistance(start: Point,end: Point,points: set[Point],size: int):
	def adj(p: Point) -> set[Point]:
		a,b = p
		offsets = {
			(-1,0),
			(1,0),
			(0,-1),
			(0,1),
		}
		for i,j in offsets:
			pt = (
				(a + i) % size,
				(b + j) % size,
			)
			if pt in points:
				yield pt
	dist = {p : -1 for p in points}
	dist[start] = 0
	q = deque([start])
	while q:
		node = q.popleft()
		if node == end:
			return dist[node]
		for neighbor in adj(node):
			if dist[neighbor] == -1:
				dist[neighbor] = dist[node] + 1
				q.append(neighbor)
	return -1
def getConnected(point: Point,height: int|float,trn: Image[int|float],size: int) -> set[Point]:
	stack = [point]
	checked = {point}
	found = {point}
	while len(stack) != 0:
		p = stack[0]
		stack = stack[1:]
		checked.add(p)
		found.add(p)
		neighbors = {n for n in getNeighbors(p,size) if trn[n] == height and n not in checked}
		stack += list(neighbors)
	return found
def getNeighbors(point: Point,size: int) -> set[Point]:
	x,y = point
	return {
		(
			(x - 1) % size,
			y,
		),(
			(x + 1) % size,
			y,
		),(
			x,
			(y - 1) % size,
		),(
			x,
			(y + 1) % size,
		)
	}
def flow(trn1: Image[int|float],trn2: Image[int|float],quant: int|float,point: Point,size: int) -> None:
	#print(f">>{quant}")
	while True:
		h = trn1[point] + trn2[point]
		connected = getConnected(point,h,trn1,trn2,size)
		neighbors = reduce(
			or_,[
				getNeighbors(p,size) for p in connected
			]
		) - connected
		lessThan = {p for p in neighbors if trn1[p] + trn2[p] < h}
		if len(lessThan) > 0:
			point = sorted(list(lessThan),key = lambda p : getGraphDistance(p,point,connected,size))[0]
		else:
			greaterThan = {trn1[p] + trn2[p] for p in neighbors if trn1[p] + trn2[p] > h}
			if len(greaterThan) == 0:
				return
			nextHeight = min(greaterThan)
			diff = nextHeight - h
			if diff >= quant:
				divided = quant/len(connected)
				for p in connected:
					trn2[p] += divided
				return
			else:
				divided = diff/len(connected)
				for p in connected:
					trn2[p] += divided
				quant -= diff
				#print(f">>{quant}")
def flowPath(src: Image[int|float],point: Point,size: int,conn: dict[Point,set[Point]],nextp: dict[Point,set[Point]],flowp: dict[Point,set[Point]]) -> None:
	if point not in flowp:
		path = {point} | conn[point]
		for p in nextp[point]:
			path |= flowPath(src,p,size,conn,nextp,flowp)
		flowp[point] = path
	return flowp[point]
def offsetsAtRadius(radius: int|float) -> set[Point]:
	points: set[Point] = set()
	for i in range(-radius,radius + 1):
		for j in range(-radius,radius + 1):
			if (i**2 + j**2)**0.5 <= radius:
				points.add((i,j))
	return points
def getDistToWater(point: Point,radius: int|float,land: Image[bool],size: int) -> float:
	offsets = offsetsAtRadius(radius)
	x,y = point
	points = {
		(
			(x + i) % size,
			(y + j) % size,
		) for i,j in offsets if not land[
			(x + i) % size,
			(y + j) % size,
		]
	}
	dists = {
		getDistance((x,y),(a,b)) for a,b in points
	}
	if len(dists) == 0: return WATER_RATIO_RADIUS
	return min(dists)
def storeTerrainValues(terrainValues: dict[str,Image|Video]) -> None:
	for name,terrain in terrainValues.items():
		filename = Path(f"terrain/{name}.json")
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
					'terrain' : [[[terrain[t,x,y] for y in range(terrain.size)] for x in range(terrain.size)] for t in range(terrain.length)]
				}))
		else:
			raise TypeError(f"Attempting to store object of type {type(terrain).__name__}")
def loadTerrainValues() -> dict[str,Image]:
	terrain = {}
	for entry in TERRAIN_DIRECTORY.iterdir():
		if not entry.is_file(): continue
		content = loadTerrain(entry)
		if content['arguments'] == ARGUMENTS[entry.stem]:
			match content['type']:
				case 'Image':
					terrain[entry.stem] = Image(
						len(content['terrain']),
						lambda x,y : content['terrain'][x][y],
					)
				case 'Video':
					terrain[entry.stem] = Video(
						len(content['terrain']),
						len(content['terrain'][0]),
						lambda t,x,y : content['terrain'][t][x][y],
					)
				case _:
					raise TypeError
	return terrain
def loadTerrain(filename: Path) -> dict[str,list|dict]:
	with open(filename,mode = 'r') as f:
		try:
			content = json.loads(f.read())
		except:
			print(f"Error in file {filename}")
			raise
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
def cleanNoiseMapping(block: NoiseBlock,terrain: dict[str,Image]) -> None:
	for name,noise in NOISE_DEPENDENCIES:
		if noise != block or name not in terrain: continue
		del terrain[name]
def clearCache() -> None:
	for entry in TERRAIN_DIRECTORY.iterdir():
		entry.unlink()
def clearNoiseCache() -> None:
	for entry in NOISE_DIRECTORY.iterdir():
		entry.unlink()
def jsonToNoise(value: dict):
	size = len(value['noise'])
	return {
		'args' : NoiseBlock(**value['args']),
		'noise' : Image(
			size,
			lambda x,y : value['noise'][x][y],
		),
	}
def noiseToJson(noise: Image,block: NoiseBlock) -> dict:
	return {
		'args' : {
			'dimensions' : block.dimensions,
			'size' : block.size,
			'seed' : block.seed,
			'scale' : block.scale,
			'frequency' : block.frequency,
			'time' : block.time,
		},
		'noise' : [
			[
				noise[x,y] for y in range(noise.size)
			] for x in range(noise.size)
		],
	}
def loadNoiseValues() -> dict[NoiseBlock,Image[float]]:
	values = {}
	for entry in NOISE_DIRECTORY.iterdir():
		with open(entry,mode = 'r',newline = '') as f:
			content = jsonToNoise(json.loads(f.read()))
		print(f"loaded {content['args']}")
		values[content['args']] = content['noise']
	return values
def getNoise(block: NoiseBlock) -> None:
	noise = perlinNoise(block)
	content = json.dumps(noiseToJson(noise,block))
	filename = str(NOISE_DIRECTORY / str(hash(block))) + '.json'
	with open(filename,mode = 'w') as f:
		f.write(content)
	return noise
def addColor(trn: dict[str,Image]) -> None:
	keys = list(trn.keys())
	for k in keys:
		print(f"adding color to {k}...")
		if isinstance(trn[k].first(),bool):
			trn[k] = scrMap(
				lambda v : (255,255,255) if v else (0,0,0),
				trn[k],
			)
		elif isinstance(trn[k].first(),int|float):
			if RANGE[k] == Interval(0,255):
				trn[k] = scrMap(
					lambda v : (int(v),int(v),int(v)),
					trn[k],
				)
			elif RANGE[k] == Interval(0,(1 << 24) - 1) or RANGE[k] == Interval(0,255 << 16):
				trn[k] = scrMap(intToColor,trn[k])
			else:
				values = {v for v in trn[k]}
				u = (min(values),max(values))
				trn[k] = scrMap(
					lambda v : (int(v),int(v),int(v)),
					trn[k].scale(RANGE[k],0,255),
				)
				values = {v for v in trn[k]}
		elif isinstance(trn[k].first(),tuple) and len(trn[k].first()) == 2:
			trn[k] = scrMap(
				lambda v : pointToColor(v),
				trn[k],
			)

clearCache()
#clearNoiseCache()
TERRAIN = loadTerrainValues()
NOISE_MAP = loadNoiseValues()
LENGTH: int = GRID_SIZE * CELL_SIZE

for i in range(TERRAIN_NOISE_OCTAVES):
	block0 = NoiseBlock(
		dimensions = 4,
		size = GRID_SIZE,
		seed = NOISE_SEED,
		scale = TERRAIN_NOISE_SCALE,
		frequency = FREQUENCIES[i],
		time = 0,
	)
	block1 = NoiseBlock(
		dimensions = 4,
		size = GRID_SIZE,
		seed = NOISE_SEED + 1,
		scale = TERRAIN_NOISE_SCALE,
		frequency = FREQUENCIES[i],
		time = 0,
	)
	block2 = NoiseBlock(
		dimensions = 4,
		size = GRID_SIZE,
		seed = NOISE_SEED + 2,
		scale = TERRAIN_NOISE_SCALE,
		frequency = FREQUENCIES[i],
		time = 0,
	)
	if block0 not in NOISE_MAP:
		NOISE_MAP[block0] = getNoise(block0)
		cleanNoiseMapping(block0,TERRAIN)
	if block1 not in NOISE_MAP:
		NOISE_MAP[block1] = getNoise(block1)
		cleanNoiseMapping(block1,TERRAIN)
	if block2 not in NOISE_MAP:
		NOISE_MAP[block2] = getNoise(block2)
		cleanNoiseMapping(block2,TERRAIN)
pBlock = NoiseBlock(
	dimensions = 4,
	size = GRID_SIZE,
	seed = NOISE_SEED + 3,
	scale = OVERWORLD_PRESSURE_SCALE,
	frequency = OVERWORLD_PRESSURE_FREQUENCY,
	time = 0,
)
if pBlock not in NOISE_MAP:
	NOISE_MAP[pBlock] = getNoise(pBlock)
	cleanNoiseMapping(pBlock,TERRAIN)
amplitudes = [0.5**i for i in range(TERRAIN_NOISE_OCTAVES)]
total_amplitude = sum(amplitudes)
perlin_noise_0: Image[float] = sum(
	NOISE_MAP[NoiseBlock(
		dimensions = 4,
		size = GRID_SIZE,
		seed = NOISE_SEED,
		scale = TERRAIN_NOISE_SCALE,
		frequency = FREQUENCIES[i],
		time = 0,
	)] * amplitudes[i] for i in range(TERRAIN_NOISE_OCTAVES)
) / total_amplitude
perlin_noise_1: Image[float] = sum(
	NOISE_MAP[NoiseBlock(
		dimensions = 4,
		size = GRID_SIZE,
		seed = NOISE_SEED + 1,
		scale = TERRAIN_NOISE_SCALE,
		frequency = FREQUENCIES[i],
		time = 0,
	)] * amplitudes[i] for i in range(TERRAIN_NOISE_OCTAVES)
) / total_amplitude
perlin_noise_2: Image[float] = sum(
	NOISE_MAP[NoiseBlock(
		dimensions = 4,
		size = GRID_SIZE,
		seed = NOISE_SEED + 2,
		scale = TERRAIN_NOISE_SCALE,
		frequency = FREQUENCIES[i],
		time = 0,
	)] * amplitudes[i] for i in range(TERRAIN_NOISE_OCTAVES)
) / total_amplitude
if 'overworld surface original' not in TERRAIN:
	print('generating overworld surface original...')
	TERRAIN['overworld surface original']: Image[float] = perlin_noise_0.scale(OVERWORLD_SURFACE_RANGE)
	cleanMapping('overworld surface original',TERRAIN)
RANGE['overworld surface original'] = OVERWORLD_SURFACE_RANGE
if 'overworld land' not in TERRAIN:
	print('generating overworld land...')
	bins = {
		(i,i + 1) : set() for i in range(RANGE['overworld surface original'].min,RANGE['overworld surface original'].max + 1)
	}
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			bins[
				int(TERRAIN['overworld surface original'][i,j]),
				int(TERRAIN['overworld surface original'][i,j]) + 1,
			].add((i,j))
	total = 0
	OVERWORLD_SEA_LEVEL = None
	for i in range(RANGE['overworld surface original'].min + 1,RANGE['overworld surface original'].max + 1):
		total += len(bins)
		if total/GRID_SIZE**2 > OVERWORLD_WATER_RATIO:
			OVERWORLD_SEA_LEVEL = i - 1
			break
	if OVERWORLD_SEA_LEVEL == None:
		OVERWORLD_SEA_LEVEL = RANGE['overworld surface original'].max + 1
	TERRAIN['overworld land']: Image[bool] = TERRAIN['overworld surface original'] > OVERWORLD_SEA_LEVEL
	cleanMapping('overworld land',TERRAIN)
else:
	water_points = {(i,j) for (i,j),v in TERRAIN['overworld land'].enumerate() if not v}
	OVERWORLD_SEA_LEVEL = int(max({TERRAIN['overworld surface original'][p] for p in water_points})) + 1
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
	'''
	scaled = TERRAIN['overworld surface original'] * (
		1 + TERRAIN['overworld surface fluctuation']
	)
	TERRAIN['overworld surface']: Image[float] = ifMap(
		scaled,
		TERRAIN['overworld land'],
		TERRAIN['overworld surface original'],
	)
	'''
	TERRAIN['overworld surface']: Image[float] = TERRAIN['overworld surface original']
	cleanMapping('overworld surface',TERRAIN)
RANGE['overworld surface'] = RANGE['overworld surface original']
if 'overworld depth' not in TERRAIN:
	print('generating overworld depth...')
	TERRAIN['overworld depth']: Image[float] = perlin_noise_1.scale(-1,1,OVERWORLD_DEPTH_RANGE)
	cleanMapping('overworld depth',TERRAIN)
RANGE['overworld depth'] = OVERWORLD_DEPTH_RANGE
if 'midworld surface' not in TERRAIN:
	print('generating midworld surface...')
	TERRAIN['midworld surface']: Image[float] = perlin_noise_2.scale(-1,1,MIDWORLD_SURFACE_RANGE)
	cleanMapping('midworld surface',TERRAIN)
RANGE['midworld surface'] = MIDWORLD_SURFACE_RANGE
if 'overworld coastline land side' not in TERRAIN:
	print('generating overworld coastline land side...')
	TERRAIN['overworld coastline land side']: Image[bool] = TERRAIN['overworld land'] & Image(
		GRID_SIZE,
		lambda x,y : not all(
			TERRAIN['overworld land'][
				(x + i) % GRID_SIZE,
				(y + j) % GRID_SIZE,
			] for i in range(-1,2) for j in range(-1,2)
		),
	)
	cleanMapping('overworld coastline land side',TERRAIN)
if 'overworld coastline water side' not in TERRAIN:
	print('generating overworld coastline water side...')
	TERRAIN['overworld coastline water side']: Image[bool] = ~TERRAIN['overworld land'] & Image(
		GRID_SIZE,
		lambda x,y : any(
			TERRAIN['overworld land'][
				(x + i) % GRID_SIZE,
				(y + j) % GRID_SIZE,
			] for i in range(-1,2) for j in range(-1,2)
		),
	)
	cleanMapping('overworld coastline water side',TERRAIN)
if 'overworld coastline' not in TERRAIN:
	print('generating overworld coastline...')
	TERRAIN['overworld coastline'] = TERRAIN['overworld coastline land side'] | TERRAIN['overworld coastline water side']
	cleanMapping('overworld coastline',TERRAIN)
if 'overworld true surface' not in TERRAIN:
	print('generating overworld true surface...')
	TERRAIN['overworld true surface']: Image[float] = ifMap(
		TERRAIN['overworld surface'],
		TERRAIN['overworld land'],
		OVERWORLD_SEA_LEVEL,
	)
	cleanMapping('overworld true surface',TERRAIN)
RANGE['overworld true surface'] = RANGE['overworld surface'] | OVERWORLD_SEA_LEVEL
if 'overworld true surface differential x' not in TERRAIN:
	dx1: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld true surface'][x,y] - TERRAIN['overworld true surface'][(x - 1) % GRID_SIZE,y],
	)
	dx2: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld true surface'][(x + 1) % GRID_SIZE,y] - TERRAIN['overworld true surface'][x,y],
	)
	print('generating overworld true surface differential x...')
	TERRAIN['overworld true surface differential x']: Image[float] = (dx1 + dx2) / 2
	cleanMapping('overworld true surface differential x',TERRAIN)
RANGE['overworld true surface differential x'] = RANGE['overworld true surface'] - RANGE['overworld true surface']
if 'overworld true surface differential y' not in TERRAIN:
	print('generating overworld true surface differential y...')
	dy1: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld true surface'][x,y] - TERRAIN['overworld true surface'][x,(y - 1) % GRID_SIZE],
	)
	dy2: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld true surface'][x,(y + 1) % GRID_SIZE] - TERRAIN['overworld true surface'][x,y],
	)
	TERRAIN['overworld true surface differential y'] = (dy1 + dy2) / 2
	cleanMapping('overworld true surface differential y',TERRAIN)
RANGE['overworld true surface differential y'] = RANGE['overworld true surface'] - RANGE['overworld true surface']
if 'midworld land' not in TERRAIN:
	print('generating midworld land...')
	bins = {
		(i,i + 1) : set() for i in range(RANGE['midworld surface'].min,RANGE['midworld surface'].max + 1)
	}
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			bins[
				int(TERRAIN['midworld surface'][i,j]),
				int(TERRAIN['midworld surface'][i,j]) + 1,
			].add((i,j))
	total = 0
	MIDWORLD_SEA_LEVEL = None
	for i in range(RANGE['midworld surface'].min + 1,RANGE['midworld surface'].max + 1):
		total += len(bins)
		if total/GRID_SIZE**2 > MIDWORLD_WATER_RATIO:
			MIDWORLD_SEA_LEVEL = i - 1
			break
	if MIDWORLD_SEA_LEVEL == None:
		MIDWORLD_SEA_LEVEL = RANGE['midworld surface'].max + 1
	TERRAIN['midworld land']: Image[bool] = TERRAIN['midworld surface'] > MIDWORLD_SEA_LEVEL
	cleanMapping('midworld land',TERRAIN)
else:
	lava_points = {(i,j) for (i,j),v in TERRAIN['midworld land'].enumerate() if not v}
	MIDWORLD_SEA_LEVEL = int(max({TERRAIN['midworld surface'][p] for p in lava_points})) + 1
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
		sunlightMax = OVERWORLD_SUNLIGHT_RANGE.max,
		sunlightMin = OVERWORLD_SUNLIGHT_RANGE.min,
		tilt = AXIS_TILT,
	)
	cleanMapping('overworld sunlight',TERRAIN)
RANGE['overworld sunlight'] = OVERWORLD_SUNLIGHT_RANGE
if 'overworld distance from sea level' not in TERRAIN:
	print('generating overworld distance from sea level...')
	TERRAIN['overworld distance from sea level']: Image[float] = abs(TERRAIN['overworld surface'] - OVERWORLD_SEA_LEVEL)
	cleanMapping('overworld distance from sea level',TERRAIN)
RANGE['overworld distance from sea level'] = abs(RANGE['overworld surface'] - OVERWORLD_SEA_LEVEL)
if 'overworld general wind magnitude' not in TERRAIN:
	print('generating overworld general wind magnitude...')
	TERRAIN['overworld general wind magnitude'] = Image(
		GRID_SIZE,
		lambda x,y : getGenWindMagnitude(y,GRID_SIZE),
	)
	cleanMapping('overworld general wind magnitude',TERRAIN)
RANGE['overworld general wind magnitude'] = Interval(0,GRID_SIZE / 8)
if 'overworld general wind angle' not in TERRAIN:
	print('generating overworld general wind angle...')
	TERRAIN['overworld general wind angle'] = Image(
		GRID_SIZE,
		lambda x,y : getGenWindAngle(y,GRID_SIZE),
	)
	cleanMapping('overworld general wind angle',TERRAIN)
RANGE['overworld general wind angle'] = Interval(0,4 * pi)
if 'overworld pressure' not in TERRAIN:
	print('generating overworld pressure...')
	surface_related_pressure = (
		RANGE['overworld true surface'].max - TERRAIN['overworld true surface']
	).scale(
		RANGE['overworld true surface'],
		OVERWORLD_PRESSURE_RANGE,
	)
	surface_related_pressure -= surface_related_pressure.min()
	sunlight_related_pressure = (
		RANGE['overworld sunlight'].max - TERRAIN['overworld sunlight']
	).scale(RANGE['overworld sunlight'],0,1)
	pressure_diff = (
		NOISE_MAP[pBlock] * sunlight_related_pressure
	).scale(-1,1,OVERWORLD_PRESSURE_RANGE)
	TERRAIN['overworld pressure'] = (
		pressure_diff + surface_related_pressure
	)/2
	cleanMapping('overworld pressure',TERRAIN)
RANGE['overworld pressure'] = OVERWORLD_PRESSURE_RANGE
if 'overworld pressure differential x' not in TERRAIN:
	print('generating overworld temperature differential x...')
	dx1: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld pressure'][(x + 1) % GRID_SIZE,y] - TERRAIN['overworld pressure'][x,y],
	)
	dx2: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld pressure'][x,y] - TERRAIN['overworld pressure'][(x - 1) % GRID_SIZE,y],
	)
	TERRAIN['overworld pressure differential x']: Image[float] = (dx1 + dx2)/2
	cleanMapping('overworld pressure differential x',TERRAIN)
RANGE['overworld pressure differential x'] = (
	(
		RANGE['overworld pressure'] - RANGE['overworld pressure']
	) + (
		RANGE['overworld pressure'] - RANGE['overworld pressure']
	)
) / 2
if 'overworld pressure differential y' not in TERRAIN:
	print('generating overworld pressure differential y...')
	dy1: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld pressure'][x,(y + 1) % GRID_SIZE] - TERRAIN['overworld pressure'][x,y],
	)
	dy2: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld pressure'][x,y] - TERRAIN['overworld pressure'][x,(y - 1) % GRID_SIZE],
	)
	TERRAIN['overworld pressure differential y']: Image[float] = (dy1 + dy2)/2
	cleanMapping('overworld pressure differential y',TERRAIN)
RANGE['overworld pressure differential y'] = (
	(
		RANGE['overworld pressure'] - RANGE['overworld pressure']
	) + (
		RANGE['overworld pressure'] - RANGE['overworld pressure']
	)
) / 2
if 'overworld temperature' not in TERRAIN:
	print('generating overworld temperature...')
	initial_temperature: Image[float] = (
		TERRAIN['overworld sunlight'] + (
			RANGE['overworld distance from sea level'].max - TERRAIN['overworld distance from sea level']
		)
	)/2
	TERRAIN['overworld temperature']: Image[float] = ifMap(
		initial_temperature,
		TERRAIN['overworld land'],
		initial_temperature - OVERWORLD_TEMPERATURE_LAND_DIFFERENCE,
	).scale(OVERWORLD_TEMPERATURE_RANGE)
	cleanMapping('overworld temperature',TERRAIN)
RANGE['overworld temperature'] = OVERWORLD_TEMPERATURE_RANGE
if 'overworld water ratio' not in TERRAIN:
	print('generating overworld water ratio...')
	TERRAIN['overworld water ratio'] = WATER_RATIO_RADIUS - Image(
		GRID_SIZE,
		lambda x,y : getDistToWater((x,y),WATER_RATIO_RADIUS,TERRAIN['overworld land'],GRID_SIZE),
	)
	cleanMapping('overworld water ratio',TERRAIN)
RANGE['overworld water ratio'] = Interval(0,WATER_RATIO_RADIUS)
if 'overworld humidity' not in TERRAIN:
	print('generating overworld humidity...')
	inv_pressure = RANGE['overworld pressure'].max - TERRAIN['overworld pressure']
	TERRAIN['overworld humidity'] = (
		inv_pressure.scale(
			RANGE['overworld pressure'],
			OVERWORLD_HUMIDITY_RANGE,
		) + TERRAIN['overworld temperature'].scale(
			RANGE['overworld temperature'],
			OVERWORLD_HUMIDITY_RANGE,
		) + TERRAIN['overworld water ratio'].scale(
			RANGE['overworld water ratio'],
			OVERWORLD_HUMIDITY_RANGE,
		)
	)/3
	cleanMapping('overworld humidity',TERRAIN)
RANGE['overworld humidity'] = OVERWORLD_HUMIDITY_RANGE
if 'overworld rain' not in TERRAIN:
	print('generating overworld rain...')
	TERRAIN['overworld rain'] = (
		TERRAIN['overworld temperature'].scale(
			RANGE['overworld temperature'],
			OVERWORLD_RAIN_RANGE,
		) + TERRAIN['overworld humidity'].scale(
			RANGE['overworld humidity'],
			OVERWORLD_RAIN_RANGE,
		)
	)/2
	cleanMapping('overworld rain',TERRAIN)
RANGE['overworld rain'] = OVERWORLD_RAIN_RANGE
if 'overworld snow' not in TERRAIN:
	print('generating overworld snow...')
	inv_temperature = RANGE['overworld temperature'].max - TERRAIN['overworld temperature']
	inv_pressure = RANGE['overworld pressure'].max - TERRAIN['overworld pressure']
	TERRAIN['overworld snow'] = (
		TERRAIN['overworld humidity'].scale(
			RANGE['overworld humidity'],
			OVERWORLD_SNOW_RANGE,
		) + inv_temperature.scale(
			RANGE['overworld temperature'].max - RANGE['overworld temperature'],
			OVERWORLD_SNOW_RANGE,
		) + inv_pressure.scale(
			RANGE['overworld pressure'].max - RANGE['overworld pressure'],
			OVERWORLD_SNOW_RANGE,
		)
	)/3
	cleanMapping('overworld snow',TERRAIN)
RANGE['overworld snow'] = OVERWORLD_SNOW_RANGE
if 'overworld clouds' not in TERRAIN:
	print('generating overworld clouds...')
	TERRAIN['overworld clouds'] = (
		TERRAIN['overworld rain'] > OVERWORLD_CLOUD_LEVEL
	) | (
		TERRAIN['overworld snow'] > OVERWORLD_CLOUD_LEVEL
	)
	cleanMapping('overworld clouds',TERRAIN)
if 'snow' not in TERRAIN:
	print('generating snow...')
	TERRAIN['snow']: Image[bool] = TERRAIN['overworld snow'] > OVERWORLD_SNOW_LEVEL
	#TERRAIN['snow']: Image[bool] = Image(GRID_SIZE,False)
	cleanMapping('snow',TERRAIN)
if 'ice' not in TERRAIN:
	print('generating ice...')
	TERRAIN['ice'] = (
		TERRAIN['overworld temperature'] < OVERWORLD_ICE_LEVEL
	) & ~TERRAIN['overworld land']
	cleanMapping('ice',TERRAIN)
if 'overworld temperature differential x' not in TERRAIN:
	print('generating overworld temperature differential x...')
	dx1: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld temperature'][(x + 1) % GRID_SIZE,y] - TERRAIN['overworld temperature'][x,y],
	)
	dx2: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld temperature'][x,y] - TERRAIN['overworld temperature'][(x - 1) % GRID_SIZE,y],
	)
	TERRAIN['overworld temperature differential x']: Image[float] = (dx1 + dx2)/2
	cleanMapping('overworld temperature differential x',TERRAIN)
RANGE['overworld temperature differential x'] = (
	(
		RANGE['overworld temperature'] - RANGE['overworld temperature']
	) + (
		RANGE['overworld temperature'] - RANGE['overworld temperature']
	)
) / 2
if 'overworld temperature differential y' not in TERRAIN:
	print('generating overworld temperature differential y...')
	dy1: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld temperature'][x,(y + 1) % GRID_SIZE] - TERRAIN['overworld temperature'][x,y],
	)
	dy2: Image[float] = Image(
		GRID_SIZE,
		lambda x,y : TERRAIN['overworld temperature'][x,y] - TERRAIN['overworld temperature'][x,(y - 1) % GRID_SIZE],
	)
	TERRAIN['overworld temperature differential y']: Image[float] = (dy1 + dy2)/2
	cleanMapping('overworld temperature differential y',TERRAIN)
RANGE['overworld temperature differential y'] = (
	(
		RANGE['overworld temperature'] - RANGE['overworld temperature']
	) + (
		RANGE['overworld temperature'] - RANGE['overworld temperature']
	)
) / 2
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
		overworld_surface_int << 8,
		TERRAIN['overworld land'],
		overworld_surface_int,
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
		k = index % sel.length
		for i in range(GRID_SIZE):
			for j in range(GRID_SIZE):
				rect = pygame.Rect(
					i * CELL_SIZE,
					j * CELL_SIZE,
					CELL_SIZE,
					CELL_SIZE,
				)
				try:
					pygame.draw.rect(WINDOW,sel[k,i,j],rect)
				except:
					print(TERRAIN[DROPDOWN.selected][k,i,j])
					raise
	index += 1
	DROPDOWN.draw(WINDOW)
	pygame.display.flip()
	CLOCK.tick(60)

pygame.quit()