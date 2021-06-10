# Import the pygame module
import pygame

# Import menu to pygame
import pygame_menu

import asyncio
# import websockets
import threading
import socket
from queue import Queue

import sys
import json
import logging
logging.basicConfig(level=logging.INFO)

from time import sleep
import math
# Import random for random numbers
import random
import pickle
# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from src.config import *
from src.game_classes import Player, Bullet
from src.utils import prepare_message, recv_msg_from_socket, recv_from_socket_to_pointer, send_to_socket_from_pointer


MAIN_SERVER_SOCKET = None
IS_LOCAL = False
if '-L' in sys.argv[1:]:
    IS_LOCAL = True

if IS_LOCAL:
    SERVER_IP = '0.0.0.0'
else:
    SERVER_IP = os.environ.get('SERVER_IP', default='159.89.9.110')


def connect_to_main_server():
    global MAIN_SERVER_SOCKET
    try:
        MAIN_SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        MAIN_SERVER_SOCKET.connect((SERVER_IP, MAIN_SERVER_SOCKET_PORT))
    except:
        print("Error while connecting to main server")
connect_to_main_server()


pygame.mixer.init()
pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 30)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

GAME_JOIN_CODE = ''

# Load and play our background music
# Sound source: http://ccmixter.org/files/Apoxode/59262
# License: https://creativecommons.org/licenses/by/3.0/
# pygame.mixer.music.load("media/Apoxode_-_Electric_1.mp3")
# pygame.mixer.music.play(loops=-1)

# collision_sound = pygame.mixer.Sound("media/Collision.ogg")
# collision_sound.set_volume(0.5)

# pygame.mixer.music.stop()
# pygame.mixer.quit()


def deserialize_game_objects(msg):
    recived_objects = json.loads(msg)
    entities = []
    for recived_object in recived_objects:
        if recived_object['type'] == 'bullet':
            entity = Bullet(recived_object['centerx'], 
                            recived_object['centery'], 
                            recived_object['angle'])
            entities.append(entity)
        elif recived_object['type'] == 'player':
            entity = Player(recived_object['nickname'], 
                            recived_object['centerx'], 
                            recived_object['centery'], 
                            recived_object['angle'],
                            recived_object['health']
                            )
            entities.append(entity)
    return entities


def start_the_game(port):
    running = True
    is_game_over = False
    player_place = 'No place'
    game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    game_socket.connect((SERVER_IP, port))

    recv_from_last_value = ['']
    send_to_newest_value = ['']
    recv_from_thread = threading.Thread(target=recv_from_socket_to_pointer, args=(game_socket, recv_from_last_value, ))
    send_to_thread = threading.Thread(target=send_to_socket_from_pointer, args=(game_socket, send_to_newest_value, ))
    recv_from_thread.start()
    send_to_thread.start()

    while running:
        screen.fill(GAME_BG)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == QUIT:
                running = False
        if is_game_over:
            textsurface = myfont.render(f"You got {player_place} place", False, (0, 0, 0))
            screen.blit(textsurface,(int(SCREEN_WIDTH/2),int(SCREEN_HEIGHT/2)))
        else:
            pressed_keys = pygame.key.get_pressed()
            dumped_pressed_keys = json.dumps(pressed_keys)
            msg = prepare_message(command='UPDATE_GAME',data=dumped_pressed_keys)
            send_to_newest_value[0] = msg
            
            PLAYER_POSITIONS = None
            if recv_from_last_value[0] != '':
                MSG_FROM_SERVER = recv_from_last_value[0]
                headers = MSG_FROM_SERVER[0]
                
                if headers[command_header_code] == 'GAME_OVER':
                    is_game_over = True
                    player_place = MSG_FROM_SERVER[1]
                elif headers[command_header_code] == 'UPDATE_GAME':
                    PLAYER_POSITIONS = MSG_FROM_SERVER[1]
                    if PLAYER_POSITIONS is not None:
                        entities = deserialize_game_objects(PLAYER_POSITIONS)
                        for entity in entities:
                            screen.blit(entity.surf, entity.rect)

        global GAME_JOIN_CODE
        textsurface = myfont.render(GAME_JOIN_CODE, False, (0, 0, 0))
        screen.blit(textsurface,(0,0))
        pygame.display.flip()
        clock.tick(30)
    send_to_newest_value[0] = None
    game_socket.close()


def create_menu_main():
    join_menu = create_menu_join()
    about_menu = create_menu_about()
    main_menu = pygame_menu.Menu('PAS 2021 - TANKS 2D', WINDOW_SIZE[1], WINDOW_SIZE[0], theme=MENU_THEME)
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
    mess = prepare_message(command='JOIN_CHANNEL',data=code)
    try:
        MAIN_SERVER_SOCKET.sendall(mess)
    except:
        connect_to_main_server()
        MAIN_SERVER_SOCKET.sendall(mess)
    
    headers, port = recv_msg_from_socket(MAIN_SERVER_SOCKET)
    print(headers, port)
    if headers.get(status_header_code) == "SUCC":
        global GAME_JOIN_CODE
        GAME_JOIN_CODE = code
        start_the_game(int(port))
    else:
        logging.info('TODO - Error podczas dołączania do room ')
        raise "Join during joinning to room"


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
    mess = prepare_message(command='START_CHANNEL',auth='')
    try:
        MAIN_SERVER_SOCKET.sendall(mess)
    except:
        connect_to_main_server()
        MAIN_SERVER_SOCKET.sendall(mess)

    headers, code = recv_msg_from_socket(MAIN_SERVER_SOCKET)
    print("HOST_GAME", headers, code)
    join_room(code)
    # start_the_game()
    # messagebox.showinfo('Continue','OK')
    # return


if __name__ == '__main__':
    main_menu = create_menu_main()
    while(True):
        main_menu.mainloop(screen)
