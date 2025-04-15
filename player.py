import pygame # type: ignore
from projectile import Projectile
from cherry_bomb import CherryProjectile

WIDTH, HEIGHT = 1000, 600
GROUND_Y = HEIGHT - 250
sprite_cache = {}

# Load and process spritesheets
def load_frames(path):
    if path in sprite_cache:
        return sprite_cache[path]
    
    spritesheet = pygame.image.load(path).convert_alpha()
    frame_w = spritesheet.get_width() // 10
    frame_h = spritesheet.get_height()
    desired_w = int(frame_w * 0.2)
    desired_h = int(frame_h * 0.2)

    frames = [
        pygame.transform.smoothscale(
            spritesheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
            (desired_w, desired_h)
        )
        for i in range(10)
    ]
    sprite_cache[path] = frames
    return frames


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
        self.opponents = None
        self.powerup=None
        self.last_powerup = None  # for optimizing sprite updates
        
        self.initial_weapon = weapon
        self.initial_projectile_image = projectile_image

        self.y_vel = 0
        self.gravity = 0.5
        self.jump_strength = -15
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

    def set_opponents(self, opponents):
        self.opponents = opponents

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
    
    def inc_health(self, amount):
        # check for full health
        if self.health < 100:
            self.health += amount

    def update(self, keys, key_left, key_right, key_jump, key_attack, opponent):
        self.tick += 1

        if self.powerup_timer > 0:
            self.powerup_timer -= 1
        if self.powerup_timer == 0 and "blueberry" in self.projectile_image:
            self.revert_powerup()

        # Update projectiles
        for projectile in self.projectiles[:]:
            if hasattr(projectile, 'collides_with'):

                projectile.update()

                if projectile.collides_with(opponent.get_hitbox()):
                    opponent.take_damage(projectile.damage)
                    self.projectiles.remove(projectile)
            else:
                possible_targets = list(self.opponents)
                possible_targets.append(self) 
                projectile.update(possible_targets)
                if projectile.exploded and not projectile.show_explosion:
                    self.projectiles.remove(projectile)


        self.projectiles = [p for p in self.projectiles if not p.should_remove()]

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
            if self.direction=="left":
                dropped_projectile = CherryProjectile(self.x -70, self.y +100)
            else:
                dropped_projectile = CherryProjectile(self.x +150, self.y +100)
            self.projectiles.append(dropped_projectile)

            # Revert player state
            self.revert_powerup()
                
        if self.state != "attacking":
            self.state = "attacking"
            self.attack_timer = 0

    def revert_powerup(self):
        self.frames = self.default_frames
        self.powerup=None

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
    
    def draw_powerup(self, surface, x, y, is_player1=True):
            if self.powerup == "cherry":
                cherry_img = pygame.image.load("imgs/powerups/cherry-ammo.png").convert_alpha()
                desired_height = 20
                original_width = cherry_img.get_width()
                original_height = cherry_img.get_height()
                aspect_ratio = original_width / original_height
                new_width = int(desired_height * aspect_ratio)
                resized_cherry_img = pygame.transform.scale(cherry_img, (new_width, desired_height))
                surface.blit(resized_cherry_img, (x, y))
            elif self.powerup == "blueberry":
                blueberry_img = pygame.image.load("imgs/powerups/blueberry.png").convert_alpha()
                desired_height = 20
                original_width = blueberry_img.get_width()
                original_height = blueberry_img.get_height()
                aspect_ratio = original_width / original_height
                new_width = int(desired_height * aspect_ratio)
                resized_blueberry_img = pygame.transform.scale(blueberry_img, (new_width, desired_height))
                if is_player1:
                    surface.blit(resized_blueberry_img, (x, y))
                    # Draw the timer bar to the right of the blueberry image for player 1
                    bar_x = x + resized_blueberry_img.get_width() + 5
                    self.draw_powerup_timer(surface, bar_x, y + (resized_blueberry_img.get_height() // 2) - 3)
                else:  # For player 2, draw bar then icon
                    bar_width = 60
                    bar_height = 6
                    bar_y = y + (resized_blueberry_img.get_height() // 2) - 3
                    bar_x = x - bar_width - 25  # Position bar to the left
                    self.draw_powerup_timer(surface, bar_x, bar_y)
                    icon_x = x - resized_blueberry_img.get_width() + 10 # Position icon to the left of the bar
                    surface.blit(resized_blueberry_img, (icon_x, y))


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
        self.powerup=powerup
        if self.is_hangry:
            spritesheet_url=f"imgs/spritesheets/{str(powerup).upper()}_angry_{self.name}_bear_spritesheet.png"
        else:
            spritesheet_url=f"imgs/spritesheets/{str(powerup).upper()}_{self.name}_bear_spritesheet.png"
        self.frames = sprite_cache.get(spritesheet_url)
        if not self.frames:
            print(f"[WARN] Sprite not preloaded: {spritesheet_url}")
            self.frames = load_frames(spritesheet_url)

        self.projectile_image=f"imgs\powerups\{powerup}-ammo.png"
        self.weapon="gun"
        self.attack_frames = {"left": [1, 0], "right": [6, 5]}

        if powerup == "blueberry":
            self.powerup_timer = self.powerup_duration

    # for pretzels and other game objects
    def pickup_obj(self, powerup):
        self.powerup=powerup
        
        if (powerup == "pretzel"):
            # increment health by 1/2 icon
            self.inc_health(10)

            # health bar updates in game loop

            
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
            "flash_mode": self.flash_mode,
            "damage_cooldown": self.damage_cooldown,
            "is_hangry": self.is_hangry,
            "weapon": self.weapon,
            "projectile_image": self.projectile_image,
            "powerup": self.powerup,
            "powerup_timer": self.powerup_timer
        }

    def deserialize(self, data):
        self.x = data["x"]
        self.y = data["y"]
        self.vel = data["vel"]
        self.state = data["state"]
        self.direction = data["direction"]
        self.health = data["health"]
        self.flash_timer = data.get("flash_timer", 0)
        self.flash_mode = data.get("flash_mode", None)
        self.damage_cooldown = data.get("damage_cooldown", 0)
        self.is_hangry = data.get("is_hangry", False)
        self.weapon = data.get("weapon", None)
        self.projectile_image = data.get("projectile_image", None)
        self.powerup_timer = data.get("powerup_timer", 0)

        # Detect powerup change and update only if necessary
        # Always set powerup
        self.powerup = data.get("powerup", None)

        # Always re-apply correct sprite if powerup or hangry status changed
        if self.powerup in ("cherry", "blueberry"):
            self.apply_powerup_sprite(self.powerup)
        elif self.is_hangry:
            self.enter_hangry_mode()
        else:
            self.exit_hangry_mode()

        self.tick += 1
        self.refresh_sprite()

    def apply_powerup_sprite(self, powerup):
        if self.is_hangry:
            spritesheet_url = f"imgs/spritesheets/{powerup.upper()}_angry_{self.name}_bear_spritesheet.png"
        else:
            spritesheet_url = f"imgs/spritesheets/{powerup.upper()}_{self.name}_bear_spritesheet.png"
        self.frames = sprite_cache.get(spritesheet_url)
        if not self.frames:
            print(f"[WARN] Sprite not preloaded: {spritesheet_url}")
            self.frames = load_frames(spritesheet_url)

        self.projectile_image = f"imgs/powerups/{powerup}-ammo.png"
        self.weapon = "gun"
        self.attack_frames = {"left": [1, 0], "right": [6, 5]}



