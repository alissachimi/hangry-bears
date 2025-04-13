import pygame #type: ignore

class Platform:
    def __init__(self, x, y, image_path, width, move_range=100, speed=2):
        original_image = pygame.image.load(image_path).convert_alpha()
        aspect_ratio = original_image.get_width() / original_image.get_height()
        height = int(width / aspect_ratio)

        self.image = pygame.transform.scale(original_image, (width, height))
        self.image_path = image_path
        self.rect = self.image.get_rect(topleft=(x, y))

        self.start_x = x
        self.move_range = move_range
        self.speed = speed
        self.direction = 1  # 1 = right, -1 = left

    def update(self):
        self.rect.x += self.speed * self.direction

        if abs(self.rect.x - self.start_x) >= self.move_range:
            self.direction *= -1

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def check_collision(self, player):
        player_rect = pygame.Rect(player.x, player.y, player.image.get_width(), player.image.get_height())

        if player.y_vel >= 0 and player_rect.colliderect(self.rect):
            if player_rect.bottom - self.rect.top < 15:
                player.y = self.rect.top - player.image.get_height()
                player.y_vel = 0
                player.on_ground = True
    
    def serialize(self):
        return {
            "x": self.rect.x,
            "y": self.rect.y,
            "start_x": self.start_x,
            "move_range": self.move_range,
            "speed": self.speed,
            "direction": self.direction,
            "image_path": self.image_path,
            "width": self.rect.width
        }

    @staticmethod
    def deserialize(data):
        platform = Platform(
            x=data["start_x"],
            y=data["y"],
            image_path=data["image_path"],
            width=data["width"],
            move_range=data["move_range"],
            speed=data["speed"]
        )
        platform.rect.x = data["x"]
        platform.rect.y = data["y"]
        platform.direction = data["direction"]
        return platform

