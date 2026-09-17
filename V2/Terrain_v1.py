import pygame,random,json
from perlin import perlin4
from Screen import (
	scrMap,
	keyMap,
	Screen,
)
from math import (
	cos,
	sin,
	tan,
	radians,
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
CELL_SIZE: int = 2  # Size of each square in pixels
MAX_COLOR: int = 255
LATTITUDE_EFFECT_STRENGTH: int = 50
HUMIDITY_RANGE: int = (GRID_SIZE >> 5) - 1
MAX_ALT = 255
TOP_SEA_LEVEL_FACTOR = 0.51
SNOW_LEVEL_FACTOR = 0.7
TERRAIN_NOISE_SCALE: int = 1
TERRAIN_NOISE_OCTAVES: int = 8
NOISE_SEED: int = 0
AXIS_TILT: float = 23.44
HUMIDITY_SMUDGE_RADIUS: int = 12
DIAMETER: float = GRID_SIZE/pi
RADIUS: float = DIAMETER/2
UI_PANEL_WIDTH: int = 200
UI_PANEL_MARGIN: int = 20
NUM_CONTINENTS: int = 12
NUM_CONTINENT_RUNS: int = 5
UI_RECT_COLOR: Color = (255,198,183)
MAX_COLOR_INTEGER: int = 255**3 - 1
ADJUSTED_EDGE_AMPLITUDE: int = 32
MAX_SPEED = 20
MAX_POINT_INTEGER: int = GRID_SIZE**2 - 1
BOTTOM_SEA_LEVEL_FACTOR = 0.4
LAYER_OVERLAP_HEIGHT = 125

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
			lambda x,y,v : values[x][y],
			Screen(GRID_SIZE),
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
def getLattitude(y: int) -> float:
	circumference = GRID_SIZE
	diameter = circumference/pi
	radius = diameter/2
	return radius + (radius**2 + y**2)**0.5
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
def getVectorFromAngle(theta: int) -> array:
	r = radians(theta)
	return array([
		cos(r),
		sin(r),
	])
def unitVector(v: array) -> array:
	return v / norm(v)
def scalarProj(a: array,b: array) -> float:
	return dot(a,unitVector(b))
def vectorProj(a: array,b: array) -> array:
	return (dot(a,b)/norm(b)**2) * b
def getAverageDistance(point: Point,trn: Screen) -> float:
	distances = []

	for i in range(-HUMIDITY_RANGE,HUMIDITY_RANGE + 1):
		for j in range(-HUMIDITY_RANGE,HUMIDITY_RANGE + 1):
			x = (point[0] + i) % GRID_SIZE
			y = (point[1] + j) % GRID_SIZE
			if not trn[x,y]:
				distances.append(getDistance(point,(x,y)))
			else:
				distances.append(GRID_SIZE - 1)
	return sum(distances)/len(distances)
def getCurrentTilt(day: int) -> float:
	min_tilt = -AXIS_TILT
	max_tilt = AXIS_TILT
	return min_tilt + day * (max_tilt - min_tilt)/365
def lattitudeToAngle(latt: int) -> float:
	return latt * 359/GRID_SIZE
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
	return (lattitudeToAngle(latt) + getCurrentTilt(day)) % 360
def getVectorForDay(latt: int,day: int) -> tuple[float,float]:
	theta = getAngleForDay(latt,day)
	return (
		RADIUS * cos(radians(theta)),
		RADIUS * sin(radians(theta)),
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
def generateNeighborsAtRange(point: Point,radius: int) -> set[Point]:
	x,y = point
	return {
		((x - radius) % GRID_SIZE,(y + i) % GRID_SIZE) for i in range(-radius,radius + 1)
	} | {
		((x + radius) % GRID_SIZE,(y + i) % GRID_SIZE) for i in range(-radius,radius + 1)
	} | {
		((x + i) % GRID_SIZE,(y - radius) % GRID_SIZE) for i in range(-radius,radius + 1)
	} | {
		((x + i) % GRID_SIZE,(y + radius) % GRID_SIZE) for i in range(-radius,radius + 1)
	}
def getClosestBorderPoint(point: Point,plates: Screen) -> Point:
	points = set()
	r = 1
	while len(points) == 0:
		points |= {p for p in generateNeighborsAtRange(point,r) if plates[point] != plates[p]}
		r += 1
	points = list(points)
	plts = [plates[p] for p in points]
	if plates[point] in plts:
		raise ValueError
	dists = [getDistance(point,p) for p in points]
	minDist = min(dists)
	index = dists.index(minDist)
	if plates[points[index]] == plates[point]:
		raise ValueError
	return points[index]
def getClosestPoint(point: Point,points: list[Point],noise_diff: int|None = None) -> Point:
	if noise_diff is None:
		dists = [getDistance(point,p) for p in points]
	else:
		dists = [getDistance(point,p) + noise_diff for p in points]
	minDist = min(dists)
	minDistIndex = [i for i,dist in enumerate(dists) if dist == minDist][0]
	return points[minDistIndex]
def getNeighborsOfPoint(point: Point,values: Screen) -> list:
	vals = set()
	x,y = point
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
	points = {(x,y) for x,y in points if x >= 0 and y >= 0 and x < GRID_SIZE and y < GRID_SIZE}
	for point in points:
		vals.add(values[point])
	return list(vals)
def getClosestBorderAndDist(point: Point,plates: Screen) -> tuple[Point,float]:
	for i in range(GRID_SIZE):
		points = [p for p in generateNeighborsAtRange(point,i) if plates[p] != plates[point]]
		if len(points) > 0: break
	dists = [getDistance(p,point) for p in points]
	minDist = min(dists)
	index = dists.index(minDist)
	return (plates[points[index]],minDist)
def getTopLand(*,altitude: Screen|None = None) -> Screen:
	print('generating top land...')
	return scrMap(
		lambda v : v > MAX_ALT * TOP_SEA_LEVEL_FACTOR,
		altitude
	)
def getBottomLand(*,altitude: Screen|None = None) -> Screen:
	print('generating top land...')
	return scrMap(
		lambda v : v > MAX_ALT * BOTTOM_SEA_LEVEL_FACTOR,
		altitude,
	)
def getHumidity(*,land: Screen|None = None,altitude: Screen|None = None) -> Screen:
	print('generating humidity...')
	filename = Path(f"humidity_{flm(NOISE_SEED)}_{flm(TERRAIN_NOISE_SCALE)}_{flm(TERRAIN_NOISE_OCTAVES)}_{flm(GRID_SIZE)}_{flm(TOP_SEA_LEVEL_FACTOR)}_{flm(HUMIDITY_SMUDGE_RADIUS)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : values[x][y],
			Screen(GRID_SIZE),
		)
	if land is None:
		land = getLand(altitude)
	humidity = 255 - smudge(
		scrMap(
			lambda v : 255 if v else 0,
			land,
		)
	)
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
			lambda x,y,v : sunlight[y],
			Screen(GRID_SIZE),
		)
	values = [getAvgSunlightValue(y) for y in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return keyMap(
		lambda x,y,v : values[y],
		Screen(GRID_SIZE),
	)
def getSnow(*,sunlight: Screen|None = None,altitude: Screen|None = None) -> Screen:
	print('generating snow...')
	filename = Path(f"snow_{flm(NOISE_SEED)}_{flm(TERRAIN_NOISE_SCALE)}_{flm(TERRAIN_NOISE_OCTAVES)}_{flm(GRID_SIZE)}_{flm(AXIS_TILT)}_{flm(SNOW_LEVEL_FACTOR)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : values[x][y],
			Screen(GRID_SIZE),
		)
	if sunlight is None:
		sunlight = getSunlight()
	snow = scrMap(
		lambda u,v : ((MAX_ALT - u) + v)/2 > MAX_ALT * SNOW_LEVEL_FACTOR,
		sunlight,
		altitude,
	)
	values = [[snow[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return snow
def getTopGreenery(
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
			int(u) // 2,
			int(u) + (255 - int(u)) // 3,
			int(u) // 2,
		) if v else (
			int(u) // 2,
			int(u) // 2,
			(255 + int(u)) // 2,
		),
		snow,
		altitude,
		land,
	)
def getBottomGreenery(
	*,
	altitude: Screen[int]|None = None,
	land: Screen[bool]|None = None,
	connected: Screen[bool]|None = None,
) -> Screen:
	print('generating bottom greenery...')
	if land is None:
		land = getLand(altitude = altitude)
	return scrMap(
		lambda w,u,v : (0,0,0) if w else (
			int(u) // 2,
			int(u) + (255 - int(u)) // 3,
			int(u) // 2,
		) if v else (
			int(u) // 2,
			int(u) // 2,
			(255 + int(u)) // 2,
		),
		connected,
		altitude,
		land,
	)
def getNeighbors(*,plates: Screen|None = None) -> Screen[list[Point]]:
	print('generating neighbors...')
	filename = Path(f"neighbors_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : [tuple(v) for v in values[x][y]],
			Screen(GRID_SIZE),
		)
	if plates is None:
		plates = getPlates()
	neighbors = keyMap(
		lambda x,y,v : getNeighborsOfPoint((x,y),v),
		plates,
	)
	values = [[neighbors[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return neighbors
def getEdges(*,neighbors: Screen|None = None,plates: Screen|None = None) -> Screen:
	print('generating edges...')
	filename = Path(f"edges_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : values[x][y],
			Screen(GRID_SIZE),
		)
	if neighbors is None:
		neighbors = getPlates(plates = plates)
	edges = scrMap(
		lambda v : len(v) == 2,
		neighbors,
	)
	values = [[edges[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return edges
def getPlates() -> Screen:
	print('generating plates...')
	filename = Path(f"plates_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : tuple(values[x][y]),
			Screen(GRID_SIZE),
		)
	points = set()
	rng = random.Random(NOISE_SEED)
	while len(points) < NUM_CONTINENTS:
		points.add(randPoint(rng))
	points = list(points)
	plates = keyMap(
		lambda x,y,v : getClosestPoint((x,y),points),
		Screen(GRID_SIZE)
	)
	for i in range(NUM_CONTINENT_RUNS):
		for j in range(NUM_CONTINENTS):
			coords = [(x,y) for (x,y),_ in plates.enumerate() if plates[x,y] == points[j]]
			points[j] = getCentroid(coords)
		plates = keyMap(
			lambda x,y,v : getClosestPoint((x,y),points),
			Screen(GRID_SIZE)
		)
	values = [[plates[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return plates
def getClosestPointAtBorder(*,plates: Screen|None = None) -> Screen[Point]:
	print('generating closest point at border...')
	filename = Path(f"closestPointAtBorder_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : tuple(values[x][y]),
			Screen(GRID_SIZE),
		)
	if plates is None:
		plates = getPlates()
	closestPointAtBorder = Screen(GRID_SIZE)
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			closestPointAtBorder[i,j] = getClosestBorderPoint((i,j),plates)
	values = [[closestPointAtBorder[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return closestPointAtBorder
def getClosestBorder(*,plates: Screen|None = None,closestPointAtBorder: Screen|None = None) -> Screen[Point]:
	print('generating closest border...')
	filename = Path(f"closestBorder_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : tuple(values[x][y]),
			Screen(GRID_SIZE),
		)
	if plates is None:
		plates = getPlates2()
	if closestPointAtBorder is None:
		closestPointAtBorder = getClosestPointAtBorder()
	closestBorder = scrMap(
		lambda v : plates[v],
		closestPointAtBorder,
	)
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			if plates[i,j] == plates[closestPointAtBorder[i,j]]:
				raise ValueError
	values = [[closestBorder[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return closestBorder
def getDistToBorder(*,closestPointAtBorder: Screen|None = None,plates: Screen|None = None) -> Screen[int]:
	print('generating distance to border...')
	filename = Path(f"distToBorder_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : values[x][y],
			Screen(GRID_SIZE),
		)
	if closestPointAtBorder is None:
		closestPointAtBorder = getClosestPointAtBorder(plates = plates)
	distToBorder = keyMap(
		lambda x,y,v : getDistance((x,y),v[x,y]),
		closestPointAtBorder,
	)
	values = [[distToBorder[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return distToBorder
def getAdjustedPlates(*,plates: Screen|None = None,pnoise: Screen|None = None,neighbors: Screen|None = None,closestBorder: Screen|None = None,distToBorder: Screen|None = None) -> Screen:
	print('generating adjusted tectonic plates...')
	filename = Path(f"adjustedPlates_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}_{flm(TERRAIN_NOISE_SCALE)}_{flm(TERRAIN_NOISE_OCTAVES)}_{flm(ADJUSTED_EDGE_AMPLITUDE)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : tuple(values[x][y]),
			Screen(GRID_SIZE),
		)
	if plates is None:
		plates = getPlates()
	if pnoise is None:
		pnoise = perlinNoise(
			seed = NOISE_SEED,
			scale = TERRAIN_NOISE_SCALE,
			octaves = TERRAIN_NOISE_OCTAVES,
		)
	if closestBorder is None:
		closestBorder = getClosestBorder(plates = plates)
	if distToBorder is None:
		distToBorder = getDistToBorder(closestBorder = closestBorder,plates = plates)
	if neighbors is None:
		neighbors = getNeighbors(plates = plates)
	chosen = set()
	for i in range(GRID_SIZE):
		for j in range(GRID_SIZE):
			chosen.add(frozenset(neighbors[i,j]))
	chosen = {c : list(c)[0] for c in chosen}
	adjustedPlates = keyMap(
		lambda x,y,a,b,c,d : c[a[x,y]] if d[x,y] + b[x,y] * ADJUSTED_EDGE_AMPLITUDE < 0 and chosen[frozenset([c[x,y],c[a[x,y]]])] == c[a[x,y]] else c[x,y],
		closestBorder,
		pnoise,
		plates,
		distToBorder,
	)
	values = [[adjustedPlates[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return adjustedPlates
def getPlates2(*,pnoise: Screen|None = None) -> Screen[Point]:
	print('generating plates2...')
	filename = Path(f"plates2_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}_{flm(TERRAIN_NOISE_SCALE)}_{flm(TERRAIN_NOISE_OCTAVES)}_{flm(ADJUSTED_EDGE_AMPLITUDE)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : tuple(values[x][y]),
			Screen(GRID_SIZE),
		)
	if pnoise is None:
		pnoise = perlinNoise(
			seed = NOISE_SEED,
			scale = TERRAIN_NOISE_SCALE,
			octaves = TERRAIN_NOISE_OCTAVES,
		)
	perlin = (pnoise + 1) * ADJUSTED_EDGE_AMPLITUDE/2
	points = set()
	rng = random.Random(NOISE_SEED)
	while len(points) < NUM_CONTINENTS:
		points.add(randPoint(rng))
	points = list(points)
	plates = keyMap(
		lambda x,y,v : getClosestPoint((x + perlin[x,y],y + perlin[x,y]),points),
		Screen(GRID_SIZE)
	)
	for i in range(NUM_CONTINENT_RUNS):
		for j in range(NUM_CONTINENTS):
			coords = [(x,y) for (x,y),_ in plates.enumerate() if plates[x,y] == points[j]]
			points[j] = getCentroid(coords)
		plates = keyMap(
			lambda x,y,v : getClosestPoint((x + perlin[x,y],y + perlin[x,y]),points),
			Screen(GRID_SIZE)
		)
	swaps = {p : None for p in points}
	for i in range(NUM_CONTINENT_RUNS):
		for j in range(NUM_CONTINENTS):
			coords = [(x,y) for (x,y),_ in plates.enumerate() if plates[x,y] == points[j]]
			swaps[points[j]] = getCentroid(coords)
	plates = scrMap(
		lambda v : swaps[v],
		plates,
	)
	values = [[plates[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return plates
def addColor(trn: dict[str,Screen]) -> None:
	keys = list(trn.keys())
	for k in keys:
		if isinstance(trn[k][0,0],bool):
			trn[f"{k} (colored)"] = scrMap(
				lambda v : (255,255,255) if v else (0,0,0),
				trn[k],
			)
		elif isinstance(trn[k][0,0],int|float):
			trn[f"{k} (colored)"] = scrMap(
				lambda v : (int(v),int(v),int(v)),
				trn[k],
			)
		elif isinstance(trn[k][0,0],tuple) and len(trn[k][0,0]) == 2:
			trn[f"{k} (colored)"] = scrMap(
				lambda v : pointToColor(v),
				trn[k],
			)
def getDirections(*,plates: Screen|None = None,pnoise: Screen|None = None) -> Screen[int]:
	filename = Path(f"directions_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}_{flm(TERRAIN_NOISE_SCALE)}_{flm(TERRAIN_NOISE_OCTAVES)}_{flm(ADJUSTED_EDGE_AMPLITUDE)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : values[x][y],
			Screen(GRID_SIZE),
		)
	if plates is None:
		plates = getPlates2(pnoise = pnoise)
	centers = {center for center in plates}
	direcs = {center : random.randint(0,359) for center in centers}
	directions = scrMap(
		lambda v : direcs[v],
		plates,
	)
	values = [[directions[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return directions
def getSpeeds(*,plates: Screen|None = None,pnoise: Screen|None = None) -> Screen[int]:
	filename = Path(f"speeds_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}_{flm(TERRAIN_NOISE_SCALE)}_{flm(TERRAIN_NOISE_OCTAVES)}_{flm(ADJUSTED_EDGE_AMPLITUDE)}_{flm(MAX_SPEED)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : values[x][y],
			Screen(GRID_SIZE),
		)
	if plates is None:
		plates = getPlates2(pnoise = pnoise)
	centers = {center for center in plates}
	spds = {center : random.randint(0,MAX_SPEED) for center in centers}
	speeds = scrMap(
		lambda v : spds[v],
		plates,
	)
	values = [[speeds[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return speeds
def getConjunctions(*,plates: Screen,neighbors: Screen|None = None) -> set[frozenset[Point]]:
	if neighbors is None:
		neighbors = getEdges(plates = plates)
	return {frozenset(v) for v in neighbors if len(v) > 1}
def getPairs(plates: Screen,neighbors: Screen|None = None) -> set[frozenset[Point]]:
	conjunctions = getConjunctions(plates = plates,neighbors = neighbors)
	pairs = set()
	for v in conjunctions:
		if len(v) == 2:
			pairs.add(v)
		else:
			vals = {frozenset(u) for u in product(v,v)} - {frozenset([u,u]) for u in v}
			pairs |= vals
	return pairs
def getConvergence(pairs,directions: Screen,speeds: Screen) -> dict[frozenset[Point],dict[Point,float]]:
	vals = {}
	for pair in pairs:
		c1,c2 = tuple(pair)
		v12 = getVector(c1,c2)
		d1 = getVectorFromAngle(directions[c1]) * speeds[c1]
		d2 = getVectorFromAngle(directions[c2]) * speeds[c2]
		vals[pair] = {
			c1 : scalarProj(d1,v12),
			c2 : scalarProj(d2,-v12),
		}
	return vals
def getTotalConvergence(*,convergence: dict[frozenset[Point],dict[Point,float]],edgeSection: Screen[frozenset[Point]],distToBorder: Screen[float],noise: Screen[float],plates: Screen[Point]) -> Screen:
	filename = Path(f"totalConvergence_{flm(NOISE_SEED)}_{flm(NUM_CONTINENTS)}_{flm(GRID_SIZE)}_{flm(NUM_CONTINENT_RUNS)}_{flm(TERRAIN_NOISE_SCALE)}_{flm(TERRAIN_NOISE_OCTAVES)}_{flm(ADJUSTED_EDGE_AMPLITUDE)}_{flm(MAX_SPEED)}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : values[x][y],
			Screen(GRID_SIZE),
		)
	distToCenter = GRID_SIZE//2 - distToBorder
	totalConvergence = scrMap(
		lambda a,b,c,d : a * convergence[b][d] * c,
		noise,
		edgeSection,
		distToCenter,
		plates,
	)
	values = [[totalConvergence[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return totalConvergence
def getAltitude(seed: int) -> Screen[int]:
	print('generating altitude...')
	return scrMap(
		lambda v : int(v),
		(perlinNoise(
			seed = seed,
			scale = TERRAIN_NOISE_SCALE,
			octaves = TERRAIN_NOISE_OCTAVES,
		) + 1) * MAX_ALT/2
	)
def getLayersConnected(*,depth: Screen[int],altitude: Screen[int]) -> Screen[bool]:
	print('generating layers connected...')
	return scrMap(
		lambda u,v : u > LAYER_OVERLAP_HEIGHT and v > LAYER_OVERLAP_HEIGHT,
		depth,
		altitude,
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
	text_surface = font.render(str(TOP_SEA_LEVEL_FACTOR),True,(0,0,0))
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

# totalConvergence = float[-MAX_SPEED,MAX_SPEED] * int[>0]

TERRAIN['altitude 1'] = getAltitude(NOISE_SEED)
TERRAIN['bottom 1'] = getAltitude(NOISE_SEED + 1)
TERRAIN['altitude 2'] = getAltitude(NOISE_SEED + 2)
TERRAIN['land 1'] = getTopLand(altitude = TERRAIN['altitude 1'])
TERRAIN['land 2'] = getBottomLand(altitude = TERRAIN['altitude 2'])
TERRAIN['altitude bottom'] = 2*LAYER_OVERLAP_HEIGHT - TERRAIN['bottom 1']
TERRAIN['true altitude 1'] = 2*LAYER_OVERLAP_HEIGHT + TERRAIN['altitude 1']
TERRAIN['thickness 1'] = TERRAIN['true altitude 1'] - TERRAIN['altitude bottom']
TERRAIN['connected'] = scrMap(
	lambda u,v : u >= v,
	TERRAIN['altitude 2'],
	TERRAIN['altitude bottom'],
)
TERRAIN['under height'] = scrMap(
	lambda w,u,v : 0 if w else u - v,
	TERRAIN['connected'],
	TERRAIN['altitude bottom'],
	TERRAIN['altitude 2'],
)
TERRAIN['sunlight'] = getSunlight()
TERRAIN['snow'] = getSnow(sunlight = TERRAIN['sunlight'],altitude = TERRAIN['altitude 1'])
TERRAIN['greenery 1'] = getTopGreenery(
	altitude = TERRAIN['altitude 1'],
	land = TERRAIN['land 1'],
	snow = TERRAIN['snow'],
	sunlight = TERRAIN['sunlight'],
)
TERRAIN['greenery 2'] = getBottomGreenery(
	altitude = TERRAIN['altitude 2'],
	land = TERRAIN['land 2'],
	connected = TERRAIN['connected'],
)
TERRAIN['connected edges'] = getConnectedEdges(
	connected = TERRAIN['connected'],
)
TERRAIN['underwater lakes'] = scrMap(
	lambda w,u,v : v if w and not u else 0,
	TERRAIN['land 1'],
	TERRAIN['connected'],
	TERRAIN['thickness 1'],
)

TERRAIN['underwater lakes'] //= 2

print(max({v for v in TERRAIN['under height']}))

addColor(TERRAIN)

SCREEN_LAYOUT[0,0] = 'greenery 1'
SCREEN_LAYOUT[1,0] = 'greenery 2'
SCREEN_LAYOUT[2,0] = 'underwater lakes (colored)'

mapLayout(TERRAIN)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()