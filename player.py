import pygame
from projectile import Projectile

WIDTH, HEIGHT = 1000, 600
GROUND_Y = HEIGHT - 250

# Player class
class Player:
    def __init__(self, x, y, frames, hangry_frames, icon, name, direction="right", weapon=None, projectile_image=None):
        self.x = x
        self.y = y
        self.frames = frames
        self.hangry_frames = hangry_frames
        self.vel = 3
        self.direction = direction
        self.frame_index = 0
        self.image = frames[8]
        self.tick = 0
        self.state = "idle"
        self.attack_timer = 0
        self.name=name
        self.damage_cooldown = 0
        self.is_hangry = False  
        self.normal_frames = frames
        self.flash_timer = 0 
        self.initial_weapon = weapon
        self.initial_projectile_image = projectile_image

        self.y_vel = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.on_ground = True

        self.health = 100

        self.stand_frames = {"left": 3, "right": 8}
        self.walk_frames = {"left": [2, 3, 4], "right": [7, 8, 9]}
        self.attack_frames = {"left": [1, 0, 1, 0], "right": [6, 5, 6, 5]}

        self.full_icon_img = pygame.image.load(icon).convert_alpha()
        self.full_icon_img = pygame.transform.scale(self.full_icon_img, (32, 32))

        half_icon_path = icon.replace(".png", "-half.png")  # naming like "bread.png" -> "bread-half.png"
        self.half_icon_img = pygame.image.load(half_icon_path).convert_alpha()
        self.half_icon_img = pygame.transform.scale(self.half_icon_img, (16, 32))

        self.projectiles = []
        self.weapon = weapon
        self.projectile_image = projectile_image  # Change to your projectile image path

    def get_hitbox(self):
        width = self.image.get_width()
        height = self.image.get_height()

        hitbox_width = int(width * 0.6)
        hitbox_height = height

        offset_x = (width - hitbox_width) // 2
        offset_y = (height - hitbox_height) // 2

        return pygame.Rect(self.x + offset_x, self.y + offset_y, hitbox_width, hitbox_height)
    
    def check_attack_collision(self, opponent):
        if opponent.state == "attacking" and self.get_hitbox().colliderect(opponent.get_hitbox()):
            if self.damage_cooldown == 0:
                self.take_damage(10)

    def take_damage(self, amount):
        self.health -= amount
        self.flash_timer = 10
        self.damage_cooldown = 30 

    def update(self, keys, key_left, key_right, key_jump, key_attack, opponent):
        self.tick += 1

        # Update projectiles
        for projectile in self.projectiles:
            projectile.update()
            if projectile.collides_with(opponent.get_hitbox()):
                opponent.take_damage(projectile.damage)
                self.projectiles.remove(projectile)

        self.projectiles = [p for p in self.projectiles if not p.off_screen(WIDTH)]

        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        if self.flash_timer > 0:
            self.flash_timer -= 1

        if self.state == "attacking":
            frame_duration = 10 if self.is_hangry else 3
            attack_frames = self.attack_frames[self.direction]
            
            if self.attack_timer < len(attack_frames) * frame_duration:
                idx = self.attack_timer // frame_duration
                self.image = self.frames[attack_frames[idx]]
                self.attack_timer += 1
            else:
                if self.weapon == "gun":
                    center_y = self.y + self.image.get_height() // 2
                    if self.direction == "right":
                        proj_x = self.x + self.image.get_width()
                    else:
                        proj_x = self.x
                    bullet = Projectile(proj_x, center_y, self.direction, self.projectile_image, 5)
                    self.projectiles.append(bullet)
                self.state = "idle"
                self.attack_timer = 0
                self.image = self.frames[self.stand_frames[self.direction]]
            return

        dx = 0
        if keys[key_left]:
            dx = -self.vel
            self.direction = "left"
            self.state = "walking"
        elif keys[key_right]:
            dx = self.vel
            self.direction = "right"
            self.state = "walking"
        else:
            self.state = "idle"

        if keys[key_jump] and self.on_ground:
            self.y_vel = self.jump_strength

        self.x += dx
        self.y_vel += self.gravity
        self.y += self.y_vel

        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.y_vel = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.state == "walking":
            frame_list = self.walk_frames[self.direction]
            frame = frame_list[(self.tick // 10) % len(frame_list)]
            self.image = self.frames[frame]
        elif self.state == "idle":
            self.image = self.frames[self.stand_frames[self.direction]]


    def attack(self):
        if self.state != "attacking":
            self.state = "attacking"
            self.attack_timer = 0


    def draw(self, surface):
        if self.flash_timer > 0:
            flash_image = self.image.copy()
            flash_image.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(flash_image, (self.x, self.y))
        else:
            surface.blit(self.image, (self.x, self.y))
        
        for projectile in self.projectiles:
            projectile.draw(surface)

    def draw_health(self, surface, x, y):
        hearts = 5
        health_per_heart = 100 / hearts
        current = int(self.health / health_per_heart)
        remainder = self.health % health_per_heart

        for i in range(hearts):
            pos = (x + i * 35, y)
            if i < current:
                surface.blit(self.full_icon_img, pos)
            elif i == current and remainder > 0:
                surface.blit(self.half_icon_img, pos)
    
    def update_mode(self):
        if self.health < 25 and not self.is_hangry:
            self.enter_hangry_mode()
        elif self.health >= 25 and self.is_hangry:
            self.exit_hangry_mode()

    def enter_hangry_mode(self):
        self.is_hangry = True
        self.frames = self.hangry_frames
        self.attack_frames = {"left": [1, 0], "right": [6, 5]}
        self.stand_frames = {"left": 3, "right": 8}  # if different, change accordingly
        self.walk_frames = {"left": [2, 3, 4], "right": [7, 8, 9]}  # or hangry versions
        self.vel = 4  # maybe make him faster?

        # give bread bear new projectile
        if self.name=="bread":
            self.projectile_image="imgs\\bagette.png"
            self.weapon="gun"
        if self.name=="donut":
            self.projectile_image="imgs\healthbar\donut.png"
    
    def exit_hangry_mode(self):
        self.is_hangry = False
        self.frames = self.normal_frames
        self.attack_frames = {"left": [1, 0, 1, 0], "right": [6, 5, 6, 5]}
        self.stand_frames = {"left": 3, "right": 8}
        self.walk_frames = {"left": [2, 3, 4], "right": [7, 8, 9]}
        self.vel = 3  # back to normal speed

    def refresh_sprite(self):
        if self.state == "walking":
            frame_list = self.walk_frames[self.direction]
            frame = frame_list[(self.tick // 10) % len(frame_list)]
            self.image = self.frames[frame]
        elif self.state == "idle":
            self.image = self.frames[self.stand_frames[self.direction]]
        elif self.state == "attacking":
            attack_frames = self.attack_frames[self.direction]
            if self.attack_timer < len(attack_frames):
                frame = attack_frames[self.attack_timer % len(attack_frames)]
                self.image = self.frames[frame]
        self.update_mode()
    
    def reset_state(self):
        self.health = 100
        self.projectiles.clear()

        # Position
        if self.name == "bread":
            self.x = 200
        elif self.name == "donut":
            self.x = 500
        self.y = GROUND_Y

        self.y_vel = 0
        self.on_ground = True

        # States
        self.state = "idle"
        self.tick = 0
        self.attack_timer = 0
        self.flash_timer = 0
        self.damage_cooldown = 0

        # Hangry mode reset — force properly
        self.is_hangry = False
        self.exit_hangry_mode()  # <- good
        self.weapon = self.initial_weapon
        self.projectile_image = self.initial_projectile_image

        # Refresh sprite
        self.refresh_sprite()

    def serialize(self):
        return {
                "x": self.x,
                "y": self.y,
                "vel": self.vel,
                "state": self.state,
                "direction": self.direction,
                "health": self.health,
                "flash_timer": self.flash_timer,
                "damage_cooldown": self.damage_cooldown
        }

    def deserialize(self, data):
        self.x = data["x"]
        self.y = data["y"]
        self.vel = data["vel"]
        self.state = data["state"]
        self.direction = data["direction"]
        self.health = data["health"]
        self.flash_timer = data.get("flash_timer", 0)
        self.damage_cooldown = data.get("damage_cooldown", 0)
        self.tick += 1


