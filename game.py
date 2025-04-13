import pygame
import sys
import time
from player import Player, WIDTH, HEIGHT, GROUND_Y
from button import Button
from projectile import Projectile
import socket
import threading
import pickle
import time

# === CONFIG ===
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 10141
#IP = "192.168.182.18"
IP = "10.194.41.9"
client_input = None
client_conn = None

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

def setup_server_lobby_screen():
    global lobby_bg, play_button
    lobby_bg = pygame.image.load("imgs/ui/server-lobby-screen.png").convert()
    play_button_x = (WIDTH - button_width) // 2
    play_button_y = HEIGHT - 340
    play_button = Button("Play Game", play_button_x, play_button_y, button_width, button_height, button_font)

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
        threading.Thread(target=initialize_client, daemon=True).start()
        current_screen = "client_wait"

def run_server_lobby_screen(events):
    global current_screen
    screen.blit(lobby_bg, (0, 0))

    mouse_pos = pygame.mouse.get_pos()
    if play_button.rect.collidepoint(mouse_pos):
        pygame.mouse.set_cursor(hand_cursor)
    else:
        pygame.mouse.set_cursor(arrow_cursor)

    play_button.draw(screen)

    if play_button.is_clicked(events):
        current_screen = "server_gameplay"
        if client_conn:
            try:
                command = b"CMD:SWITCH_TO_GAMEPLAY\n"
                length = len(command).to_bytes(4, 'big')
                client_conn.sendall(length + command)
            except:
                print("Failed to send mode switch to client.")

def display_ui(screen_path):
    bg = pygame.image.load(screen_path).convert()
    screen.blit(bg, (0, 0))

# === SERVER / CLIENT ===

def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    global client_input
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("Client disconnected")
                break
            command = data.decode().strip()
            print("Received:", command)
            client_input = command  # ✅ store the latest input
        except ConnectionResetError:
            print("Connection lost")
            break
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
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((SERVER_HOST, SERVER_PORT))
    server_sock.listen(1)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    def accept_connection():
        global current_screen, client_conn
        conn, addr = server_sock.accept()
        client_conn = conn  # ✅ store for sending game state
        print("Client connected!")
        current_screen = "server_lobby"
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    threading.Thread(target=accept_connection, daemon=True).start()

def initialize_client():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False

    while not connected:
        try:
            client_sock.connect((IP, SERVER_PORT))
            print("Connected to server.")
            global current_screen
            current_screen = "client_lobby"
            connected = True
        except Exception as e:
            print("Failed to connect, retrying...", e)
            time.sleep(1)

    def send_input():
        while True:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                client_sock.sendall(b"MOVE_LEFT\n")
            if keys[pygame.K_d]:
                client_sock.sendall(b"MOVE_RIGHT\n")
            if keys[pygame.K_w]:
                client_sock.sendall(b"JUMP\n")
            if keys[pygame.K_f]:
                client_sock.sendall(b"ATTACK\n")
            time.sleep(0.02)  # ~50 times per second

    def receive_data():
        while True:
            try:
                # Step 1: read the length prefix (4 bytes)
                length_data = recv_exact(client_sock, 4)
                if not length_data:
                    print("Disconnected")
                    break

                message_length = int.from_bytes(length_data, 'big')

                # Step 2: read the actual message
                message = recv_exact(client_sock, message_length)
                if not message:
                    print("Disconnected during message")
                    break

                # Step 3: process message
                if message.startswith(b"CMD:"):
                    command = message[4:].decode().strip()
                    if command == "SWITCH_TO_GAMEPLAY":
                        global current_screen
                        current_screen = "client_gameplay"
                        print("Switching to client gameplay!")

                elif message.startswith(b"DATA:"):
                    try:
                        game_state = pickle.loads(message[5:])  # skip "DATA:"
                        if isinstance(game_state, dict):
                            player1.deserialize(game_state["player1"])
                            player2.deserialize(game_state["player2"])
                            player1.refresh_sprite()
                            player2.refresh_sprite()

                            player1.projectiles.clear()
                            player2.projectiles.clear()

                            for proj_data in game_state.get("projectiles", []):
                                if "bread" in proj_data["image_path"]:
                                    player1.projectiles.append(Projectile.create_projectile_from_data(proj_data))
                                else:
                                    player2.projectiles.append(Projectile.create_projectile_from_data(proj_data))
                        else:
                            print("Received non-dictionary data:", game_state)
                    except Exception as e:
                        print("Error decoding pickle:", e)

                else:
                    print("Unknown message type:", message)

            except Exception as e:
                print("Error:", e)
                break

        client_sock.close()


    threading.Thread(target=receive_data, daemon=True).start()
    #threading.Thread(target=send_input, daemon=True).start()

# === GAME SETUP ===

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
player2 = Player(500, GROUND_Y, donut_frames, hangry_donut_frames, "imgs/healthbar/donut.png", "donut", "left", weapon="gun", projectile_image="imgs/sprinkle_ammo.png")

def draw_gameplay_scene(surface):
    surface.fill((240, 240, 240))
    pygame.draw.rect(surface, (180, 180, 180), (0, GROUND_Y + 40, WIDTH, HEIGHT - GROUND_Y))

    player1.draw(surface)
    player2.draw(surface)

    surface.blit(profile1, (20, HEIGHT - 80))
    surface.blit(profile2, (WIDTH - 80, HEIGHT - 80))
    player1.draw_health(surface, 90, HEIGHT - 60)
    player2.draw_health(surface, WIDTH - 290, HEIGHT - 60)

    elapsed_seconds = int(time.time() - start_time)
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    clock_text = font.render(f"{minutes:02}:{seconds:02}", True, (0, 0, 0))
    clock_rect = clock_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    surface.blit(clock_text, clock_rect)

def run_client_gameplay_loop(events):
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    draw_gameplay_scene(screen)


def run_server_gameplay_loop(events):
    keys = pygame.key.get_pressed()

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player1.attack()
            if event.key == pygame.K_f:
                player2.attack()

    player1.update(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_l, player2)
    player2.update(keys, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_f, player1)
    player1.check_attack_collision(player2)
    player2.check_attack_collision(player1)

    player1.update_mode()
    player2.update_mode()

    draw_gameplay_scene(screen)

    if client_conn:
        try:
            game_state = {
                "player1": player1.serialize(),
                "player2": player2.serialize(),
                "projectiles": [p.serialize() for p in player1.projectiles + player2.projectiles]
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

    if current_screen != previous_screen:
        if current_screen == "title":
            setup_title_screen()
        elif current_screen == "multiplayer_options":
            setup_multiplayer_options_screen()
        elif current_screen == "server_lobby":
            setup_server_lobby_screen()
        previous_screen = current_screen

    if current_screen == "title":
        run_title_screen(events)
    elif current_screen == "multiplayer_options":
        run_multiplayer_options_screen(events)
    elif current_screen == "server_wait":
        display_ui("imgs/ui/server-waiting-screen.png")
    elif current_screen == "client_wait":
        display_ui("imgs/ui/client-waiting-screen.png")
    elif current_screen == "server_lobby":
        run_server_lobby_screen(events)
    elif current_screen == "client_lobby":
        display_ui("imgs/ui/client-lobby-screen.png")
    elif current_screen == "server_gameplay":
        run_server_gameplay_loop(events)
    elif current_screen == "client_gameplay":
        run_client_gameplay_loop(events)

    pygame.display.update()
    clock.tick(60)

pygame.mouse.set_cursor(arrow_cursor)
pygame.quit()
sys.exit()
