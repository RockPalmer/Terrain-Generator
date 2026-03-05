import pygame,random
import numpy as np
from typing import Iterable,Any
from screen import (
	Screen,
	select_rand
)

def random_map(values : list,size : int) -> list[list]:
	return Screen([[select_rand(values) for i in range(size)] for j in range(size)])

COLORS = {
	'white' : [255,255,255],
	'black' : [0,0,0],
	'green' : [77,251,43],
	'blue' : [0,0,255],
}
def rgb(*args):
	global COLORS

	if len(args) == 1:
		return COLORS[args[0].lower()]
	return list(args)

# Example: 2D array with values 0–2 for 3 colors
main_screen = Screen(8).spatter(
	[rgb('green'),rgb('blue')],
	'color'
).batch_blend(
	4,
	[
		(-1,-1),
		(-1,0),
		(0,-1),
		(0,0),
	],
	'color'
)
window_size = 800
border_width = 10
surface = pygame.transform.scale(
	pygame.surfarray.make_surface(main_screen['color'].as_array()),
	(window_size,window_size)
)

screen2 = main_screen.batch_smooth('color')
screen2[10,10,'color'] = rgb('black')
surface2 = pygame.transform.scale(
	pygame.surfarray.make_surface(screen2['color'].as_array()),
	(window_size,window_size)
)

pygame.init()
screen = pygame.display.set_mode(
	(window_size * 2 + 10,window_size),
	flags = pygame.RESIZABLE
)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(surface,(0,0))
    screen.blit(surface2,(window_size + 10,0))
    pygame.display.flip()
pygame.quit()