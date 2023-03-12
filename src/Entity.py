import pygame
import numpy as np
from Common_Variables import *

class Entity():
    def __init__(self
                 , c = None
                 , r = None
                 , speed = None
                 , direction = None
                 , typ = None
                 , timer = None
                 , player = None
                 , parent = None):
        self.game = parent
        self.player = player
        self.bombTimer = None
        # Size, position, velocity
        self.r = rng.integers(4, 19) if r == None else r
        if type(c) == type(None):
            x = rng.integers(self.r + 1, screen_width - self.r)
            y = rng.integers(self.r + 1, screen_height - self.r)
            self.c = np.array([x, y], dtype='float64')
        else:
            self.c = c
        self.speed = 1 + 3 * rng.random() if speed == None else speed
        # radians
        if type(direction) == type(None):
            self.dir = 2*rng.random(2) - 1
            self.dir = self.dir / np.linalg.norm(self.dir)
        else:
            self.dir = direction
        
        # Controls behavior.
        # -2 = debug
        # -1 = player
        # 0 = food, runs from player
        # 1 = neutral, travels linearly, no damage
        # 2 = predator, moves toward player
        # 10 = powerup, allows killing reds
        # 11 = powerup, immune to damage
        # 12 = powerup, forcefield
        # 13 = powerup, circles slow down for 8 seconds
        # 14 = powerup, yellow circles double diameter
        # 15 = powerup, spawn extra yellow circle
        # 16 = powerup, gain an extra life
        # 17 = powerup, all red circles turn blue for 5 seconds
        # 18 = powerup, you strongly repel close red circles for 5 seconds
        # 19 = powerup, bomb
        # 20 = bomb entity
        self.type = 0 if typ == None else typ
        
        # Used to time out temporary state changes
        self.timer = 0 if timer == None else timer
    
    def left(self):
        return self.c[0] - self.r
    def right(self):
        return self.c[0] + self.r
    def bottom(self):
        return self.c[1] - self.r
    def top(self):
        return self.c[1] + self.r

    def isPowerup(self):
        if self.type >= 10:
            return True
        return False

    def bounce(self, entity):
        if self.type == -1 or self.speed == 0: # Player doesn't bounce
            return
        diffs = self.getDiffs(entity)
        diffs = diffs / np.linalg.norm(diffs)
        angle = np.arccos(np.dot(self.dir, diffs))
        f = -1 if angle > PI/2 else 1
        norm = self.getDiffs(entity)
        norm = norm / np.linalg.norm(norm)
        self.dir -= 2*np.dot(norm, self.dir)*norm
        self.dir *= f

    def collides(self, entity):
        diffs = self.getDiffs(entity)
        if np.linalg.norm(diffs) <= self.r + entity.r:
            return True
        return False
    
    def color(self):
        if self.type == 0: # Food
            return YELLOW
        elif self.type == 1: # Blue
            return BLUE
        elif self.type == 2: # Red
            return RED
        elif self.type == -2: # Debug
            return PURPLE
        elif self.type == 10: # Powerup, lets you kill reds
            return CYAN
        elif self.type == 11: # Powerup, immune to damage
            return GREEN
        elif self.type == 12: # Powerup, forcefield
            return (255, 128, 128)
        elif self.type == 13: # Powerup, circles move half speed
            return (128, 255, 128)
        elif self.type == 14: # Powerup, yellow circles double radius
            return (64, 128, 128)
        elif self.type == 15: # Powerup, spawn extra yellow circle
            return (255, 255, 128)
        elif self.type == 16: # Powerup, +1 life
            return (255, 64, 64)
        elif self.type == 17: # Powerup, all red circles turn blue for 5 seconds
            return (64, 64, 255)
        elif self.type == 18: # Powerup, repel red circles
            return (64, 255, 255)
        elif self.type == 19: # Powerup, bomb
            return (0, 0, 128)
        elif self.type == 20: # Active bomb
            if self.bombTimer > 60:
                if self.bombTimer % 30 < 15:
                    return (0, 0, 128)
                return (200, 128, 0)
            if self.bombTimer >= 0:
                if self.bombTimer % 20 < 10:
                    return (0, 0, 128)
                return (200, 128, 0)
            if self.bombTimer >= -10:
                return (255, 0, 0)
            return (200, 200, 0)
        else: # Forgot to add color, fallback to grey
            return (128, 128, 128)

    # Draws the entity on screen
    def draw(self):
        for coord in self.wrappedCoords():
            pygame.draw.circle(screen
                               , self.color()
                               , [coord[0], screen_height - coord[1]]
                               , self.r)

    # Gets x- and y-differences between self and another entity
    # Accounts for screen wrapping if necessary, finding diffs
    # via the nearest path through edges
    def getDiffs(self, entity):
        xDiff = entity.c[0] - self.c[0]
        yDiff = entity.c[1] - self.c[1]
        if self.game.wrapping:
            if xDiff > screen_width / 2:
                xDiff -= screen_width
            elif xDiff < -screen_width / 2:
                xDiff += screen_width
            if yDiff > screen_height / 2:
                yDiff -= screen_height
            elif yDiff < -screen_height / 2:
                yDiff += screen_height
        return np.array([xDiff, yDiff])

    # Moves the entity, accounting for edge collision or wrapping, as well as collision with the player or other entities
    def move(self, colliders = []):
        if self.speed == 0:
            return
        speed = self.speed
        if self.player.powerup(13) and self.type != -1: speed /= 3
        newCoords = self.c + speed * self.dir
        if not self.game.wrapping:
            # Then collide with the edges
            if newCoords[0] - self.r <= 0:
                self.dir[0] = abs(self.dir[0])
                newCoords[0] = self.c[0]
            elif newCoords[0] + self.r >= screen_width:
                self.dir[0] = -abs(self.dir[0])
                newCoords[0] = self.c[0]
            if newCoords[1] - self.r <= 0:
                self.dir[1] = abs(self.dir[1])
                newCoords[1] = self.c[1]
            elif newCoords[1] + self.r >= screen_height:
                self.dir[1] = -abs(self.dir[1])
                newCoords[1] = self.c[1]
        newEntity = Entity(c = newCoords, r = self.r, speed = self.speed, direction = self.dir, typ = self.type, timer = self.timer, parent = self.game)
        for collider in colliders:
            if collider == self: continue
            if self.collides(collider):
                if collider.type == 20:
                    if collider.bombTimer <= 0:
                        self.game.entities.remove(self)
                        return
                    if not self.game.powerupsCollide:
                        continue
                self.bounce(collider)
                collider.bounce(self)
                while self.collides(collider):
                    collider.move()
            if newEntity.collides(collider):
                if collider.type == 20:
                    if collider.bombTimer <= 0:
                        self.game.entities.remove(self)
                        return
                    if not self.game.powerupsCollide:
                        continue
                if collider.type == -1:
                    collider.collide(self)
                if not self.collides(collider):
                    newCoords = self.c
                    self.bounce(collider)
                    collider.bounce(self)
        self.c = newCoords
        if self.game.wrapping:
            # And if necessary, wrap
            if self.right() <= 0: self.c[0] = screen_width - self.r
            if self.left() >= screen_width: self.c[0] = self.r
            if self.top() <= 0: self.c[1] = screen_height - self.r
            if self.bottom() >= screen_height: self.c[1] = self.r

    # Red and yellow circles bend toward and away from the player, respectively
    def turn(self, player, parent):
        if (self.type != 0 and self.type != 2) or self.speed == 0:
            return
        vectSelfToPlayer = self.getDiffs(player)
        x = vectSelfToPlayer - self.dir
        dist = np.linalg.norm(vectSelfToPlayer)
        if self.type == 0: # Runs from player
            x = self.dir - vectSelfToPlayer
        elif self.type == 2: # Runs to player
            # Powerup that strongly repels nearby red circles
            if self.player.powerup(18) and dist < 0.5*min(screen_width, screen_height):
                x = 20*(self.dir - vectSelfToPlayer)
            else:
                x = vectSelfToPlayer - self.dir
        self.dir = self.dir + x / dist / 100
        self.dir = self.dir / np.linalg.norm(self.dir)

    # Returns a list of coordinate pairs necessary to draw on screen to fully account
    # for edge wrapping
    def wrappedCoords(self):
        wrappedCoords = [self.c]
        if not self.game.wrapping:
            return wrappedCoords
        if self.left() < 0:
            wrappedCoords.append((self.c[0] + screen_width, self.c[1]))
            if self.bottom() < 0:
                wrappedCoords.append((self.c[0] + screen_width, self.c[1] + screen_height))
            elif self.top() > screen_height:
                wrappedCoords.append((self.c[0] + screen_width, self.c[1] - screen_height))
        elif self.right() > screen_width:
            wrappedCoords.append((self.c[0] - screen_width, self.c[1]))
            if self.bottom() < 0:
                wrappedCoords.append((self.c[0] - screen_width, self.c[1] + screen_height))
            elif self.top() > screen_height:
                wrappedCoords.append((self.c[0] - screen_width, self.c[1] - screen_height))
        if self.bottom() < 0:
            wrappedCoords.append((self.c[0], self.c[1] + screen_height))
        elif self.top() > screen_height:
            wrappedCoords.append((self.c[0], self.c[1] - screen_height))
        return wrappedCoords
