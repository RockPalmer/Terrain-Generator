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

SCREEN_LAYOUT = {}
FINAL_SCREEN_LAYOUT = []

Color = tuple[int,int,int]
Point = tuple[int,int]
GRID_SIZE: int = 256
CELL_SIZE: int = 2  # Size of each square in pixels
MAX_ANGLE: int = 359
MAX_COLOR: int = 255
LATTITUDE_EFFECT_DISTANCE: int = 1000
LATTITUDE_EFFECT_STRENGTH: int = 50
MAX_THICKNESS: int = 255
HUMIDITY_RANGE: int = (GRID_SIZE >> 5) - 1
SEA_LEVEL: int = 130
SNOW_LEVEL: int = 160
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
MAX_POINT_INTEGER: int = GRID_SIZE**2 - 1

random.seed(0)

# a(x - x0) + b(y - y0) + c(z - z0) = 0
# a(x - a) + b(y - b) + c(z - c) = 0
# ax - a2 + by - b2 + cz - c2 = 0

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
def perlinNoise(seed: int|float = 0,scale: int = 1,octaves: int = 1) -> Screen:
	"""
	Generate seamless wrapping 2D Perlin noise using 4D Perlin.

	Returns:
	    list[list[float]]: values approximately [-1, 1]
	"""
	filename = Path(f"pnoise_{GRID_SIZE}_{seed}_{scale}_{octaves}.json")
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
def getAverageDistance(point: Point,trn: Screen) -> float:
	distances = []

	for i in range(-HUMIDITY_RANGE,HUMIDITY_RANGE + 1):
		for j in range(-HUMIDITY_RANGE,HUMIDITY_RANGE + 1):
			x = (point[0] + i) % GRID_SIZE
			y = (point[1] + j) % GRID_SIZE
			if not trn[x,y]:
				a = getDistance(point,(x,y))
				if a == 256:
					print((point,(x,y)))
				distances.append(a)
			else:
				distances.append(GRID_SIZE - 1)
	x = sum(distances)/len(distances)
	if x == 256:
		print(x)
	return x
def getCurrentTilt(day: int) -> float:
	min_tilt = -AXIS_TILT
	max_tilt = AXIS_TILT
	return min_tilt + day * (max_tilt - min_tilt)/365
def lattitudeToAngle(latt: int) -> float:
	return latt * 359/GRID_SIZE
def randPoint() -> Point:
	return (
		random.randint(0,GRID_SIZE),
		random.randint(0,GRID_SIZE),
	)
def randColor() -> Color:
	return (
		random.randint(0,255),
		random.randint(0,255),
		random.randint(0,255),
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
def generateNeighborPointsAtRange(radius: int) -> set[Point]:
	values = {
		(i,j) : getDistance((0,0),(i,j)) for i in range(
			-GRID_SIZE//2,
			GRID_SIZE//2,
		) for j in range(
			-GRID_SIZE//2,
			GRID_SIZE//2,
		)
	}
	return {
		k for k,v in values.items() if floor(v) <= radius and ceil(radius) >= radius
	}

print('generating surrounding points...')
#SURROUNDING_POINTS = {i : generateNeighborPointsAtRange(i) for i in range(GRID_SIZE)}

def generateSurroundingPointsAtRange(point: Point,radius: int) -> list[Point]:
	x,y = point
	return sorted(list({
		(
			(x + a) % GRID_SIZE,
			(y + b) % GRID_SIZE,
		) for a,b in SURROUNDING_POINTS[radius]
	}))
def getClosestBorderPoint(point: Point,plates: Screen) -> Point:
	value = plates[point]
	other_plates = {}
	radius = 1
	while len(other_plates):
		for p in generateSurroundingPointsAtRange(point,radius):
			if plates[p] != value:
				other_plates[p] = getDistance(point,p)
		radius += 1
	vals = list(other_plates.items())
	minDist = min({v for _,v in vals})
	index = [k for k,v in vals if v == minDist][0]
	return vals[index][0]
def getClosestPoint(point: Point,points: list[Point],noise_diff: int|None = None) -> Point:
	if noise_diff is None:
		dists = [getDistance(point,p) for p in points]
	else:
		dists = [getDistance(point,p) + noise_diff for p in points]
	minDist = min(dists)
	minDistIndex = [i for i,dist in enumerate(dists) if dist == minDist][0]
	return points[minDistIndex]
def getAltitude() -> Screen:
	filename = Path(f"altitude_{NOISE_SEED}_{TERRAIN_NOISE_SCALE}_{TERRAIN_NOISE_OCTAVES}_{GRID_SIZE}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : values[x][y],
			Screen(GRID_SIZE),
		)
	pnoise = perlinNoise(
		seed = random.randint(0,255),
		scale = TERRAIN_NOISE_SCALE,
		octaves = TERRAIN_NOISE_OCTAVES,
	)
	values = [[(pnoise[x,y] + 1) * 255/2 for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return scrMap(
		lambda v : (v + 1) * 255/2,
		pnoise,
	)
def getLand(*,altitude: Screen|None = None) -> Screen:
	filename = Path(f"land_{NOISE_SEED}_{TERRAIN_NOISE_SCALE}_{TERRAIN_NOISE_OCTAVES}_{GRID_SIZE}_{SEA_LEVEL}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : values[x][y],
			Screen(GRID_SIZE),
		)
	if altitude is None:
		altitude = getAltitude()
	values = [[altitude[x,y] > SEA_LEVEL for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return scrMap(
		lambda v : v > SEA_LEVEL,
		altitude,
	)
def getHumidity(*,land: Screen|None = None,altitude: Screen|None = None) -> Screen:
	filename = Path(f"humidity_{NOISE_SEED}_{TERRAIN_NOISE_SCALE}_{TERRAIN_NOISE_OCTAVES}_{GRID_SIZE}_{SEA_LEVEL}_{HUMIDITY_SMUDGE_RADIUS}.json")
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
	filename = Path(f"sunlight_{GRID_SIZE}_{str(AXIS_TILT).replace('.','_')}.json")
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
	filename = Path(f"snow_{NOISE_SEED}_{TERRAIN_NOISE_SCALE}_{TERRAIN_NOISE_OCTAVES}_{GRID_SIZE}_{str(AXIS_TILT).replace('.','-')}.json")
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
	if altitude is None:
		altitude = getAltitude()
	snow = scrMap(
		lambda u,v : (255 - u)/7 + v > SNOW_LEVEL,
		sunlight,
		altitude,
	)
	values = [[snow[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return snow
def getGreenery(
	*,
	altitude: Screen|None = None,
	land: Screen|None = None,
	snow : Screen|None = None,
	sunlight: Screen|None = None,
) -> Screen:
	if altitude is None:
		altitude = getAltitude()
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
def getTectonicPlates() -> Screen:
	filename = Path(f"tectonicPlates_{NOISE_SEED}_{NUM_CONTINENTS}_{GRID_SIZE}_{NUM_CONTINENT_RUNS}_{TERRAIN_NOISE_SCALE}_{TERRAIN_NOISE_OCTAVES}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : tuple(values[x][y]),
			Screen(GRID_SIZE),
		)
	points = set()
	while len(points) < NUM_CONTINENTS:
		points.add(randPoint())
	points = list(points)
	tectonicPlates = keyMap(
		lambda x,y,v : getClosestPoint((x,y),points),
		Screen(GRID_SIZE)
	)
	for i in range(NUM_CONTINENT_RUNS):
		for j in range(NUM_CONTINENTS):
			coords = [(x,y) for (x,y),_ in tectonicPlates.enumerate() if tectonicPlates[x,y] == points[j]]
			points[j] = getCentroid(coords)
		tectonicPlates = keyMap(
			lambda x,y,v : getClosestPoint((x,y),points),
			Screen(GRID_SIZE)
		)
	values = [[tectonicPlates[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	content = json.dumps(values)
	with open(filename,mode = 'w') as f:
		f.write(content)
	return tectonicPlates
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
def getNeighbors(plates: Screen|None = None) -> Screen:
	filename = Path(f"tectonicNeighbors_{NOISE_SEED}_{NUM_CONTINENTS}_{GRID_SIZE}_{NUM_CONTINENT_RUNS}_{TERRAIN_NOISE_SCALE}_{TERRAIN_NOISE_OCTAVES}.json")
	if filename.is_file():
		with open(filename,mode = 'r') as f:
			content = f.read()
		values = json.loads(content)
		return keyMap(
			lambda x,y,v : tuple(values[x][y]),
			Screen(GRID_SIZE),
		)
	neighbors = keyMap(
		lambda x,y,v : getNeighborsOfPoint((x,y),v),
		plates,
	)
	values = [[neighbors[x,y] for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
	
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
	text_surface = font.render(str(SEA_LEVEL),True,(0,0,0))
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

# y = 10e^(-(x - 127)^2)

print('generating altitude...')
#TERRAIN['altitude'] = getAltitude()
print('generating land...')
#TERRAIN['land'] = getLand(altitude = TERRAIN['altitude'])
print('generating humidity...')
#TERRAIN['humidity'] = getHumidity(land = TERRAIN['land'])
print('generating sunlight...')
#TERRAIN['sunlight'] = getSunlight()
print('generating snow...')
#TERRAIN['snow'] = getSnow(sunlight = TERRAIN['sunlight'],altitude = TERRAIN['altitude'])
print('generating tectonic plates...')
TERRAIN['tectonic plates'] = getTectonicPlates()
print('generating greenery...')
#TERRAIN['greenery'] = getGreenery(snow = TERRAIN['snow'],altitude = TERRAIN['altitude'],land = TERRAIN['land'])

addColor(TERRAIN)
print(TERRAIN.keys())

SCREEN_LAYOUT[0,0] = 'tectonic plates (colored)'

mapLayout(TERRAIN)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()