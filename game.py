import pygame
import sys
import time
from player import Player, WIDTH, HEIGHT, GROUND_Y, load_frames
from powerup import Powerup

# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangry Bears")

clock = pygame.time.Clock()
start_time = time.time()

# Font for clock
font = pygame.font.SysFont("Arial", 28)

# Load playing stage
stage = pygame.image.load("imgs/stages/wide-stage.png").convert()
desired_height = GROUND_Y  # So it fits exactly up to the ground

# Scale image
background_img = pygame.transform.scale(stage, (WIDTH, desired_height))
offset = 160  # adjust as needed

# Load conveyor belt and set up scroll
conveyor_belt = pygame.image.load("imgs/stages/conveyor-belt.png").convert_alpha()
belt_y_axis = GROUND_Y - conveyor_belt.get_height() + offset # position above ground
tile_width = conveyor_belt.get_width()
tile_height = conveyor_belt.get_height()
conveyor_belt = pygame.transform.scale(conveyor_belt, (tile_width, tile_height))
scroll_x = 0


# Load profile pictures
profile1 = pygame.image.load("imgs/bread_bear_profile.png").convert_alpha()
profile2 = pygame.image.load("imgs/donut_bear_profile.png").convert_alpha()
profile_size = (80, 80)
profile1 = pygame.transform.scale(profile1, profile_size)
profile2 = pygame.transform.scale(profile2, profile_size)

bread_frames = load_frames("imgs/spritesheets/bread_bear_spritesheet.png")
donut_frames = load_frames("imgs/spritesheets/donut_bear_spritesheet.png")
hangry_bread_frames = load_frames("imgs/spritesheets/angry_bread_bear_spritesheet.png")
hangry_donut_frames = load_frames("imgs/spritesheets/angry_donut_bear_spritesheet.png")

# Create players
player1 = Player(200, GROUND_Y, bread_frames, hangry_bread_frames, "imgs/healthbar/bread.png", "bread", "right")
player2 = Player(500, GROUND_Y, donut_frames, hangry_donut_frames, "imgs/healthbar/donut.png", "donut", "left", weapon="gun", projectile_image="imgs\sprinkle_ammo.png")
# List of powerups
powerups = [Powerup(300, GROUND_Y, "cherry"), Powerup(600, GROUND_Y, "blueberry")]

# Game loop
while True:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player1.attack()
            if event.key == pygame.K_f:
                player2.attack()

    player1.update(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_r, player2)
    player2.update(keys, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_f, player1)
    player1.check_attack_collision(player2)
    player2.check_attack_collision(player1)

    player1.update_mode()
    player2.update_mode()

    # THIS IS THE GROUND.  RENDER OUT EVERYTHING ELSE ON TOP OF THIS!!!
    # set background color
    screen.fill((240, 240, 240))
    # screen.fill((255,237,204))

    # Calculate Y position so the bottom of the stage is displayed above the ground
    stage_y_axis = GROUND_Y - stage.get_height() + offset
    screen.blit(stage, (0, stage_y_axis))

    # Move the conveyor left (-=) or right (+=)
    scroll_x += 1  # adjust speed here

    # Wrap around so it scrolls infinitely (scroll left is -conveyor_belt and <=, scroll right is positive and >=)
    if scroll_x >= conveyor_belt.get_width():
        scroll_x = 0

    # Draw two copies to make the scroll seamless
    screen.blit(conveyor_belt, (scroll_x, belt_y_axis))
    # + for left, - for right
    screen.blit(conveyor_belt, (scroll_x - conveyor_belt.get_width(), belt_y_axis))


        # --- In your main loop ---
    for powerup in list(powerups):  # Iterate over a copy of the list
        powerup.check_collision(player1)
        powerup.check_collision(player2)
        powerup.draw(screen)
        if powerup.collected:
            powerups.remove(powerup) # Remove the collected powerup

    # Draw players
    player1.draw(screen)
    player2.draw(screen)

    # Health bars & profiles
    screen.blit(profile1, (20, HEIGHT - 80))
    screen.blit(profile2, (WIDTH - 80, HEIGHT - 80))
    player1.draw_health(screen, 90, HEIGHT - 60)
    player2.draw_health(screen, WIDTH - 290, HEIGHT - 60)
    player1.draw_powerup_timer(screen, 90, HEIGHT - 90)
    player2.draw_powerup_timer(screen, WIDTH - 290, HEIGHT - 90)

    # Game clock
    elapsed_seconds = int(time.time() - start_time)
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    clock_text = font.render(f"{minutes:02}:{seconds:02}", True, (0, 0, 0))
    clock_rect = clock_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    screen.blit(clock_text, clock_rect)

    pygame.display.flip()