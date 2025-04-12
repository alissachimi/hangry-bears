import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display (width, height)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Hangry Bears")

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a color (e.g., black)
    screen.fill((0, 0, 0))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
