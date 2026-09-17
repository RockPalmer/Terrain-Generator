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
HUMIDITY_RANGE: int = (GRID_SIZE >> 5) - 1
OVERWORLD_SURFACE_MAX: int = 255
OVERWORLD_DEPTH_MAX: int = 255
MIDWORLD_SURFACE_MAX: int = 255
OVERWORLD_SEA_LEVEL_FACTOR = 0.51
SNOW_LEVEL_FACTOR = 0.7
TERRAIN_NOISE_SCALE: int = 1
TERRAIN_NOISE_OCTAVES: int = 8
NOISE_SEED: int = 0
AXIS_TILT: float = 23.44 * tau/360
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
MIDWORLD_SEA_LEVEL_FACTOR = 0.4
OVERWORLD_DEPTH_OVERLAP_HEIGHT_FACTOR = 0.5
MIDWORLD_ALTITUDE_OVERLAP_HEIGHT_FACTOR = OVERWORLD_DEPTH_OVERLAP_HEIGHT_FACTOR

OVERWORLD_SEA_LEVEL: float = OVERWORLD_SEA_LEVEL_FACTOR * OVERWORLD_SURFACE_MAX
MIDWORLD_SEA_LEVEL: float = MIDWORLD_SEA_LEVEL_FACTOR * MIDWORLD_SURFACE_MAX
OVERWORLD_DEPTH_OVERLAP_HEIGHT: float = OVERWORLD_DEPTH_OVERLAP_HEIGHT_FACTOR * OVERWORLD_DEPTH_MAX
MIDWORLD_ALTITUDE_OVERLAP_HEIGHT: float = MIDWORLD_ALTITUDE_OVERLAP_HEIGHT_FACTOR * MIDWORLD_SURFACE_MAX
SNOW_LEVEL: float = OVERWORLD_SURFACE_MAX * SNOW_LEVEL_FACTOR

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
def getHumidity(*,land: Screen|None = None,altitude: Screen|None = None) -> Screen:
	print('generating humidity...')
	filename = Path(f"humidity_{flm(NOISE_SEED)}_{flm(TERRAIN_NOISE_SCALE)}_{flm(TERRAIN_NOISE_OCTAVES)}_{flm(GRID_SIZE)}_{flm(OVERWORLD_SEA_LEVEL_FACTOR)}_{flm(HUMIDITY_SMUDGE_RADIUS)}.json")
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

# totalConvergence = float[-MAX_SPEED,MAX_SPEED] * int[>0]

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
TERRAIN['overworld thickness']: Screen[float] = TERRAIN['overworld surface'] - TERRAIN['overworld depth']
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
TERRAIN['overworld greenery'] = getTopGreenery(
	altitude = TERRAIN['overworld surface'],
	land = TERRAIN['overworld land'],
	snow = TERRAIN['snow'],
	sunlight = TERRAIN['sunlight'],
)
TERRAIN['midworld greenery'] = getBottomGreenery(
	altitude = TERRAIN['midworld surface'],
	land = TERRAIN['midworld land'],
	connected = TERRAIN['overworld-midworld connections'],
)
TERRAIN['overworld-midworld connection edges'] = getConnectedEdges(
	connected = TERRAIN['overworld-midworld connections'],
)
TERRAIN['midworld surface flow vector x'] = Screen(GRID_SIZE)
TERRAIN['midworld surface flow vector y'] = Screen(GRID_SIZE)
TERRAIN['midworld surface flow divergence'] = Screen(GRID_SIZE)
for x in range(GRID_SIZE):
	for y in range(GRID_SIZE):
		if not TERRAIN['overworld-midworld connections'][x,y]:
			tl = TERRAIN['midworld surface'][(x-1) % GRID_SIZE,(y-1) % GRID_SIZE] if not TERRAIN['overworld-midworld connections'][(x-1) % GRID_SIZE,(y-1) % GRID_SIZE] else MIDWORLD_SURFACE_MAX
			tc = TERRAIN['midworld surface'][x,(y-1) % GRID_SIZE] if not TERRAIN['overworld-midworld connections'][x,(y-1) % GRID_SIZE] else MIDWORLD_SURFACE_MAX
			tr = TERRAIN['midworld surface'][(x+1) % GRID_SIZE,(y-1) % GRID_SIZE] if not TERRAIN['overworld-midworld connections'][(x+1) % GRID_SIZE,(y-1) % GRID_SIZE] else MIDWORLD_SURFACE_MAX

			ml = TERRAIN['midworld surface'][(x-1) % GRID_SIZE,y] if not TERRAIN['overworld-midworld connections'][(x-1) % GRID_SIZE,y] else MIDWORLD_SURFACE_MAX
			mc = TERRAIN['midworld surface'][x,y]
			mr = TERRAIN['midworld surface'][(x+1) % GRID_SIZE,y] if not TERRAIN['overworld-midworld connections'][(x+1) % GRID_SIZE,y] else MIDWORLD_SURFACE_MAX

			bl = TERRAIN['midworld surface'][(x-1) % GRID_SIZE,(y+1) % GRID_SIZE] if not TERRAIN['overworld-midworld connections'][(x-1) % GRID_SIZE,(y+1) % GRID_SIZE] else MIDWORLD_SURFACE_MAX
			bc = TERRAIN['midworld surface'][x,(y+1) % GRID_SIZE] if not TERRAIN['overworld-midworld connections'][x,(y+1) % GRID_SIZE] else MIDWORLD_SURFACE_MAX
			br = TERRAIN['midworld surface'][(x+1) % GRID_SIZE,(y+1) % GRID_SIZE] if not TERRAIN['overworld-midworld connections'][(x+1) % GRID_SIZE,(y+1) % GRID_SIZE] else MIDWORLD_SURFACE_MAX

			TERRAIN['midworld surface flow vector x'][x,y] = ((tr + 2*mr + br) - (tl + 2*ml + bl)) / 8
			TERRAIN['midworld surface flow vector y'][x,y] = ((bl + 2*bc + br) - (tl + 2*tc + tr)) / 8
		else:
			TERRAIN['midworld surface flow vector x'][x,y] = 0
			TERRAIN['midworld surface flow vector y'][x,y] = 0
for x in range(GRID_SIZE):
	for y in range(GRID_SIZE):
		if not TERRAIN['overworld-midworld connections'][x,y]:
			TERRAIN['midworld surface flow divergence'][x,y] = (
				TERRAIN['midworld surface flow vector x'][(x + 1) % GRID_SIZE,y] - TERRAIN['midworld surface flow vector x'][(x - 1) % GRID_SIZE,y]
			) / 2 + (
				TERRAIN['midworld surface flow vector y'][x,(y + 1) % GRID_SIZE] - TERRAIN['midworld surface flow vector y'][x,(y - 1) % GRID_SIZE]
			) / 2
		else:
			TERRAIN['midworld surface flow divergence'][x,y] = None
vals = {v for v in TERRAIN['midworld surface flow divergence'] if v is not None}
minval = min(vals)
maxval = max(vals)
TERRAIN['midworld surface flow divergence'] = scrMap(
	lambda v : COLOR_SCALE[int((v + minval) * len(COLOR_SCALE)/(maxval - minval))] if v is not None else (0,0,0),
	TERRAIN['midworld surface flow divergence'],
)

addColor(TERRAIN)

SCREEN_LAYOUT[0,0] = 'overworld greenery'
SCREEN_LAYOUT[1,0] = 'midworld greenery'
SCREEN_LAYOUT[2,0] = 'midworld surface flow divergence'

mapLayout(TERRAIN)
drawMap()

# Keep the window open
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

pygame.quit()