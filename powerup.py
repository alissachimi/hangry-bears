import pygame
import random

class Powerup:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type  # "cherry" or "blueberry"
        self.image = pygame.image.load(f"imgs\powerups\{type}.png").convert_alpha()
        
        # scale down projectile, but keep same aspect ratio
        desired_height = 30
        original_width = self.image.get_width()
        original_height = self.image.get_height()
        aspect_ratio = original_width / original_height
        new_width = int(desired_height * aspect_ratio)
        self.image = pygame.transform.scale(self.image, (new_width, desired_height))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.collected = False
        self.flash_duration = 15  # How long the player flashes rainbow

    def draw(self, surface):
        if not self.collected:
            surface.blit(self.image, (self.x, self.y))

    def check_collision(self, player):
        if not self.collected and self.rect.colliderect(player.get_hitbox()):
            self.collected = True
            player.pickup_powerup(self.type)
            player.flash_timer = self.flash_duration
            player.flash_mode = "rainbow"
