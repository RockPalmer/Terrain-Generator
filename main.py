import pygame,random
import numpy as np
from typing import Iterable,Any
from terrain import *

# Example: 2D array with values 0–2 for 3 colors
main_screen = Terrain(5,1024)
main_screen = main_screen.continents(
	count = 12,
	iterations = 4
)
main_screen = main_screen.lattitudes(
	maximum = 11,
	minimum = 1,
	color = lambda x,mx,mn : (
		round((255 * (x - mn))/(mx - mn)),
		round((255 * (x - mn))/(mx - mn)),
		round((255 * (x - mn))/(mx - mn)),
	),
	poles = (
		(True,True),
		(True,True)
	),
	smoothing_factor = 4
)

window_size = 800
border_width = 10
surface = pygame.transform.scale(
	pygame.surfarray.make_surface(main_screen['continent'].as_array()),
	(window_size,window_size)
)

pygame.init()
screen = pygame.display.set_mode(
	(window_size,window_size),
	flags = pygame.RESIZABLE
)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(surface,(0,0))
    pygame.display.flip()
pygame.quit()
