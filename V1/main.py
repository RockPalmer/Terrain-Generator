import pygame,random
import numpy as np
from typing import Iterable,Any
from terrain import *

# Example: 2D array with values 0–2 for 3 colors
main_screen = Terrain(5,256)
main_screen.set_bounds(0,255**3 - 1)
main_screen['continents'] = main_screen.continents(
	count = 12,
	iterations = 4
)
new_nums = list(main_screen.randset(12))
main_screen['continents'] = main_screen['continents'].apply(
	lambda v : Color(
		new_nums[v] % 255,
		new_nums[v] // 255 % 255,
		new_nums[v] // 255**2 % 255
	)
)
main_screen['lattitudes'] = main_screen.lattitudes(
	(0,0),
	(0,255),
	(255,0),
	(255,255)
) / (
	len(main_screen)*2**0.5
) * 255
main_screen['lattitudes'] = main_screen['lattitudes'].apply(
	lambda v : Color(v,v,v)
)

window_size = 800
border_width = 10
surface = pygame.transform.scale(
	pygame.surfarray.make_surface(main_screen['lattitudes'].as_array()),
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
