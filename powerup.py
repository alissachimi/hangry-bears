import pygame  # type: ignore

class Powerup:
    scroll_speed = 1  # Class-level scroll speed (can be set externally)
    image_cache = {}  # Cache to prevent reloading images multiple times
    valid_types = {"cherry", "blueberry", "pretzel"}  # Extend this as needed

    def __init__(self, x, y, type):
        if type not in Powerup.valid_types:
            raise ValueError(f"Invalid powerup type: {type}")

        self.x = x
        self.y = y
        self.type = type
        self.collected = False
        self.flash_duration = 15  # Frames the player flashes after collecting

        # Load and cache image
        if type not in Powerup.image_cache:
            raw_image = pygame.image.load(f"imgs/powerups/{type}.png").convert_alpha()
            desired_height = 30
            aspect_ratio = raw_image.get_width() / raw_image.get_height()
            new_width = int(desired_height * aspect_ratio)
            scaled_image = pygame.transform.scale(raw_image, (new_width, desired_height))
            Powerup.image_cache[type] = scaled_image

        self.image = Powerup.image_cache[type]
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        if not self.collected:
            surface.blit(self.image, (self.x, self.y))

    def check_collision(self, player):
        if not self.collected and self.rect.colliderect(player.get_hitbox()):
            self.collected = True

            if self.type in {"blueberry", "cherry"}:
                player.pickup_powerup(self.type)
            else:
                player.pickup_obj(self.type)

            player.flash_timer = self.flash_duration
            player.flash_mode = "rainbow"

    def update(self):
        self.x += Powerup.scroll_speed
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
        try:
            powerup = Powerup(data["x"], data["y"], data["type"])
            powerup.collected = data.get("collected", False)
            return powerup
        except Exception as e:
            print("Failed to deserialize powerup:", e)
            return None

    def update_from_data(self, data):
        self.x = data.get("x", self.x)
        self.y = data.get("y", self.y)
        self.rect.topleft = (self.x, self.y)
        self.collected = data.get("collected", self.collected)