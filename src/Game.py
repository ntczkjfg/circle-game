import sys
import pygame
import numpy as np
from Common_Variables import *
from Entity import Entity
from Player import Player

class Game():
    def __init__(self
                 , gamemode = 0
                 , powerups = powerups
                 , wrapping = False
                 , entitiesCollide = True
                 , powerupsCollide = False
                 , maxPowerups = 5
                 , timeLimit = None
                 , lifeCount = 3
                 , initialState = [[0, 1]]):
        self.gamemode = gamemode
        self.powerups = powerups
        self.wrapping = wrapping
        self.entitiesCollide = entitiesCollide
        self.powerupsCollide = self.entitiesCollide and powerupsCollide
        self.maxPowerups = maxPowerups
        self.timeLimit = timeLimit
        
        self.player = Player(lifeCount = lifeCount, parent = self)
        self.score = 0

        self.entities = []
        for entityType in initialState:
            for i in range(entityType[1]):
                self.entities.append(Entity(player = self.player, parent = self, typ = entityType[0]))
        
        self.paused = False
        self.pausedTicks = 0
        self.pauseStartTime = 0
        
        self.food = 0
        self.powerupCount = 0
        self.colliders = [self.player]
        for entity in self.entities:
            if self.entitiesCollide and (self.powerupsCollide or not entity.isPowerup()):
                self.colliders.append(entity)
            if entity.type == 0:
                self.food += 1
            if entity.type in powerups:
                self.powerupCount += 1
                
        self.clock = pygame.time.Clock()
        self.startTime = pygame.time.get_ticks()

    def drawScreen(self):
        # Paused
        if self.paused:
            # Don't clear game display, write "Paused" over screen
            font = pygame.font.Font(None, 150)
            text = font.render("Paused", True, WHITE)
            screen.blit(text, ((screen_width - text.get_width()) / 2
                               , (screen_height - text.get_height()) / 2))
            pygame.display.update()
            self.clock.tick(60)
            return
        
        # Clear everything, redraw
        screen.fill((200, 150, 150))
        for entity in self.entities + [self.player]: entity.draw()
        
        # Life counter
        font = pygame.font.Font(None, 30)
        text = font.render("Lives: " + str(self.player.lifeCount), True, WHITE)
        screen.blit(text, (10, 10))
        
        # Timer
        if self.timeLimit:
            timer = round(self.timeLimit - (pygame.time.get_ticks() - self.startTime - self.pausedTicks) / 1000)
        else:
            timer = round((pygame.time.get_ticks() - self.startTime - self.pausedTicks) / 1000)
        text = font.render("Time: " + str(timer), True, WHITE)
        screen.blit(text, (screen_width - text.get_width() - 10, 10))
        
        # Draw all of the above
        pygame.display.update()
        
        # 60 fps
        self.clock.tick(60)

    def gameOver(self):
        # Endless mode - continues until lives are gone
        # Game ends when player runs out of lives
        if self.gamemode == 0:
            if self.player.lifeCount <= 0:
                return True
            return False
        # Collect all the yellows
        # Game ends when player runs out of lives (loss) or all yellows are eaten (win)
        if self.gamemode == 1:
            if self.food == 0 or self.player.lifeCount <= 0:
                return True
            return False
        # Countdown timer to get all yellows
        # Game ends when player runs out of lives or the timer expires (loss) or all yellows are eaten (win)
        if self.gamemode == 2:
            if self.food == 0 or self.player.lifeCount <= 0 or self.timeLimit <= (pygame.time.get_ticks() - self.startTime - self.pausedTicks) / 1000:
                return True
            return False
        # Countdown timer, pure survival
        # Game ends when player  runs out of lives (loss) or timer runs out (win)
        if self.gamemode == 3:
            if self.player.lifeCount <= 0 or self.timeLimit <= (pygame.time.get_ticks() - self.startTime - self.pausedTicks) / 1000:
                return True
            return False

    def removeEntity(self, entity):
        if entity in self.entities:
            if entity.type == 0:
                self.food -= 1
            elif entity.isPowerup():
                self.powerupCount -= 1
            if entity in self.colliders:
                self.colliders.remove(entity)
            self.entities.remove(entity)

    def spawnFood(self):
        attempts = 0
        while True:
            if attempts > 10:
                return
            attempts += 1
            newEntity = Entity(player = self.player, parent = self)
            if self.player.powerup(14):
                newEntity.r *= 2
            # Don't let it spawn inside of the player or another entity
            try_again = False
            for entity in self.colliders:
                if newEntity.collides(entity):
                    try_again = True
                    break
            if try_again: continue
            break
        self.entities.append(newEntity)
        if self.entitiesCollide:
            self.colliders.append(newEntity)
        self.food += 1

    def spawnPowerup(self, fromPowerup = False):
        powerup = rng.choice(self.powerups)
        # Means this powerup was spawned by powerup #20, so don't spawn powerup #20 again
        while fromPowerup and powerup == 20:
            powerup = rng.choice(self.powerups)
        despawn = 60*(10 + rng.integers(11))
        attempts = 0
        while True:
            if attempts > 10:
                return
            attempts += 1
            newEntity = Entity(r = 15, speed = 0, typ = powerup, despawnTimer = despawn, player = self.player, parent = self)
            # Don't let it spawn inside of the player or another entity
            try_again = False
            for entity in self.colliders:
                if newEntity.collides(entity):
                    try_again = True
                    break
            if try_again: continue
            break
        self.entities.append(newEntity)
        if self.powerupsCollide:
            self.colliders.append(newEntity)
        self.powerupCount += 1

    def start(self):
        # Main loop
        while True:
            # Check if food needs to be spawned
            if self.food <= 0: self.spawnFood()
            # Handle events
            for event in pygame.event.get():
                # Clicked the X
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # Paused
                    if event.key == pygame.K_SPACE:
                        if self.paused:
                            self.paused = False
                            self.pausedTicks += pygame.time.get_ticks() - self.pauseStartTime
                        else:
                            self.paused = True
                            self.pauseStartTime = pygame.time.get_ticks()
                    # Pressed q
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    # Pressed e (Toggles edge wrapping)
                    if event.key == pygame.K_e:
                        self.wrapping = not self.wrapping
            # Handle being paused
            if self.paused:
                self.drawScreen()
                continue
            # Remove from powerup timers
            self.player.decrementPowerups()
            # Handle player movement
            keys = pygame.key.get_pressed()
            for key in self.player.dirMap:
                if keys[key]:
                    self.player.turn(key)
            self.player.move()
            # Handle entities
            for entity in self.entities:
                if entity.despawnTimer:
                    entity.despawnTimer -= 1
                    if entity.despawnTimer == 0:
                        self.removeEntity(entity)
                        continue
                if entity.bombTimer:
                    entity.bombTimer -= 1
                    if entity.bombTimer == 0:
                        if entity.type == 19:
                            entity.type = 3
                            entity.r = 100
                            entity.bombTimer = 20
                            entity.speed = 0
                            if entity not in self.colliders:
                                self.colliders.append(entity)
                        else:
                            self.removeEntity(entity)
                            continue
                # entity is blue, remove from blueTimer and transmute if necessary
                elif entity.type == 1:
                    entity.blueTimer -= 1
                    if entity.blueTimer <= 0:
                        entity.type = 2
                # Check if the player moved into entity
                if entity.collides(self.player):
                    self.player.collide(entity)
                    if entity.isPowerup() and entity.type != 19: # 19 = bomb
                        # If this is true then self.player.collide will have removed this entity
                        continue
                    else:
                        entity.bounce(self.player)
                        while entity.collides(self.player) and entity.speed != 0: entity.move()
                if entity.type == 3: # Bomb explosion
                    for collider in self.entities:
                        if entity.collides(collider):
                            self.removeEntity(collider)
                    continue
                # Move entities
                if entity.speed == 0: continue
                entity.turn(self.player, self)
                colliders = self.colliders
                if not self.powerupsCollide and entity.isPowerup():
                    colliders = [self.player]
                entity.move(colliders)
            # Spawn powerups
            if rng.random() < 0.002 and self.powerupCount < self.maxPowerups:
                self.spawnPowerup()
            # Check for game over
            if self.gameOver():
                # Draw final frame
                self.drawScreen()
                font = pygame.font.Font(None, 50)
                timer = round(pygame.time.get_ticks() / 1000)
                text = font.render("Game over!  Your score: " + str(self.score), True, WHITE)
                screen.blit(text
                                 , ((screen_width - text.get_width()) / 2
                                    , (screen_height - text.get_height()) / 2))
                pygame.display.update()
                pygame.time.delay(3000)
                break
            self.drawScreen()
