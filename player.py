import pygame
from projectile import Projectile
from cherry_bomb import CherryProjectile

WIDTH, HEIGHT = 800, 600
GROUND_Y = HEIGHT - 250

# Load and process spritesheets
def load_frames(path):
    spritesheet = pygame.image.load(path).convert_alpha()
    frame_w = spritesheet.get_width() // 10
    frame_h = spritesheet.get_height()
    desired_w = int(frame_w * 0.2)
    desired_h = int(frame_h * 0.2)
    return [
        pygame.transform.smoothscale(
            spritesheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
            (desired_w, desired_h)
        )
        for i in range(10)
    ]

# Player class
class Player:
    def __init__(self, x, y, frames, hangry_frames, icon, name, direction="right", weapon=None, projectile_image="None"):
        self.x = x
        self.y = y
        self.default_frames = frames
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
        self.flash_mode = None  # can be 'rainbow' or None
        

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
        self.powerup_timer = 0
        self.powerup_duration = 300  # 5 seconds at 60 FPS

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

        if self.powerup_timer > 0:
            self.powerup_timer -= 1
        if self.powerup_timer == 0 and "blueberry" in self.projectile_image:
            self.revert_powerup()

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if hasattr(projectile, 'collides_with'):
                if projectile.collides_with(opponent.get_hitbox()):
                    opponent.take_damage(projectile.damage)
                    self.projectiles.remove(projectile)
            else:
                if projectile.exploded:
                    self.projectiles.remove(projectile)


        self.projectiles = [p for p in self.projectiles if ((hasattr(p, 'collides_with') and not p.off_screen(WIDTH)) or not p.exploded)]

        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        if self.flash_timer > 0:
            self.flash_timer -= 1

        if self.state == "attacking":
            if self.weapon=="gun" and "blueberry" not in self.projectile_image:
                frame_duration = 15
            else:
                frame_duration = 5
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
        if self.weapon == "gun" and "cherry" in self.projectile_image:
            # Drop cherry ammo on ground
            dropped_projectile = CherryProjectile(self.x, self.y)
            self.projectiles.append(dropped_projectile)

            # Revert player state
            self.revert_powerup()
                
        if self.state != "attacking":
            self.state = "attacking"
            self.attack_timer = 0

    def revert_powerup(self):
        self.frames = self.default_frames

        if self.is_hangry:
            self.frames = self.hangry_frames
            self.attack_frames = {"left": [1, 0], "right": [6, 5]}
            if self.name == "bread":
                self.projectile_image = "imgs\\bagette.png"
                self.weapon = "gun"
            elif self.name == "donut":
                self.projectile_image = "imgs\\healthbar\\donut.png"
        else:
            self.attack_frames = {"left": [1, 0, 1, 0], "right": [6, 5, 6, 5]}
            if self.name == "bread":
                self.weapon = None
            else:
                self.projectile_image = "imgs\\sprinkle_ammo.png"


    def draw(self, surface):
        # will flash rainbow if get a powerup
        if self.flash_timer > 0 and self.flash_mode == "rainbow":
            flash_image = self.image.copy()

            width, height = flash_image.get_size()
            # Define a list of rainbow colors (you can expand this)
            rainbow_colors = [
                (255, 0, 0),     # Red
                (255, 127, 0),   # Orange
                (255, 255, 0),   # Yellow
                (0, 255, 0),     # Green
                (0, 0, 255),     # Blue
                (75, 0, 130),    # Indigo
                (148, 0, 211)    # Violet
            ]

            band_width = width // len(rainbow_colors)

            for i, color in enumerate(rainbow_colors):
                band_rect = pygame.Rect(i * band_width, 0, band_width, height)
                flash_image.fill(color + (80,), band_rect, special_flags=pygame.BLEND_RGBA_MULT)

            surface.blit(flash_image, (self.x, self.y))
        elif self.flash_timer > 0:
            flash_image = self.image.copy()
            flash_image.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(flash_image, (self.x, self.y))
        else:
            self.flash_mode = None
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

    def draw_powerup_timer(self, surface, x, y):
        if self.powerup_timer > 0:
            bar_width = 60
            bar_height = 6
            fill_width = int(bar_width * (self.powerup_timer / self.powerup_duration))
            border_rect = pygame.Rect(x, y, bar_width, bar_height)
            fill_rect = pygame.Rect(x, y, fill_width, bar_height)
            pygame.draw.rect(surface, (0, 0, 255), fill_rect)       # blue fill
            pygame.draw.rect(surface, (255, 255, 255), border_rect, 1)  # white border


    def update_mode(self):
        if self.health < 25 and not self.is_hangry:
            self.enter_hangry_mode()
        elif self.health >= 25 and self.is_hangry:
            self.exit_hangry_mode()

    def enter_hangry_mode(self):
        self.is_hangry = True
        self.frames = self.hangry_frames
        self.attack_frames = {"left": [1, 0], "right": [6, 5]}
        self.vel = 4  # maybe make him faster?

        # give bread bear new projectile
        if self.name=="bread":
            self.projectile_image="imgs\\bagette.png"
            self.weapon="gun"
        # give donut bear new projectile
        if self.name=="donut":
            self.projectile_image="imgs\healthbar\donut.png"
    
    def exit_hangry_mode(self):
        self.is_hangry = False
        self.frames = self.normal_frames
        self.attack_frames = {"left": [1, 0, 1, 0], "right": [6, 5, 6, 5]}
        self.stand_frames = {"left": 3, "right": 8}
        self.walk_frames = {"left": [2, 3, 4], "right": [7, 8, 9]}
        self.vel = 3  # back to normal speed
    
    # powerup should be cherry or blueberry
    def pickup_powerup(self, powerup):
        if self.is_hangry:
            spritesheet_url=f"imgs/spritesheets/{str(powerup).upper()}_angry_{self.name}_bear_spritesheet.png"
        else:
            spritesheet_url=f"imgs/spritesheets/{str(powerup).upper()}_{self.name}_bear_spritesheet.png"
        powerup_frames = load_frames(spritesheet_url)

        self.frames = powerup_frames
        self.projectile_image=f"imgs\powerups\{powerup}-ammo.png"
        self.weapon="gun"
        self.attack_frames = {"left": [1, 0], "right": [6, 5]}

        if powerup == "blueberry":
            self.powerup_timer = self.powerup_duration

