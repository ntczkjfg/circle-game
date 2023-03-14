import pygame
import numpy as np
from Common_Variables import *
from Entity import Entity

class Player(Entity):
    def __init__(self, lifeCount = None, parent = None):
        super().__init__(c = np.array([screen_width / 2, screen_height / 2])
                         , r = 10
                         , speed = 5
                         , direction = np.array([0, 0])
                         , typ = -1
                         , player = self
                         , parent = parent)
        self.lifeCount = 3 if lifeCount == None else lifeCount
        self.iframes = 0
        # Powerups added as list:  [n, t] where n is the powerup state, and t is the powerup duration (in frames)
        # See self.collide for powerup functions
        self.powerups = []
        self.dirMap = {pygame.K_d: np.array([1, 0])
                       , pygame.K_w: np.array([0, 1])
                       , pygame.K_a: np.array([-1, 0])
                       , pygame.K_s: np.array([0, -1])
                       , pygame.K_RIGHT: np.array([1, 0])
                       , pygame.K_UP: np.array([0, 1])
                       , pygame.K_LEFT: np.array([-1, 0])
                       , pygame.K_DOWN: np.array([0, -1])}

    def collide(self, entity):
        if entity.type == 0: # food
            if self.powerup(14):
                entity.r /= 2
            entity.type = 1
            entity.blueTimer = 60
            self.game.food -= 1
            self.game.score += 1
        elif entity.type == 1 or entity.type == -2: # blue, purple
            pass
        elif entity.type == 2: # red
            if self.powerup(10): # Kill red circles
                self.game.entities.remove(entity)
            elif self.powerup(11) or self.iframes > 0: # Immune to damage
                pass
            elif self.powerup(12): # Forcefield that breaks
                entity.type = 1
                entity.blueTimer = 60
                for powerup in self.powerups:
                    if powerup[0] == 12:
                        self.powerups.remove(powerup)
                        break
            else:
                self.damage()
                entity.type = 1
                entity.blueTimer = 60
        elif entity.type == 3: # Activated bomb entity
            if self.iframes == 0:
                self.damage()
        elif entity.type == 10: # Lets you kill red circles for 3 seconds
            self.powerups.append([10, 3*60])
        elif entity.type == 11: # Immune to damage for 5 seconds
            self.powerups.append([11, 5*60])
        elif entity.type == 12: # Forcefield, last 15 seconds or 1 hit
            self.powerups.append([12, 15*60])
        elif entity.type == 13: # Entities move 1/3 speed for 8 seconds
            self.powerups.append([13, 8*60])
        elif entity.type == 14: # Yellow circles double in size for 20 seconds
            if not self.powerup(14):
                self.powerups.append([14, 20*60])
            else:
                for powerup in self.powerups:
                    if powerup[0] == 14:
                        powerup[1] = 20*60
                        return
            for entity in self.game.entities:
                if entity.type == 0:
                    entity.r *= 2
        elif entity.type == 15: # Spawn extra yellow circle
            self.game.spawnFood()
        elif entity.type == 16: # Gain extra life
            self.lifeCount += 1
        elif entity.type == 17: # All reds turn blue for 5 seconds
            for entity1 in self.game.entities:
                if entity1.type == 2:
                    entity1.type = 1
                    entity1.blueTimer = 5*60
        elif entity.type == 18: # Repel red circles for 5 seconds
            self.powerups.append([18, 5*60])
        elif entity.type == 19 and not entity.bombTimer: # Bomb, explodes after 5 seconds damaging player and killing entities within radius
            entity.bombTimer = 5*60
    
    def color(self):
        for powerup in self.powerups:
            if powerup[0] == 10:
                return CYAN
            elif powerup[0] == 11:
                return GREEN
        if self.iframes % 4 > 1:
            return BLACK
        return WHITE

    def damage(self):
        if self.powerup(12):
            for powerup in self.powerups:
                if powerup[0] == 12:
                    self.powerups.remove(powerup)
                    return
        if self.powerup(11):
            return
        self.lifeCount -= 1
        self.iframes = 30

    def decrementPowerups(self):
        if self.iframes > 0:
            self.iframes -= 1
        for powerup in self.powerups:
            powerup[1] -= 1
            if powerup[1] <= 0:
                if powerup[0] == 14:
                    for entity in self.game.entities:
                        if entity.type == 0:
                            entity.r /= 2
                self.powerups.remove(powerup)

    def draw(self):
        if self.powerup(12):
            for coord in self.wrappedCoords():
                pygame.draw.circle(screen
                                   , (128, 128, 255)
                                   , [coord[0], screen_height - coord[1]]
                                   , self.r + 4)
        super().draw()

    def isPowerup(self):
        return False

    def move(self):
        if np.array_equal(self.dir, np.array([0, 0])):
            return
        super().move()
        self.dir = np.array([0, 0])

    def powerup(self, key):
        powerups = [powerup[0] for powerup in self.powerups]
        if key in powerups:
            return True
        return False
    
    def turn(self, key):
        self.dir += self.dirMap[key]
