import pygame

sfx_shoot_donut = pygame.mixer.Sound("sounds/Fire 1.mp3")
sfx_throw_sprinkle = pygame.mixer.Sound("sounds/Fire 2.mp3")
sfx_shoot_blueberry = pygame.mixer.Sound("sounds/Fire 4.mp3")
sfx_bread_bazooka = pygame.mixer.Sound("sounds/Fire 5.mp3")
sfx_sword_swish = pygame.mixer.Sound("sounds/swish_2.wav")

collect_item = pygame.mixer.Sound("sounds/Rise01.wav")
# collect_blueberry = pygame.mixer.Sound("sounds/Rise03")
# collect_cherry = pygame.mixer.Sound("sounds/Rise02")

bg_music = pygame.mixer.music.load("sounds/The Last Encounter Short Loop.wav")

def start_music():
    # Load background music and loop
    pygame.mixer.music.load("sounds/The Last Encounter Short Loop.wav")
    pygame.mixer.music.play(-1)

# def pause_music():

# def collect_item():
#     pygame.mixer.Sound(collect_item)