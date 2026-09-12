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

WIDTH: int = 1000
HEIGHT: int = 700
FPS: int = 60

NUM_AGENTS: int = 100

MAX_SPEED: float = 2.5
AGENT_RADIUS: int = 5

BACKGROUND: Color = (20,20,30)

# ------------------------
# Agent
# ------------------------

class Agent:
	def __init__(self):
		self.pos: ndarray[float64,float64] = numpy.array(
			[
				random.uniform(0,WIDTH),
				random.uniform(0,HEIGHT),
			],
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
	def update(self):
		# Small random steering
		steer: ndarray[float64,float64] = numpy.random.uniform(-0.2,0.2,2)
		self.vel += steer
		speed: float64 = linalg.norm(self.vel)
		if speed > MAX_SPEED:
			self.vel /= speed * MAX_SPEED
		self.pos += self.vel
		# Bounce off walls
		if self.pos[0] < 0:
			self.pos[0] = 0
			self.vel[0] *= -1
		if self.pos[0] > WIDTH:
			self.pos[0] = WIDTH
			self.vel[0] *= -1
		if self.pos[1] < 0:
			self.pos[1] = 0
			self.vel[1] *= -1
		if self.pos[1] > HEIGHT:
			self.pos[1] = HEIGHT
			self.vel[1] *= -1
	def draw(self, screen):
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

# ------------------------
# Simulation
# ------------------------

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Agent Simulation")

clock = pygame.time.Clock()

agents = [Agent() for _ in range(NUM_AGENTS)]

running = True

while running:
	dt = clock.tick(FPS)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	for agent in agents:
		agent.update()
	screen.fill(BACKGROUND)
	for agent in agents:
		agent.draw(screen)
	pygame.display.flip()
pygame.quit()