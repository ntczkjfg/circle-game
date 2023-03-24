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
                 , blueTimer = None
                 , bombTimer = None
                 , despawnTimer = None
                 , player = None
                 , parent = None):
        self.game = parent
        self.player = player
        # Timers for controlling temporary states
        self.blueTimer = blueTimer
        self.bombTimer = bombTimer
        self.despawnTimer = despawnTimer
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
        # 3 = bomb explosion, damages player and kills other entities
        # 10 = powerup, allows killing reds
        # 11 = powerup, immune to damage
        # 12 = powerup, forcefield
        # 13 = powerup, circles slow down for 8 seconds
        # 14 = powerup, yellow circles double diameter
        # 15 = powerup, spawn extra yellow circle
        # 16 = powerup, gain an extra life
        # 17 = powerup, all red circles turn blue for 5 seconds
        # 18 = powerup, you strongly repel close red circles for 5 seconds
        # 19 = bomb
        # 20 = powerup, spawns 2 more powerups
        self.type = 0 if typ == None else typ
    
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
        if entity == self: return False
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
        elif self.type == 3: # Bomb explosion
            if self.bombTimer >= 10:
                return RED
            return (200, 200, 0)
        elif self.type == -2: # Debug
            return PURPLE
        elif self.type in [10, 11, 12, 13, 14, 15, 16, 17, 18]: # Powerup, lets you kill reds
            return images[str(self.type)]
        elif self.type == 19: # Powerup, bomb
            if self.bombTimer == None:
                return images["19_1"]
            if self.bombTimer > 60:
                if self.bombTimer % 30 < 15:
                    return images["19_2"]
                return images["19_3"]
            if self.bombTimer % 20 < 10:
                return images["19_2"]
            return images["19_3"]
        elif self.type == 20: # Temporary, haven't made graphic yet
            return (128, 128, 128)

    # Draws the entity on screen
    def draw(self):
        for coord in self.wrappedCoords():
            if self.type in [-2, -1, 0, 1, 2, 3, 20]:
                pygame.draw.circle(screen
                                   , self.color()
                                   , [coord[0], screen_height - coord[1]]
                                   , self.r)
            else:
                screen.blit(self.color(), (coord[0] - self.r, screen_height - (coord[1] + self.r)))

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
            if self.left() < 0: self.c[0] = self.r
            if self.right() > screen_width: self.c[0] = screen_width - self.r
            if self.bottom() < 0: self.c[1] = self.r
            if self.top() > screen_height: self.c[1] = screen_height - self.r
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
        newEntity = Entity(c = newCoords, r = self.r, speed = self.speed, direction = self.dir, typ = self.type, blueTimer = self.blueTimer, parent = self.game)
        for collider in colliders:
            # Don't collide with self
            if collider == self: continue
            # Check if we're already in collision
            if self.collides(collider):
                self.bounce(collider)
                collider.bounce(self)
                # Move the other object if possible
                if collider.speed > 0:
                    while self.collides(collider): collider.move()
                # Otherwise move self
                else:
                    while self.collides(collider): self.move()
            # Check if we're about to be in collision
            if newEntity.collides(collider):
                # Colliding with a player?  
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
