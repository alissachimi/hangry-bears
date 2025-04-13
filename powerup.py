import pygame # type: ignore
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
    
    def update(self):
        scroll_speed = 1
        self.x += scroll_speed
        self.rect.x = self.x

    def serialize(self):
        return {
            "x": self.x,
            "y": self.y,
            "type": self.type,
            "collected": self.collected
        }
    
    @staticmethod
    def deserialize(data):
        powerup = Powerup(data["x"], data["y"], data["type"])
        powerup.collected = data["collected"]
        return powerup

    def update_from_data(self, data):
        self.x = data["x"]
        self.y = data["y"]
        self.collected = data["collected"]