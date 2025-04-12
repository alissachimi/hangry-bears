import pygame
import sys

# Initialize Pygame
pygame.init()

WIDTH, HEIGHT = 800, 600


# Set up the display (width, height)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangry Bears")


############################################# BEGIN PLAYER MOVING LOGIC ##############################################
clock = pygame.time.Clock()

# Load spritesheet
spritesheet = pygame.image.load("imgs/bread_bear_spritesheet.png").convert_alpha()
FRAME_WIDTH = spritesheet.get_width() // 10
FRAME_HEIGHT = spritesheet.get_height()

# Extract individual frames
frames = []
# Set desired size
DESIRED_WIDTH = FRAME_WIDTH*.2
DESIRED_HEIGHT = FRAME_HEIGHT*.2

# In your frame extraction section:
for i in range(10):
    frame = spritesheet.subsurface(pygame.Rect(i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT))
    frame = pygame.transform.smoothscale(frame, (DESIRED_WIDTH, DESIRED_HEIGHT))
    frames.append(frame)

# Player class
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.vel = 3
        self.direction = "right"
        self.frame_index = 0
        self.image = frames[8]  # Stand right
        self.tick = 0
        self.state = "idle"
        self.attack_timer = 0

        # Animation frame maps
        self.stand_frames = {"left": 3, "right": 8}
        self.walk_frames = {"left": [2, 3, 4], "right": [7, 8, 9]}
        self.attack_frames = {"left": [1, 0, 1, 0], "right": [6, 5, 6, 5]}

    def update(self, keys):
        self.tick += 1

        if self.state == "attacking":
            if self.attack_timer < len(self.attack_frames[self.direction]) * 5:
                idx = self.attack_timer // 5
                self.image = frames[self.attack_frames[self.direction][idx]]
                self.attack_timer += 1
            else:
                self.state = "idle"
                self.attack_timer = 0
                self.image = frames[self.stand_frames[self.direction]]
            return

        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.vel
            self.direction = "left"
            self.state = "walking"
        elif keys[pygame.K_RIGHT]:
            dx = self.vel
            self.direction = "right"
            self.state = "walking"
        else:
            self.state = "idle"

        self.x += dx

        if self.state == "walking":
            frame_list = self.walk_frames[self.direction]
            frame = frame_list[(self.tick // 10) % len(frame_list)]
            self.image = frames[frame]
        elif self.state == "idle":
            self.image = frames[self.stand_frames[self.direction]]

    def attack(self):
        if self.state != "attacking":
            self.state = "attacking"
            self.attack_timer = 0

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


############################################# END PLAYER MOVING LOGIC ##############################################

player = Player()

# Main loop
while True:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player.attack()

    player.update(keys)

    screen.fill((240, 240, 240))
    player.draw(screen)
    pygame.display.flip()