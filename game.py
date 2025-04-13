import pygame
import sys
import time

# Initialize Pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
GROUND_Y = HEIGHT - 250

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangry Bears")

clock = pygame.time.Clock()
start_time = time.time()

# Font for clock
font = pygame.font.SysFont("Arial", 28)

# Load profile pictures
profile1 = pygame.image.load("imgs/bread_bear_profile.png").convert_alpha()
profile2 = pygame.image.load("imgs/donut_bear_profile.png").convert_alpha()
profile_size = (80, 80)
profile1 = pygame.transform.scale(profile1, profile_size)
profile2 = pygame.transform.scale(profile2, profile_size)

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

bread_frames = load_frames("imgs/bread_bear_spritesheet.png")
donut_frames = load_frames("imgs/donut_bear_spritesheet.png")
hangry_bread_frames = load_frames("imgs/angry_bear_spritesheet.png")

# Player class
class Player:
    def __init__(self, x, y, frames, hangry_frames, direction="right"):
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
        self.damage_cooldown = 0

        self.y_vel = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.on_ground = True

        self.health = 100

        self.stand_frames = {"left": 3, "right": 8}
        self.walk_frames = {"left": [2, 3, 4], "right": [7, 8, 9]}
        self.attack_frames = {"left": [1, 0, 1, 0], "right": [6, 5, 6, 5]}

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
                self.health -= 10
                print(self.health)
                self.damage_cooldown = 30

    def update(self, keys, key_left, key_right, key_jump, key_attack, opponent):
        self.tick += 1

        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

        if self.state == "attacking":
            frame_duration = 10 if self.is_hangry else 3
            if self.attack_timer < len(self.attack_frames[self.direction]) * frame_duration:
                idx = self.attack_timer // frame_duration
                self.image = self.frames[self.attack_frames[self.direction][idx]]
                self.attack_timer += 1
            else:
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

        if keys[key_attack]:
            self.attack()

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
        surface.blit(self.image, (self.x, self.y))

    def draw_health(self, surface, x, y, icon):
        hearts = 5
        health_per_heart = 100 / hearts
        current = int(self.health / health_per_heart)
        icon_img = pygame.image.load(icon).convert_alpha()
        icon_img = pygame.transform.scale(icon_img, (32, 32))

        for i in range(hearts):
            if i < current:
                surface.blit(icon_img, (x + i * 35, y))
    
    def enter_hangry_mode(self):
        self.is_hangry = True
        self.frames = self.hangry_frames
        self.attack_frames = {"left": [1, 0], "right": [6, 5]}
        self.stand_frames = {"left": 3, "right": 8}  # if different, change accordingly
        self.walk_frames = {"left": [2, 3, 4], "right": [7, 8, 9]}  # or hangry versions
        self.vel = 4  # maybe make him faster?


# Create players
player1 = Player(200, GROUND_Y, bread_frames, hangry_bread_frames, "right")
player2 = Player(500, GROUND_Y, donut_frames, hangry_bread_frames, "left")

# Game loop
while True:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update players
    player1.update(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_r, player2)
    player2.update(keys, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_f, player1)
    player1.check_attack_collision(player2)
    player2.check_attack_collision(player1)



    screen.fill((240, 240, 240))
    pygame.draw.rect(screen, (180, 180, 180), (0, GROUND_Y + 40, WIDTH, HEIGHT - GROUND_Y))

    # Draw players
    player1.draw(screen)
    player2.draw(screen)

    # Health bars & profiles
    screen.blit(profile1, (20, HEIGHT - 80))
    player1.draw_health(screen, 90, HEIGHT - 60, "imgs/healthbar/bread.png")
    player1.enter_hangry_mode()


    screen.blit(profile2, (WIDTH - 80, HEIGHT - 80))
    player2.draw_health(screen, WIDTH - 290, HEIGHT - 60, "imgs/healthbar/donut.png")

    # Game clock
    elapsed_seconds = int(time.time() - start_time)
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    clock_text = font.render(f"{minutes:02}:{seconds:02}", True, (0, 0, 0))
    clock_rect = clock_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    screen.blit(clock_text, clock_rect)

    pygame.display.flip()