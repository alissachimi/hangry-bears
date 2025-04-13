import pygame

class CherryProjectile:
    def __init__(self, x, y):
        self.image = pygame.image.load("imgs/powerups/cherry-ammo.png").convert_alpha()

        # scale down projectile, but keep same aspect ratio
        desired_height = 50
        original_width = self.image.get_width()
        original_height = self.image.get_height()
        aspect_ratio = original_width / original_height
        new_width = int(desired_height * aspect_ratio)
        self.image = pygame.transform.scale(self.image, (new_width, desired_height))

        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.blink_count = 0
        self.max_blinks = 5
        self.visible = True
        self.exploded = False

    def update(self):
        self.timer += 1
        if self.timer % 20 == 0:  # blink every 10 ticks
            self.visible = not self.visible
            self.blink_count += 1

        if self.blink_count >= self.max_blinks:
            self.explode()

    def draw(self, surface):
        if self.visible and not self.exploded:
            surface.blit(self.image, self.rect.topleft)

    def explode(self):
        self.exploded = True
        # Optional: play sound, particle effect, damage nearby players, etc.
