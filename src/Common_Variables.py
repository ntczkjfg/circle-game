import pygame
import numpy as np
from os import listdir

# Initialize the game window
screen_width = 504
screen_height = 896
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Veler")

rng = np.random.default_rng()
PI = float(np.pi)
TAU = 2 * PI
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

powerups = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

images = {}
PATH = "C:/Users/User/My Stuff/GitHub/circle-game/img/"
imgList = listdir(PATH)
for filename in imgList:
    images[filename[:-4]] = pygame.transform.scale(pygame.image.load(PATH + filename), (30, 30))
    images[filename[:-4]].set_colorkey(WHITE)
