import pygame # type: ignore


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
        self.max_blinks = 10
        self.visible = True
        self.damage_radius = 300  # affects players within 20 pixels
        self.explosion_radius = 300  # for visuals
        self.damage = 20

        # for explosion annimation
        self.exploded = False
        self.explosion_frame = 0
        self.explosion_max_frames = 5
        self.explosion_frame_duration = 5  # ticks per frame
        self.explosion_tick = 0
        self.show_explosion = False

        # Load explosion sprite frames
        self.explosion_frames = self.load_explosion_frames("imgs/spritesheets/explosion_spritesheet.png", 5)
        self.explosion_rect = None

    def update(self, players=None):
        if not self.exploded:
            self.timer += 1
            if self.timer % 20 == 0:
                self.visible = not self.visible
                self.blink_count += 1
            if self.blink_count >= self.max_blinks:
                self.explode(players)
        else:
            if self.show_explosion:
                self.explosion_tick += 1
                if self.explosion_tick >= self.explosion_frame_duration:
                    self.explosion_tick = 0
                    self.explosion_frame += 1
                    if self.explosion_frame >= self.explosion_max_frames:
                        self.show_explosion = False  # animation done

            
    def explode(self, players=None):
        self.exploded = True
        self.visible = False
        self.show_explosion = True
        self.explosion_tick = 0
        self.explosion_frame = 0
        self.explosion_rect = self.explosion_frames[0].get_rect(center=self.rect.center)
        print(players)
        if players:
            for player in players:
                dist = pygame.math.Vector2(player.x, player.y).distance_to(self.rect.center)
                if dist <= self.damage_radius:
                    player.take_damage(20)

    def draw(self, surface):
        if self.visible and not self.exploded:
            print("Drawing cherry bomb at", self.rect.topleft)
            surface.blit(self.image, self.rect.topleft)
        elif self.show_explosion and self.explosion_frame < 5:
            print("Drawing explosion frame", self.explosion_frame)
            surface.blit(self.explosion_frames[self.explosion_frame], self.explosion_rect.topleft)

    
    def load_explosion_frames(self, spritesheet_path, frame_count):
        spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        frame_w = spritesheet.get_width() // frame_count
        frame_h = spritesheet.get_height()
        desired_w = self.explosion_radius
        desired_h = self.explosion_radius
        return [
            pygame.transform.smoothscale(
                spritesheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
                (desired_w, desired_h)
            )
            for i in range(frame_count)
        ]

    def should_remove(self):
        return self.exploded and not self.show_explosion

    def serialize(self):
        return {
            "type": "cherry",
            "x": self.rect.centerx,
            "y": self.rect.centery,
            "timer": self.timer,
            "blink_count": self.blink_count,
            "visible": self.visible,
            "exploded": self.exploded,
            "explosion_frame": self.explosion_frame,
            "explosion_tick": self.explosion_tick,
            "show_explosion": self.show_explosion,
        }

        
    @staticmethod
    def deserialize(data):
        obj = CherryProjectile(data["x"], data["y"])
        obj.timer = data["timer"]
        obj.blink_count = data["blink_count"]
        obj.visible = data["visible"]
        obj.exploded = data["exploded"]
        obj.explosion_frame = data["explosion_frame"]
        obj.explosion_tick = data["explosion_tick"]
        obj.show_explosion = data["show_explosion"]

        return obj
