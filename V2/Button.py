import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))

class CustomSlider:
	def __init__(self, x, y, width, height, min_val, max_val):
		self.rect = pygame.Rect(x, y, width, height)
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

	def draw(self, screen, color=(0, 100, 255)):
		# Draw track
		pygame.draw.rect(screen, (200, 200, 200), self.rect)
		# Draw fill
		fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
		pygame.draw.rect(screen, color, (self.rect.x, self.rect.y, fill_width, self.rect.height))
		# Draw handle
		handle_x = self.rect.x + fill_width - self.handle_width
		pygame.draw.rect(screen, (50, 50, 50), (handle_x, self.rect.y, self.handle_width, self.rect.height))

slider = CustomSlider(100, 100, 600, 40, 0, 100)

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	mouse_pos = pygame.mouse.get_pos()
	mouse_pressed = pygame.mouse.get_pressed()

	slider.update(mouse_pos, mouse_pressed)

	screen.fill((255,255,255))
	slider.draw(screen)

	# Display value
	font = pygame.font.SysFont(None, 36)
	text = font.render(f"Value: {slider.value:.1f}", True, (0, 0, 0))
	screen.blit(text, (100, 160))

	pygame.display.flip()

pygame.quit()   