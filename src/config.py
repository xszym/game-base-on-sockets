import os

import pygame_menu


# GAME
ABOUT = ['Authors: Dorota i Szymon',
         'PAS 2021']
MENU_THEME = pygame_menu.themes.THEME_DARK
FONT_NAME = 'Comic Sans MS'

# Sound source: http://ccmixter.org/files/Apoxode/59262
# License: https://creativecommons.org/licenses/by/3.0/
BACKGROUND_MUSIC_FILE_NAME = "media/Apoxode_-_Electric_1.ogg"


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
WINDOW_SIZE = (SCREEN_HEIGHT, SCREEN_WIDTH)
USER_NAME = "PLAYER"

PLAYER_DEFAULT_SPEED = 5
BULLET_DEFAULT_SPEED = 17
BULLET_FROM_PLAYER_OFFSET = 5
BULLET_GAUSS_SIGMA = 15 / 3
DEFAULT_PLAYER_HEALTH = 50

GAME_BG = (55, 90, 55)

K_UP = 0
K_DOWN = 1
K_LEFT = 2
K_RIGHT = 3
K_ESCAPE = 4
K_SPACE = 5


# SOCKETS / NETWORK
PUBLIC_SERVER_IP = '159.89.9.110'
MAIN_SERVER_SOCKET_PORT = int(os.environ.get('PORT', default=40000))
MIN_PORT = int(os.environ.get('GAME_PORTS_MIN', default=40400))
MAX_PORT = int(os.environ.get('GAME_PORTS_MAX', default=40420))
MAX_TIME_WITH_NO_SEND_TO_SOCKET_IN_GAME_IN_MILLIS = 1000

RECV_BUFFOR_SIZE = 1
SERVER_NO_OF_QUEUED_CONNECTIONS = 5

soft_end = '\r\n'
hard_end = '\r\n\r\n'

command_header_code = 'command'
status_header_code = 'status'
length_header_code = 'length'
auth_header_code = 'auth'
data_header_code = 'data'
