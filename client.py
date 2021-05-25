# Import the pygame module
import pygame

# Import menu to pygame
import pygame_menu

# dialog box
from tkinter import *
from tkinter import messagebox
Tk().wm_withdraw() #to hide the main window

import json

def show_popup(msg):
    messagebox.showinfo(msg,'OK')


import logging
logging.basicConfig(level=logging.INFO)

import math
# Import random for random numbers
import random


import pickle
# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
)


ABOUT = ['Authors: Dorota i Szymon',
         'PAS 2021']
MENU_THEME = pygame_menu.themes.THEME_DARK

# Define constants for the screen width and height
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
WINDOW_SIZE = (SCREEN_HEIGHT, SCREEN_WIDTH)
USER_NAME = "ProKiller"


# Define the Player object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Player(pygame.sprite.Sprite):
    def __init__(self, name, x, y, angle):
        super(Player, self).__init__()
        self.surf = pygame.image.load("media/player.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                x,
                y,
            )
        )
        self.angle = angle
        self.surf = pygame.transform.rotate(self.surf, angle-90)

        self.font = pygame.font.SysFont("Arial", 10)
        self.textSurf = self.font.render(name, 1, pygame.Color('white'))
        self.textSurfRotated = pygame.transform.rotate(self.textSurf, 180)

        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.surf.blit(self.textSurf, [self.rect.width/2 - W/2, self.rect.height/4 - H/2]) # 
        self.surf.blit(self.textSurfRotated, [self.rect.width/2 - W/2, self.rect.height*3/4 - H/2]) # 


# Define the Bullet object extending pygame.sprite.Sprite
# Instead of a surface, we use an image for a better looking sprite
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super(Bullet, self).__init__()
        self.surf = pygame.image.load("media/missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # The starting position is randomly generated, as is the speed
        self.rect = self.surf.get_rect(
            center=(
                x,
                y,
            )
        )
        self.speed = 17
        self.surf = pygame.transform.rotate(self.surf, angle+90)
        self.angle = angle


import asyncio
import websockets
import threading

pressed_keys = None
PLAYER_POSITIONS = None
async def serve_client():
    uri = "ws://localhost:8881"
    async with websockets.connect(uri) as websocket:
        while True:
            global pressed_keys
            if pressed_keys is not None:
                # print(pressed_keys)
                # buttons = str(pressed_keys).split("(")[1].split(")")[0]
                # print(str(pressed_keys[:10]))
                # print("Not None")
                my_pickled_object = pickle.dumps(pressed_keys)
                await websocket.send(my_pickled_object)
            else:
                print("None")
                await websocket.send(str("None"))

            recived_from_server = await websocket.recv()
            if recived_from_server is not 'None':
                global PLAYER_POSITIONS
                PLAYER_POSITIONS = recived_from_server # pickle.loads(recived_from_server)
                # print(name)

            delay = 30.0/1000.0
            await asyncio.sleep(delay)

def start_loop():
    new_loop = asyncio.new_event_loop()
    new_loop.run_until_complete(serve_client())
    # loop.run_forever()

t = threading.Thread(target=start_loop)
t.start()

# Setup for sounds, defaults are good
pygame.mixer.init()

# Initialize pygame
pygame.init()

# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load and play our background music
# Sound source: http://ccmixter.org/files/Apoxode/59262
# License: https://creativecommons.org/licenses/by/3.0/
# pygame.mixer.music.load("media/Apoxode_-_Electric_1.mp3")
# pygame.mixer.music.play(loops=-1)

# Load all our sound files
# collision_sound = pygame.mixer.Sound("media/Collision.ogg")

# Set the base volume for all sounds
# collision_sound.set_volume(0.5)

# At this point, we're done, so we can stop and quit the mixer
# pygame.mixer.music.stop()
# pygame.mixer.quit()

bullets = pygame.sprite.Group()
clouds = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

def start_the_game():
    # Variable to keep our main loop running
    running = True

    # Create our 'player'
    # player = Player(USER_NAME)

    # Create groups to hold Bullet sprites, cloud sprites, and all sprites
    # - bullets is used for collision detection and position updates
    # - clouds is used for position updates
    # - all_sprites isused for rendering
    global bullets
    global clouds
    global all_sprites

    # bullets = pygame.sprite.Group()
    # clouds = pygame.sprite.Group()
    # all_sprites = pygame.sprite.Group()
    # all_sprites.add(player)

    # Our main loop
    while running:
    # Look at every event in the queue
        for event in pygame.event.get():
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop
                if event.key == K_ESCAPE:
                    running = False

            # Did the user click the window close button? If so, stop the loop
            elif event.type == QUIT:
                running = False

        # Get the set of keys pressed and check for user input
        global pressed_keys
        pressed_keys = pygame.key.get_pressed()
        # player.update(pressed_keys)


        # Update the position of our bullets and clouds
        # bullets.update()
        # clouds.update()

        # Fill the screen with sky blue
        screen.fill((55, 90, 55))

        # Draw all our sprites
        global PLAYER_POSITIONS
        if PLAYER_POSITIONS is not None:
            recived_objects = json.loads(PLAYER_POSITIONS)
            for recived_object in recived_objects:
                print(recived_object)
                if recived_object['type'] == 'bullet':
                    entity = Bullet(recived_object['centerx'], 
                                    recived_object['centery'], 
                                    recived_object['angle'])
                    screen.blit(entity.surf, entity.rect)
                elif recived_object['type'] == 'player':
                    entity = Player(recived_object['nickname'], 
                                    recived_object['centerx'], 
                                    recived_object['centery'], 
                                    recived_object['angle'])
                    screen.blit(entity.surf, entity.rect)

        # Check if any bullets have collided with the player
        # if pygame.sprite.spritecollideany(player, bullets):
        #     # If so, remove the player
        #     player.kill()

        #     # Stop any moving sounds and play the collision sound
        #     # move_up_sound.stop()
        #     # move_down_sound.stop()
        #     # collision_sound.play()

        #     # Stop the loop
        #     running = False

        # Flip everything to the display
        pygame.display.flip()

        # Ensure we maintain a 30 frames per second rate
        clock.tick(30)


def create_menu_main():
    join_menu = create_menu_join()
    about_menu = create_menu_about()
    main_menu = pygame_menu.Menu('PAS 2021 - CS 2D', WINDOW_SIZE[1], WINDOW_SIZE[0], theme=MENU_THEME)
    main_menu.add.text_input('Name: ', default=USER_NAME, maxchar=10, onchange=check_name)
    main_menu.add.button('Host Game', host_game)
    main_menu.add.button('Join game', join_menu)#  maxchar=4, onreturn=)
    main_menu.add.button('About', about_menu)
    main_menu.add.button('Quit', pygame_menu.events.EXIT)
    return main_menu
    

def create_menu_join():
    join_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[0],
        title='Play Menu',
        width=WINDOW_SIZE[1],
        theme=MENU_THEME
    )

    join_menu.add.text_input('Room Key: ', default='', maxchar=4, onchange=update_join_status)
    join_status_button = join_menu.add.button('Status: Insert code', None)
    # join_menu.add.button('Join room', join_room)
    join_menu.add.button('Main menu', pygame_menu.events.BACK)
    join_status_button.add_draw_callback(draw_update_function_join_status_button)
    return join_menu


join_status = 'Insert room key'
def update_join_status(code):
    logging.debug(f'Room key {code}')
    global join_status
    if len(code) < 4:
        join_status = 'Insert room key...'
    else:
        try:
            join_status = 'Key looking okey!'
            join_room(code)
        except:
            join_status = 'Joining fail :('


def join_room(code):
    try:
        logging.info('TODO - próba dołączenia do  room')
    except:
        show_popup("Error")
    return


def draw_update_function_join_status_button(widget, menu):
    global join_status
    widget.set_title(join_status)


def create_menu_about():

    about_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[0],
        title='About',
        width=WINDOW_SIZE[1],
        theme=MENU_THEME
    )

    for m in ABOUT:
        about_menu.add.label(m, align=pygame_menu.locals.ALIGN_CENTER, font_size=20)
    
    about_menu.add.vertical_margin(30)
    about_menu.add.button('Return to menu', pygame_menu.events.BACK)
    return about_menu


def check_name(value):
    global USER_NAME
    USER_NAME = value
    # TODO - Update pliku / serializacja


def host_game():
    start_the_game()
    # messagebox.showinfo('Continue','OK')
    return


if __name__ == '__main__':
    main_menu = create_menu_main()
    while(True):
        main_menu.mainloop(screen)