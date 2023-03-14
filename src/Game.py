import sys
import pygame
import numpy as np
from Common_Variables import *
from Entity import Entity
from Player import Player

class Game():
    def __init__(self, screen):
        self.player = Player(lifeCount = 3, parent = self)
        self.entities = [Entity(player = self.player, parent = self)]
        self.paused = False
        self.pausedTicks = 0
        self.pauseStartTime = 0
        self.food = 0
        self.powerupCount = 0
        for entity in self.entities:
            if entity.type == 0:
                self.food += 1
            if entity.type in powerups:
                self.powerupCount += 1
        self.maxPowerups = 5
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.score = 0
        self.startTime = pygame.time.get_ticks()
        self.phantomEntities = []
        self.wrapping = False
        self.entitiesCollide = True
        self.powerupsCollide = False

    def drawScreen(self):
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
        self.screen.fill((200, 150, 150))
        for entity in self.entities + [self.player]: entity.draw()
        
        # Life counter
        font = pygame.font.Font(None, 30)
        text = font.render("Lives: " + str(self.player.lifeCount), True, WHITE)
        screen.blit(text, (10, 10))
        
        # Timer
        timer = round((pygame.time.get_ticks() - self.startTime - self.pausedTicks) / 1000)
        text = font.render("Time: " + str(timer), True, WHITE)
        screen.blit(text, (screen_width - text.get_width() - 10, 10))
        
        # Draw all of the above
        pygame.display.update()
        
        # 60 fps
        self.clock.tick(60)

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
            for entity in [self.player] + self.entities:
                if newEntity.collides(entity):
                    try_again = True
                    break
            if try_again: continue
            break
        self.entities.append(newEntity)
        self.food += 1

    def spawnPowerup(self):
        powerup = rng.choice(powerups)
        colliders = [self.player]
        if self.powerupsCollide:
            colliders += self.entities
        despawn = 10 + rng.integers(11)
        attempts = 0
        while True:
            if attempts > 10:
                return
            attempts += 1
            newEntity = Entity(r = 15, speed = 0, typ = powerup, despawnTimer = despawn*60, player = self.player, parent = self)
            # Don't let it spawn inside of the player or another entity
            try_again = False
            for entity in colliders:
                if newEntity.collides(entity):
                    try_again = True
                    break
            if try_again: continue
            break
        self.entities.append(newEntity)

    def startGame(self):
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
            self.food = 0
            self.powerupCount = 0
            for entity in self.entities:
                if entity.despawnTimer:
                    entity.despawnTimer -= 1
                    if entity.despawnTimer == 0:
                        self.entities.remove(entity)
                        continue
                if entity.bombTimer:
                    entity.bombTimer -= 1
                    if entity.bombTimer == 0:
                        if entity.type == 19:
                            entity.type = 3
                            entity.r = 100
                            entity.bombTimer = 20
                            entity.speed = 0
                        else:
                            self.entities.remove(entity)
                            continue
                if entity.type == 0: # Food
                    self.food += 1
                # entity is blue, remove from blueTimer and transmute if necessary
                elif entity.type == 1:
                    entity.blueTimer -= 1
                    if entity.blueTimer <= 0:
                        entity.type = 2
                elif entity.type in powerups:
                    self.powerupCount += 1
                # Check if the player moved into entity
                if entity.collides(self.player):
                    self.player.collide(entity)
                    if entity.isPowerup() and entity.type != 19:
                        self.entities.remove(entity)
                    else:
                        entity.bounce(self.player)
                        while entity.collides(self.player) and entity.speed != 0: entity.move()
                if entity.type == 3:
                    for collider in self.entities:
                        if entity.collides(collider):
                            self.entities.remove(collider)
                    continue
                # Move entities
                if entity.speed == 0: continue
                entity.turn(self.player, self)
                colliders = [self.player]
                if self.entitiesCollide:
                    if self.powerupsCollide:
                        colliders += self.entities
                    else:
                        if not entity.isPowerup():
                            for collider in self.entities:
                                if collider.type in [0, 1, 2, 3]:
                                    colliders.append(collider)
                entity.move(colliders)
            if rng.random() < 0.001 and self.powerupCount < self.maxPowerups:
                self.spawnPowerup()
            # Check for game over
            if self.player.lifeCount <= 0:
                self.drawScreen()
                font = pygame.font.Font(None, 50)
                timer = round(pygame.time.get_ticks() / 1000)
                text = font.render("Game over!  Your score: " + str(self.score), True, WHITE)
                self.screen.blit(text
                                 , ((screen_width - text.get_width()) / 2
                                    , (screen_height - text.get_height()) / 2))
                pygame.display.update()
                pygame.time.delay(3000)
                break
            self.drawScreen()
