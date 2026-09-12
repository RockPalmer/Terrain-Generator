import pygame,random,numpy
from math import (
	tau,
	cos,
	sin
)
from numpy import (
	ndarray,
	linalg,
	float64
)

# ------------------------
# Configuration
# ------------------------

Color = tuple[int,int,int]

ENV_SIZE: int = 700
UI_WIDTH: int = 200
UI_MARGIN_WIDTH: int = 10
UI_X: int = ENV_SIZE
UI_Y: int = 0
FPS: int = 60
SLIDER_HEIGHT: int = 20

NUM_AGENTS: int = 100

MAX_SPEED: float = 2.5
AGENT_RADIUS: int = 5

BACKGROUND: Color = (20,20,30)
UI_RECT_COLOR: Color = (255,198,183)
SLIDER_HANDLE_COLOR: Color = (255,255,255)
SLIDER_FILL_COLOR: Color = (0,100,255)

# ------------------------
# Agent
# ------------------------

class Agent:
	def __init__(self,arg1,arg2):
		if isinstance(arg1,int|float) and isinstance(arg2,int|float):
			
			self.pos: ndarray[float64,float64] = numpy.array(
				[x,y],
				dtype = float,
			)
		angle: float64 = random.uniform(0,tau)

		self.vel: ndarray[float64,float64] = numpy.array([
			cos(angle),
			sin(angle),
		]) * MAX_SPEED
		self.color: Color = (
			random.randint(80,255),
			random.randint(80,255),
			random.randint(80,255),
		)
		self.days_since_eating = 0
		self.days_since_drinking = 0
		self.days_since_mating = 0
	def update(self):
		# Small random steering
		steer: ndarray[float64,float64] = numpy.random.uniform(-0.2,0.2,2)
		self.vel += steer
		speed: float64 = linalg.norm(self.vel)
		if speed > MAX_SPEED:
			self.vel /= speed * MAX_SPEED
		self.pos += self.vel
		if self.pos[0] < 0:
			self.pos[0] = SIZE + self.pos[0]
		if self.pos[0] >= SIZE:
			self.pos[0] = self.pos[0] - SIZE
		if self.pos[1] < 0:
			self.pos[1] = SIZE + self.pos[1]
		if self.pos[1] >= SIZE:
			self.pos[1] = self.pos[1] - SIZE
	def draw(self,screen):
		pygame.draw.circle(
			screen,
			self.color,
			self.pos.astype(int),
			AGENT_RADIUS
		)
		# Draw heading
		heading = self.pos + self.vel * 5
		pygame.draw.line(
			screen,
			(255,255,255),
			self.pos.astype(int),
			heading.astype(int),
			2
		)
class CustomSlider:
	def __init__(self,x,y,min_val,max_val):
		self.rect = pygame.Rect(x,y,UI_WIDTH - 2*UI_MARGIN_WIDTH,SLIDER_HEIGHT)
		self.min_val = min_val
		self.max_val = max_val
		self.value = 50  # Initial value
		self.dragging = False
		self.handle_width = 20

	def get_value_from_pos(self, x):
		# Map mouse X position to value range
		ratio = (x - self.rect.x) / self.rect.width
		ratio = max(0, min(1, ratio)) # Clamp between 0 and 1
		return self.min_val + ratio * (self.max_val - self.min_val)

	def update(self, mouse_pos, mouse_pressed):
		if mouse_pressed[0]:  # Left click
			# Check if clicking inside slider or handle
			if self.rect.collidepoint(mouse_pos):
				self.dragging = True
				self.value = self.get_value_from_pos(mouse_pos[0])
		else:
			self.dragging = False

	def draw(self, screen):
		# Draw track
		pygame.draw.rect(screen,BACKGROUND, self.rect)
		# Draw fill
		fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
		pygame.draw.rect(screen,SLIDER_FILL_COLOR,(self.rect.x, self.rect.y, fill_width, self.rect.height))
		# Draw handle
		handle_x = self.rect.x + fill_width - self.handle_width
		pygame.draw.rect(screen,SLIDER_HANDLE_COLOR, (handle_x, self.rect.y, self.handle_width, self.rect.height))

# ------------------------
# Simulation
# ------------------------

pygame.init()

screen = pygame.display.set_mode((ENV_SIZE + UI_WIDTH,ENV_SIZE))
pygame.display.set_caption("AI Agent Simulation")

UI_RECT = pygame.Rect(UI_X,UI_Y,UI_WIDTH,ENV_SIZE)

clock = pygame.time.Clock()

agents = [Agent(
	random.randint(0,SIZE),
	random.randint(0,SIZE),
) for _ in range(NUM_AGENTS)]

running = True
slider = CustomSlider(
	x = UI_X + UI_MARGIN_WIDTH,
	y = UI_Y + UI_MARGIN_WIDTH,
	min_val = 0,
	max_val = 100,
)

while running:
	dt = clock.tick(FPS)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	mouse_pos = pygame.mouse.get_pos()
	mouse_pressed = pygame.mouse.get_pressed()
	for agent in agents:
		agent.update()
	screen.fill(BACKGROUND)
	slider.update(mouse_pos,mouse_pressed)
	for agent in agents:
		agent.draw(screen)
	pygame.draw.rect(screen,UI_RECT_COLOR,UI_RECT)
	slider.draw(screen)
	pygame.display.flip()
pygame.quit()