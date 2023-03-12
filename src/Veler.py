import sys
import pygame
import numpy as np
from Common_Variables import *
from Entity import Entity
from Player import Player
from Game import Game



if __name__ == '__main__':
    while True:
        newGame = Game(screen)
        newGame.startGame()
