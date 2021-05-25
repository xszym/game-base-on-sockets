# Import the pygame module
import pygame

# Import menu to pygame
import pygame_menu

import asyncio
import websockets
import threading

# dialog box
from tkinter import *
from tkinter import messagebox
Tk().wm_withdraw() #to hide the main window

import json
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

from game_config import *
from game_classes import Player, Bullet


def show_popup(msg):
    messagebox.showinfo(msg,'OK')


pressed_keys = None
PLAYER_POSITIONS = None
async def serve_client():
    uri = "ws://localhost:8881"
    async with websockets.connect(uri) as websocket:
        while True:
            global pressed_keys
            if pressed_keys is not None:
                my_pickled_object = pickle.dumps(pressed_keys)
                await websocket.send(my_pickled_object)
            else:
                await websocket.send(str("None"))

            recived_from_server = await websocket.recv()
            if recived_from_server is not 'None':
                global PLAYER_POSITIONS
                PLAYER_POSITIONS = recived_from_server

            delay = 30.0/1000.0
            await asyncio.sleep(delay)

def start_loop():
    new_loop = asyncio.new_event_loop()
    new_loop.run_until_complete(serve_client())

t = threading.Thread(target=start_loop)
t.start()


pygame.mixer.init()
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load and play our background music
# Sound source: http://ccmixter.org/files/Apoxode/59262
# License: https://creativecommons.org/licenses/by/3.0/
# pygame.mixer.music.load("media/Apoxode_-_Electric_1.mp3")
# pygame.mixer.music.play(loops=-1)

# collision_sound = pygame.mixer.Sound("media/Collision.ogg")
# collision_sound.set_volume(0.5)

# pygame.mixer.music.stop()
# pygame.mixer.quit()

bullets = pygame.sprite.Group()
clouds = pygame.sprite.Group()

def start_the_game():
    running = True

    global bullets
    global clouds
    global all_sprites
    global pressed_keys

    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

            elif event.type == QUIT:
                running = False

        pressed_keys = pygame.key.get_pressed()

        screen.fill(GAME_BG)

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

        pygame.display.flip()
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