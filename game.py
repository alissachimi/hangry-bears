import pygame # type: ignore
import sys
import time
from conveyor_belt import PowerUp, ConveyorObject
from player import Player, WIDTH, HEIGHT, GROUND_Y, load_frames
from powerup import Powerup
import random

# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangry Bears")

clock = pygame.time.Clock()
start_time = time.time()

# Font for clock
font = pygame.font.SysFont("Arial", 28)

# Load playing stage
stage = pygame.image.load("imgs/stages/stage.png").convert()
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

# Setup for power up scroll on conveyor belt
ConveyorObject.ground_y = GROUND_Y - stage.get_height() + offset
ConveyorObject.conveyor_height = conveyor_belt.get_height()
ConveyorObject.scroll_speed = 1
PowerUp.scroll_speed = 1  # Try + or - depending on scroll direction

# Create list of power ups
power_up_list = []

# Load in power up images
blueberry_img = pygame.image.load("imgs/powerups/blueberry.png").convert_alpha()
cherry_img = pygame.image.load("imgs/powerups/cherry.png").convert_alpha()

# Scale images
power_up_size = (40, 40)
blueberry_img = pygame.transform.scale(blueberry_img, power_up_size)
cherry_img = pygame.transform.scale(cherry_img, power_up_size)

# Create power up objects
blueberry = PowerUp(image=blueberry_img, start_x=-100)
cherry = PowerUp(image=cherry_img, start_x=200)

# Add objects to power up list at start
# power_up_list.append(blueberry)
# power_up_list.append(cherry)

# Spawn timing config for power ups
SPAWN_POWERUP_INTERVAL = 7000  # milliseconds (every 7 seconds)
last_spawn_time = pygame.time.get_ticks()
# print("initial last_spawn_time: ", last_spawn_time)

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

player1.set_opponents([player2])
player2.set_opponents([player1])

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
    # screen.fill((240, 240, 240))
    screen.fill((180, 180, 180))
    # screen.fill((255,237,204))
    # screen.fill((204, 226, 255))

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

    # Generate power ups on a timer
    current_time = pygame.time.get_ticks()

    if current_time - last_spawn_time > SPAWN_POWERUP_INTERVAL:
        last_spawn_time = current_time
        # print("in game loop, updated last_spawn_time: ", last_spawn_time)

        # Randomly spawn new power-up (0=blueberry, 1=cherry)
        rand = random.randint(0, 1)
        if (rand == 0):
            # generate blueberry
            new_powerup = PowerUp(image=blueberry_img, start_x=-50)
        if (rand == 1):
            # generate cherry
            new_powerup = PowerUp(image=cherry_img, start_x=-50)

        power_up_list.append(new_powerup)
        # print(power_up_list)
        # print(f"New power up position: ({new_powerup.x}, {new_powerup.y})")

    # Display power ups on conveyor belt
    for obj in power_up_list:
        obj.update()
        obj.draw(screen)
        # print(f"Blueberry position: ({blueberry.x}, {blueberry.y})")

    # Remove off-screen objects
    power_ups = [p for p in power_up_list if not p.is_off_screen(WIDTH)]


    # Draw players
    player1.draw(screen)
    player2.draw(screen)

    # ensures they are drawn on top of players
    for projectile in player1.projectiles:
        projectile.draw(screen)
    for projectile in player2.projectiles:
        projectile.draw(screen)

    for powerup in list(powerups):  # Iterate over a copy of the list
        powerup.check_collision(player1)
        powerup.check_collision(player2)
        powerup.draw(screen)
        if powerup.collected:
            powerups.remove(powerup) # Remove the collected powerup

    # Health bars & profiles
    screen.blit(profile1, (20, HEIGHT - 80))
    screen.blit(profile2, (WIDTH - 80, HEIGHT - 80))
    player1.draw_health(screen, 90, HEIGHT - 60)
    player2.draw_health(screen, WIDTH - 290, HEIGHT - 60)

    # Draw power-ups under the health bars, specifying the player
    player1.draw_powerup(screen, 90, HEIGHT - 30, is_player1=True)
    player2.draw_powerup(screen, WIDTH - 90, HEIGHT - 30, is_player1=False)


    # Game clock
    elapsed_seconds = int(time.time() - start_time)
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    clock_text = font.render(f"{minutes:02}:{seconds:02}", True, (0, 0, 0))
    clock_rect = clock_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    screen.blit(clock_text, clock_rect)

    pygame.display.flip()