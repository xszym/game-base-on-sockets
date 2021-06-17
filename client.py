import json
import logging
import socket
import ssl
import sys
import threading

import pygame
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from src.config import *
from src.serializers import deserialize_game_objects, map_pressed_keys_to_list
from src.utils import prepare_standard_msg, recv_msg_from_socket, recv_from_socket_to_pointer, \
    send_to_socket_from_pointer, decode_status_msg, prepare_game_msg, decode_game_msg

logging.basicConfig(level=logging.DEBUG)

MAIN_SERVER_SOCKET = None
IS_LOCAL = False
MY_UUID = None

if '-L' in sys.argv[1:] or '--local' in sys.argv[1:]:
    IS_LOCAL = True

if IS_LOCAL:
    SERVER_IP = '0.0.0.0'
else:
    SERVER_IP = os.environ.get('SERVER_IP', default=PUBLIC_SERVER_IP)


def create_ssl_context():
    ssl_context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH,
        cafile='keys/server.crt'
    )
    ssl_context.load_cert_chain('keys/client.crt', 'keys/client.key')
    ssl_context.check_hostname = False
    return ssl_context


ssl_context = create_ssl_context()


def connect_to_main_server():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, MAIN_SERVER_SOCKET_PORT))

        ssock = ssl_context.wrap_socket(sock, server_hostname=SERVER_IP)

        global MAIN_SERVER_SOCKET
        MAIN_SERVER_SOCKET = ssock
    except:
        logging.error("Error while connecting to main server")


def get_own_uuid():
    global MY_UUID
    global MAIN_SERVER_SOCKET
    if not MY_UUID:
        mess = prepare_standard_msg(command='REGISTER')
        logging.info("START REGISTER")
        MAIN_SERVER_SOCKET.sendall(mess)
        recv_data = recv_msg_from_socket(MAIN_SERVER_SOCKET)
        response = decode_status_msg(recv_data)
        logging.info(response)
        MY_UUID = response.get(data_header_code)


connect_to_main_server()
get_own_uuid()

pygame.mixer.init()
pygame.init()
pygame.font.init()
pygame.display.set_caption('PAS 2021 - Tank2D')
myfont = pygame.font.SysFont(FONT_NAME, 30)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

GAME_JOIN_CODE = ''
join_status = 'Insert room key'
AVAILABLE_GAMES = [('', '')]

pygame.mixer.music.load(BACKGROUND_MUSIC_FILE_NAME)
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(0.1)


def start_the_game(port):
    running = True
    is_game_over = False
    player_place = 'No place'
    game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    game_socket.connect((SERVER_IP, port))
    game_socket = ssl_context.wrap_socket(game_socket, server_hostname=SERVER_IP)

    recv_from_last_value = ['']
    send_to_newest_value = ['']
    recv_from_thread = threading.Thread(target=recv_from_socket_to_pointer, args=(game_socket, recv_from_last_value,))
    send_to_thread = threading.Thread(target=send_to_socket_from_pointer, args=(game_socket, send_to_newest_value,))
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
            screen.blit(textsurface, (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2)))
        else:
            pressed_keys = pygame.key.get_pressed()
            pressed_keys = map_pressed_keys_to_list(pressed_keys)
            global MY_UUID
            response = f"{USER_NAME},{MY_UUID},{json.dumps(pressed_keys)}"
            msg = prepare_game_msg(response)
            send_to_newest_value[0] = msg

            if recv_from_last_value[0] != '':
                game_data = recv_from_last_value[0]
                game_data = decode_game_msg(game_data)
                if 'GAME_OVER' in game_data:
                    is_game_over = True
                    player_place = game_data[1]
                else:
                    player_positions = game_data
                    if player_positions is not None:
                        entities = deserialize_game_objects(player_positions)
                        for entity in entities:
                            screen.blit(entity.surf, entity.rect)

        global GAME_JOIN_CODE
        textsurface = myfont.render(GAME_JOIN_CODE, False, (0, 0, 0))
        screen.blit(textsurface, (0, 0))
        pygame.display.flip()
        clock.tick(30)
    send_to_newest_value[0] = None
    game_socket.close()


def create_menu_main():
    join_menu = create_menu_join()
    about_menu = create_menu_about()
    main_menu = pygame_menu.Menu('PAS 2021 - TANKS 2D', WINDOW_SIZE[1], WINDOW_SIZE[0], theme=MENU_THEME)
    main_menu.add.text_input('Name: ', default=USER_NAME, maxchar=7, onchange=check_name)
    main_menu.add.button('Host Game', host_game)
    main_menu.add.button('Join game', join_menu)  # maxchar=4, onreturn=)
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
    game_selector = join_menu.add.selector('Select game ',
                                           AVAILABLE_GAMES,
                                           onchange=list_games,
                                           onreturn=join_room,
                                           selector_id='select_difficulty')
    join_menu.add.button('Main menu', pygame_menu.events.BACK)
    join_status_button.add_draw_callback(draw_update_function_join_status_button)
    game_selector.add_draw_callback(draw_update_function_games_list_selector)
    return join_menu


def list_games(_=None, __=None):
    global MY_UUID
    mess = prepare_standard_msg(command='LIST_GAMES', auth=MY_UUID)
    try:
        MAIN_SERVER_SOCKET.sendall(mess)
    except:
        connect_to_main_server()
        MAIN_SERVER_SOCKET.sendall(mess)

    recv_data = recv_msg_from_socket(MAIN_SERVER_SOCKET)
    response = decode_status_msg(recv_data)
    if response['code'] == 200:
        global AVAILABLE_GAMES
        games = response.get('data', '[]')
        games = eval(games)
        games = [(nick, code) for nick, code in games]
        if len(games) > 0:
            AVAILABLE_GAMES = games
        else:
            AVAILABLE_GAMES = [('', '')]
        logging.debug("AVAILABLE_GAMES", AVAILABLE_GAMES)
    else:
        logging.error(f"Code {response['code']} with message {response['message']} ")


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


def join_room(code, _=None):
    global MY_UUID
    if isinstance(code, tuple):
        code = code[0][1]
    mess = prepare_standard_msg(command='JOIN_CHANNEL', auth=MY_UUID, data=code)
    try:
        MAIN_SERVER_SOCKET.sendall(mess)
    except:
        connect_to_main_server()
        MAIN_SERVER_SOCKET.sendall(mess)

    recv_data = recv_msg_from_socket(MAIN_SERVER_SOCKET)
    response = decode_status_msg(recv_data)

    if response['code'] == 200:
        global GAME_JOIN_CODE
        GAME_JOIN_CODE = code
        port = response['data']
        start_the_game(int(port))
    else:
        global join_status
        join_status = 'Joining fail :('
        logging.error(f"Code {response['code']} with message {response['message']} ")


def draw_update_function_join_status_button(widget, menu):
    global join_status
    widget.set_title(join_status)


def draw_update_function_games_list_selector(widget, menu):
    global AVAILABLE_GAMES
    widget.update_items(AVAILABLE_GAMES)


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


def host_game():
    global MY_UUID
    mess = prepare_standard_msg(command='START_CHANNEL', auth=MY_UUID)
    try:
        MAIN_SERVER_SOCKET.sendall(mess)
    except:
        connect_to_main_server()
        MAIN_SERVER_SOCKET.sendall(mess)

    recv_data = recv_msg_from_socket(MAIN_SERVER_SOCKET)
    response = decode_status_msg(recv_data)
    if response['code'] == 200:
        code = response['data']
        join_room(code)
    else:
        logging.info('TODO - Error during hosting')
        logging.error(f"Code {response['code']} with message {response['message']} ")


if __name__ == '__main__':
    main_menu = create_menu_main()
    while True:
        main_menu.mainloop(screen)
