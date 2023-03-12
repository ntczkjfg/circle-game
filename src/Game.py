import sys
import pygame
import numpy as np
from Common_Variables import *
from Entity import Entity
from Player import Player

class Game():
    def __init__(self, screen):
        self.player = Player(self)
        self.entities = [Entity(player = self.player, parent = self)]
        self.entities.append(Entity(player = self.player, parent = self, typ = 19, speed = 0))
        self.paused = False
        self.pausedTicks = 0
        self.pauseStartTime = 0
        self.food = 0
        for entity in self.entities:
            if entity.type == 0:
                self.food += 1
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.score = 0
        self.startTime = pygame.time.get_ticks()
        self.phantomEntities = []
        self.wrapping = False
        self.entitiesCollide = True
        self.powerupsCollide = True

    def spawnFood(self):
        while True:
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
        self.screen.fill(BLACK)
        self.food = 0
        for entity in self.entities + [self.player]:
            # entity is player, remove from powerup timers
            if entity.type == -1: # Player
                entity.decrementPowerups()
            elif entity.type == 0: # Food
                self.food += 1
            # entity is blue, remove from blue timer and transmute if necessary
            elif entity.type == 1:
                entity.timer -= 1
                if entity.timer <= 0:
                    entity.type = 2
            elif entity.type == 20:
                entity.bombTimer -= 1
                if entity.bombTimer == 0:
                    entity.r = 100
                elif entity.bombTimer < -20:
                    self.entities.remove(entity)
            entity.draw()
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
            # Handle player movement
            keys = pygame.key.get_pressed()
            for key in self.player.dirMap:
                if keys[key]:
                    self.player.turn(key)
            self.player.move()
            # Handle entities
            for entity in self.entities:
                # Check if the player moved into entity
                if entity.collides(self.player):
                    self.player.collide(entity)
                    if entity.isPowerup() and entity.type != 20:
                        self.entities.remove(entity)
                    else:
                        entity.bounce(self.player)
                        while entity.collides(self.player) and entity.speed != 0: entity.move()
                # Move entities
                if entity.speed == 0:
                    continue
                entity.turn(self.player, self)
                colliders = [self.player]
                if self.entitiesCollide:
                    if self.powerupsCollide:
                        colliders += self.entities
                    else:
                        if not entity.isPowerup():
                            for collider in self.entities:
                                if collider.type in [0, 1, 2, 20]:
                                    colliders.append(collider)
                entity.move(colliders)

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
