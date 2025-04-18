import pygame # type: ignore
import sys
from conveyor_belt import ConveyorObject
from player import Player, WIDTH, HEIGHT, GROUND_Y, load_frames
from powerup import Powerup
import random
from plat import Platform
from button import Button
from projectile import Projectile
from cherry_bomb import CherryProjectile
import socket
import threading
import pickle
import time
from moviepy.editor import VideoFileClip

# === CONFIG ===
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 10141
IP = ""
#IP = "10.7.190.196"
client_input = None
client_conn = None

client_ip_input = ""
input_active = True
thread_running = True

# === INIT ===
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangry Bears")

clock = pygame.time.Clock()
start_time = time.time()
is_host = False

font = pygame.font.SysFont("Arial", 28)
button_font = pygame.font.Font("fonts/silkscreen.ttf", 32)

button_width = 270
button_height = 60

arrow_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
hand_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)

# === GLOBALS ===
current_screen = "title"
previous_screen = None
running = True

# Title screen globals
title_bg = None
start_button = None

# Multiplayer options globals
multiplayer_bg = None
host_game_button = None
join_game_button = None

# Server lobby globals
lobby_bg = None
play_button = None

# Client input globals
enter_button = None
client_input_bg = None

# Game over screen globals
winner_bg = None
return_button = None
winner_image_path = None
winner_player_number = None

# === SETUP FUNCTIONS ===

def setup_title_screen():
    global title_bg, start_button
    title_bg = pygame.image.load("imgs/ui/title-screen.png").convert()
    start_button_x = (WIDTH - button_width) // 2
    start_button_y = HEIGHT - 340
    start_button = Button("Start Game", start_button_x, start_button_y, button_width, button_height, button_font)

def setup_multiplayer_options_screen():
    global multiplayer_bg, host_game_button, join_game_button
    multiplayer_bg = pygame.image.load("imgs/ui/multiplayer-options-screen.png").convert()

    button_x = (WIDTH - button_width) // 2
    host_game_button_y = HEIGHT - 300
    join_game_button_y = HEIGHT - 230

    host_game_button = Button("Host a Game", button_x, host_game_button_y, button_width, button_height, button_font)
    join_game_button = Button("Join a Game", button_x, join_game_button_y, button_width, button_height, button_font)

def setup_client_input_screen():
    global client_input_bg, enter_button
    client_input_bg = pygame.image.load("imgs/ui/client-input-screen.png").convert()
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT - 150
    enter_button = Button("Enter", button_x, button_y, button_width, button_height, button_font)

def setup_server_lobby_screen():
    global lobby_bg, play_button
    lobby_bg = pygame.image.load("imgs/ui/server-lobby-screen.png").convert()
    play_button_x = (WIDTH - button_width) // 2
    play_button_y = HEIGHT - 340
    play_button = Button("Play Game", play_button_x, play_button_y, button_width, button_height, button_font)

def setup_winner_screen(player_number):
    global winner_bg, return_button, winner_image_path

    if player_number == 1:
        winner_image_path = "imgs/ui/player1_winner_screen.png"
    else:
        winner_image_path = "imgs/ui/player2_winner_screen.png"

    winner_bg = pygame.image.load(winner_image_path).convert()
    return_button = Button("Play Again", WIDTH - 300, HEIGHT - 100, button_width, button_height, button_font)

# === SCREEN RUN FUNCTIONS ===

def run_title_screen(events):
    global current_screen
    screen.blit(title_bg, (0, 0))

    mouse_pos = pygame.mouse.get_pos()
    if start_button.rect.collidepoint(mouse_pos):
        pygame.mouse.set_cursor(hand_cursor)
    else:
        pygame.mouse.set_cursor(arrow_cursor)

    start_button.draw(screen)

    if start_button.is_clicked(events):
        current_screen = "multiplayer_options"

def run_multiplayer_options_screen(events):
    global is_host, current_screen
    screen.blit(multiplayer_bg, (0, 0))

    mouse_pos = pygame.mouse.get_pos()
    if host_game_button.rect.collidepoint(mouse_pos) or join_game_button.rect.collidepoint(mouse_pos):
        pygame.mouse.set_cursor(hand_cursor)
    else:
        pygame.mouse.set_cursor(arrow_cursor)

    host_game_button.draw(screen)
    join_game_button.draw(screen)

    if host_game_button.is_clicked(events):
        is_host = True
        threading.Thread(target=initialize_server, daemon=True).start()
        current_screen = "server_wait"
    elif join_game_button.is_clicked(events):
        current_screen = "client_input"

def run_client_input_screen(events):
    global current_screen, IP, client_ip_input

    screen.blit(client_input_bg, (0, 0))

    # Draw input box
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 250, 300, 50)
    pygame.draw.rect(screen, (255, 255, 255), input_box)
    pygame.draw.rect(screen, (0, 0, 0), input_box, 3)

    # Render IP text
    ip_surface = font.render(client_ip_input, True, (0, 0, 0))
    screen.blit(ip_surface, (input_box.x + 10, input_box.y + 10))

    # Draw button
    mouse_pos = pygame.mouse.get_pos()
    if enter_button.rect.collidepoint(mouse_pos):
        pygame.mouse.set_cursor(hand_cursor)
    else:
        pygame.mouse.set_cursor(arrow_cursor)

    enter_button.draw(screen)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                client_ip_input = client_ip_input[:-1]
            elif event.key == pygame.K_RETURN:
                IP = client_ip_input
                threading.Thread(target=initialize_client, daemon=True).start()
                current_screen = "client_wait"
            else:
                if len(client_ip_input) < 15 and event.unicode.isprintable():
                    client_ip_input += event.unicode
        elif enter_button.is_clicked(events):
            IP = client_ip_input
            threading.Thread(target=initialize_client, daemon=True).start()
            current_screen = "client_wait"

def run_server_lobby_screen(events):
    global current_screen, played_video
    screen.blit(lobby_bg, (0, 0))

    mouse_pos = pygame.mouse.get_pos()
    if play_button.rect.collidepoint(mouse_pos):
        pygame.mouse.set_cursor(hand_cursor)
    else:
        pygame.mouse.set_cursor(arrow_cursor)

    play_button.draw(screen)

    if play_button.is_clicked(events):
        if client_conn:
            try:
                command = b"CMD:SWITCH_TO_GAMEPLAY\n"
                length = len(command).to_bytes(4, 'big')
                client_conn.sendall(length + command)
            except:
                print("Failed to send mode switch to client.")
        if played_video == False:
            play_video("imgs/main.mp4")
            played_video = True
        current_screen = "server_gameplay"
            

def run_winner_screen(events):
    global current_screen, winner_player_number

    screen.blit(winner_bg, (0, 0))

    if is_host:
        mouse_pos = pygame.mouse.get_pos()
        if return_button.rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(hand_cursor)
        else:
            pygame.mouse.set_cursor(arrow_cursor)

        return_button.draw(screen)

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if return_button.is_clicked(events):
                current_screen = "server_lobby"
                winner_player_number = None
                reset_game()

                # Send command to client to return to client lobby
                if client_conn:
                    try:
                        command = b"CMD:RETURN_TO_LOBBY\n"
                        length = len(command).to_bytes(4, 'big')
                        client_conn.sendall(length + command)
                    except Exception as e:
                        print("Error sending return to lobby:", e)
    else:
        pygame.mouse.set_cursor(arrow_cursor)


def display_ui(screen_path):
    bg = pygame.image.load(screen_path).convert()
    screen.blit(bg, (0, 0))

# === SERVER / CLIENT ===

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "Unavailable"
    finally:
        s.close()

def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    global client_input
    try:
        while True:
            # Step 1: read length prefix
            length_data = recv_exact(conn, 4)
            if not length_data:
                print("Client disconnected")
                break

            message_length = int.from_bytes(length_data, 'big')

            # Step 2: read the actual message
            message = recv_exact(conn, message_length)
            if not message:
                print("Client disconnected during message")
                break

            # Step 3: process message
            if message.startswith(b"INPUT:"):
                try:
                    client_input = pickle.loads(message[6:])  # skip 'INPUT:'
                except Exception as e:
                    print("Failed to load client input:", e)

            else:
                print("Unknown client message:", message)

    except ConnectionResetError:
        print("Connection lost")
    finally:
        conn.close()

# Helper function to read in data
def recv_exact(sock, num_bytes):
    data = b''
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            return None
        data += packet
    return data

def initialize_server():
    global IP
    IP = get_local_ip()
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((SERVER_HOST, SERVER_PORT))
    server_sock.listen(1)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    def accept_connection():
        global current_screen, client_conn
        conn, addr = server_sock.accept()
        client_conn = conn
        print("Client connected!")
        current_screen = "server_lobby"
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    threading.Thread(target=accept_connection, daemon=True).start()

def initialize_client():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False

    while not connected and thread_running:
        try:
            client_sock.connect((IP, SERVER_PORT))
            print("Connected to server.")
            global current_screen
            current_screen = "client_lobby"
            connected = True
        except Exception as e:
            if thread_running:
                print("Failed to connect, retrying...", e)
            time.sleep(1)

    def send_input():
        while thread_running:
            if not pygame.get_init():
                break
            keys = pygame.key.get_pressed()
            input_state = {
                "left": keys[pygame.K_a],
                "right": keys[pygame.K_d],
                "jump": keys[pygame.K_w],
                "attack": keys[pygame.K_f]
            }
            try:
                payload = pickle.dumps(input_state)
                message = b"INPUT:" + payload
                length = len(message).to_bytes(4, 'big')
                client_sock.sendall(length + message)
            except Exception as e:
                if thread_running:
                    print("Error sending input:", e)
                break
            time.sleep(0.05)

    def receive_data():
        global current_screen, winner_player_number, scroll_x, powerups, played_video
        while thread_running:
            try:
                length_data = recv_exact(client_sock, 4)
                if not length_data:
                    break
                message_length = int.from_bytes(length_data, 'big')
                message = recv_exact(client_sock, message_length)
                if not message:
                    break

                if message.startswith(b"CMD:"):
                    command = message[4:].decode().strip()
                    if command == "SWITCH_TO_GAMEPLAY":
                        current_screen = "video"
                    elif command == "PLAYER1_WINS":
                        winner_player_number = 1
                        current_screen = "winner"
                    elif command == "PLAYER2_WINS":
                        winner_player_number = 2
                        current_screen = "winner"
                    elif command == "RETURN_TO_LOBBY":
                        reset_game()
                        current_screen = "client_lobby"

                elif message.startswith(b"DATA:"):
                    try:
                        game_state = pickle.loads(message[5:])
                        if isinstance(game_state, dict):
                            player1.deserialize(game_state["player1"])
                            player2.deserialize(game_state["player2"])
                            player1.refresh_sprite()
                            player2.refresh_sprite()
                            player1.projectiles.clear()
                            player2.projectiles.clear()
                            for proj_data in game_state.get("projectiles", []):
                                proj_type = proj_data.get("type", "normal")
                                if proj_type == "cherry":
                                    projectile = CherryProjectile.deserialize(proj_data)
                                else:
                                    projectile = Projectile.create_projectile_from_data(proj_data)
                                player1.projectiles.append(projectile)
                            powerups.clear()
                            for powerup_data in game_state.get("power_ups", []):
                                powerup = Powerup.deserialize(powerup_data)
                                if powerup:
                                    powerups.append(powerup)
                            incoming_platform_data = game_state.get("platforms", [])
                            for i, platform_data in enumerate(incoming_platform_data):
                                if i < len(platforms):
                                    platforms[i].rect.x = platform_data["x"]
                                    platforms[i].rect.y = platform_data["y"]
                                else:
                                    platforms.append(Platform.deserialize(platform_data))
                    except Exception as e:
                        if thread_running:
                            print("Deserialization Error:", e)
                        break
                else:
                    if thread_running:
                        print("Unknown message type:", message)
            except Exception as e:
                if thread_running:
                    print("Receive thread error:", e)
                break
        client_sock.close()

    threading.Thread(target=receive_data).start()
    threading.Thread(target=send_input).start()

def reset_game():
    player1.reset_state()
    player2.reset_state()

# === GAME SETUP ===

played_video = False

def play_video(video_path):
    clip = VideoFileClip(video_path)

    # Resize the clip to match your screen size
    clip = clip.resize((WIDTH, HEIGHT))

    for frame in clip.iter_frames(fps=clip.fps, dtype="uint8"):
        # Convert frame to pygame surface
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        screen.blit(frame_surface, (0, 0))
        pygame.display.update()
        clock.tick(clip.fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    clip.close()

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
Powerup.scroll_speed = 1  # Try + or - depending on scroll direction

# Create list of power ups

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
player2 = Player(500, GROUND_Y, donut_frames, hangry_donut_frames, "imgs/healthbar/donut.png", "donut", "left", weapon="gun", projectile_image="imgs/sprinkle_ammo.png")

player1.set_opponents([player2])
player2.set_opponents([player1])

# powerups = [Powerup(300, GROUND_Y, "cherry"), Powerup(600, GROUND_Y, "blueberry")]
powerups = []

platforms = [
    Platform(100, 300, "imgs/platform.png", width=120, move_range=70, speed=.7),
    Platform(300, 200, "imgs/platform.png", width=120, move_range=50, speed=.7),
    Platform(500, 350, "imgs/platform.png", width=120, move_range=100, speed=1),
    Platform(600, 150, "imgs/platform.png", width=120, move_range=70, speed=.8),
]

def draw_gameplay_scene(surface):
    surface.fill((180, 180, 180))

    # Draw stage
    stage_y_axis = GROUND_Y - stage.get_height() + offset
    surface.blit(stage, (0, stage_y_axis))

    # Draw conveyor belt
    surface.blit(conveyor_belt, (scroll_x, belt_y_axis))
    surface.blit(conveyor_belt, (scroll_x - conveyor_belt.get_width(), belt_y_axis))

    # Draw players
    player1.draw(surface)
    player2.draw(surface)

    for projectile in player1.projectiles:
        projectile.draw(surface)
    for projectile in player2.projectiles:
        projectile.draw(surface)

    for powerup in list(powerups):
        powerup.draw(surface)

    for platform in platforms:
        platform.draw(surface)
    
    # Health bars & profiles
    surface.blit(profile1, (20, HEIGHT - 80))
    surface.blit(profile2, (WIDTH - 80, HEIGHT - 80))
    player1.draw_health(surface, 90, HEIGHT - 60)
    player2.draw_health(surface, WIDTH - 290, HEIGHT - 60)

    # Draw player power-ups
    player1.draw_powerup(surface, 90, HEIGHT - 30, is_player1=True)
    player2.draw_powerup(surface, WIDTH - 90, HEIGHT - 30, is_player1=False)


def run_client_gameplay_loop(events):
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    draw_gameplay_scene(screen)


def run_server_gameplay_loop(events):
    global powerups, scroll_x, last_spawn_time
    global current_screen, winner_player_number

    keys = pygame.key.get_pressed()

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                player1.attack()

    player1.update(keys, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_f, player2)

    input_state = client_input if client_input else {"left": False, "right": False, "jump": False, "attack": False}

    # Simulate keys dictionary for Player 2
    player2_keys = {
        pygame.K_a: input_state["left"],
        pygame.K_d: input_state["right"],
        pygame.K_w: input_state["jump"],
        pygame.K_f: input_state["attack"]
    }

    if input_state["attack"]:
        player2.attack()

    player2.update(player2_keys, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_f, player1)

    player1.check_attack_collision(player2)
    player2.check_attack_collision(player1)

    player1.update_mode()
    player2.update_mode()

    scroll_x += 1
    if scroll_x >= conveyor_belt.get_width():
        scroll_x = 0

    # Power-up spawning
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time > SPAWN_POWERUP_INTERVAL:
        last_spawn_time = current_time
        # print("in game loop, updated last_spawn_time: ", last_spawn_time)

        # Randomly spawn new power-up (0=blueberry, 1=cherry)
        rand = random.randint(0, 10)
        if (rand % 2 == 0):
            # generate pretzel
            new_powerup = Powerup(-50, 435, "pretzel")
        elif (rand < 5):
            # generate blueberry
            new_powerup = Powerup(-50, 435, "blueberry")
        elif (rand >= 5 ):
            # generate cherrya
            new_powerup = Powerup(-50, 435, "cherry")

        powerups.append(new_powerup)

    for powerup in list(powerups):  # Iterate over a copy of the list
        powerup.check_collision(player1)
        powerup.check_collision(player2)
        powerup.update()
        if powerup.collected:
            powerups.remove(powerup)

    # Update platforms
    for platform in platforms:
        platform.update()
        platform.check_collision(player1)
        platform.check_collision(player2)

    draw_gameplay_scene(screen)
    
    if player1.health <= 0 or player2.health <= 0:
        winner_player_number = 2 if player1.health <= 0 else 1
        current_screen = "winner"

        if client_conn:
            try:
                if winner_player_number == 1:
                    command = b"CMD:PLAYER1_WINS\n"
                else:
                    command = b"CMD:PLAYER2_WINS\n"
                length = len(command).to_bytes(4, 'big')
                client_conn.sendall(length + command)
            except Exception as e:
                print("Failed to send winner message:", e)
        return

    if client_conn:
        try:
            game_state = {
                "player1": player1.serialize(),
                "player2": player2.serialize(),
                "projectiles": [p.serialize() for p in player1.projectiles + player2.projectiles],
                "power_ups": [p.serialize() for p in powerups],
                "scroll_x": scroll_x,
                "platforms": [platform.serialize() for platform in platforms]
            }

            payload = pickle.dumps(game_state)
            message = b"DATA:" + payload
            length = len(message).to_bytes(4, 'big')  # 4-byte length prefix
            client_conn.sendall(length + message)

        except Exception as e:
            print("Failed to send game state:", e)

# === MAIN GAME LOOP ===

while running:
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and current_screen == "client_wait" and input_active:
            if event.key == pygame.K_BACKSPACE:
                client_ip_input = client_ip_input[:-1]
            elif event.key == pygame.K_RETURN:
                IP = client_ip_input  # ← Use this IP when connecting
                threading.Thread(target=initialize_client, daemon=True).start()
            else:
                if len(client_ip_input) < 15:
                    client_ip_input += event.unicode


    if current_screen != previous_screen:
        if current_screen == "title":
            setup_title_screen()
        elif current_screen == "multiplayer_options":
            setup_multiplayer_options_screen()
        elif current_screen == "client_input":
            setup_client_input_screen()
        elif current_screen == "server_lobby":
            setup_server_lobby_screen()
        elif current_screen == "winner":
            if winner_player_number is not None:
                setup_winner_screen(winner_player_number)

        previous_screen = current_screen


    if current_screen == "title":
        run_title_screen(events)
    elif current_screen == "multiplayer_options":
        run_multiplayer_options_screen(events)
    elif current_screen == "server_wait":
        display_ui("imgs/ui/server-waiting-screen.png")
        ip_text = font.render(f"Your IP: {IP}", True, (235, 153, 176))
        text_rect = ip_text.get_rect()
        screen.blit(ip_text, (WIDTH - text_rect.width - 20, HEIGHT - text_rect.height - 20))
    elif current_screen == "client_wait":
        display_ui("imgs/ui/client-waiting-screen.png")
    elif current_screen == "client_input":
        run_client_input_screen(events)
    elif current_screen == "server_lobby":
        run_server_lobby_screen(events)
    elif current_screen == "client_lobby":
        display_ui("imgs/ui/client-lobby-screen.png")
    elif current_screen == "server_gameplay":
        run_server_gameplay_loop(events)
    elif current_screen == "client_gameplay":
        run_client_gameplay_loop(events)
    elif current_screen == "winner":
        run_winner_screen(events)
    elif current_screen == "video":
        if played_video == False:
            play_video("imgs/main.mp4")
            played_video = True
        current_screen = "client_gameplay"

    pygame.display.update()
    clock.tick(60)

pygame.mouse.set_cursor(arrow_cursor)
thread_running = False
pygame.quit()
sys.exit()
