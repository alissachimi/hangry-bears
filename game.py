import pygame
import sys
import time
from player import Player, WIDTH, HEIGHT, GROUND_Y
from button import Button

# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangry Bears")

clock = pygame.time.Clock()
start_time = time.time()

font = pygame.font.SysFont("Arial", 28)
button_font = pygame.font.Font("fonts/silkscreen.ttf", 32)

button_width = 250
button_height = 60

arrow_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
hand_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)

def title_screen():
    title_bg = pygame.image.load("imgs/title-screen.png").convert()
    title_bg = pygame.transform.scale(title_bg, (WIDTH, HEIGHT))
    start_button_x = (WIDTH - button_width) // 2
    start_button_y = HEIGHT - 340

    start_button = Button("Start Game", start_button_x, start_button_y, button_width, button_height, button_font)
    
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        screen.blit(title_bg, (0, 0))
        
        # Centralized cursor update:
        mouse_pos = pygame.mouse.get_pos()
        if start_button.rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(hand_cursor)
        else:
            pygame.mouse.set_cursor(arrow_cursor)
        
        # Draw the button.
        start_button.draw(screen)
        
        # Check if the button was clicked.
        if start_button.is_clicked(events):
            return  # Exit title screen on button click.
        
        pygame.display.update()
        clock.tick(60)


def multiplayer_options_screen():
    bg = pygame.image.load("imgs/multiplayer-options-screen.png").convert()

    host_game_button_x = join_game_button_x = (WIDTH - button_width) // 2
    host_game_button_y = HEIGHT - 300
    join_game_button_y = HEIGHT - 230
    host_game_button = Button("Host a Game", host_game_button_x, host_game_button_y, button_width, button_height, button_font)
    join_game_button = Button("Join a Game", join_game_button_x, join_game_button_y, button_width, button_height, button_font)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(bg, (0, 0))
        
        # Centralized cursor update for multiple buttons:
        mouse_pos = pygame.mouse.get_pos()
        if host_game_button.rect.collidepoint(mouse_pos) or join_game_button.rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(hand_cursor)
        else:
            pygame.mouse.set_cursor(arrow_cursor)
        
        # Draw both buttons.
        host_game_button.draw(screen)
        join_game_button.draw(screen)
        
        # Check for button clicks.
        if host_game_button.is_clicked(events):
            return  # Or handle hosting a game.
        if join_game_button.is_clicked(events):
            return  # Or handle joining a game.
        
        pygame.display.update()
        clock.tick(60)

title_screen()
multiplayer_options_screen()
pygame.mouse.set_cursor(arrow_cursor)

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

bread_frames = load_frames("imgs/spritesheets/bread_bear_spritesheet.png")
donut_frames = load_frames("imgs/spritesheets/donut_bear_spritesheet.png")
hangry_bread_frames = load_frames("imgs/spritesheets/angry_bread_bear_spritesheet.png")
hangry_donut_frames = load_frames("imgs/spritesheets/angry_donut_bear_spritesheet.png")

# Create players
player1 = Player(200, GROUND_Y, bread_frames, hangry_bread_frames, "imgs/healthbar/bread.png", "bread", "right")
player2 = Player(500, GROUND_Y, donut_frames, hangry_donut_frames, "imgs/healthbar/donut.png", "donut", "left", weapon="gun", projectile_image="imgs\sprinkle_ammo.png")

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

    # Update players
    player1.update(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_r, player2)
    player2.update(keys, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_f, player1)
    player1.check_attack_collision(player2)
    player2.check_attack_collision(player1)

    player1.update_mode()
    player2.update_mode()

    screen.fill((240, 240, 240))
    pygame.draw.rect(screen, (180, 180, 180), (0, GROUND_Y + 40, WIDTH, HEIGHT - GROUND_Y))

    # Draw players
    player1.draw(screen)
    player2.draw(screen)

    # Health bars & profiles
    screen.blit(profile1, (20, HEIGHT - 80))
    screen.blit(profile2, (WIDTH - 80, HEIGHT - 80))
    player1.draw_health(screen, 90, HEIGHT - 60)
    player2.draw_health(screen, WIDTH - 290, HEIGHT - 60)

    # Game clock
    elapsed_seconds = int(time.time() - start_time)
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    clock_text = font.render(f"{minutes:02}:{seconds:02}", True, (0, 0, 0))
    clock_rect = clock_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    screen.blit(clock_text, clock_rect)

    pygame.display.flip()