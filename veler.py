import pygame
from random import random, randint
from math import sin, cos, atan
from sys import exit as sysexit

DegToRad = 2*3.14159 / 360

pygame.init()

# Set up the screen
screen_width = 504
screen_height = 896
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Veler")

# Define some colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)

# Set up the player and circles
invincibilityTicks = 1000
player_size = 20
player_x = screen_width / 2 - player_size / 2
player_y = screen_height / 2 + player_size / 2
min_circle_radius = 4
max_circle_radius = 8
circles = []
redcircles = 0
for i in range(20):
    circle_x = randint(0, screen_width)
    circle_y = randint(0, screen_height)
    circle_color = yellow
    circle_speed = 1 + 2*random()
    circle_direction = randint(0, 359)
    circle_radius = randint(min_circle_radius, max_circle_radius)
    circles.append((circle_x, circle_y, circle_color, circle_speed, circle_direction, circle_radius, 0))
lives = 3

# Set up the clock
clock = pygame.time.Clock()

# Set up the timer
time_elapsed = 0
font = pygame.font.Font(None, 30)

# Helper function for updating circle position
def update_circle_position(circle_x, circle_y, circle_speed, circle_direction):
    # Convert the direction to radians
    direction_radians = circle_direction * DegToRad
    # Calculate the new position
    new_x = circle_x + circle_speed * cos(direction_radians)
    new_y = circle_y + circle_speed * sin(direction_radians)
    return new_x, new_y

# Helper function for updating circle direction
def update_circle_direction(circle_x, circle_y, circle_color, circle_direction):
    xDiff, yDiff = player_x + player_size/2 - circle_x, player_y - player_size/2 - circle_y
    dist = (xDiff**2 + yDiff**2)**0.5
    if xDiff == 0: xDiff = 0.01 # Don't divide by 0
    
    angleDiff = atan(yDiff / xDiff) / DegToRad
    if xDiff < 0: angleDiff += 180 # In quadrant 2 or 3
    angleDiff %= 360
    
    if circle_color == red: # Move toward the player
        angleDiff -= circle_direction
    elif circle_color == yellow: # Move away from the player - to the angle 180° away
        angleDiff = ((angleDiff - 180) % 360) - circle_direction
    else: # Blue circles are linear
        return circle_direction
    if angleDiff > 180: angleDiff = angleDiff - 360 # So it can bend clockwise if it's more efficient
    circle_direction = (circle_direction + angleDiff/dist) % 360 # Divide by dist so closer points bend more, gives a gravitational effect
    return circle_direction

# Draw the player and circles
def drawScreen():
    screen.fill(black)
    if pygame.time.get_ticks() < invincibilityTicks: # Invincibility is active
        pygame.draw.rect(screen, green, [player_x, screen_height - player_y, player_size, player_size])
    else:
        pygame.draw.rect(screen, white, [player_x, screen_height - player_y, player_size, player_size])
    for circle in circles:
        circle_x, circle_y, circle_color, circle_speed, circle_direction, circle_radius, blueTimer = circle
        pygame.draw.circle(screen
                           , circle_color
                           , [circle_x, screen_height - circle_y]
                           , circle_radius)

    # Draw the lives counter
    font = pygame.font.Font(None, 30)
    text = font.render("Lives: " + str(lives), True, white)
    screen.blit(text, (10, 10))

    # Draw the timer
    timer = round(pygame.time.get_ticks() / 1000)
    text = font.render("Time: " + str(timer), True, white)
    screen.blit(text, (screen_width - text.get_width() - 10, 10))

    # Update the screen
    pygame.display.update()
    clock.tick(60)

# Main game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sysexit()

    # Handle player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_y += 5
    if keys[pygame.K_s]:
        player_y -= 5
    if keys[pygame.K_a]:
        player_x -= 5
    if keys[pygame.K_d]:
        player_x += 5

    # Wrap player around the edges
    if player_x < -player_size:
        player_x = screen_width - player_size
    elif player_x > screen_width:
        player_x = 0
    if player_y < 0:
        player_y = screen_height
    elif player_y > screen_height + player_size:
        player_y = player_size

    # Move the circles
    for i, circle in enumerate(circles):
        circle_x, circle_y, circle_color, circle_speed, circle_direction, circle_radius, blueTimer = circle
        
        circle_direction = update_circle_direction(circle_x, circle_y, circle_color, circle_direction)
        circle_x, circle_y = update_circle_position(circle_x, circle_y, circle_speed, circle_direction)
        # Wrap circles around the edges
        if blueTimer > 0:
            blueTimer -= 1
            if blueTimer == 0:
                circle_color = red
                redcircles += 1
        if circle_x < -circle_radius:
            circle_x = screen_width - circle_radius
        elif circle_x > screen_width:
            circle_x = 0
        if circle_y < 0:
            circle_y = screen_height
        elif circle_y > screen_height + circle_radius:
            circle_y = circle_radius
        circles[i] = (circle_x, circle_y, circle_color, circle_speed, circle_direction, circle_radius, blueTimer)
        circle = circles[i]

        # Check for collisions with player
        if (pygame.time.get_ticks() >= invincibilityTicks
            and player_x + player_size >= circle_x - circle_radius
            and player_x <= circle_x + circle_radius
            and player_y >= circle_y - circle_radius
            and player_y - player_size <= circle_y + circle_radius):
            if circle_color == yellow:
                circle = (circle_x, circle_y, blue, 1 + 2*random(), randint(0, 359), circle_radius, 60)
                circles[i] = circle
            elif circle_color == red:
                lives -= 1
                circles.remove(circle)
                redcircles -= 1
                if lives <= 0:
                    drawScreen()
                    font = pygame.font.Font(None, 50)
                    text = font.render("Game over!", True, white)
                    screen.blit(text, (screen_width/2 - text.get_width()/2, screen_height/2 - text.get_height()/2))
                    pygame.display.update()
                    pygame.time.delay(3000)
                    pygame.quit()
                    sysexit()
        
        # Check for game over
        if len(circles) == redcircles:
            drawScreen()
            font = pygame.font.Font(None, 50)
            timer = round(pygame.time.get_ticks() / 1000)
            text = font.render("You win! Time taken: " + str(timer) + " seconds", True, white)
            screen.blit(text, (screen_width/2 - text.get_width()/2, screen_height/2 - text.get_height()/2))
            pygame.display.update()
            pygame.time.delay(3000)
            pygame.quit()
            sysexit()
    drawScreen()
