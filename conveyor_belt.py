class ConveyorObject:
    def __init__(self, image, y, speed, start_x=None, image_path=None):
        self.image = image
        self.image_path = image_path
        self.x = start_x if start_x is not None else -image.get_width()
        self.y = y
        self.speed = speed

    def update(self):
        self.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def is_off_screen(self, screen_width):
        return self.x > screen_width or self.x < -self.image.get_width()
    
    def serialize(self):
        return {
            "x": self.x,
            "y": self.y,
            "speed": self.speed,
            "class": self.__class__.__name__,
            "image_path": self.image_path
        }

    @staticmethod
    def deserialize(data, loaded_images):
        image = loaded_images[data["image_path"]]
        if data["class"] == "PowerUp":
            obj = PowerUp(image=image, start_x=data["x"])
        else:
            obj = ConveyorObject(image=image, y=data["y"], speed=data["speed"], start_x=data["x"])

        obj.x = data["x"]
        obj.y = data["y"]
        obj.speed = data["speed"]
        return obj