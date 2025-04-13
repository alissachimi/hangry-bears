class ConveyorObject:
    def __init__(self, image, y, speed, start_x=None):
        self.image = image
        self.x = start_x if start_x is not None else -image.get_width()
        self.y = y
        self.speed = speed

    def update(self):
        self.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def is_off_screen(self, screen_width):
        return self.x > screen_width or self.x < -self.image.get_width()

class PowerUp(ConveyorObject):
    def __init__(self, image, start_x=None):
        power_up_y = 435  #  consistent y-position
        super().__init__(image, power_up_y, speed=PowerUp.scroll_speed, start_x=start_x)

    # Shared settings
    scroll_speed = 0  # Set before instantiating in game.py