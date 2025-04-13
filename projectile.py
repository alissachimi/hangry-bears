import pygame

class Projectile:
    def __init__(self, x, y, direction, image_path, damage, speed=6):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image_path = image_path
        # scale down projectile, but keep same aspect ratio
        desired_height = 15
        original_width = self.image.get_width()
        original_height = self.image.get_height()
        aspect_ratio = original_width / original_height
        new_width = int(desired_height * aspect_ratio)
        self.image = pygame.transform.scale(self.image, (new_width, desired_height))

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed if direction == "right" else -speed
        self.damage = damage
        self.direction = direction

    def update(self):
        self.rect.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def collides_with(self, target_rect):
        return self.rect.colliderect(target_rect)

    def off_screen(self, width):
        return self.rect.right < 0 or self.rect.left > width

    @staticmethod
    def create_projectile_from_data(data):
        return Projectile(
            x=data["x"],
            y=data["y"],
            direction=data["direction"],
            image_path=data["image_path"],
            damage=data["damage"],
            speed=data["speed"]
        )

    def serialize(self):
        return {
            "x": self.rect.centerx,
            "y": self.rect.centery,
            "direction": self.direction,
            "speed": self.speed,
            "damage": self.damage,
            "image_path": self.image_path  # you'll need to save this
        }
